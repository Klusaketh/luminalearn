"use client";

import { useRef } from "react";
import { useInView, useReducedMotion } from "framer-motion";
import { AnimatedNumber } from "@/components/ui/AnimatedNumber";

interface CounterProps {
  value: number;
  format?: (value: number) => string;
  className?: string;
  duration?: number;
}

const defaultFormat = (v: number) => Math.round(v).toString();

/**
 * Counts up from 0 to `value` the first time it scrolls into view. Screen readers always get the
 * final figure (the animated digits are aria-hidden); reduced-motion users see it immediately.
 */
export function Counter({ value, format = defaultFormat, className, duration = 1.6 }: CounterProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.6 });
  const reduceMotion = useReducedMotion();
  return (
    <span ref={ref}>
      <span className="sr-only">{format(value)}</span>
      <span aria-hidden="true">
        <AnimatedNumber value={inView || reduceMotion ? value : 0} format={format} className={className} duration={duration} />
      </span>
    </span>
  );
}
