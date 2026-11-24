"""
LuminaLearn AI — Study documents for the tutor.
Module: backend/app/services/document_service.py

A learner uploads a PDF (lecture notes, a textbook chapter, an assignment) and asks the tutor about
it. The text is extracted page by page, stored per learner, and indexed with the same hybrid
retriever the curriculum uses, so answers cite the page they came from.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import re
import uuid
from collections import OrderedDict

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.rag.curriculum_rag import CurriculumRAGService
from app.models.tutor_document import TutorDocument

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_PAGES = 300
MAX_TEXT_CHARS = 1_500_000
MAX_DOCUMENTS_PER_USER = 10
MAX_DOCUMENTS_PER_QUESTION = 5
EXTRACTION_TIMEOUT_S = 45.0
_INDEX_CACHE_SIZE = 32

_HYPHEN_BREAK = re.compile(r"(\w)-\n(\w)")
_SPACES = re.compile(r"[ \t ]+")
_BLANK_LINES = re.compile(r"\n{3,}")
_UNSAFE_NAME = re.compile(r"[^\w.\- ()]+")


class DocumentError(ValueError):
    """The upload cannot be used; the message is safe to show to the learner."""


def clean_page_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\x00", "")
    text = _HYPHEN_BREAK.sub(r"\1\2", text)  # re-join words hyphenated across a line break
    text = _SPACES.sub(" ", text)
    return _BLANK_LINES.sub("\n\n", text).strip()


def extract_pdf_pages(data: bytes) -> list[tuple[int, str]]:
    """(page number, text) for every page with selectable text. Raises DocumentError when nothing is usable."""
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    if not data.startswith(b"%PDF-"):
        raise DocumentError("That file is not a PDF.")
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted and not reader.decrypt(""):
            raise DocumentError("This PDF is password-protected. Remove the password and upload it again.")
        if len(reader.pages) > MAX_PAGES:
            raise DocumentError(f"This PDF has {len(reader.pages)} pages; the limit is {MAX_PAGES}. Upload the chapter you need.")
        pages: list[tuple[int, str]] = []
        total = 0
        for number, page in enumerate(reader.pages, start=1):
            try:
                text = clean_page_text(page.extract_text() or "")
            except Exception as exc:  # noqa: BLE001 - one unreadable page must not lose the rest
                logger.info("Skipping unreadable PDF page %d: %s", number, exc)
                continue
            if not text:
                continue
            total += len(text)
            if total > MAX_TEXT_CHARS:
                raise DocumentError("This PDF has too much text for the tutor. Upload a shorter part of it.")
            pages.append((number, text))
    except DocumentError:
        raise
    except (PdfReadError, ValueError, KeyError, TypeError, IndexError) as exc:
        raise DocumentError("This PDF could not be read. It may be damaged; try exporting it again.") from exc
    if not pages:
        raise DocumentError(
            "No text could be found in this PDF. It may be scanned images: export it with selectable text, "
            "or run OCR on it first."
        )
    return pages


def safe_filename(name: str | None) -> str:
    base = (name or "document.pdf").replace("\\", "/").rsplit("/", 1)[-1]
    base = _UNSAFE_NAME.sub("_", base).strip(" ._") or "document"
    if not base.lower().endswith(".pdf"):
        base += ".pdf"
    return base[-120:]


async def read_upload(file: UploadFile) -> bytes:
    """Reads the upload in chunks, refusing it as soon as it passes the size limit."""
    buffer = bytearray()
    while chunk := await file.read(1024 * 1024):
        buffer.extend(chunk)
        if len(buffer) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"The PDF is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
            )
    return bytes(buffer)


class DocumentService:
    def __init__(self) -> None:
        self._indexes: OrderedDict[uuid.UUID, CurriculumRAGService] = OrderedDict()

    # ------------------------------------------------------------------ storage

    async def create(self, db: AsyncSession, user_id: uuid.UUID, file: UploadFile) -> TutorDocument:
        data = await read_upload(file)
        try:
            pages = await asyncio.wait_for(asyncio.to_thread(extract_pdf_pages, data), timeout=EXTRACTION_TIMEOUT_S)
        except DocumentError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except TimeoutError as exc:
            raise HTTPException(
                status_code=422,
                detail="Reading this PDF took too long. Upload a smaller part of it.",
            ) from exc
        filename = safe_filename(file.filename)
        pages_json = json.dumps(pages, ensure_ascii=False)
        existing = await db.scalar(
            select(TutorDocument).where(
                TutorDocument.user_id == user_id, TutorDocument.filename == filename, TutorDocument.pages_json == pages_json
            )
        )
        if existing is not None:  # the same file uploaded again: reuse it instead of storing a duplicate
            return existing
        count = await db.scalar(select(func.count()).select_from(TutorDocument).where(TutorDocument.user_id == user_id))
        if (count or 0) >= MAX_DOCUMENTS_PER_USER:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"You can keep up to {MAX_DOCUMENTS_PER_USER} documents. Delete one to upload another.",
            )
        document = TutorDocument(
            user_id=user_id,
            filename=filename,
            page_count=len(pages),
            char_count=sum(len(text) for _, text in pages),
            pages_json=pages_json,
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document

    async def list_for_user(self, db: AsyncSession, user_id: uuid.UUID) -> list[TutorDocument]:
        result = await db.execute(
            select(TutorDocument).where(TutorDocument.user_id == user_id).order_by(TutorDocument.created_at.desc())
        )
        return list(result.scalars())

    async def delete(self, db: AsyncSession, user_id: uuid.UUID, document_id: uuid.UUID) -> None:
        document = await db.get(TutorDocument, document_id)
        if document is None or document.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
        await db.delete(document)
        await db.commit()
        self._indexes.pop(document_id, None)

    async def load_indexes(
        self, db: AsyncSession, user_id: uuid.UUID, document_ids: list[uuid.UUID]
    ) -> list[CurriculumRAGService]:
        """Search indexes for the learner's own documents. Unknown or foreign ids are a 404."""
        wanted = list(dict.fromkeys(document_ids))[:MAX_DOCUMENTS_PER_QUESTION]
        if not wanted:
            return []
        result = await db.execute(
            select(TutorDocument).where(TutorDocument.user_id == user_id, TutorDocument.id.in_(wanted))
        )
        documents = {document.id: document for document in result.scalars()}
        if len(documents) != len(wanted):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
        return [self._index(documents[document_id]) for document_id in wanted]

    # ------------------------------------------------------------------ search

    def _index(self, document: TutorDocument) -> CurriculumRAGService:
        index = self._indexes.get(document.id)
        if index is None:
            pages = [(int(page), str(text)) for page, text in json.loads(document.pages_json)]
            index = CurriculumRAGService.from_pages(title=document.filename, pages=pages)
            self._indexes[document.id] = index
            while len(self._indexes) > _INDEX_CACHE_SIZE:
                self._indexes.popitem(last=False)
        else:
            self._indexes.move_to_end(document.id)
        return index


document_service = DocumentService()
