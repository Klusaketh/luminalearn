"""Full-duplex voice WebSocket: handshake, streaming turns, and barge-in cancellation."""
import asyncio
import struct
import threading
import uuid
from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import app.api.v1.voice as voice_api
import app.services.voice_session as voice_session_module
from ai.agents.schema import TutorEvent, TutorRequest
from app.main import app
from app.services.voice_session import SentenceStream, VoiceSession


class SlowOrchestrator:
    """Streams one token every 50 ms so a test can barge in mid-answer."""

    def __init__(self, tokens: int = 200) -> None:
        self.tokens = tokens
        self.cancelled = threading.Event()
        self.requests: list[TutorRequest] = []

    async def stream(self, request: TutorRequest) -> AsyncIterator[TutorEvent]:
        self.requests.append(request)
        yield TutorEvent("route", {"agent": "socratic_tutor", "display_name": "Socratic Tutor", "rationale": "test"})
        try:
            for index in range(self.tokens):
                await asyncio.sleep(0.05)
                yield TutorEvent("delta", {"text": f"word{index}. "})
        except asyncio.CancelledError:
            self.cancelled.set()
            raise
        yield TutorEvent("done", {"engine": "fake", "text": ""})


def receive_until(ws: Any, event: str, limit: int = 400) -> list[dict[str, Any]]:
    seen = []
    for _ in range(limit):
        message = ws.receive_json()
        seen.append(message)
        if message.get("event") == event:
            return seen
    raise AssertionError(f"never received {event!r}; got {[m.get('event') for m in seen]}")


VALID_TOKEN = "valid-test-token"


@pytest.fixture(autouse=True)
def signed_in_learner(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Accept VALID_TOKEN as a verified learner without touching the database from the test thread."""
    learner = SimpleNamespace(id=uuid.uuid4(), full_name="Ada Lovelace", preferred_modality=None)

    async def resolve(_db: Any, token: str | None) -> SimpleNamespace | None:
        return learner if token == VALID_TOKEN else None

    async def no_mastery(*_args: Any) -> None:
        return None

    monkeypatch.setattr(voice_session_module, "user_from_access_token", resolve)
    monkeypatch.setattr(voice_session_module.tutor_service, "lookup_mastery", no_mastery)
    return learner


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize("start", [{"event": "start"}, {"event": "start", "token": "forged"}, {"event": "ping"}])
def test_sessions_without_a_valid_token_are_refused(client: TestClient, start: dict[str, Any]) -> None:
    with client.websocket_connect("/api/v1/voice/session") as ws:
        ws.send_json(start)
        refusal = ws.receive_json()
        assert refusal["event"] == "error" and refusal["code"] == "auth_required"
        with pytest.raises(WebSocketDisconnect) as closed:
            ws.receive_json()
        assert closed.value.code == 4401


def test_handshake_ping_and_full_offline_turn(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/voice/session") as ws:
        ws.send_json({"event": "start", "token": VALID_TOKEN, "topic": "Recursion", "modality": "auditory"})
        ready = ws.receive_json()
        assert ready["event"] == "ready"
        assert ready["authenticated"] is True
        assert ready["capabilities"] == {"llm": False, "server_stt": False, "server_tts": False}
        assert ready["tts"] == "browser"
        assert ws.receive_json() == {"event": "state", "state": "listening", "turn_id": 0}

        ws.send_json({"event": "ping"})
        assert ws.receive_json() == {"event": "pong"}

        ws.send_json({"event": "transcript", "text": "What is a base case in recursion?"})
        messages = receive_until(ws, "audio_end")
        events = [m["event"] for m in messages]
        assert events[0] == "state" and messages[0]["state"] == "thinking"
        assert "route" in events and "token" in events and "sentence" in events
        assert events.index("response_end") < events.index("audio_end")
        end = next(m for m in messages if m["event"] == "response_end")
        assert end["turn_id"] == 1 and end["engine"] == "offline" and end["text"]
        tokens = "".join(m["text"] for m in messages if m["event"] == "token")
        assert tokens.strip() == end["text"]


def test_barge_in_cancels_generation_and_silences_the_turn(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    slow = SlowOrchestrator()
    monkeypatch.setattr(voice_api, "tutor_orchestrator", slow)
    with client.websocket_connect("/api/v1/voice/session") as ws:
        ws.send_json({"event": "start", "token": VALID_TOKEN})
        receive_until(ws, "state")  # ready, then listening
        ws.send_json({"event": "transcript", "text": "explain recursion slowly"})
        receive_until(ws, "token")  # the tutor is mid-answer

        ws.send_json({"event": "interrupt"})
        after = receive_until(ws, "interrupted")
        interrupted = after[-1]
        assert interrupted["turn_id"] == 1
        assert ws.receive_json() == {"event": "state", "state": "listening", "turn_id": 1}

        # Nothing from the cancelled turn may follow the acknowledgement.
        ws.send_json({"event": "ping"})
        assert ws.receive_json() == {"event": "pong"}
        assert slow.cancelled.is_set()


def test_new_utterance_while_speaking_is_an_implicit_barge_in(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    slow = SlowOrchestrator()
    monkeypatch.setattr(voice_api, "tutor_orchestrator", slow)
    with client.websocket_connect("/api/v1/voice/session") as ws:
        ws.send_json({"event": "start", "token": VALID_TOKEN})
        receive_until(ws, "state")
        ws.send_json({"event": "transcript", "text": "first question"})
        receive_until(ws, "token")
        ws.send_json({"event": "transcript", "text": "actually, a different question"})
        messages = receive_until(ws, "route")
        events = [m["event"] for m in messages]
        assert "interrupted" in events
        assert messages[-1]["turn_id"] == 2
        ws.send_json({"event": "interrupt"})
        receive_until(ws, "interrupted")
    assert [r.message for r in slow.requests] == ["first question", "actually, a different question"]
    # The second turn carries no history from the cancelled first answer.
    assert slow.requests[1].history == []


class BrokenOrchestrator:
    async def stream(self, request: TutorRequest) -> AsyncIterator[TutorEvent]:
        yield TutorEvent("route", {"agent": "socratic_tutor", "display_name": "Socratic Tutor", "rationale": "test"})
        raise RuntimeError("model exploded")


def test_a_crashing_turn_settles_the_client_instead_of_hanging(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(voice_api, "tutor_orchestrator", BrokenOrchestrator())
    with client.websocket_connect("/api/v1/voice/session") as ws:
        ws.send_json({"event": "start", "token": VALID_TOKEN})
        receive_until(ws, "state")
        ws.send_json({"event": "transcript", "text": "What is recursion?"})
        messages = receive_until(ws, "audio_end")
        failure = next(m for m in messages if m["event"] == "error")
        assert failure["code"] == "turn_failed" and failure["turn_id"] == 1
        assert ws.receive_json() == {"event": "state", "state": "listening", "turn_id": 1}
        ws.send_json({"event": "ping"})
        assert ws.receive_json() == {"event": "pong"}  # the session survives the failed turn


def test_server_audio_path_reports_unavailable_speech_recognition(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/voice/session") as ws:
        ws.send_json({"event": "start", "token": VALID_TOKEN})
        receive_until(ws, "state")
        ws.send_json({"event": "audio_start", "format": "pcm16", "sample_rate": 16000})
        ws.send_bytes(b"\x00\x01" * 16000)  # one second of near-silence
        ws.send_json({"event": "audio_end"})
        error = receive_until(ws, "error")[-1]
        assert error["code"] == "stt_unavailable"


def test_short_utterances_are_ignored_as_noise(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/voice/session") as ws:
        ws.send_json({"event": "start", "token": VALID_TOKEN})
        receive_until(ws, "state")
        ws.send_json({"event": "audio_start", "format": "pcm16", "sample_rate": 16000})
        ws.send_bytes(b"\x00" * 200)
        ws.send_json({"event": "audio_end"})
        assert ws.receive_json()["state"] == "listening"


def test_malformed_and_unknown_frames_get_typed_errors(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/voice/session") as ws:
        ws.send_json({"event": "start", "token": VALID_TOKEN})
        receive_until(ws, "state")
        ws.send_text("not json")
        assert ws.receive_json()["code"] == "bad_frame"
        ws.send_json({"event": "teleport"})
        assert ws.receive_json()["code"] == "unknown_event"


def test_cross_site_origins_are_rejected() -> None:
    assert voice_api.origin_allowed(None)
    assert voice_api.origin_allowed("http://localhost:3000")
    assert voice_api.origin_allowed("http://127.0.0.1:3000")
    assert not voice_api.origin_allowed("https://evil.example.com")


def test_sentence_stream_segments_incrementally() -> None:
    stream = SentenceStream()
    out = stream.feed("Recursion needs a base case. Wh")
    assert out == ["Recursion needs a base case."]
    out = stream.feed("at should fact(0) return? Ok. And then")
    assert out == ["What should fact(0) return?"]
    assert stream.flush() == ["Ok. And then"]  # a short "Ok." waits to ride along with what follows


def test_audio_frame_header_layout() -> None:
    header = struct.pack("<II", 7, 24000)
    turn_id, rate = struct.unpack("<II", header)
    assert (turn_id, rate, len(header)) == (7, 24000, 8)
    assert VoiceSession.__doc__
