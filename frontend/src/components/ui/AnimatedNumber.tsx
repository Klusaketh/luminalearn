"use client";

import { useEffect, useRef } from "react";
import { animate, useReducedMotion } from "framer-motion";

interface AnimatedNumberProps {
  value: number;
  /** Formats the in-flight value; defaults to a rounded integer. */
  format?: (value: number) => string;
  className?: string;
  duration?: number;
}

/**
 * Counts smoothly from the previous value to the new one with tabular figures, writing to
 * the DOM directly so a 60fps count never re-renders React. Jumps instantly for users who
 * prefer reduced motion.
 */
export function AnimatedNumber({ value, format = (v) => Math.round(v).toString(), className, duration = 0.9 }: AnimatedNumberProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const previous = useRef(value);
  const reduceMotion = useReducedMotion();
  const formatRef = useRef(format);
  formatRef.current = format;

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const from = previous.current;
    previous.current = value;
    if (reduceMotion || from === value) {
      node.textContent = formatRef.current(value);
      return;
    }
    const controls = animate(from, value, {
      duration,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (latest) => {
        node.textContent = formatRef.current(latest);
      },
    });
    return () => controls.stop();
  }, [value, duration, reduceMotion]);

  return (
    <span ref={ref} className={`tabular ${className ?? ""}`}>
      {format(value)}
    </span>
  );
}
