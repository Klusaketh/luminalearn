"use client";

import { useEffect, useId, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { AnimatedNumber } from "@/components/ui/AnimatedNumber";

export function retentionTier(mastery: number): "Novice" | "Developing" | "Competent" | "Mastered" {
  if (mastery >= 0.85) return "Mastered";
  if (mastery >= 0.6) return "Competent";
  if (mastery >= 0.3) return "Developing";
  return "Novice";
}

interface MasteryGaugeProps {
  /** Posterior BKT mastery P(L) in [0, 1]. */
  value: number;
  /** Prior mastery the arc sweeps from (defaults to the previous value). */
  from?: number;
  size?: number;
  label?: string;
  className?: string;
}

const SWEEP = 270;
const THRESHOLDS = [0.3, 0.6, 0.85];

function polar(cx: number, cy: number, r: number, fraction: number) {
  const angle = ((135 + SWEEP * fraction) * Math.PI) / 180;
  return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
}

/**
 * Bayesian Knowledge Tracing gauge: a 270° arc that sweeps from prior to posterior mastery
 * with spring physics, with ticks at the competency thresholds (30 / 60 / 85%).
 */
export function MasteryGauge({ value, from, size = 180, label = "Bayesian mastery", className }: MasteryGaugeProps) {
  const id = useId().replace(/:/g, "");
  const reduceMotion = useReducedMotion();
  const clamped = Math.max(0, Math.min(1, value));
  const [start, setStart] = useState(from ?? clamped);
  useEffect(() => {
    if (from !== undefined) setStart(Math.max(0, Math.min(1, from)));
  }, [from]);

  const stroke = size * 0.075;
  const r = size / 2 - stroke;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = 2 * Math.PI * r;
  const arc = (circumference * SWEEP) / 360;
  const offsetFor = (fraction: number) => arc * (1 - fraction);
  const tier = retentionTier(clamped);
  const delta = clamped - start;

  return (
    <div
      className={`relative inline-flex flex-col items-center ${className ?? ""}`}
      role="meter"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(clamped * 100)}
      aria-valuetext={`${Math.round(clamped * 100)} percent, ${tier}`}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true">
        <defs>
          <linearGradient id={`g-${id}`} x1="0" y1="1" x2="1" y2="0">
            <stop offset="0%" stopColor="#8B5CF6" />
            <stop offset="60%" stopColor="#22D3EE" />
            <stop offset="100%" stopColor="#FCD34D" />
          </linearGradient>
          <filter id={`glow-${id}`} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation={stroke * 0.55} result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.07)"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${arc} ${circumference}`}
          transform={`rotate(135 ${cx} ${cy})`}
        />
        <motion.circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke={`url(#g-${id})`}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${arc} ${circumference}`}
          transform={`rotate(135 ${cx} ${cy})`}
          filter={`url(#glow-${id})`}
          initial={{ strokeDashoffset: offsetFor(start) }}
          animate={{ strokeDashoffset: offsetFor(clamped) }}
          transition={reduceMotion ? { duration: 0 } : { type: "spring", stiffness: 60, damping: 16, mass: 1 }}
        />
        {THRESHOLDS.map((t) => {
          const a = polar(cx, cy, r - stroke * 0.95, t);
          const b = polar(cx, cy, r + stroke * 0.95, t);
          return <line key={t} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={clamped >= t ? "rgba(255,255,255,0.75)" : "rgba(255,255,255,0.22)"} strokeWidth={1.5} />;
        })}
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center pt-1">
        <span className="font-display leading-none text-white" style={{ fontSize: size * 0.26 }}>
          <AnimatedNumber value={clamped * 100} format={(v) => `${Math.round(v)}`} />
          <span className="text-[0.45em] text-slate-300">%</span>
        </span>
        <span className="mt-1 text-xs font-semibold text-slate-200">{tier}</span>
        {from !== undefined && Math.abs(delta) >= 0.005 && (
          <span className={`tabular mt-0.5 text-[11px] font-semibold ${delta > 0 ? "text-emerald-300" : "text-rose-300"}`}>
            {delta > 0 ? "+" : "−"}
            {Math.abs(Math.round(delta * 100))} pts
          </span>
        )}
      </div>
      <span className="-mt-3 text-[11px] text-slate-400">{label}</span>
    </div>
  );
}
