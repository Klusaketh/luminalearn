"""Study documents: a learner uploads a PDF and the tutor answers from it, citing pages."""
import json
import textwrap
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.services import document_service as documents_module
from app.services.document_service import clean_page_text, safe_filename
from tests.conftest import create_verified_learner

NOTES = [
    (
        "Photosynthesis converts light energy into chemical energy. It takes place in the chloroplasts of plant cells, "
        "where chlorophyll absorbs mostly red and blue light. The light-dependent reactions split water and release oxygen."
    ),
    (
        "The Calvin cycle uses ATP and NADPH from the light reactions to fix carbon dioxide into sugar. The enzyme RuBisCO "
        "attaches carbon dioxide to ribulose bisphosphate. Three turns of the cycle make one molecule of "
        "glyceraldehyde-3-phosphate."
    ),
    (
        "Cellular respiration releases energy from glucose. Glycolysis happens in the cytoplasm, and the Krebs cycle runs "
        "in the mitochondrial matrix, producing NADH and FADH2 for the electron transport chain."
    ),
]


def make_pdf(pages: list[str]) -> bytes:
    """A minimal, valid PDF with one Helvetica text page per string (no dependencies)."""
    count = len(pages)
    page_ids = [4 + 2 * i for i in range(count)]
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: f"<< /Type /Pages /Kids [{' '.join(f'{pid} 0 R' for pid in page_ids)}] /Count {count} >>".encode(),
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    for pid, text in zip(page_ids, pages, strict=True):
        operations = ["BT", "/F1 11 Tf", "14 TL", "50 750 Td"]
        for line in textwrap.wrap(text, 80):
            escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            operations.append(f"({escaped}) Tj T*")
        operations.append("ET")
        stream = "\n".join(operations).encode("latin-1")
        objects[pid] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> "
            f"/Contents {pid + 1} 0 R >>"
        ).encode()
        objects[pid + 1] = b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
    out = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}
    for number in sorted(objects):
        offsets[number] = len(out)
        out += f"{number} 0 obj\n".encode() + objects[number] + b"\nendobj\n"
    xref = len(out)
    size = max(objects) + 1
    out += f"xref\n0 {size}\n".encode() + b"0000000000 65535 f \n"
    for number in range(1, size):
        out += f"{offsets[number]:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {size} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


def parse_sse(body: str) -> list[tuple[str, dict]]:
    events = []
    for frame in body.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in frame.splitlines() if ": " in line)
        events.append((lines["event"], json.loads(lines["data"])))
    return events


async def _client_for_new_learner() -> AsyncClient:
    user = await create_verified_learner()
    headers = {"Authorization": f"Bearer {create_access_token(subject=str(user.id))}"}
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=headers)


async def _upload(client: AsyncClient, data: bytes, name: str = "biology-notes.pdf"):
    return await client.post("/api/v1/tutor/documents", files={"file": (name, data, "application/pdf")})


async def _ask(client: AsyncClient, message: str, document_ids: list[str]) -> list[tuple[str, dict]]:
    res = await client.post("/api/v1/tutor/chat/stream", json={"message": message, "document_ids": document_ids})
    assert res.status_code == 200, res.text
    return parse_sse(res.text)


# ---------------------------------------------------------------------- helpers


def test_page_text_is_cleaned():
    assert clean_page_text("mito-\nchondria   make\u00a0ATP\n\n\n\nnext") == "mitochondria make ATP\n\nnext"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("notes.pdf", "notes.pdf"), ("../../etc/passwd", "passwd.pdf"), ("C:\\Users\\me\\ch 3.PDF", "ch 3.PDF"), (None, "document.pdf")],
)
def test_filenames_are_made_safe(raw, expected):
    assert safe_filename(raw) == expected


# ---------------------------------------------------------------------- API


@pytest.mark.asyncio
async def test_upload_list_ask_and_delete():
    async with await _client_for_new_learner() as client:
        res = await _upload(client, make_pdf(NOTES))
        assert res.status_code == 201, res.text
        doc = res.json()
        assert doc["filename"] == "biology-notes.pdf" and doc["page_count"] == 3 and doc["char_count"] > 300

        listed = (await client.get("/api/v1/tutor/documents")).json()
        assert [d["id"] for d in listed] == [doc["id"]]
        again = await _upload(client, make_pdf(NOTES))
        assert again.json()["id"] == doc["id"], "re-uploading the same file reuses the stored document"
        assert len((await client.get("/api/v1/tutor/documents")).json()) == 1

        events = await _ask(client, "Which enzyme fixes carbon dioxide in the Calvin cycle?", [doc["id"]])
        citations = next(payload for name, payload in events if name == "citations")
        assert citations["grounded"] is True
        top = citations["items"][0]
        assert top["source"] == "biology-notes.pdf" and top["page"] == 2 and "p. 2" in top["label"]
        done = next(payload for name, payload in events if name == "done")
        assert done["grounded"] is True and done["text"]

        res = await client.delete(f"/api/v1/tutor/documents/{doc['id']}")
        assert res.status_code == 204
        assert (await client.get("/api/v1/tutor/documents")).json() == []
        res = await client.post("/api/v1/tutor/chat/stream", json={"message": "what is RuBisCO", "document_ids": [doc["id"]]})
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_summary_requests_get_passages_from_the_whole_document():
    async with await _client_for_new_learner() as client:
        doc = (await _upload(client, make_pdf(NOTES))).json()
        events = await _ask(client, "Summarise this PDF for me", [doc["id"]])
        citations = next(payload for name, payload in events if name == "citations")
        pages = {item["page"] for item in citations["items"] if item["source"] == "biology-notes.pdf"}
        assert pages == {1, 2, 3}


@pytest.mark.asyncio
async def test_documents_are_private_to_their_owner():
    async with await _client_for_new_learner() as owner, await _client_for_new_learner() as other:
        doc = (await _upload(owner, make_pdf(NOTES))).json()
        assert (await other.get("/api/v1/tutor/documents")).json() == []
        res = await other.post("/api/v1/tutor/chat/stream", json={"message": "what is RuBisCO", "document_ids": [doc["id"]]})
        assert res.status_code == 404
        assert (await other.delete(f"/api/v1/tutor/documents/{doc['id']}")).status_code == 404
        assert (await owner.get("/api/v1/tutor/documents")).json()[0]["id"] == doc["id"]


@pytest.mark.asyncio
async def test_unusable_uploads_are_refused_with_a_reason(monkeypatch):
    async with await _client_for_new_learner() as client:
        res = await _upload(client, b"hello, not a pdf", "notes.pdf")
        assert res.status_code == 422 and "not a PDF" in res.json()["detail"]

        res = await _upload(client, make_pdf([""]), "scan.pdf")  # a page with no text, like a scanned image
        assert res.status_code == 422 and "No text" in res.json()["detail"]

        res = await _upload(client, b"%PDF-1.4 broken", "broken.pdf")
        assert res.status_code == 422 and "could not be read" in res.json()["detail"]

        monkeypatch.setattr(documents_module, "MAX_UPLOAD_BYTES", 200)
        res = await _upload(client, make_pdf(NOTES))
        assert res.status_code == 413
        assert (await client.get("/api/v1/tutor/documents")).json() == []


@pytest.mark.asyncio
async def test_document_limit_per_learner(monkeypatch):
    monkeypatch.setattr(documents_module, "MAX_DOCUMENTS_PER_USER", 2)
    async with await _client_for_new_learner() as client:
        for index in range(2):
            assert (await _upload(client, make_pdf(NOTES[index : index + 1]))).status_code == 201
        res = await _upload(client, make_pdf(NOTES[2:]))
        assert res.status_code == 409 and "Delete one" in res.json()["detail"]


@pytest.mark.asyncio
async def test_unknown_document_id_is_not_found(authed_client: AsyncClient):
    res = await authed_client.post(
        "/api/v1/tutor/chat/stream", json={"message": "explain recursion", "document_ids": [str(uuid.uuid4())]}
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_guests_cannot_upload(async_client: AsyncClient):
    res = await async_client.post("/api/v1/tutor/documents", files={"file": ("a.pdf", make_pdf(NOTES), "application/pdf")})
    assert res.status_code == 401
