"use client";

import { useEffect, useRef } from "react";
import { useReducedMotion } from "framer-motion";

export type OrbMode = "idle" | "listening" | "thinking" | "speaking";

interface VoiceOrbProps {
  mode: OrbMode;
  /** Live audio source: the microphone while listening, tutor playback while speaking. */
  analyser?: AnalyserNode | null;
  className?: string;
  label?: string;
}

type RGB = [number, number, number];

interface Palette {
  core: RGB;
  rim: RGB;
  halo: RGB;
}

const PALETTES: Record<OrbMode, Palette> = {
  idle: { core: [139, 92, 246], rim: [34, 211, 238], halo: [139, 92, 246] },
  listening: { core: [34, 211, 238], rim: [167, 139, 250], halo: [6, 182, 212] },
  thinking: { core: [124, 58, 237], rim: [196, 181, 253], halo: [109, 40, 217] },
  speaking: { core: [245, 158, 11], rim: [167, 139, 250], halo: [245, 158, 11] },
};

const MODES: OrbMode[] = ["idle", "listening", "thinking", "speaking"];
const BAND_COUNT = 48;
const POINTS = 120;

const mix = (a: RGB, b: RGB, t: number): RGB => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
const rgba = (c: RGB, alpha: number) => `rgba(${c[0] | 0}, ${c[1] | 0}, ${c[2] | 0}, ${Math.max(0, Math.min(1, alpha))})`;

/** Log-spaced band edges (in FFT bins) covering ~80 Hz to ~8 kHz, where speech energy lives. */
function bandEdges(binCount: number, sampleRate: number): Array<[number, number]> {
  const nyquist = sampleRate / 2;
  const edges: Array<[number, number]> = [];
  for (let i = 0; i < BAND_COUNT; i += 1) {
    const lo = 80 * Math.pow(8000 / 80, i / BAND_COUNT);
    const hi = 80 * Math.pow(8000 / 80, (i + 1) / BAND_COUNT);
    const a = Math.min(binCount - 1, Math.floor((lo / nyquist) * binCount));
    const b = Math.min(binCount, Math.max(a + 1, Math.ceil((hi / nyquist) * binCount)));
    edges.push([a, b]);
  }
  return edges;
}

/**
 * Holographic voice orb rendered on a 2D canvas.
 *  - idle: slow breathing luminescence
 *  - listening: radial frequency bars driven by the microphone spectrum
 *  - thinking: three tilted orbit rings with travelling sparks
 *  - speaking: a flowing harmonic fluid mesh driven by the tutor's voice
 * Modes cross-fade through per-mode weights, so state changes never pop.
 */
export function VoiceOrb({ mode, analyser = null, className, label }: VoiceOrbProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const modeRef = useRef(mode);
  const analyserRef = useRef(analyser);
  const reduceMotion = useReducedMotion();
  modeRef.current = mode;
  analyserRef.current = analyser;

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    let width = 0;
    let height = 0;
    let visible = true;
    let frame = 0;
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const weights: Record<OrbMode, number> = { idle: 0, listening: 0, thinking: 0, speaking: 0 };
    weights[modeRef.current] = 1;
    const bands = new Float32Array(BAND_COUNT);
    let energy = 0;
    let freq: Uint8Array<ArrayBuffer> | null = null;
    let edges: Array<[number, number]> = [];
    let edgesFor: AnalyserNode | null = null;
    const started = performance.now();
    let last = started;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      width = Math.max(1, rect.width);
      height = Math.max(1, rect.height);
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const readAudio = (t: number, dt: number) => {
      const source = analyserRef.current;
      const smoothing = 1 - Math.exp(-dt * 14);
      if (source) {
        if (edgesFor !== source) {
          freq = new Uint8Array(new ArrayBuffer(source.frequencyBinCount));
          edges = bandEdges(source.frequencyBinCount, source.context.sampleRate);
          edgesFor = source;
        }
        if (freq) source.getByteFrequencyData(freq);
        let sum = 0;
        for (let i = 0; i < BAND_COUNT; i += 1) {
          const [a, b] = edges[i];
          let peak = 0;
          for (let k = a; k < b; k += 1) peak = Math.max(peak, freq ? freq[k] : 0);
          const value = Math.pow(peak / 255, 1.6);
          bands[i] += (value - bands[i]) * smoothing;
          sum += bands[i];
        }
        energy += (Math.min(1, (sum / BAND_COUNT) * 2.2) - energy) * smoothing;
      } else {
        // No analysable stream (e.g. browser speech synthesis): a syllable-rate envelope.
        const speaking = modeRef.current === "speaking";
        const synthetic = speaking ? 0.32 + 0.3 * Math.max(0, Math.sin(t * 26.4) * Math.sin(t * 4.4)) + 0.12 * Math.sin(t * 9.1) : 0;
        energy += (synthetic - energy) * smoothing;
        for (let i = 0; i < BAND_COUNT; i += 1) {
          const target = speaking ? energy * (0.55 + 0.45 * Math.sin(t * 3 + i * 0.7)) : 0;
          bands[i] += (target - bands[i]) * smoothing;
        }
      }
    };

    const blobPath = (cx: number, cy: number, radius: number, displace: (angle: number) => number) => {
      ctx.beginPath();
      const pts: Array<[number, number]> = [];
      for (let i = 0; i < POINTS; i += 1) {
        const angle = (i / POINTS) * Math.PI * 2;
        const r = radius * (1 + displace(angle));
        pts.push([cx + Math.cos(angle) * r, cy + Math.sin(angle) * r]);
      }
      const mid = (a: [number, number], b: [number, number]): [number, number] => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
      const start = mid(pts[POINTS - 1], pts[0]);
      ctx.moveTo(start[0], start[1]);
      for (let i = 0; i < POINTS; i += 1) {
        const next = mid(pts[i], pts[(i + 1) % POINTS]);
        ctx.quadraticCurveTo(pts[i][0], pts[i][1], next[0], next[1]);
      }
      ctx.closePath();
    };

    const draw = (now: number) => {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      const t = reduceMotion ? 1.2 : (now - started) / 1000;
      for (const m of MODES) {
        const target = m === modeRef.current ? 1 : 0;
        weights[m] = reduceMotion ? target : weights[m] + (target - weights[m]) * (1 - Math.exp(-dt * 5));
      }
      if (!reduceMotion) readAudio(t, dt);

      const palette = MODES.reduce<Palette>(
        (acc, m) => ({ core: mix(acc.core, PALETTES[m].core, weights[m]), rim: mix(acc.rim, PALETTES[m].rim, weights[m]), halo: mix(acc.halo, PALETTES[m].halo, weights[m]) }),
        { ...PALETTES.idle }
      );
      const cx = width / 2;
      const cy = height / 2;
      const base = Math.min(width, height) * 0.27;
      const breathe = 0.03 * Math.sin(t * 1.25) * (weights.idle + weights.thinking * 0.5);
      const radius = base * (1 + breathe + energy * 0.09 * (weights.listening + weights.speaking));

      ctx.clearRect(0, 0, width, height);
      ctx.globalCompositeOperation = "source-over";

      // halo
      // Keep the halo inside the canvas so it fades to nothing instead of clipping into a box.
      const haloRadius = Math.min(radius * 2.15, Math.min(width, height) / 2);
      const halo = ctx.createRadialGradient(cx, cy, radius * 0.6, cx, cy, haloRadius);
      halo.addColorStop(0, rgba(palette.halo, 0.32 + energy * 0.25));
      halo.addColorStop(0.45, rgba(palette.halo, 0.1 + energy * 0.08));
      halo.addColorStop(1, rgba(palette.halo, 0));
      ctx.fillStyle = halo;
      ctx.fillRect(0, 0, width, height);

      // listening: radial frequency bars
      if (weights.listening > 0.01) {
        ctx.lineCap = "round";
        ctx.lineWidth = Math.max(1.5, radius * 0.035);
        const bars = 72;
        for (let i = 0; i < bars; i += 1) {
          const angle = (i / bars) * Math.PI * 2 - Math.PI / 2 + t * 0.15;
          const band = bands[Math.floor((Math.abs(i - bars / 2) / (bars / 2)) * (BAND_COUNT - 1))];
          const inner = radius * 1.22;
          const length = radius * (0.06 + band * 0.62);
          ctx.strokeStyle = rgba(mix(palette.rim, palette.core, band), weights.listening * (0.35 + band * 0.65));
          ctx.beginPath();
          ctx.moveTo(cx + Math.cos(angle) * inner, cy + Math.sin(angle) * inner);
          ctx.lineTo(cx + Math.cos(angle) * (inner + length), cy + Math.sin(angle) * (inner + length));
          ctx.stroke();
        }
      }

      // thinking: orbit rings with sparks
      if (weights.thinking > 0.01) {
        for (let ring = 0; ring < 3; ring += 1) {
          const tilt = ring * (Math.PI / 3) + t * (0.35 + ring * 0.18) * (ring % 2 ? -1 : 1);
          const rx = radius * (1.45 + ring * 0.13);
          const ry = radius * (0.42 + ring * 0.07);
          ctx.lineWidth = 1.2;
          ctx.strokeStyle = rgba(palette.rim, weights.thinking * (0.45 - ring * 0.1));
          ctx.beginPath();
          ctx.ellipse(cx, cy, rx, ry, tilt, 0, Math.PI * 2);
          ctx.stroke();
          const phase = t * (1.6 + ring * 0.55) + ring * 2;
          const sx = cx + Math.cos(phase) * rx * Math.cos(tilt) - Math.sin(phase) * ry * Math.sin(tilt);
          const sy = cy + Math.cos(phase) * rx * Math.sin(tilt) + Math.sin(phase) * ry * Math.cos(tilt);
          const spark = ctx.createRadialGradient(sx, sy, 0, sx, sy, radius * 0.16);
          spark.addColorStop(0, rgba([255, 255, 255], weights.thinking * 0.95));
          spark.addColorStop(0.35, rgba(palette.rim, weights.thinking * 0.6));
          spark.addColorStop(1, rgba(palette.rim, 0));
          ctx.fillStyle = spark;
          ctx.beginPath();
          ctx.arc(sx, sy, radius * 0.16, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // orb body
      const low = (bands[2] + bands[4] + bands[6]) / 3;
      const mid = (bands[14] + bands[18] + bands[22]) / 3;
      const displace = (angle: number) =>
        weights.listening * (low * 0.07 * Math.sin(angle * 3 + t * 2.2) + mid * 0.05 * Math.sin(angle * 5 - t * 2.9)) +
        weights.speaking * (energy * 0.08 * Math.sin(angle * 2 + t * 1.9) + energy * 0.05 * Math.sin(angle * 4 - t * 2.6)) +
        0.012 * Math.sin(angle * 3 + t * 0.9);
      blobPath(cx, cy, radius, displace);
      const body = ctx.createRadialGradient(cx - radius * 0.35, cy - radius * 0.4, radius * 0.05, cx, cy, radius * 1.08);
      body.addColorStop(0, rgba(mix(palette.core, [255, 255, 255], 0.75), 1));
      body.addColorStop(0.32, rgba(palette.core, 0.95));
      body.addColorStop(0.78, rgba(mix(palette.core, [10, 8, 30], 0.55), 0.95));
      body.addColorStop(1, rgba([8, 6, 22], 0.9));
      ctx.fillStyle = body;
      ctx.fill();

      // speaking: additive harmonic fluid mesh inside the body
      if (weights.speaking > 0.01) {
        ctx.save();
        blobPath(cx, cy, radius, displace);
        ctx.clip();
        ctx.globalCompositeOperation = "lighter";
        for (let layer = 0; layer < 3; layer += 1) {
          const k = layer + 2;
          blobPath(cx + Math.sin(t * (0.7 + layer * 0.4)) * radius * 0.18, cy + Math.cos(t * (0.6 + layer * 0.3)) * radius * 0.14, radius * (0.62 - layer * 0.1), (angle) =>
            (0.12 + energy * 0.22) * Math.sin(angle * k + t * (1.4 + layer * 0.8)) + bands[8 + layer * 9] * 0.12 * Math.sin(angle * (k + 2) - t * 2)
          );
          const fluid = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
          const tint = layer === 1 ? PALETTES.speaking.rim : mix(PALETTES.speaking.core, [255, 236, 179], layer * 0.4);
          fluid.addColorStop(0, rgba(tint, weights.speaking * (0.28 + energy * 0.25)));
          fluid.addColorStop(1, rgba(tint, 0));
          ctx.fillStyle = fluid;
          ctx.fill();
        }
        ctx.restore();
        ctx.globalCompositeOperation = "source-over";
      }

      // rim light + specular highlight
      blobPath(cx, cy, radius, displace);
      const rim = ctx.createLinearGradient(cx - radius, cy - radius, cx + radius, cy + radius);
      rim.addColorStop(0, rgba(palette.rim, 0.75));
      rim.addColorStop(0.5, rgba(palette.rim, 0.12));
      rim.addColorStop(1, rgba(palette.core, 0.6));
      ctx.lineWidth = Math.max(1, radius * 0.022);
      ctx.strokeStyle = rim;
      ctx.stroke();
      const gloss = ctx.createRadialGradient(cx - radius * 0.38, cy - radius * 0.46, 0, cx - radius * 0.38, cy - radius * 0.46, radius * 0.5);
      gloss.addColorStop(0, "rgba(255,255,255,0.55)");
      gloss.addColorStop(1, "rgba(255,255,255,0)");
      ctx.fillStyle = gloss;
      ctx.beginPath();
      ctx.ellipse(cx - radius * 0.34, cy - radius * 0.42, radius * 0.42, radius * 0.26, -0.6, 0, Math.PI * 2);
      ctx.fill();
    };

    const loop = (now: number) => {
      if (visible) draw(now);
      if (!reduceMotion) frame = requestAnimationFrame(loop);
    };

    const redraw = () => draw(performance.now());
    resize();
    const observer = new ResizeObserver(() => {
      resize();
      if (reduceMotion) redraw();
    });
    observer.observe(canvas);
    const io = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
    });
    io.observe(canvas);
    canvas.addEventListener("orb-redraw", redraw);
    frame = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      io.disconnect();
      canvas.removeEventListener("orb-redraw", redraw);
    };
    // Re-create the loop only when the motion preference changes; mode/analyser flow through refs.
  }, [reduceMotion]);

  // Reduced motion draws on demand: repaint once per mode change.
  useEffect(() => {
    if (!reduceMotion) return;
    const canvas = canvasRef.current;
    if (canvas) canvas.dispatchEvent(new Event("orb-redraw"));
  }, [mode, reduceMotion]);

  const stateLabel = label ?? `Voice tutor is ${mode === "idle" ? "idle" : mode}`;
  return <canvas ref={canvasRef} role="img" aria-label={stateLabel} className={className} />;
}
