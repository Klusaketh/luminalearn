"use client";

import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "framer-motion";

/**
 * Reveals streamed text at a smooth, backlog-aware pace: it speeds up when the model
 * outruns the animation and settles to a readable rhythm otherwise. Updates are throttled
 * to ~30fps so markdown re-parsing stays cheap. Text that was already complete when the
 * component mounted, or any text for reduced-motion users, appears immediately.
 */
export function useTypewriter(target: string, streaming: boolean): string {
  const reduceMotion = useReducedMotion();
  const animate = useRef(streaming);
  const [shown, setShown] = useState(() => (streaming ? "" : target));
  const shownLength = useRef(shown.length);

  useEffect(() => {
    if (streaming) animate.current = true;
  }, [streaming]);

  useEffect(() => {
    if (reduceMotion || !animate.current) {
      shownLength.current = target.length;
      setShown(target);
      return;
    }
    if (target.length < shownLength.current) {
      shownLength.current = 0; // the message was replaced: start over
    }
    let frame = 0;
    let last = 0;
    const tick = (now: number) => {
      if (now - last >= 32) {
        last = now;
        const backlog = target.length - shownLength.current;
        if (backlog <= 0) return;
        let next = shownLength.current + Math.max(2, Math.ceil(backlog / 9));
        const space = target.indexOf(" ", next);
        if (space !== -1 && space - next < 8) next = space + 1; // land on word boundaries
        shownLength.current = Math.min(target.length, next);
        setShown(target.slice(0, shownLength.current));
      }
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, reduceMotion]);

  return shown;
}
