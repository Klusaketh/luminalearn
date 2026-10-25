"""
LuminaLearn AI — Full-Duplex Voice Session & Barge-In Engine.
Module: backend/app/services/voice_session.py

Protocol (JSON text frames unless noted)

Client -> server
  start        {token, topic?, modality?, tts?: "server"|"browser", voice?}   first frame (required)
  config       {topic?, modality?, tts?}                                     update mid-session
  transcript   {text}           final utterance from the browser's speech recognizer
  text         {text}           typed message while in voice mode
  audio_start  {format: "pcm16", sample_rate} | {format: "audio/ogg"}     begin an utterance
  <binary>     audio bytes for the current utterance (server speech-to-text path)
  audio_end    {}               transcribe the buffered utterance and answer it
  interrupt    {}               barge-in: the learner started talking over the tutor
  ping         {}

Server -> client
  ready        {session_id, authenticated, capabilities{llm, server_stt, server_tts}, tts}
  state        {state: "listening"|"thinking"|"speaking", turn_id}
  transcript   {turn_id, text}  (server speech-to-text result)
  route        {turn_id, agent, display_name, rationale, ...}
  token        {turn_id, text}  streamed reply text
  sentence     {turn_id, index, text}  speakable sentence (browser TTS speaks these)
  <binary>     8-byte header <uint32 LE turn_id><uint32 LE sample_rate> + mono PCM16 audio
  tts_fallback {turn_id, from_index}  server voice failed; speak sentences from index locally
  response_end {turn_id, text, agent, engine}
  audio_end    {turn_id}        no more audio will follow for this turn
  interrupted  {turn_id}        barge-in acknowledged; in-flight generation and TTS were cancelled
  error        {message, code, turn_id?}  code "turn_failed" is followed by audio_end and listening
  pong         {}

Authentication: browsers cannot set headers on a WebSocket, so the access token travels in the
`start` frame. A session without a valid token gets `error {code: "auth_required"}` and is closed
with code 4401 before any tutoring happens.

Barge-in: every learner turn runs as one asyncio task (STT -> agents -> TTS). An `interrupt`
frame, or a new utterance, cancels that task tree immediately; cancellation closes the Gemini
stream and the TTS worker, and the `interrupted` ack is only sent once nothing else for the
turn can be emitted. Audio frames carry the turn id so clients can drop stale audio in flight.
"""

import asyncio
import json
import logging
import re
import struct
import uuid
from contextlib import suppress
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect, WebSocketState

from ai.agents import DialogueTurn, Modality, SocraticOrchestrator, TutorRequest
from ai.agents.schema import MODALITIES
from ai.llm import GeminiGateway, LLMUnavailableError, pcm_to_wav
from app.api.deps import user_from_access_token
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.rate_limit import SlidingWindowRateLimiter
from app.models.user import User
from app.services.speech_text import speech_text
from app.services.tutor_service import MODALITY_BY_ENUM, rate_limit_key, tutor_service

logger = logging.getLogger("luminalearn.voice")

AUDIO_CHUNK_BYTES = 9600  # 200 ms of 24 kHz mono PCM16: small enough for responsive barge-in
MAX_UTTERANCE_BYTES = 2_000_000
MIN_UTTERANCE_BYTES = 9600  # ~0.3 s at 16 kHz; anything shorter is a click, not speech
START_TIMEOUT_S = 10.0
AUTH_REQUIRED_CLOSE_CODE = 4401  # application range (4000-4999), mirrors HTTP 401
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\n+")


class SentenceStream:
    """Incrementally cuts streamed text into speakable sentences."""

    def __init__(self, min_chars: int = 18) -> None:
        self.min_chars = min_chars
        self._buffer = ""

    def feed(self, text: str) -> list[str]:
        self._buffer += text
        sentences: list[str] = []
        while True:
            match = _SENTENCE_END.search(self._buffer)
            if match is None:
                return sentences
            candidate = self._buffer[: match.start()].strip()
            if len(candidate) < self.min_chars and match.end() < len(self._buffer) and not match.group(0).startswith("\n"):
                # Too short to speak on its own ("Hmm."): keep it and look for the next boundary.
                next_match = _SENTENCE_END.search(self._buffer, match.end())
                if next_match is None:
                    return sentences
                match = next_match
                candidate = self._buffer[: match.start()].strip()
            self._buffer = self._buffer[match.end():]
            if candidate:
                sentences.append(candidate)

    def flush(self) -> list[str]:
        remaining, self._buffer = self._buffer.strip(), ""
        return [remaining] if remaining else []


class VoiceSession:
    """One learner's live voice connection."""

    def __init__(
        self,
        websocket: WebSocket,
        orchestrator: SocraticOrchestrator,
        gateway: GeminiGateway,
        limiter: SlidingWindowRateLimiter,
    ) -> None:
        self.ws = websocket
        self.orchestrator = orchestrator
        self.gateway = gateway
        self.limiter = limiter
        self.session_id = uuid.uuid4().hex[:12]
        self.user: User | None = None
        self.topic: str | None = None
        self.modality: Modality = "auditory"
        self.mastery: float | None = None
        self.voice: str | None = None
        self.tts_mode = "server" if gateway.speech_enabled else "browser"
        self.history: list[DialogueTurn] = []
        self.turn_id = 0
        self.turn_task: asyncio.Task[None] | None = None
        self._audio = bytearray()
        self._audio_format: str | None = None
        self._audio_rate = 16000
        self._send_lock = asyncio.Lock()
        self._closed = False

    # ------------------------------------------------------------------ transport

    async def send_json(self, payload: dict[str, Any]) -> None:
        if self._closed or self.ws.application_state != WebSocketState.CONNECTED:
            return
        async with self._send_lock:
            with suppress(WebSocketDisconnect, RuntimeError):
                await self.ws.send_text(json.dumps(payload, ensure_ascii=False))

    async def send_bytes(self, payload: bytes) -> None:
        if self._closed or self.ws.application_state != WebSocketState.CONNECTED:
            return
        async with self._send_lock:
            with suppress(WebSocketDisconnect, RuntimeError):
                await self.ws.send_bytes(payload)

    async def send_state(self, state: str) -> None:
        await self.send_json({"event": "state", "state": state, "turn_id": self.turn_id})

    # ------------------------------------------------------------------ lifecycle

    async def run(self) -> None:
        try:
            if not await self._handshake():
                return
            while True:
                message = await self.ws.receive()
                if message["type"] == "websocket.disconnect":
                    break
                if message.get("bytes") is not None:
                    self._on_audio(message["bytes"])
                elif message.get("text") is not None:
                    await self._on_text_frame(message["text"])
        except WebSocketDisconnect:
            pass
        finally:
            self._closed = True
            await self._cancel_turn()

    async def _handshake(self) -> bool:
        """Authenticate and announce capabilities; False when the session was refused and closed."""
        first: dict[str, Any] | None = None
        try:
            message = await asyncio.wait_for(self.ws.receive(), timeout=START_TIMEOUT_S)
            if message["type"] == "websocket.disconnect":
                raise WebSocketDisconnect(code=1000)
            if message.get("text") is not None:
                first = self._parse(message["text"])
        except TimeoutError:
            first = None
        if first is not None and first.get("event") == "start":
            await self._configure(first, authenticate=True)
        if self.user is None:
            await self.send_json({
                "event": "error",
                "code": "auth_required",
                "message": "Sign in to start a voice session.",
            })
            self._closed = True
            with suppress(WebSocketDisconnect, RuntimeError):
                await self.ws.close(code=AUTH_REQUIRED_CLOSE_CODE)
            return False
        await self.send_json({
            "event": "ready",
            "session_id": self.session_id,
            "authenticated": True,
            "tts": self.tts_mode,
            "capabilities": {
                "llm": self.gateway.enabled,
                "server_stt": self.gateway.enabled,
                "server_tts": self.gateway.speech_enabled,
            },
        })
        await self.send_state("listening")
        return True

    async def _configure(self, data: dict[str, Any], authenticate: bool = False) -> None:
        if authenticate and isinstance(data.get("token"), str):
            async with AsyncSessionLocal() as db:
                self.user = await user_from_access_token(db, data["token"])
                if self.user and self.user.preferred_modality and "modality" not in data:
                    self.modality = MODALITY_BY_ENUM[self.user.preferred_modality]
        if isinstance(data.get("topic"), str):
            self.topic = data["topic"].strip()[:150] or None
        if data.get("modality") in MODALITIES:
            self.modality = data["modality"]
        if data.get("tts") in {"server", "browser"}:
            self.tts_mode = "server" if data["tts"] == "server" and self.gateway.speech_enabled else "browser"
        if isinstance(data.get("voice"), str) and re.fullmatch(r"[A-Za-z]{2,24}", data["voice"]):
            self.voice = data["voice"]
        if self.user is not None and "topic" in data:
            async with AsyncSessionLocal() as db:
                self.mastery = await tutor_service.lookup_mastery(db, self.user.id, self.topic)

    @staticmethod
    def _parse(raw: str) -> dict[str, Any] | None:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) else None

    async def _on_text_frame(self, raw: str) -> None:
        data = self._parse(raw)
        if data is None:
            await self.send_json({"event": "error", "code": "bad_frame", "message": "Frames must be JSON objects."})
            return
        await self._dispatch(data)

    async def _dispatch(self, data: dict[str, Any]) -> None:
        event = data.get("event")
        if event == "ping":
            await self.send_json({"event": "pong"})
        elif event in {"start", "config"}:
            # Identity is fixed at the handshake; later frames may only retune topic, modality and voice.
            await self._configure(data)
        elif event == "interrupt":
            await self.interrupt()
        elif event in {"transcript", "text"}:
            text = str(data.get("text", "")).strip()[:4000]
            if text:
                await self._start_turn(text=text)
        elif event == "audio_start":
            await self.interrupt()  # talking over the tutor is a barge-in
            fmt = str(data.get("format", "pcm16"))
            self._audio_format = fmt if fmt in {"pcm16", "audio/ogg", "audio/webm", "audio/wav"} else "pcm16"
            rate = data.get("sample_rate")
            self._audio_rate = int(rate) if isinstance(rate, int) and 8000 <= rate <= 48000 else 16000
            self._audio.clear()
        elif event == "audio_end":
            await self._finish_utterance()
        else:
            await self.send_json({"event": "error", "code": "unknown_event", "message": f"Unknown event {event!r}."})

    def _on_audio(self, chunk: bytes) -> None:
        if self._audio_format is None or len(self._audio) + len(chunk) > MAX_UTTERANCE_BYTES:
            return
        self._audio.extend(chunk)

    async def _finish_utterance(self) -> None:
        fmt, audio = self._audio_format, bytes(self._audio)
        self._audio_format = None
        self._audio.clear()
        if fmt is None or len(audio) < MIN_UTTERANCE_BYTES:
            await self.send_state("listening")
            return
        if fmt == "pcm16":
            audio, mime = pcm_to_wav(audio, self._audio_rate), "audio/wav"
        else:
            mime = fmt
        await self._start_turn(audio=audio, mime=mime)

    # ------------------------------------------------------------------ turns

    async def interrupt(self) -> None:
        """Barge-in: cancel in-flight generation and speech, then acknowledge once nothing more can be sent."""
        running = self.turn_task is not None and not self.turn_task.done()
        await self._cancel_turn()
        if running:
            await self.send_json({"event": "interrupted", "turn_id": self.turn_id})
            await self.send_state("listening")

    async def _cancel_turn(self) -> None:
        task, self.turn_task = self.turn_task, None
        if task is not None and not task.done():
            task.cancel()
            with suppress(asyncio.CancelledError, Exception):
                await task

    async def _start_turn(self, text: str | None = None, audio: bytes | None = None, mime: str | None = None) -> None:
        await self.interrupt()
        assert self.user is not None  # the handshake refuses unauthenticated sessions
        if self.limiter.hit(rate_limit_key(self.user), settings.TUTOR_RATE_LIMIT_AUTHENTICATED) is not None:
            await self.send_json({
                "event": "error",
                "code": "rate_limited",
                "message": "You've reached the tutoring limit for now. Take a short break and try again.",
            })
            return
        self.turn_id += 1
        self.turn_task = asyncio.create_task(self._guarded_turn(self.turn_id, text, audio, mime))

    async def _guarded_turn(self, turn_id: int, text: str | None, audio: bytes | None, mime: str | None) -> None:
        """Run a turn so that an unexpected failure still settles the client instead of leaving it 'thinking'."""
        try:
            await self._run_turn(turn_id, text, audio, mime)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Voice turn %s failed", turn_id)
            await self.send_json({
                "event": "error",
                "code": "turn_failed",
                "turn_id": turn_id,
                "message": "Something went wrong while answering. Please ask again.",
            })
            await self.send_json({"event": "audio_end", "turn_id": turn_id})
            await self.send_state("listening")

    async def _run_turn(self, turn_id: int, text: str | None, audio: bytes | None, mime: str | None) -> None:
        await self.send_state("thinking")
        if audio is not None:
            try:
                text = await self.gateway.transcribe_audio(audio, mime or "audio/wav")
            except LLMUnavailableError:
                await self.send_json({
                    "event": "error",
                    "code": "stt_unavailable",
                    "message": "Server speech recognition is unavailable right now. Try typing, or use a browser with built-in speech recognition.",
                })
                await self.send_state("listening")
                return
            await self.send_json({"event": "transcript", "turn_id": turn_id, "text": text})
        if not text:
            await self.send_state("listening")
            return

        request = TutorRequest(
            message=text,
            topic=self.topic,
            modality=self.modality,
            mastery=self.mastery,
            history=self.history[-8:],
            channel="voice",
            learner_name=self.user.full_name.split(" ")[0] if self.user and self.user.full_name else None,
        )
        sentences: asyncio.Queue[tuple[int, str] | None] = asyncio.Queue()
        speaker = asyncio.create_task(self._speak(turn_id, sentences)) if self.tts_mode == "server" else None
        segmenter = SentenceStream()
        reply: list[str] = []
        index = 0
        agent = engine = None
        try:
            async for event in self.orchestrator.stream(request):
                if event.type == "route":
                    agent = event.data["agent"]
                    await self.send_json({"event": "route", "turn_id": turn_id, **event.data})
                elif event.type == "delta":
                    chunk = event.data["text"]
                    reply.append(chunk)
                    await self.send_json({"event": "token", "turn_id": turn_id, "text": chunk})
                    for sentence in segmenter.feed(chunk):
                        await self._emit_sentence(turn_id, index, sentence, sentences)
                        index += 1
                elif event.type == "done":
                    engine = event.data.get("engine")
            for sentence in segmenter.flush():
                await self._emit_sentence(turn_id, index, sentence, sentences)
                index += 1
            full = "".join(reply).strip()
            self.history.extend([DialogueTurn(role="student", text=text), DialogueTurn(role="tutor", text=full)])
            await self.send_json({"event": "response_end", "turn_id": turn_id, "text": full, "agent": agent, "engine": engine})
            if speaker is not None:
                await sentences.put(None)
                await speaker
            await self.send_json({"event": "audio_end", "turn_id": turn_id})
        finally:
            if speaker is not None and not speaker.done():
                speaker.cancel()
                with suppress(asyncio.CancelledError):
                    await speaker

    async def _emit_sentence(self, turn_id: int, index: int, sentence: str, queue: asyncio.Queue[tuple[int, str] | None]) -> None:
        spoken = speech_text(sentence)
        if not spoken:
            return
        await self.send_json({"event": "sentence", "turn_id": turn_id, "index": index, "text": spoken})
        await queue.put((index, spoken))

    async def _speak(self, turn_id: int, queue: asyncio.Queue[tuple[int, str] | None]) -> None:
        """
        TTS worker. The first sentence is synthesized alone for the fastest first audio; later
        sentences that queue up during synthesis are batched into one request to avoid gaps.
        """
        speaking = False
        while True:
            item = await queue.get()
            if item is None:
                return
            batch = [item]
            finished = False
            while not queue.empty():
                queued = queue.get_nowait()
                if queued is None:
                    finished = True
                    break
                batch.append(queued)
            first_index = batch[0][0]
            try:
                audio = await self.gateway.synthesize_speech(" ".join(s for _, s in batch), voice=self.voice)
            except LLMUnavailableError:
                logger.info("Server TTS unavailable; client falls back to browser speech from sentence %s.", first_index)
                await self.send_json({"event": "tts_fallback", "turn_id": turn_id, "from_index": first_index})
                self.tts_mode = "browser"
                return
            if not speaking:
                speaking = True
                await self.send_state("speaking")
            header = struct.pack("<II", turn_id, audio.sample_rate)
            for offset in range(0, len(audio.pcm), AUDIO_CHUNK_BYTES):
                await self.send_bytes(header + audio.pcm[offset:offset + AUDIO_CHUNK_BYTES])
            if finished:
                return
