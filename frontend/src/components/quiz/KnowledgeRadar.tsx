"use client";

import { useId } from "react";
import { motion } from "framer-motion";
import type { TopicMasterySummary } from "@/services/quizService";

const SIZE = 320;
const CENTER = SIZE / 2;
const RADIUS = 104;

function point(index: number, count: number, value: number) {
  const angle = -Math.PI / 2 + (index / count) * Math.PI * 2;
  return { x: CENTER + Math.cos(angle) * RADIUS * value, y: CENTER + Math.sin(angle) * RADIUS * value, angle };
}

/** Bayesian mastery across assessed topics: a radar for three or more, bars otherwise. */
export function KnowledgeRadar({ items }: { items: TopicMasterySummary[] }) {
  const id = useId().replace(/:/g, "");
  const topics = items.slice(0, 7);
  const description = topics.map((t) => `${t.topic_title} ${Math.round(t.current_mastery * 100)}%`).join(", ");

  if (topics.length < 3) {
    return (
      <ul className="space-y-3" aria-label="Mastery by topic">
        {topics.map((t) => (
          <li key={t.topic_title}>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-200">{t.topic_title}</span>
              <span className="tabular font-semibold text-white">{Math.round(t.current_mastery * 100)}%</span>
            </div>
            <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-white/[0.06]">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400"
                initial={{ width: 0 }}
                animate={{ width: `${t.current_mastery * 100}%` }}
                transition={{ type: "spring", stiffness: 90, damping: 18 }}
              />
            </div>
          </li>
        ))}
      </ul>
    );
  }

  const polygon = topics.map((t, i) => point(i, topics.length, Math.max(0.04, t.current_mastery)));
  return (
    <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="mx-auto w-full max-w-[22rem]" role="img" aria-label={`Mastery by topic: ${description}`}>
      <defs>
        <radialGradient id={`fill-${id}`}>
          <stop offset="0%" stopColor="rgba(34,211,238,0.45)" />
          <stop offset="100%" stopColor="rgba(139,92,246,0.25)" />
        </radialGradient>
      </defs>
      {[0.25, 0.5, 0.75, 1].map((ring) => (
        <polygon
          key={ring}
          points={topics.map((_, i) => point(i, topics.length, ring)).map((p) => `${p.x},${p.y}`).join(" ")}
          fill="none"
          stroke={ring === 1 ? "rgba(255,255,255,0.14)" : "rgba(255,255,255,0.06)"}
        />
      ))}
      {topics.map((t, i) => {
        const edge = point(i, topics.length, 1);
        const label = point(i, topics.length, 1.22);
        const anchor = Math.abs(Math.cos(label.angle)) < 0.2 ? "middle" : Math.cos(label.angle) > 0 ? "start" : "end";
        return (
          <g key={t.topic_title}>
            <line x1={CENTER} y1={CENTER} x2={edge.x} y2={edge.y} stroke="rgba(255,255,255,0.06)" />
            <text x={label.x} y={label.y + 4} textAnchor={anchor} fontSize={11} fill="#C2C7DC">
              {t.topic_title.length > 16 ? `${t.topic_title.slice(0, 15)}…` : t.topic_title}
            </text>
          </g>
        );
      })}
      <motion.polygon
        points={polygon.map((p) => `${p.x},${p.y}`).join(" ")}
        fill={`url(#fill-${id})`}
        stroke="#A78BFA"
        strokeWidth={1.8}
        style={{ transformOrigin: `${CENTER}px ${CENTER}px` }}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 90, damping: 16 }}
      />
      {polygon.map((p, i) => (
        <motion.circle key={topics[i].topic_title} cx={p.x} cy={p.y} r={3.5} fill="#22D3EE" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 + i * 0.05 }} />
      ))}
    </svg>
  );
}
