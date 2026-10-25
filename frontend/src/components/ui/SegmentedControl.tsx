"use client";

import React, { useId, useRef } from "react";
import { motion } from "framer-motion";
import { cn } from "@/utils/cn";

export interface SegmentOption<T extends string> {
  value: T;
  label: string;
  icon?: React.ReactNode;
  description?: string;
}

interface SegmentedControlProps<T extends string> {
  options: ReadonlyArray<SegmentOption<T>>;
  value: T;
  onChange: (value: T) => void;
  label: string;
  className?: string;
  size?: "sm" | "md";
  /** Hide labels below the `sm` breakpoint, keeping icons (labels stay in the accessibility tree). */
  compactOnMobile?: boolean;
}

/**
 * Radio-group segmented control with a spring-animated selection pill (shared layoutId).
 * Arrow keys move the selection, matching the WAI-ARIA radio group pattern.
 */
export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
  label,
  className,
  size = "md",
  compactOnMobile = false,
}: SegmentedControlProps<T>) {
  const layoutId = useId();
  const refs = useRef<Array<HTMLButtonElement | null>>([]);

  const onKeyDown = (event: React.KeyboardEvent, index: number) => {
    const delta = event.key === "ArrowRight" || event.key === "ArrowDown" ? 1 : event.key === "ArrowLeft" || event.key === "ArrowUp" ? -1 : 0;
    if (!delta) return;
    event.preventDefault();
    const next = (index + delta + options.length) % options.length;
    onChange(options[next].value);
    refs.current[next]?.focus();
  };

  return (
    <div role="radiogroup" aria-label={label} className={cn("glass inline-flex items-center gap-1 rounded-2xl p-1", className)}>
      {options.map((option, index) => {
        const selected = option.value === value;
        return (
          <button
            key={option.value}
            ref={(node) => {
              refs.current[index] = node;
            }}
            type="button"
            role="radio"
            aria-checked={selected}
            tabIndex={selected ? 0 : -1}
            title={option.description}
            onClick={() => onChange(option.value)}
            onKeyDown={(event) => onKeyDown(event, index)}
            className={cn(
              "relative flex items-center justify-center gap-1.5 rounded-xl font-medium outline-none transition-colors duration-200",
              "focus-visible:ring-2 focus-visible:ring-indigo-300/80",
              size === "sm" ? "h-8 px-2.5 text-xs" : "h-9 px-3.5 text-[13px]",
              selected ? "text-white" : "text-slate-400 hover:text-slate-100"
            )}
          >
            {selected && (
              <motion.span
                layoutId={layoutId}
                aria-hidden="true"
                className="absolute inset-0 rounded-xl bg-[linear-gradient(135deg,rgba(139,92,246,0.55),rgba(6,182,212,0.35))] shadow-[0_0_0_1px_rgba(196,181,253,0.35),0_6px_20px_-6px_rgba(139,92,246,0.6)]"
                transition={{ type: "spring", stiffness: 420, damping: 34 }}
              />
            )}
            <span className="relative z-[1] flex items-center gap-1.5">
              {option.icon}
              <span className={cn(compactOnMobile && "sr-only sm:not-sr-only")}>{option.label}</span>
            </span>
          </button>
        );
      })}
    </div>
  );
}
