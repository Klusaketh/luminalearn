"use client";

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Pause, Play, RotateCcw, StepForward } from "lucide-react";
import type { LabWidget } from "@/services/tutorService";
import { SegmentedControl } from "@/components/ui/SegmentedControl";
import { AnimatedNumber } from "@/components/ui/AnimatedNumber";

const LABS: ReadonlyArray<{ value: LabWidget; label: string }> = [
  { value: "recursion", label: "Call stack" },
  { value: "gradient_descent", label: "Gradient descent" },
  { value: "bayes", label: "Bayes' rule" },
];

function Slider({ label, value, min, max, step, onChange, format }: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
  format: (value: number) => string;
}) {
  return (
    <label className="block">
      <span className="flex items-center justify-between text-xs text-slate-300">
        {label}
        <span className="tabular font-semibold text-white">{format(value)}</span>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="mt-2 h-1.5 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-indigo-400"
      />
    </label>
  );
}

/* ---------------------------------------------------------------- call stack */

type StackStep = { kind: "call"; k: number } | { kind: "return"; k: number; value: number };

function factorialSteps(n: number): StackStep[] {
  const steps: StackStep[] = [];
  for (let k = n; k >= 1; k -= 1) steps.push({ kind: "call", k });
  let value = 1;
  for (let k = 1; k <= n; k += 1) {
    value = k === 1 ? 1 : value * k;
    steps.push({ kind: "return", k, value });
  }
  return steps;
}

function RecursionLab() {
  const [n, setN] = useState(4);
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const steps = useMemo(() => factorialSteps(n), [n]);

  useEffect(() => {
    setStep(0);
    setPlaying(false);
  }, [n]);
  useEffect(() => {
    if (!playing) return;
    if (step >= steps.length) {
      setPlaying(false);
      return;
    }
    const timer = window.setTimeout(() => setStep((s) => s + 1), 650);
    return () => window.clearTimeout(timer);
  }, [playing, step, steps.length]);

  const togglePlay = () => {
    if (step >= steps.length) {
      setStep(0);
      setPlaying(true);
    } else {
      setPlaying((value) => !value);
    }
  };

  const shown = steps.slice(0, step);
  const calls = shown.filter((s) => s.kind === "call").length;
  const returns = shown.filter((s): s is Extract<StackStep, { kind: "return" }> => s.kind === "return");
  const frames = Array.from({ length: calls - returns.length }, (_, i) => n - i);
  const last = shown[shown.length - 1];
  const narration = !last
    ? `Press play to call factorial(${n}).`
    : last.kind === "call"
      ? last.k === 1
        ? "Base case reached: factorial(1) can answer immediately."
        : `factorial(${last.k}) can't finish yet, so it calls factorial(${last.k - 1}) and waits.`
      : last.k === 1
        ? "factorial(1) returns 1, and the stack starts to unwind."
        : `factorial(${last.k}) returns ${last.k} × ${last.value / last.k} = ${last.value}.`;

  return (
    <div className="grid gap-5 md:grid-cols-[1fr_1.1fr]">
      <div className="space-y-4">
        <Slider label="Input n" value={n} min={1} max={7} step={1} onChange={setN} format={(v) => String(v)} />
        <div className="flex gap-2">
          <button type="button" onClick={togglePlay} className="flex items-center gap-1.5 rounded-xl bg-indigo-500/20 px-3 py-2 text-xs font-semibold text-indigo-100 ring-1 ring-indigo-400/30 hover:bg-indigo-500/30">
            {playing ? <Pause className="h-3.5 w-3.5" aria-hidden="true" /> : <Play className="h-3.5 w-3.5" aria-hidden="true" />}
            {playing ? "Pause" : step >= steps.length ? "Replay" : "Play"}
          </button>
          <button type="button" disabled={step >= steps.length} onClick={() => setStep((s) => Math.min(steps.length, s + 1))} className="flex items-center gap-1.5 rounded-xl px-3 py-2 text-xs font-medium text-slate-200 ring-1 ring-white/10 hover:bg-white/5 disabled:opacity-40">
            <StepForward className="h-3.5 w-3.5" aria-hidden="true" /> Step
          </button>
          <button type="button" onClick={() => { setStep(0); setPlaying(false); }} aria-label="Reset" className="rounded-xl px-2.5 py-2 text-slate-300 ring-1 ring-white/10 hover:bg-white/5">
            <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
          </button>
        </div>
        <p className="min-h-[3rem] text-sm leading-relaxed text-slate-200" aria-live="polite">{narration}</p>
        {returns.length === n && <p className="text-sm font-semibold text-emerald-300">Result: factorial({n}) = {returns[returns.length - 1]?.value}</p>}
      </div>
      <div className="flex min-h-[15rem] flex-col-reverse justify-start gap-1.5 rounded-2xl border border-white/[0.06] bg-black/20 p-3" aria-label="Call stack, newest frame on top">
        <AnimatePresence initial={false}>
          {frames.map((k, index) => (
            <motion.div
              key={k}
              layout
              initial={{ opacity: 0, y: -14, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: 24 }}
              transition={{ type: "spring", stiffness: 380, damping: 30 }}
              className={`flex items-center justify-between rounded-xl px-3 py-2 font-mono text-xs ring-1 ${index === frames.length - 1 ? "bg-indigo-500/25 text-white ring-indigo-300/40" : "bg-white/[0.04] text-slate-300 ring-white/10"}`}
            >
              <span>factorial({k})</span>
              <span className="text-[11px] text-slate-400">{k === 1 ? "base case" : `waits for factorial(${k - 1})`}</span>
            </motion.div>
          ))}
        </AnimatePresence>
        {frames.length === 0 && <p className="m-auto text-xs text-slate-500">The stack is empty</p>}
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------- gradient descent */

function GradientDescentLab() {
  const [eta, setEta] = useState(0.3);
  const [theta0, setTheta0] = useState(3.5);
  const path = useMemo(() => {
    const points = [theta0];
    for (let i = 0; i < 14; i += 1) points.push(points[points.length - 1] * (1 - 2 * eta)); // θ ← θ − η·dL/dθ, L = θ²
    return points;
  }, [eta, theta0]);
  const factor = Math.abs(1 - 2 * eta);
  const bouncing = Math.abs(factor - 1) < 1e-9; // slider steps are floats: 1.0000000000000002 means exactly 1
  const status = bouncing
    ? "Stuck bouncing forever"
    : factor < 1
      ? 1 - 2 * eta < 0
        ? "Converging, but overshooting each step"
        : "Converging smoothly"
      : "Diverging: steps grow every time";
  const tone = bouncing ? "text-amber-300" : factor < 1 ? (1 - 2 * eta < 0 ? "text-amber-300" : "text-emerald-300") : "text-rose-300";
  const W = 320, H = 200, X = 5;
  const sx = (x: number) => ((x + X) / (2 * X)) * W;
  const sy = (y: number) => H - 12 - Math.min(1, y / (X * X)) * (H - 24);
  const curve = Array.from({ length: 81 }, (_, i) => {
    const x = -X + (i / 80) * 2 * X;
    return `${i ? "L" : "M"} ${sx(x).toFixed(1)} ${sy(x * x).toFixed(1)}`;
  }).join(" ");
  const visible = path.filter((p) => Math.abs(p) <= X * 1.2);

  return (
    <div className="grid gap-5 md:grid-cols-[1fr_1.2fr]">
      <div className="space-y-4">
        <Slider label="Learning rate η" value={eta} min={0.05} max={1.15} step={0.05} onChange={setEta} format={(v) => v.toFixed(2)} />
        <Slider label="Starting θ" value={theta0} min={-4.5} max={4.5} step={0.5} onChange={setTheta0} format={(v) => v.toFixed(1)} />
        <p className={`text-sm font-semibold ${tone}`} aria-live="polite">{status}</p>
        <p className="text-xs leading-relaxed text-slate-400">
          Each step multiplies θ by (1 − 2η). Predict the result before you move a slider: what happens when that factor drops below −1?
        </p>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full rounded-2xl border border-white/[0.06] bg-black/20" role="img" aria-label={`Loss curve with ${visible.length} gradient steps. ${status}.`}>
        <path d={curve} fill="none" stroke="#5D6384" strokeWidth={1.5} />
        <line x1={sx(0)} x2={sx(0)} y1={8} y2={H - 8} stroke="rgba(255,255,255,0.06)" />
        {visible.slice(1).map((p, i) => (
          <motion.line
            key={`${eta}-${theta0}-${i}`}
            x1={sx(visible[i])}
            y1={sy(visible[i] ** 2)}
            x2={sx(p)}
            y2={sy(p ** 2)}
            stroke="#A78BFA"
            strokeWidth={1.4}
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.85 }}
            transition={{ delay: i * 0.12, duration: 0.25 }}
          />
        ))}
        {visible.map((p, i) => (
          <motion.circle
            key={`${eta}-${theta0}-dot-${i}`}
            cx={sx(p)}
            cy={sy(p ** 2)}
            r={i === 0 ? 5 : 3.5}
            fill={i === 0 ? "#FCD34D" : "#67E8F9"}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: i * 0.12, type: "spring", stiffness: 500, damping: 22 }}
          />
        ))}
      </svg>
    </div>
  );
}

/* ---------------------------------------------------------------- Bayes */

function BayesLab() {
  const [prior, setPrior] = useState(0.01);
  const [sensitivity, setSensitivity] = useState(0.9);
  const [falsePositive, setFalsePositive] = useState(0.05);
  const truePos = prior * sensitivity;
  const falsePos = (1 - prior) * falsePositive;
  const posterior = truePos / (truePos + falsePos);
  const per1000 = { tp: Math.round(truePos * 1000), fp: Math.round(falsePos * 1000) };
  const share = per1000.tp + per1000.fp > 0 ? per1000.tp / (per1000.tp + per1000.fp) : 0;
  const pct = (v: number) => `${(v * 100).toFixed(v < 0.1 ? 1 : 0)}%`;

  return (
    <div className="grid gap-5 md:grid-cols-[1fr_1.1fr]">
      <div className="space-y-4">
        <Slider label="Prior: how common is it?" value={prior} min={0.005} max={0.5} step={0.005} onChange={setPrior} format={pct} />
        <Slider label="Sensitivity P(positive | has it)" value={sensitivity} min={0.5} max={0.99} step={0.01} onChange={setSensitivity} format={pct} />
        <Slider label="False-positive rate" value={falsePositive} min={0.01} max={0.3} step={0.01} onChange={setFalsePositive} format={pct} />
      </div>
      <div className="rounded-2xl border border-white/[0.06] bg-black/20 p-4">
        <p className="text-xs text-slate-400">After one positive test, the chance it's real</p>
        <p className="font-display text-5xl text-white">
          <AnimatedNumber value={posterior * 100} format={(v) => `${v.toFixed(1)}%`} />
        </p>
        <p className="mt-4 text-xs text-slate-300">
          Out of 1,000 people, <span className="tabular font-semibold text-cyan-300">{per1000.tp}</span> true positives and{" "}
          <span className="tabular font-semibold text-amber-300">{per1000.fp}</span> false alarms test positive.
        </p>
        <div className="mt-2 flex h-3 overflow-hidden rounded-full bg-white/5" aria-hidden="true">
          <motion.div className="bg-cyan-400" animate={{ width: `${share * 100}%` }} transition={{ type: "spring", stiffness: 140, damping: 22 }} />
          <motion.div className="bg-amber-400/80" animate={{ width: `${(1 - share) * 100}%` }} transition={{ type: "spring", stiffness: 140, damping: 22 }} />
        </div>
      </div>
    </div>
  );
}

/** Hands-on simulations for kinesthetic learners; the tutor picks the starting lab. */
export function KinestheticLab({ widget }: { widget?: LabWidget }) {
  const [lab, setLab] = useState<LabWidget>(widget ?? "recursion");
  return (
    <section aria-label="Interactive lab" className="mt-4 rounded-2xl border border-white/[0.07] bg-white/[0.02] p-4">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-white">Try it yourself</h3>
        <SegmentedControl label="Choose a lab" size="sm" options={LABS} value={lab} onChange={setLab} />
      </div>
      {lab === "recursion" && <RecursionLab />}
      {lab === "gradient_descent" && <GradientDescentLab />}
      {lab === "bayes" && <BayesLab />}
    </section>
  );
}
