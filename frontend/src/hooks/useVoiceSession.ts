"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { tutorService, type RouteInfo } from "@/services/tutorService";
import { useAuthStore } from "@/stores/useAuthStore";
import { newMessageId, useTutorStore, type VoiceState } from "@/stores/useTutorStore";

/* ----------------------------------------------------------------------------------------
 * Full-duplex voice client for /api/v1/voice/session (protocol: backend voice_session.py).
 *
 *  Speech-to-text: the browser's streaming recognizer when available (fast, interim
 *  results); otherwise 16 kHz PCM captured in an AudioWorklet and segmented by a local
 *  voice-activity detector, transcribed on the server.
 *  Text-to-speech: server PCM frames scheduled gaplessly through Web Audio (and an
 *  analyser that drives the orb), or browser speech synthesis as the instant fallback.
 *  Barge-in: sustained mic energy above an adaptive noise floor, or interim speech that is
 *  not an echo of the tutor, stops playback locally at once and sends `interrupt`; audio
 *  frames from the interrupted turn that are still in flight are dropped by turn id.
 * -------------------------------------------------------------------------------------- */

type SttMode = "browser" | "server" | "none";
export type TtsPreference = "server" | "browser";

interface Capabilities {
  llm: boolean;
  server_stt: boolean;
  server_tts: boolean;
}

interface SpeechAlternativeLike {
  transcript: string;
}
interface SpeechResultLike {
  isFinal: boolean;
  0: SpeechAlternativeLike;
}
interface SpeechEventLike {
  resultIndex: number;
  results: { length: number; [index: number]: SpeechResultLike };
}
interface SpeechRecognitionLike {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: SpeechEventLike) => void) | null;
  onerror: ((event: { error?: string }) => void) | null;
  onend: (() => void) | null;
}
type SpeechRecognitionCtor = new () => SpeechRecognitionLike;

function recognitionCtor(): SpeechRecognitionCtor | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as { SpeechRecognition?: SpeechRecognitionCtor; webkitSpeechRecognition?: SpeechRecognitionCtor };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

const PCM_WORKLET = `
class LuminaPcmCapture extends AudioWorkletProcessor {
  constructor() { super(); this.step = sampleRate / 16000; this.pos = 0; this.out = new Int16Array(1600); this.n = 0; }
  process(inputs) {
    const input = inputs[0] && inputs[0][0];
    if (input) {
      let pos = this.pos;
      while (pos < input.length) {
        const i = Math.floor(pos), frac = pos - i;
        const a = input[i], b = i + 1 < input.length ? input[i + 1] : a;
        const s = Math.max(-1, Math.min(1, a + (b - a) * frac));
        this.out[this.n++] = s < 0 ? s * 0x8000 : s * 0x7fff;
        if (this.n === this.out.length) { this.port.postMessage(this.out.buffer, [this.out.buffer]); this.out = new Int16Array(1600); this.n = 0; }
        pos += this.step;
      }
      this.pos = pos - input.length;
    }
    return true;
  }
}
registerProcessor("lumina-pcm-capture", LuminaPcmCapture);
`;

const VAD_INTERVAL_MS = 50;
const BARGE_IN_MS = 220;
const UTTERANCE_SILENCE_MS = 900;
const MAX_UTTERANCE_MS = 25_000;
const PREROLL_CHUNKS = 4; // 4 x 100 ms of audio before the detector fired

function words(text: string): string[] {
  return text.toLowerCase().replace(/[^\p{L}\p{N}\s']/gu, " ").split(/\s+/).filter(Boolean);
}

/** True when what the mic "heard" is mostly the tutor's own recent speech (speaker echo). */
function isEcho(heard: string, spoken: string): boolean {
  const heardWords = words(heard);
  if (heardWords.length === 0) return true;
  const recent = new Set(words(spoken).slice(-60));
  const overlap = heardWords.filter((w) => recent.has(w)).length;
  return overlap / heardWords.length >= 0.6;
}

function pickVoice(): SpeechSynthesisVoice | null {
  const voices = window.speechSynthesis?.getVoices() ?? [];
  const lang = (navigator.language || "en-US").toLowerCase();
  const sameLang = voices.filter((v) => v.lang.toLowerCase().startsWith(lang.slice(0, 2)));
  const preferred = /natural|neural|google|aria|jenny|samantha|daniel|serena/i;
  return sameLang.find((v) => preferred.test(v.name)) ?? sameLang[0] ?? voices[0] ?? null;
}

export interface VoiceSession {
  active: boolean;
  state: VoiceState;
  error: string | null;
  partial: string;
  sttMode: SttMode | null;
  ttsMode: TtsPreference;
  capabilities: Capabilities | null;
  micAnalyser: AnalyserNode | null;
  playbackAnalyser: AnalyserNode | null;
  start: () => Promise<void>;
  stop: () => void;
  interrupt: () => void;
  sendText: (text: string) => void;
  setTtsPreference: (preference: TtsPreference) => void;
}

export function useVoiceSession(): VoiceSession {
  const [state, setStateValue] = useState<VoiceState>("off");
  const [error, setError] = useState<string | null>(null);
  const [partial, setPartial] = useState("");
  const [sttMode, setSttMode] = useState<SttMode | null>(null);
  const [ttsMode, setTtsMode] = useState<TtsPreference>("server");
  const [capabilities, setCapabilities] = useState<Capabilities | null>(null);
  const [micAnalyser, setMicAnalyser] = useState<AnalyserNode | null>(null);
  const [playbackAnalyser, setPlaybackAnalyser] = useState<AnalyserNode | null>(null);

  const activeRef = useRef(false);
  const stateRef = useRef<VoiceState>("off");
  const wsRef = useRef<WebSocket | null>(null);
  const ctxRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const micAnalyserRef = useRef<AnalyserNode | null>(null);
  const gainRef = useRef<GainNode | null>(null);
  const workletRef = useRef<AudioWorkletNode | null>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const sttModeRef = useRef<SttMode | null>(null);
  const ttsModeRef = useRef<TtsPreference>("server");
  const vadTimerRef = useRef<number | null>(null);

  const sourcesRef = useRef(new Set<AudioBufferSourceNode>());
  const nextStartRef = useRef(0);
  const latestTurnRef = useRef(0);
  const minTurnRef = useRef(0);
  const replyIdRef = useRef<string | null>(null);
  const responseDoneRef = useRef(true);
  const audioDoneRef = useRef(true);
  const sentencesRef = useRef<Map<number, string>>(new Map());
  const spokenRef = useRef("");
  const speechQueueRef = useRef<Array<{ turnId: number; text: string }>>([]);
  const synthSpeakingRef = useRef(false);

  const capturingRef = useRef(false);
  const captureStartedRef = useRef(0);
  const prerollRef = useRef<ArrayBuffer[]>([]);
  const vadRef = useRef({ noise: 0.008, speechMs: 0, silenceMs: 0 });

  const setState = useCallback((next: VoiceState) => {
    stateRef.current = next;
    setStateValue(next);
    useTutorStore.getState().setVoiceState(next);
  }, []);

  const send = useCallback((payload: Record<string, unknown>) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(payload));
  }, []);

  /** Return to listening once the reply text is complete and nothing is still being voiced. */
  const maybeFinishSpeaking = useCallback(() => {
    if (!activeRef.current || !responseDoneRef.current) return;
    const serverAudioPending = ttsModeRef.current === "server" && (!audioDoneRef.current || sourcesRef.current.size > 0);
    const browserSpeechPending = synthSpeakingRef.current || speechQueueRef.current.length > 0;
    if (!serverAudioPending && !browserSpeechPending && stateRef.current !== "listening") setState("listening");
  }, [setState]);

  /** A new learner turn is in flight: nothing from the previous turn may end it early. */
  const markTurnPending = useCallback(() => {
    responseDoneRef.current = false;
    audioDoneRef.current = ttsModeRef.current !== "server";
  }, []);

  const markTurnSettled = useCallback(() => {
    responseDoneRef.current = true;
    audioDoneRef.current = true;
    if (activeRef.current) setState("listening");
  }, [setState]);

  const stopPlayback = useCallback(() => {
    for (const source of sourcesRef.current) {
      try {
        source.onended = null;
        source.stop();
      } catch {
        /* already stopped */
      }
    }
    sourcesRef.current.clear();
    nextStartRef.current = 0;
    speechQueueRef.current = [];
    synthSpeakingRef.current = false;
    if (typeof window !== "undefined") window.speechSynthesis?.cancel();
  }, []);

  const speakNext = useCallback(() => {
    const synth = typeof window !== "undefined" ? window.speechSynthesis : undefined;
    if (!synth || synthSpeakingRef.current) return;
    const item = speechQueueRef.current.shift();
    if (!item) {
      maybeFinishSpeaking();
      return;
    }
    if (item.turnId < minTurnRef.current) {
      speakNext();
      return;
    }
    const utterance = new SpeechSynthesisUtterance(item.text);
    const voice = pickVoice();
    if (voice) utterance.voice = voice;
    utterance.rate = 1.03;
    const finish = () => {
      synthSpeakingRef.current = false;
      speakNext();
    };
    utterance.onend = finish;
    utterance.onerror = finish;
    synthSpeakingRef.current = true;
    setState("speaking");
    synth.speak(utterance);
  }, [maybeFinishSpeaking, setState]);

  /** Barge-in: silence the tutor locally right now, then tell the server to cancel the turn. */
  const interrupt = useCallback(() => {
    minTurnRef.current = latestTurnRef.current + 1;
    stopPlayback();
    send({ event: "interrupt" });
    const replyId = replyIdRef.current;
    if (replyId) {
      const reply = useTutorStore.getState().messages.find((m) => m.id === replyId);
      if (reply?.status === "streaming") useTutorStore.getState().patchMessage(replyId, { status: "interrupted" });
    }
    responseDoneRef.current = true;
    audioDoneRef.current = true;
    vadRef.current.speechMs = 0;
    if (activeRef.current) setState("listening");
  }, [send, setState, stopPlayback]);

  const submitTranscript = useCallback(
    (text: string) => {
      const clean = text.trim();
      if (!clean) return;
      if (stateRef.current === "speaking") interrupt();
      useTutorStore.getState().addMessage({ id: newMessageId(), role: "student", text: clean, status: "done", channel: "voice" });
      markTurnPending();
      send({ event: "transcript", text: clean });
      setState("thinking");
    },
    [interrupt, markTurnPending, send, setState]
  );

  const playPcm = useCallback(
    (buffer: ArrayBuffer) => {
      const ctx = ctxRef.current;
      const gain = gainRef.current;
      if (!ctx || !gain || buffer.byteLength <= 8) return;
      const header = new DataView(buffer, 0, 8);
      const turnId = header.getUint32(0, true);
      const rate = header.getUint32(4, true);
      if (turnId < minTurnRef.current) return; // stale audio from an interrupted turn
      const pcm = new Int16Array(buffer, 8, Math.floor((buffer.byteLength - 8) / 2));
      const audio = ctx.createBuffer(1, pcm.length, rate);
      const channel = audio.getChannelData(0);
      for (let i = 0; i < pcm.length; i += 1) channel[i] = pcm[i] / 32768;
      const source = ctx.createBufferSource();
      source.buffer = audio;
      source.connect(gain);
      const startAt = Math.max(ctx.currentTime + 0.04, nextStartRef.current);
      source.start(startAt);
      nextStartRef.current = startAt + audio.duration;
      sourcesRef.current.add(source);
      source.onended = () => {
        sourcesRef.current.delete(source);
        maybeFinishSpeaking();
      };
      if (stateRef.current !== "speaking") setState("speaking");
    },
    [maybeFinishSpeaking, setState]
  );

  const enqueueSpeech = useCallback(
    (turnId: number, text: string) => {
      speechQueueRef.current.push({ turnId, text });
      speakNext();
    },
    [speakNext]
  );

  const startBrowserRecognition = useCallback((Ctor: SpeechRecognitionCtor) => {
    const recognition = new Ctor();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = navigator.language || "en-US";
    recognition.onresult = (event) => {
      let interim = "";
      let final = "";
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i];
        if (result.isFinal) final += result[0].transcript;
        else interim += result[0].transcript;
      }
      const tutorTalking = stateRef.current === "speaking";
      if (interim) {
        setPartial(interim);
        if (tutorTalking && words(interim).length >= 2 && !isEcho(interim, spokenRef.current)) interrupt();
      }
      if (final.trim()) {
        setPartial("");
        if (!(tutorTalking && isEcho(final, spokenRef.current))) submitTranscript(final);
      }
    };
    recognition.onerror = (event) => {
      if (event.error === "not-allowed" || event.error === "service-not-allowed") {
        setError("Speech recognition is blocked in this browser. You can still type; replies will be spoken.");
        sttModeRef.current = "none";
        setSttMode("none");
      }
    };
    recognition.onend = () => {
      // Recognizers stop after long silences; keep listening for the whole session.
      if (activeRef.current && sttModeRef.current === "browser") {
        try {
          recognition.start();
        } catch {
          /* already restarting */
        }
      }
    };
    recognitionRef.current = recognition;
    try {
      recognition.start();
    } catch {
      /* started twice */
    }
  }, [interrupt, submitTranscript]);

  const startServerCapture = useCallback(async () => {
    const ctx = ctxRef.current;
    const stream = streamRef.current;
    if (!ctx || !stream) return;
    const url = URL.createObjectURL(new Blob([PCM_WORKLET], { type: "application/javascript" }));
    try {
      await ctx.audioWorklet.addModule(url);
    } finally {
      URL.revokeObjectURL(url);
    }
    const node = new AudioWorkletNode(ctx, "lumina-pcm-capture");
    const sink = ctx.createGain();
    sink.gain.value = 0; // keep the node pulled by the graph without making it audible
    ctx.createMediaStreamSource(stream).connect(node);
    node.connect(sink).connect(ctx.destination);
    node.port.onmessage = (event: MessageEvent<ArrayBuffer>) => {
      const chunk = event.data;
      if (capturingRef.current) {
        wsRef.current?.send(chunk);
      } else {
        prerollRef.current.push(chunk);
        if (prerollRef.current.length > PREROLL_CHUNKS) prerollRef.current.shift();
      }
    };
    workletRef.current = node;
  }, []);

  const runVad = useCallback(() => {
    const analyser = micAnalyserRef.current;
    if (!analyser) return;
    const samples = new Float32Array(analyser.fftSize);
    vadTimerRef.current = window.setInterval(() => {
      analyser.getFloatTimeDomainData(samples);
      let sum = 0;
      for (let i = 0; i < samples.length; i += 1) sum += samples[i] * samples[i];
      const rms = Math.sqrt(sum / samples.length);
      const vad = vadRef.current;
      const current = stateRef.current;
      if (current === "listening" && vad.speechMs === 0) vad.noise = vad.noise * 0.96 + rms * 0.04;
      const threshold = current === "speaking" ? Math.max(0.03, vad.noise * 5) : Math.max(0.012, vad.noise * 3.2);
      if (rms > threshold) {
        vad.speechMs += VAD_INTERVAL_MS;
        vad.silenceMs = 0;
      } else {
        vad.silenceMs += VAD_INTERVAL_MS;
        vad.speechMs = Math.max(0, vad.speechMs - VAD_INTERVAL_MS / 2);
      }

      if (current === "speaking" && vad.speechMs >= BARGE_IN_MS) interrupt();

      if (sttModeRef.current !== "server") return;
      if (!capturingRef.current && vad.speechMs >= 150 && (current === "listening" || current === "thinking")) {
        capturingRef.current = true;
        captureStartedRef.current = performance.now();
        send({ event: "audio_start", format: "pcm16", sample_rate: 16000 });
        for (const chunk of prerollRef.current) wsRef.current?.send(chunk);
        prerollRef.current = [];
      } else if (
        capturingRef.current &&
        (vad.silenceMs >= UTTERANCE_SILENCE_MS || performance.now() - captureStartedRef.current > MAX_UTTERANCE_MS)
      ) {
        capturingRef.current = false;
        markTurnPending();
        send({ event: "audio_end" });
        setState("thinking");
      }
    }, VAD_INTERVAL_MS);
  }, [interrupt, markTurnPending, send, setState]);

  const handleEvent = useCallback(
    (message: Record<string, unknown>) => {
      const turnId = typeof message.turn_id === "number" ? message.turn_id : null;
      if (turnId !== null) latestTurnRef.current = Math.max(latestTurnRef.current, turnId);
      const store = useTutorStore.getState();
      switch (message.event) {
        case "ready": {
          const caps = message.capabilities as Capabilities;
          setCapabilities(caps);
          ttsModeRef.current = message.tts === "server" ? "server" : "browser";
          setTtsMode(ttsModeRef.current);
          const Ctor = recognitionCtor();
          const mode: SttMode = Ctor ? "browser" : caps.server_stt ? "server" : "none";
          sttModeRef.current = mode;
          setSttMode(mode);
          if (mode === "browser" && Ctor) startBrowserRecognition(Ctor);
          else if (mode === "server") {
            startServerCapture().catch(() => {
              sttModeRef.current = "none";
              setSttMode("none");
              setError("This browser can't capture microphone audio for the tutor. Type below; replies will still be spoken.");
            });
          } else setError("This browser can't recognize speech and server transcription is offline. Type below; replies will still be spoken.");
          setState("listening");
          break;
        }
        case "state":
          if (message.state === "thinking") setState("thinking");
          else if (message.state === "speaking" && ttsModeRef.current === "server") setState("speaking");
          else if (message.state === "listening") maybeFinishSpeaking();
          break;
        case "transcript": {
          const text = String(message.text ?? "").trim();
          if (text) store.addMessage({ id: newMessageId(), role: "student", text, status: "done", channel: "voice" });
          else markTurnSettled(); // nothing intelligible was heard
          break;
        }
        case "route": {
          if (turnId !== null && turnId < minTurnRef.current) break;
          const id = newMessageId();
          replyIdRef.current = id;
          responseDoneRef.current = false;
          audioDoneRef.current = ttsModeRef.current !== "server";
          sentencesRef.current = new Map();
          spokenRef.current = "";
          store.addMessage({ id, role: "tutor", text: "", status: "streaming", channel: "voice", route: message as unknown as RouteInfo });
          break;
        }
        case "token":
          if (replyIdRef.current && (turnId === null || turnId >= minTurnRef.current)) store.appendText(replyIdRef.current, String(message.text ?? ""));
          break;
        case "sentence": {
          if (turnId === null || turnId < minTurnRef.current) break;
          const text = String(message.text ?? "");
          sentencesRef.current.set(Number(message.index), text);
          spokenRef.current = `${spokenRef.current} ${text}`;
          if (ttsModeRef.current === "browser") enqueueSpeech(turnId, text);
          break;
        }
        case "tts_fallback": {
          if (turnId === null || turnId < minTurnRef.current) break;
          ttsModeRef.current = "browser";
          setTtsMode("browser");
          audioDoneRef.current = true;
          const from = Number(message.from_index ?? 0);
          [...sentencesRef.current.entries()].filter(([index]) => index >= from).sort((a, b) => a[0] - b[0]).forEach(([, text]) => enqueueSpeech(turnId, text));
          break;
        }
        case "response_end":
          if (replyIdRef.current && (turnId === null || turnId >= minTurnRef.current)) {
            store.patchMessage(replyIdRef.current, { status: "done", engine: String(message.engine ?? "") });
            responseDoneRef.current = true;
            maybeFinishSpeaking(); // with server voice, audio may still be synthesizing
          }
          break;
        case "audio_end":
          if (turnId === null || turnId >= minTurnRef.current) {
            audioDoneRef.current = true;
            maybeFinishSpeaking();
          }
          break;
        case "error":
          setError(
            message.code === "auth_required"
              ? "Your session has ended. Sign in again to talk with the tutor."
              : String(message.message ?? "The voice tutor hit a problem.")
          );
          if (stateRef.current === "thinking") markTurnSettled();
          break;
        default:
          break;
      }
    },
    [enqueueSpeech, markTurnSettled, maybeFinishSpeaking, setState, startBrowserRecognition, startServerCapture]
  );

  const teardown = useCallback(() => {
    activeRef.current = false;
    if (vadTimerRef.current !== null) window.clearInterval(vadTimerRef.current);
    vadTimerRef.current = null;
    stopPlayback();
    const recognition = recognitionRef.current;
    recognitionRef.current = null;
    if (recognition) {
      recognition.onend = null;
      try {
        recognition.abort();
      } catch {
        /* not running */
      }
    }
    workletRef.current?.disconnect();
    workletRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    const ws = wsRef.current;
    wsRef.current = null;
    if (ws) {
      ws.onclose = null;
      ws.close();
    }
    void ctxRef.current?.close().catch(() => undefined);
    ctxRef.current = null;
    micAnalyserRef.current = null;
    gainRef.current = null;
    capturingRef.current = false;
    prerollRef.current = [];
    setMicAnalyser(null);
    setPlaybackAnalyser(null);
    setPartial("");
    setSttMode(null);
    setState("off");
  }, [setState, stopPlayback]);

  const start = useCallback(async () => {
    if (activeRef.current) return;
    setError(null);
    setState("connecting");
    // The socket authenticates once, in its first frame, so start with a token that won't expire mid-handshake.
    const token = await useAuthStore.getState().ensureFreshAccessToken();
    if (stateRef.current !== "connecting") return; // stopped while the session was refreshing
    if (!token) {
      setState("off");
      setError("Your session has ended. Sign in again to talk with the tutor.");
      return;
    }
    try {
      const AudioCtx = window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      const ctx = new AudioCtx();
      await ctx.resume();
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1 },
      });
      const mic = ctx.createAnalyser();
      mic.fftSize = 1024;
      mic.smoothingTimeConstant = 0.55;
      ctx.createMediaStreamSource(stream).connect(mic);
      const gain = ctx.createGain();
      const playback = ctx.createAnalyser();
      playback.fftSize = 512;
      playback.smoothingTimeConstant = 0.6;
      gain.connect(playback).connect(ctx.destination);
      ctxRef.current = ctx;
      streamRef.current = stream;
      micAnalyserRef.current = mic;
      gainRef.current = gain;
      setMicAnalyser(mic);
      setPlaybackAnalyser(playback);
    } catch (err) {
      const name = err instanceof DOMException ? err.name : "";
      teardown();
      setError(
        name === "NotAllowedError"
          ? "Microphone access is blocked. Allow it from the address bar to talk with the tutor."
          : name === "NotFoundError"
            ? "No microphone was found. Connect one, or type your question instead."
            : "Voice mode couldn't start in this browser. You can still type your question."
      );
      return;
    }

    activeRef.current = true;
    minTurnRef.current = 0;
    latestTurnRef.current = 0;
    const ws = new WebSocket(tutorService.voiceSocketUrl());
    ws.binaryType = "arraybuffer";
    wsRef.current = ws;
    ws.onopen = () => {
      const { topic, modality } = useTutorStore.getState();
      ws.send(
        JSON.stringify({
          event: "start",
          token,
          topic: topic.trim() || undefined,
          modality,
          tts: ttsModeRef.current,
        })
      );
    };
    ws.onmessage = (event: MessageEvent<string | ArrayBuffer>) => {
      if (typeof event.data === "string") {
        try {
          handleEvent(JSON.parse(event.data) as Record<string, unknown>);
        } catch {
          /* ignore malformed frames */
        }
      } else {
        playPcm(event.data);
      }
    };
    ws.onerror = () => setError("Can't reach the voice service right now. Make sure the LuminaLearn server is running, then try again.");
    ws.onclose = () => {
      if (activeRef.current) teardown();
    };
    runVad();
  }, [handleEvent, playPcm, runVad, setState, teardown]);

  const stop = useCallback(() => {
    if (activeRef.current) send({ event: "interrupt" });
    teardown();
  }, [send, teardown]);

  const sendText = useCallback((text: string) => submitTranscript(text), [submitTranscript]);

  const setTtsPreference = useCallback(
    (preference: TtsPreference) => {
      ttsModeRef.current = preference;
      setTtsMode(preference);
      send({ event: "config", tts: preference });
    },
    [send]
  );

  // Keep the live session's topic and modality in sync with the workspace.
  const topic = useTutorStore((s) => s.topic);
  const modality = useTutorStore((s) => s.modality);
  useEffect(() => {
    if (activeRef.current) send({ event: "config", topic, modality });
  }, [topic, modality, send]);

  useEffect(() => () => teardown(), [teardown]);

  return {
    active: state !== "off",
    state,
    error,
    partial,
    sttMode,
    ttsMode,
    capabilities,
    micAnalyser,
    playbackAnalyser,
    start,
    stop,
    interrupt,
    sendText,
    setTtsPreference,
  };
}
