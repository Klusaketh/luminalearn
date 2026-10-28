"""Resilient Gemini gateway: fallback chain, circuit breaker, deadlines and speech decoding."""
import asyncio
import io
import os
import sys
import wave
from types import SimpleNamespace
from typing import Any

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ai.llm import (
    GatewayConfig,
    GeminiGateway,
    LLMUnavailableError,
    decode_speech_payload,
    pcm_to_wav,
)
from ai.llm.gemini_gateway import classify_failure, thinking_config_for


class FakeAPIError(Exception):
    def __init__(self, code: int, message: str = "") -> None:
        super().__init__(message or f"HTTP {code}")
        self.code = code


class FakeModels:
    """Scripted stand-in for `client.aio.models`, keyed by model name."""

    def __init__(self, behaviour: dict[str, Any]) -> None:
        self.behaviour = behaviour
        self.calls: list[str] = []

    async def generate_content(self, *, model: str, contents: Any, config: Any) -> Any:
        self.calls.append(model)
        outcome = self.behaviour[model]
        if isinstance(outcome, Exception):
            raise outcome
        if outcome == "hang":
            await asyncio.sleep(10)
        if isinstance(outcome, tuple):  # (bytes, mime) audio payload
            data, mime = outcome
            part = SimpleNamespace(inline_data=SimpleNamespace(data=data, mime_type=mime))
            return SimpleNamespace(text=None, candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))])
        return SimpleNamespace(text=outcome)

    async def generate_content_stream(self, *, model: str, contents: Any, config: Any) -> Any:
        self.calls.append(model)
        outcome = self.behaviour[model]
        if isinstance(outcome, Exception):
            raise outcome

        async def chunks() -> Any:
            for piece in outcome:
                if piece == "hang":
                    await asyncio.sleep(10)
                yield SimpleNamespace(text=piece)

        return chunks()


def gateway_with(behaviour: dict[str, Any], models: tuple[str, ...], tts: tuple[str, ...] = ()) -> tuple[GeminiGateway, FakeModels]:
    gateway = GeminiGateway(GatewayConfig(api_key="test-key", text_models=models, tts_models=tts, request_timeout_s=0.3))
    fake = FakeModels(behaviour)
    gateway._sdk = lambda: SimpleNamespace(aio=SimpleNamespace(models=fake))  # type: ignore[method-assign]
    return gateway, fake


@pytest.mark.asyncio
async def test_retired_model_is_skipped_and_remembered() -> None:
    gateway, fake = gateway_with({"old": FakeAPIError(404), "new": "hello"}, ("old", "new"))
    assert (await gateway.generate_text("hi")).text == "hello"
    assert (await gateway.generate_text("hi")).model == "new"
    assert fake.calls == ["old", "new", "new"]  # the 404 model is never retried
    assert gateway.status()["text_models"][0]["state"] == "retired"


@pytest.mark.asyncio
async def test_overloaded_model_cools_down_then_recovers() -> None:
    gateway, fake = gateway_with({"busy": FakeAPIError(503), "backup": "ok"}, ("busy", "backup"))
    await gateway.generate_text("hi")
    assert gateway.health.describe("busy")["state"] == "cooling_down"
    gateway.health.mark_healthy("busy")
    fake.behaviour["busy"] = "recovered"
    assert (await gateway.generate_text("hi")).text == "recovered"


@pytest.mark.asyncio
async def test_slow_model_hits_deadline_and_fails_over() -> None:
    gateway, _ = gateway_with({"slow": "hang", "fast": "quick"}, ("slow", "fast"))
    result = await gateway.generate_text("hi", timeout_s=0.1)
    assert result.model == "fast"


@pytest.mark.asyncio
async def test_rejected_api_key_disables_the_gateway() -> None:
    gateway, _ = gateway_with({"m": FakeAPIError(400, "API key not valid")}, ("m",))
    with pytest.raises(LLMUnavailableError):
        await gateway.generate_text("hi")
    assert gateway.enabled is False


@pytest.mark.asyncio
async def test_offline_and_dummy_keys_never_call_the_api() -> None:
    offline = GeminiGateway(GatewayConfig(api_key="real", text_models=("m",), offline=True))
    dummy = GeminiGateway(GatewayConfig(api_key="YOUR_GEMINI_API_KEY_HERE", text_models=("m",)))
    assert not offline.enabled and not dummy.enabled
    with pytest.raises(LLMUnavailableError):
        await offline.generate_text("hi")


@pytest.mark.asyncio
async def test_stream_fails_over_before_first_token_and_reports_model() -> None:
    gateway, _ = gateway_with({"dead": FakeAPIError(404), "live": ["Hel", "lo ", "there"]}, ("dead", "live"))
    committed: list[str] = []
    text = "".join([d async for d in gateway.stream_text("hi", on_model=committed.append)])
    assert text == "Hello there"
    assert committed == ["live"]


@pytest.mark.asyncio
async def test_stream_first_token_deadline() -> None:
    gateway, _ = gateway_with({"stuck": ["hang"], "ok": ["fine"]}, ("stuck", "ok"))
    text = "".join([d async for d in gateway.stream_text("hi", first_token_timeout_s=0.1)])
    assert text == "fine"


@pytest.mark.asyncio
async def test_speech_synthesis_normalizes_wav_and_raw_pcm() -> None:
    pcm = (b"\x10\x00" * 2400)
    wav_bytes = pcm_to_wav(pcm, 24000)
    gateway, _ = gateway_with({"tts-a": (wav_bytes, "audio/wav")}, ("text",), tts=("tts-a",))
    audio = await gateway.synthesize_speech("hello")
    assert audio.pcm == pcm and audio.sample_rate == 24000
    assert round(audio.duration_s, 2) == 0.1

    raw, rate = decode_speech_payload(pcm, "audio/L16;codec=pcm;rate=22050")
    assert raw == pcm and rate == 22050


def test_stereo_wav_is_downmixed_to_the_left_channel() -> None:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b"\x01\x00\x02\x00" * 10)
    pcm, rate = decode_speech_payload(buffer.getvalue(), "audio/wav")
    assert pcm == b"\x01\x00" * 10 and rate == 16000


def test_failure_classification_and_thinking_config() -> None:
    assert classify_failure(FakeAPIError(404)) == "retired"
    assert classify_failure(FakeAPIError(429)) == "overloaded"
    assert classify_failure(FakeAPIError(401)) == "auth"
    assert classify_failure(FakeAPIError(400, "bad thinking config")) == "invalid"
    assert classify_failure(TimeoutError()) == "overloaded"
    assert thinking_config_for("gemini-2.5-flash", "low").thinking_budget == 0  # type: ignore[union-attr]
    assert thinking_config_for("gemini-3.5-flash", "minimal").thinking_level is not None  # type: ignore[union-attr]
    assert thinking_config_for("gemini-2.5-flash-preview-tts", "low") is None
