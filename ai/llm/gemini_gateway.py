"""
LuminaLearn AI — Resilient Gemini Gateway.
Module: ai/llm/gemini_gateway.py

Single entry point for every Gemini call the platform makes: Socratic tutoring streams,
quiz generation, speech-to-text and text-to-speech. It adds what the raw SDK lacks:

  * Ordered model fallback (configured model first, then fallbacks).
  * A per-model circuit breaker: retired models (404) are skipped for the process
    lifetime, overloaded or slow models (429 / 5xx / timeouts) for a cooldown.
  * Hard deadlines, including a first-token deadline for streams, so callers never hang.
  * An offline switch so every caller can degrade to its deterministic engine.
"""

from __future__ import annotations

import asyncio
import io
import logging
import re
import time
import wave
from collections.abc import AsyncIterator, Callable, Sequence
from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from google import genai
    from google.genai import types

logger = logging.getLogger("luminalearn.ai.gateway")

ThinkingEffort = Literal["minimal", "low", "medium", "high"]

_DUMMY_KEY_PREFIXES = ("AQ.dummy", "YOUR_", "your_", "changeme")


class LLMUnavailableError(RuntimeError):
    """No configured model could serve the request (offline, unhealthy, or every attempt failed)."""


class LLMStreamInterruptedError(RuntimeError):
    """A stream failed after it had already produced text, so it cannot transparently fail over."""


@dataclass(frozen=True)
class GatewayConfig:
    """Runtime configuration for the gateway, decoupled from any web framework settings object."""

    api_key: str | None
    text_models: tuple[str, ...]
    tts_models: tuple[str, ...] = ()
    tts_voice: str = "Kore"
    temperature: float = 0.6
    max_output_tokens: int = 2048
    request_timeout_s: float = 20.0
    offline: bool = False


@dataclass(frozen=True)
class GenerationResult:
    text: str
    model: str


@dataclass(frozen=True)
class SpeechAudio:
    """Mono 16-bit little-endian PCM audio."""

    pcm: bytes
    sample_rate: int
    model: str

    @property
    def duration_s(self) -> float:
        return len(self.pcm) / 2 / self.sample_rate if self.sample_rate else 0.0


class ModelHealth:
    """Per-model circuit breaker. Retired models stay blocked; overloaded ones cool down."""

    COOLDOWN_S = 45.0

    def __init__(self) -> None:
        self._blocked_until: dict[str, float] = {}
        self._last_error: dict[str, str] = {}

    def available(self, model: str) -> bool:
        return time.monotonic() >= self._blocked_until.get(model, 0.0)

    def mark_retired(self, model: str, reason: str) -> None:
        self._blocked_until[model] = float("inf")
        self._last_error[model] = reason

    def mark_overloaded(self, model: str, reason: str, cooldown_s: float = COOLDOWN_S) -> None:
        self._blocked_until[model] = time.monotonic() + cooldown_s
        self._last_error[model] = reason

    def mark_healthy(self, model: str) -> None:
        self._blocked_until.pop(model, None)
        self._last_error.pop(model, None)

    def describe(self, model: str) -> dict[str, Any]:
        until = self._blocked_until.get(model, 0.0)
        if until == float("inf"):
            state = "retired"
        elif time.monotonic() < until:
            state = "cooling_down"
        else:
            state = "available"
        return {"model": model, "state": state, "last_error": self._last_error.get(model)}


FailureKind = Literal["retired", "auth", "invalid", "overloaded"]


def classify_failure(exc: BaseException) -> FailureKind:
    """Maps an SDK / transport exception onto the breaker action it deserves."""
    if isinstance(exc, TimeoutError):
        return "overloaded"
    code = getattr(exc, "code", None)
    message = str(exc).lower()
    if isinstance(code, int):
        if code == 404:
            return "retired"
        if code in (401, 403) or (code == 400 and "api key" in message):
            return "auth"
        if code == 400:
            return "invalid"
    return "overloaded"


def thinking_config_for(model: str, effort: ThinkingEffort) -> types.ThinkingConfig | None:
    """Gemini 2.5 takes a token budget, Gemini 3+ takes a thinking level, older/TTS models take neither."""
    from google.genai import types

    name = model.lower()
    if "tts" in name or name.startswith(("gemini-1", "gemini-2.0")):
        return None
    if name.startswith("gemini-2.5"):
        return types.ThinkingConfig(thinking_budget=0) if "flash" in name else None
    return types.ThinkingConfig(thinking_level=types.ThinkingLevel(effort.upper()))


def decode_speech_payload(data: bytes, mime_type: str | None) -> tuple[bytes, int]:
    """
    Normalizes Gemini TTS output to raw PCM. Depending on the model the API returns either a
    complete WAV file (`audio/wav`) or bare PCM (`audio/L16;codec=pcm;rate=24000`).
    """
    mime = (mime_type or "").lower()
    if data[:4] == b"RIFF" or "wav" in mime:
        with wave.open(io.BytesIO(data), "rb") as wav:
            if wav.getsampwidth() != 2:
                raise ValueError(f"Unsupported WAV sample width: {wav.getsampwidth()} bytes.")
            frames = wav.readframes(wav.getnframes())
            rate = wav.getframerate()
            if wav.getnchannels() == 2:
                # Keep the left channel: tutoring speech is mono content.
                frames = b"".join(frames[i : i + 2] for i in range(0, len(frames), 4))
            return frames, rate
    if "l16" in mime or "pcm" in mime:
        match = re.search(r"rate=(\d+)", mime)
        return data, int(match.group(1)) if match else 24000
    raise ValueError(f"Unsupported speech payload mime type: {mime_type!r}.")


def pcm_to_wav(pcm: bytes, sample_rate: int) -> bytes:
    """Wraps mono 16-bit PCM in a WAV container (for browsers and for speech-to-text uploads)."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm)
    return buffer.getvalue()


async def _close_quietly(iterator: Any) -> None:
    """Closes an SDK stream (releasing its HTTP connection), ignoring errors during teardown."""
    aclose = getattr(iterator, "aclose", None)
    if aclose is not None:
        with suppress(Exception):
            await aclose()


_NO_SPEECH_PATTERN = re.compile(r"^[\W_]*(no speech|silence|inaudible|no audio|\[?blank\]?)[\W_]*$", re.IGNORECASE)


class GeminiGateway:
    """Async, fault-tolerant facade over the `google-genai` SDK."""

    def __init__(self, config: GatewayConfig) -> None:
        self.config = config
        self.health = ModelHealth()
        self._client: genai.Client | None = None
        self._client_loop: asyncio.AbstractEventLoop | None = None
        self._auth_blocked_until = 0.0

    # ------------------------------------------------------------------ status

    @property
    def has_credentials(self) -> bool:
        key = (self.config.api_key or "").strip()
        return bool(key) and not key.startswith(_DUMMY_KEY_PREFIXES)

    @property
    def enabled(self) -> bool:
        return (
            not self.config.offline
            and self.has_credentials
            and time.monotonic() >= self._auth_blocked_until
        )

    @property
    def speech_enabled(self) -> bool:
        return self.enabled and bool(self.config.tts_models)

    def status(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "offline_mode": self.config.offline,
            "credentials_configured": self.has_credentials,
            "text_models": [self.health.describe(m) for m in self.config.text_models],
            "tts_models": [self.health.describe(m) for m in self.config.tts_models],
        }

    # ------------------------------------------------------------------ plumbing

    def _sdk(self) -> genai.Client:
        """One SDK client per event loop: the underlying HTTP pool is bound to the loop that created it."""
        from google import genai
        from google.genai import types

        loop = asyncio.get_running_loop()
        if self._client is None or self._client_loop is not loop:
            self._client = genai.Client(
                api_key=self.config.api_key,
                http_options=types.HttpOptions(
                    timeout=int(self.config.request_timeout_s * 1000),
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
            self._client_loop = loop
        return self._client

    def _candidates(self, models: Sequence[str]) -> list[str]:
        return [m for m in dict.fromkeys(models) if m and self.health.available(m)]

    def _record_failure(self, model: str, exc: BaseException) -> FailureKind:
        kind = classify_failure(exc)
        reason = f"{type(exc).__name__}: {str(exc)[:160]}"
        if kind == "retired":
            self.health.mark_retired(model, reason)
            logger.warning("Gemini model %s is unavailable (%s); skipping it from now on.", model, reason)
        elif kind == "auth":
            self._auth_blocked_until = time.monotonic() + 300.0
            logger.error("Gemini rejected the API key (%s); AI features fall back to offline engines.", reason)
        else:
            self.health.mark_overloaded(model, reason)
            logger.info("Gemini model %s failed (%s); trying the next model.", model, reason)
        return kind

    def _config(
        self,
        model: str,
        *,
        system_instruction: str | None,
        temperature: float | None,
        max_output_tokens: int | None,
        thinking: ThinkingEffort | None,
        json_mode: bool = False,
    ) -> types.GenerateContentConfig:
        from google.genai import types

        return types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=self.config.temperature if temperature is None else temperature,
            max_output_tokens=max_output_tokens or self.config.max_output_tokens,
            thinking_config=thinking_config_for(model, thinking) if thinking else None,
            response_mime_type="application/json" if json_mode else None,
        )

    # ------------------------------------------------------------------ text

    async def generate_text(
        self,
        contents: Any,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        thinking: ThinkingEffort | None = "low",
        json_mode: bool = False,
        timeout_s: float | None = None,
    ) -> GenerationResult:
        """Single-shot generation with model fallback. Raises LLMUnavailableError when nothing works."""
        if not self.enabled:
            raise LLMUnavailableError("Gemini gateway is offline or has no credentials.")
        deadline = timeout_s or self.config.request_timeout_s
        for model in self._candidates(self.config.text_models):
            effort = thinking
            for _ in range(2):  # second pass retries the same model without thinking config
                try:
                    response = await asyncio.wait_for(
                        self._sdk().aio.models.generate_content(
                            model=model,
                            contents=contents,
                            config=self._config(
                                model,
                                system_instruction=system_instruction,
                                temperature=temperature,
                                max_output_tokens=max_output_tokens,
                                thinking=effort,
                                json_mode=json_mode,
                            ),
                        ),
                        timeout=deadline,
                    )
                    text = (response.text or "").strip()
                    if not text:
                        raise ValueError("Gemini returned an empty response.")
                    self.health.mark_healthy(model)
                    return GenerationResult(text=text, model=model)
                except Exception as exc:  # noqa: BLE001 - every SDK/transport failure must fail over
                    kind = classify_failure(exc)
                    if kind == "invalid" and effort is not None:
                        effort = None
                        continue
                    self._record_failure(model, exc)
                    if kind == "auth":
                        raise LLMUnavailableError("Gemini API key rejected.") from exc
                    break
        raise LLMUnavailableError("Every configured Gemini model failed or is cooling down.")

    async def stream_text(
        self,
        contents: Any,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        thinking: ThinkingEffort | None = "minimal",
        first_token_timeout_s: float = 12.0,
        total_timeout_s: float = 60.0,
        on_model: Callable[[str], None] | None = None,
    ) -> AsyncIterator[str]:
        """
        Streams text deltas. Fails over between models until the first token arrives; after that
        the stream is committed to one model (reported through `on_model`) and mid-stream
        failures raise LLMStreamInterruptedError.
        """
        if not self.enabled:
            raise LLMUnavailableError("Gemini gateway is offline or has no credentials.")
        started = time.monotonic()
        model, iterator, first_text = await self._open_first_available_stream(
            contents, system_instruction, temperature, max_output_tokens, thinking, first_token_timeout_s
        )
        if on_model is not None:
            on_model(model)
        try:
            yield first_text
            while True:
                remaining = total_timeout_s - (time.monotonic() - started)
                if remaining <= 0:
                    raise LLMStreamInterruptedError(f"{model} exceeded the {total_timeout_s:.0f}s stream deadline.")
                try:
                    chunk = await asyncio.wait_for(iterator.__anext__(), timeout=remaining)
                except StopAsyncIteration:
                    return
                except Exception as exc:  # noqa: BLE001 - surface as a typed mid-stream failure
                    self._record_failure(model, exc)
                    raise LLMStreamInterruptedError(str(exc)) from exc
                text = getattr(chunk, "text", None) or ""
                if text:
                    yield text
        finally:
            await _close_quietly(iterator)

    async def _open_first_available_stream(
        self,
        contents: Any,
        system_instruction: str | None,
        temperature: float | None,
        max_output_tokens: int | None,
        thinking: ThinkingEffort | None,
        first_token_timeout_s: float,
    ) -> tuple[str, AsyncIterator[Any], str]:
        """Walks the model chain until one stream produces its first token."""
        for model in self._candidates(self.config.text_models):
            effort = thinking
            for _ in range(2):  # second pass retries the same model without thinking config
                try:
                    iterator, first_text = await self._open_stream(
                        model, contents, system_instruction, temperature, max_output_tokens, effort, first_token_timeout_s
                    )
                except Exception as exc:  # noqa: BLE001 - every SDK/transport failure must fail over
                    kind = classify_failure(exc)
                    if kind == "invalid" and effort is not None:
                        effort = None
                        continue
                    self._record_failure(model, exc)
                    if kind == "auth":
                        raise LLMUnavailableError("Gemini API key rejected.") from exc
                    break
                self.health.mark_healthy(model)
                return model, iterator, first_text
        raise LLMUnavailableError("Every configured Gemini model failed or is cooling down.")

    async def _open_stream(
        self,
        model: str,
        contents: Any,
        system_instruction: str | None,
        temperature: float | None,
        max_output_tokens: int | None,
        thinking: ThinkingEffort | None,
        first_token_timeout_s: float,
    ) -> tuple[AsyncIterator[Any], str]:
        """Opens a stream and waits (bounded) for its first non-empty text chunk."""
        opened = time.monotonic()
        stream = await asyncio.wait_for(
            self._sdk().aio.models.generate_content_stream(
                model=model,
                contents=contents,
                config=self._config(
                    model,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    thinking=thinking,
                ),
            ),
            timeout=first_token_timeout_s,
        )
        iterator = stream.__aiter__()
        try:
            while True:
                remaining = first_token_timeout_s - (time.monotonic() - opened)
                if remaining <= 0:
                    raise TimeoutError(f"{model} produced no text within {first_token_timeout_s:.0f}s.")
                chunk = await asyncio.wait_for(iterator.__anext__(), timeout=remaining)
                text = getattr(chunk, "text", None) or ""
                if text:
                    return iterator, text
        except StopAsyncIteration:
            raise ValueError(f"{model} closed the stream without producing text.") from None
        except BaseException:
            await _close_quietly(iterator)
            raise

    # ------------------------------------------------------------------ speech

    async def transcribe_audio(self, audio: bytes, mime_type: str, *, timeout_s: float = 25.0) -> str:
        """Server-side speech-to-text for browsers without a native speech recognizer."""
        from google.genai import types

        result = await self.generate_text(
            [
                types.Part.from_bytes(data=audio, mime_type=mime_type),
                "Transcribe the speech in this audio verbatim. Output only the transcript, "
                "with no labels or commentary. If there is no intelligible speech, output nothing.",
            ],
            temperature=0.0,
            max_output_tokens=800,
            thinking="minimal",
            timeout_s=timeout_s,
        )
        transcript = result.text.strip().strip('"').strip()
        return "" if _NO_SPEECH_PATTERN.match(transcript) else transcript

    async def synthesize_speech(self, text: str, *, voice: str | None = None, timeout_s: float = 18.0) -> SpeechAudio:
        """Text-to-speech through the Gemini TTS models, normalized to mono 16-bit PCM."""
        from google.genai import types

        if not self.speech_enabled:
            raise LLMUnavailableError("Speech synthesis is offline or no TTS model is configured.")
        speech_config = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice or self.config.tts_voice)
            )
        )
        for model in self._candidates(self.config.tts_models):
            try:
                response = await asyncio.wait_for(
                    self._sdk().aio.models.generate_content(
                        model=model,
                        contents=text,
                        config=types.GenerateContentConfig(response_modalities=["AUDIO"], speech_config=speech_config),
                    ),
                    timeout=timeout_s,
                )
                inline = next(
                    (
                        part.inline_data
                        for candidate in response.candidates or []
                        for part in (candidate.content.parts or [] if candidate.content else [])
                        if part.inline_data is not None and part.inline_data.data
                    ),
                    None,
                )
                if inline is None or inline.data is None:
                    raise ValueError(f"{model} returned no audio payload.")
                pcm, rate = decode_speech_payload(inline.data, inline.mime_type)
                self.health.mark_healthy(model)
                return SpeechAudio(pcm=pcm, sample_rate=rate, model=model)
            except Exception as exc:  # noqa: BLE001 - every SDK/transport failure must fail over
                if self._record_failure(model, exc) == "auth":
                    raise LLMUnavailableError("Gemini API key rejected.") from exc
        raise LLMUnavailableError("Every configured TTS model failed or is cooling down.")
