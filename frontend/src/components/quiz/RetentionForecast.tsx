"use client";

import { useId, useMemo, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import { motion } from "framer-motion";
import { forecastRetention } from "@/utils/retention";

const W = 640;
const H = 280;
const PAD = { left: 44, right: 16, top: 18, bottom: 34 };
const HORIZON = 30;

const x = (day: number) => PAD.left + (day / HORIZON) * (W - PAD.left - PAD.right);
const y = (value: number) => PAD.top + (1 - value) * (H - PAD.top - PAD.bottom);

function pathOf(days: number[], values: number[]): string {
  return days.map((d, i) => `${i ? "L" : "M"} ${x(d).toFixed(1)} ${y(values[i]).toFixed(1)}`).join(" ");
}

const formatList = (items: string[]) => (items.length <= 1 ? items.join("") : `${items.slice(0, -1).join(", ")} and ${items[items.length - 1]}`);

/**
 * Interactive Ebbinghaus forecast: forgetting without review versus spaced retrieval at the
 * learner's current mastery. Hover or scrub to read any day; the slider moves the review target.
 */
export function RetentionForecast({ mastery, topic }: { mastery: number; topic: string }) {
  const id = useId().replace(/:/g, "");
  const svgRef = useRef<SVGSVGElement>(null);
  const [target, setTarget] = useState(0.8);
  const [hover, setHover] = useState<number | null>(null);
  const data = useMemo(() => forecastRetention(mastery, target, HORIZON), [mastery, target]);

  const onPointer = (event: ReactPointerEvent<SVGSVGElement>) => {
    const svg = svgRef.current;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    const svgX = ((event.clientX - rect.left) / rect.width) * W;
    const fraction = (svgX - PAD.left) / (W - PAD.left - PAD.right);
    setHover(fraction < 0 || fraction > 1 ? null : Math.round(fraction * (data.days.length - 1)));
  };

  const spacedPath = pathOf(data.days, data.spaced);
  const decayPath = pathOf(data.days, data.noReview);
  const areaPath = `${spacedPath} L ${x(HORIZON)} ${y(0)} L ${x(0)} ${y(0)} Z`;
  const reviews = data.reviewDays.map((d) => `day ${Math.max(1, Math.round(d))}`);
  const day30 = data.noReview[data.noReview.length - 1];
  const summary = `At your current mastery of ${topic}, half of it fades in about ${data.halfLife.toFixed(1)} days without review (${Math.round(day30 * 100)}% left by day 30). Reviewing on ${formatList(reviews) || "no day in this window"} keeps it above ${Math.round(target * 100)}%.`;
  const hoverDay = hover !== null ? data.days[hover] : null;

  return (
    <section aria-label="Retention forecast" className="glass rounded-3xl p-5 sm:p-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h3 className="text-base font-semibold text-white">Retention forecast</h3>
          <p className="mt-1 max-w-xl text-sm leading-relaxed text-slate-300">{summary}</p>
        </div>
        <label className="w-full max-w-[14rem]">
          <span className="flex items-center justify-between text-xs text-slate-300">
            Keep retention above
            <span className="tabular font-semibold text-amber-200">{Math.round(target * 100)}%</span>
          </span>
          <input
            type="range"
            min={0.6}
            max={0.95}
            step={0.05}
            value={target}
            onChange={(event) => setTarget(Number(event.target.value))}
            className="mt-2 h-1.5 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-amber-400"
          />
        </label>
      </div>

      <div className="relative mt-5">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${W} ${H}`}
          className="w-full touch-none select-none"
          role="img"
          aria-label={summary}
          onPointerMove={onPointer}
          onPointerDown={onPointer}
          onPointerLeave={() => setHover(null)}
        >
          <defs>
            <linearGradient id={`stroke-${id}`} x1="0" x2="1" y1="0" y2="0">
              <stop offset="0%" stopColor="#A78BFA" />
              <stop offset="100%" stopColor="#22D3EE" />
            </linearGradient>
            <linearGradient id={`area-${id}`} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="rgba(139,92,246,0.32)" />
              <stop offset="100%" stopColor="rgba(6,182,212,0)" />
            </linearGradient>
          </defs>
          {[0, 0.25, 0.5, 0.75, 1].map((v) => (
            <g key={v}>
              <line x1={PAD.left} x2={W - PAD.right} y1={y(v)} y2={y(v)} stroke="rgba(255,255,255,0.06)" />
              <text x={PAD.left - 8} y={y(v) + 4} textAnchor="end" fontSize={11} fill="#9399B7">
                {Math.round(v * 100)}%
              </text>
            </g>
          ))}
          {[0, 5, 10, 15, 20, 25, 30].map((d) => (
            <text key={d} x={x(d)} y={H - 10} textAnchor={d === 0 ? "start" : d === HORIZON ? "end" : "middle"} fontSize={11} fill="#9399B7">
              {d === 0 ? "Today" : `Day ${d}`}
            </text>
          ))}
          <line x1={PAD.left} x2={W - PAD.right} y1={y(target)} y2={y(target)} stroke="#F59E0B" strokeOpacity={0.7} strokeDasharray="4 5" />
          <motion.path key={`area-${target}`} d={areaPath} fill={`url(#area-${id})`} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.6 }} />
          <motion.path d={decayPath} fill="none" stroke="#FB7185" strokeOpacity={0.8} strokeWidth={2} strokeDasharray="6 6" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1.1, ease: "easeOut" }} />
          <motion.path key={`spaced-${target}`} d={spacedPath} fill="none" stroke={`url(#stroke-${id})`} strokeWidth={2.5} initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1.3, ease: "easeOut" }} />
          {data.reviewDays.map((d, i) => (
            <motion.g key={`${target}-${d}`} initial={{ opacity: 0, scale: 0 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.5 + i * 0.12, type: "spring", stiffness: 400, damping: 20 }}>
              <line x1={x(d)} x2={x(d)} y1={y(1)} y2={y(target)} stroke="#FCD34D" strokeOpacity={0.35} strokeDasharray="2 4" />
              <circle cx={x(d)} cy={y(1)} r={4.5} fill="#FCD34D" />
            </motion.g>
          ))}
          {hover !== null && hoverDay !== null && (
            <g pointerEvents="none">
              <line x1={x(hoverDay)} x2={x(hoverDay)} y1={PAD.top} y2={H - PAD.bottom} stroke="rgba(255,255,255,0.35)" />
              <circle cx={x(hoverDay)} cy={y(data.spaced[hover])} r={5} fill="#22D3EE" stroke="#05050A" strokeWidth={2} />
              <circle cx={x(hoverDay)} cy={y(data.noReview[hover])} r={5} fill="#FB7185" stroke="#05050A" strokeWidth={2} />
            </g>
          )}
        </svg>
        {hover !== null && hoverDay !== null && (
          <div
            className="glass-strong pointer-events-none absolute top-2 z-10 -translate-x-1/2 rounded-xl px-3 py-2 text-xs shadow-glass"
            style={{ left: `${(x(hoverDay) / W) * 100}%` }}
          >
            <p className="tabular font-semibold text-white">Day {hoverDay.toFixed(1)}</p>
            <p className="tabular text-cyan-200">Spaced review: {Math.round(data.spaced[hover] * 100)}%</p>
            <p className="tabular text-rose-200">No review: {Math.round(data.noReview[hover] * 100)}%</p>
          </div>
        )}
      </div>
      <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-300">
        <span className="flex items-center gap-1.5"><span className="h-0.5 w-5 rounded bg-gradient-to-r from-indigo-400 to-cyan-400" aria-hidden="true" />With spaced review</span>
        <span className="flex items-center gap-1.5"><span className="h-0.5 w-5 border-t-2 border-dashed border-rose-400" aria-hidden="true" />Without review</span>
        <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-amber-300" aria-hidden="true" />Review session</span>
      </div>
    </section>
  );
}
