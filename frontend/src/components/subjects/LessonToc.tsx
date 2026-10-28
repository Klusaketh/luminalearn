"use client";

import { useEffect, useState } from "react";
import type { Heading } from "./lessonFormat";

/** Just below the sticky navbar: a heading above this line has been scrolled into reading position. */
const READING_LINE_PX = 140;

/** "On this page" navigation for a lesson; highlights the section being read. */
export function LessonToc({ headings }: { headings: Heading[] }) {
  const [active, setActive] = useState<string | null>(headings[0]?.id ?? null);

  useEffect(() => {
    // The section being read is the last one whose heading has scrolled above the reading line.
    let frame = 0;
    const update = () => {
      frame = 0;
      let current = headings[0]?.id ?? null;
      for (const heading of headings) {
        const el = document.getElementById(heading.id);
        if (!el || el.getBoundingClientRect().top > READING_LINE_PX) break;
        current = heading.id;
      }
      setActive(current);
    };
    const onScroll = () => {
      if (!frame) frame = window.requestAnimationFrame(update);
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      if (frame) window.cancelAnimationFrame(frame);
    };
  }, [headings]);

  if (headings.length === 0) return null;
  return (
    <nav aria-label="On this page" className="text-sm">
      <p className="mb-2 text-xs font-semibold text-slate-400">On this page</p>
      <ul className="space-y-0.5 border-l border-white/[0.08]">
        {headings.map((h) => (
          <li key={h.id}>
            <a
              href={`#${h.id}`}
              aria-current={active === h.id ? "location" : undefined}
              className={`-ml-px block border-l py-1 pl-3 outline-none transition-colors focus-visible:text-white ${
                active === h.id ? "border-indigo-300 text-white" : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              {h.text}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
