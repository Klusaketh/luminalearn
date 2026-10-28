"use client";

import { useEffect, useRef, useState } from "react";

const INTERACTIVE = "a, button, [role='button'], [data-cursor], label, summary";

/**
 * Desktop cursor: a dot that tracks the pointer exactly and a ring that follows with lag.
 * Over interactive elements the ring grows; elements with `data-cursor="Open"` show that label.
 * Only mounts for fine, hover-capable pointers without reduced motion; touch, pen and
 * keyboard users keep the native cursor and focus rings untouched.
 */
export function CustomCursor() {
  const [enabled, setEnabled] = useState(false);
  const dotRef = useRef<HTMLDivElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);
  const labelRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const query = window.matchMedia("(pointer: fine) and (hover: hover) and (prefers-reduced-motion: no-preference)");
    const update = () => setEnabled(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    if (!enabled) return;
    const dot = dotRef.current;
    const ring = ringRef.current;
    const label = labelRef.current;
    if (!dot || !ring || !label) return;

    document.documentElement.classList.add("ll-custom-cursor");
    const target = { x: -100, y: -100 };
    const ringPos = { x: -100, y: -100 };
    let scale = 1;
    let targetScale = 1;
    let visible = false;
    let frame = 0;

    const onMove = (event: PointerEvent) => {
      if (event.pointerType !== "mouse") return;
      target.x = event.clientX;
      target.y = event.clientY;
      if (!visible) {
        visible = true;
        ringPos.x = target.x;
        ringPos.y = target.y;
        dot.style.opacity = "1";
        ring.style.opacity = "1";
      }
      const el = (event.target as Element | null)?.closest?.(INTERACTIVE) ?? null;
      const text = el?.getAttribute("data-cursor") ?? "";
      targetScale = text ? 2.6 : el ? 1.7 : 1;
      if (label.textContent !== text) label.textContent = text;
      ring.dataset.active = el ? "true" : "false";
    };
    const onLeave = () => {
      visible = false;
      dot.style.opacity = "0";
      ring.style.opacity = "0";
    };
    const onDown = () => {
      targetScale *= 0.85;
    };

    const loop = () => {
      ringPos.x += (target.x - ringPos.x) * 0.18;
      ringPos.y += (target.y - ringPos.y) * 0.18;
      scale += (targetScale - scale) * 0.2;
      dot.style.transform = `translate3d(${target.x}px, ${target.y}px, 0) translate(-50%, -50%)`;
      ring.style.transform = `translate3d(${ringPos.x}px, ${ringPos.y}px, 0) translate(-50%, -50%) scale(${scale})`;
      label.style.transform = `translate3d(${ringPos.x}px, ${ringPos.y}px, 0) translate(-50%, -50%)`;
      label.style.opacity = label.textContent ? "1" : "0";
      frame = requestAnimationFrame(loop);
    };
    frame = requestAnimationFrame(loop);

    window.addEventListener("pointermove", onMove, { passive: true });
    window.addEventListener("pointerdown", onDown, { passive: true });
    document.documentElement.addEventListener("pointerleave", onLeave);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerdown", onDown);
      document.documentElement.removeEventListener("pointerleave", onLeave);
      document.documentElement.classList.remove("ll-custom-cursor");
    };
  }, [enabled]);

  if (!enabled) return null;
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 z-[200]">
      <div
        ref={ringRef}
        className="absolute left-0 top-0 h-8 w-8 rounded-full border border-white/40 opacity-0 transition-[border-color,background-color] duration-300 will-change-transform data-[active=true]:border-aurora-teal/70 data-[active=true]:bg-aurora-teal/[0.06]"
      />
      <div ref={dotRef} className="absolute left-0 top-0 h-1.5 w-1.5 rounded-full bg-white opacity-0 will-change-transform" />
      <span
        ref={labelRef}
        className="absolute left-0 top-0 font-mono text-[9px] font-medium uppercase tracking-[0.16em] text-white opacity-0 will-change-transform"
      />
    </div>
  );
}
