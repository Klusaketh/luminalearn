"use client";

import { Fragment } from "react";
import { motion, useReducedMotion, type Variants } from "framer-motion";
import { cn } from "@/utils/cn";

type Tag = "h1" | "h2" | "h3" | "p" | "span";

interface RevealTextProps {
  /** Text to reveal. Wrap a word in asterisks ("Learning that *adapts* to you") for the serif accent. */
  text: string;
  as?: Tag;
  className?: string;
  /** Seconds before the first word moves. */
  delay?: number;
  /** Seconds between words. */
  stagger?: number;
  /** Reveal on mount instead of when scrolled into view. */
  immediate?: boolean;
}

const MOTION_TAGS = {
  h1: motion.h1,
  h2: motion.h2,
  h3: motion.h3,
  p: motion.p,
  span: motion.span,
} as const;

/** Splits "a *b* c" into words, flagging the ones inside asterisks as accent words. */
function parseWords(text: string): Array<{ word: string; accent: boolean }> {
  const words: Array<{ word: string; accent: boolean }> = [];
  text.split(/(\*[^*]+\*)/).forEach((part) => {
    const accent = part.startsWith("*") && part.endsWith("*") && part.length > 2;
    const body = accent ? part.slice(1, -1) : part;
    body.split(/\s+/).filter(Boolean).forEach((word) => words.push({ word, accent }));
  });
  return words;
}

/**
 * Masked word-by-word reveal: each word rises out of its own clipping line as the text enters
 * the viewport. Screen readers get the plain sentence once (the animated words are aria-hidden),
 * and reduced-motion users see the final text immediately.
 */
export function RevealText({ text, as = "h2", className, delay = 0, stagger = 0.06, immediate = false }: RevealTextProps) {
  const reduceMotion = useReducedMotion();
  const words = parseWords(text);
  const plain = words.map((w) => w.word).join(" ");
  const MotionTag = MOTION_TAGS[as];

  const container: Variants = {
    hidden: {},
    shown: { transition: { staggerChildren: stagger, delayChildren: delay } },
  };
  const item: Variants = {
    hidden: { y: "110%", opacity: 0 },
    shown: { y: "0%", opacity: 1, transition: { duration: 0.9, ease: [0.16, 1, 0.3, 1] } },
  };

  const trigger = reduceMotion
    ? { initial: "shown", animate: "shown" }
    : immediate
      ? { initial: "hidden", animate: "shown" }
      : { initial: "hidden", whileInView: "shown", viewport: { once: true, amount: 0.4 } };

  return (
    <MotionTag className={className} aria-label={plain} variants={container} {...trigger}>
      {words.map(({ word, accent }, index) => (
        <Fragment key={`${word}-${index}`}>
          <span aria-hidden="true" className="inline-block overflow-hidden pb-[0.12em] align-bottom">
            <motion.span variants={item} className={cn("inline-block will-change-transform", accent && "font-accent")}>
              {word}
            </motion.span>
          </span>
          {index < words.length - 1 ? " " : null}
        </Fragment>
      ))}
    </MotionTag>
  );
}
