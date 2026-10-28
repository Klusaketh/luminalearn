import React, { useId } from "react";

/** The Aurora beacon: a luminous node with an orbit, drawn as inline SVG (no network asset). */
export function BrandMark({ className = "h-9 w-9" }: { className?: string }) {
  const id = useId().replace(/:/g, "");
  return (
    <svg viewBox="0 0 40 40" className={className} aria-hidden="true" focusable="false">
      <defs>
        <radialGradient id={`core-${id}`} cx="40%" cy="35%" r="65%">
          <stop offset="0%" stopColor="#F5F3FF" />
          <stop offset="35%" stopColor="#A78BFA" />
          <stop offset="75%" stopColor="#6D28D9" />
          <stop offset="100%" stopColor="#2E1065" />
        </radialGradient>
        <linearGradient id={`orbit-${id}`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#67E8F9" />
          <stop offset="55%" stopColor="#A78BFA" stopOpacity="0.6" />
          <stop offset="100%" stopColor="#FCD34D" />
        </linearGradient>
      </defs>
      <rect x="1" y="1" width="38" height="38" rx="12" fill="#0B0C15" stroke="rgba(255,255,255,0.1)" />
      <circle cx="20" cy="20" r="8.5" fill={`url(#core-${id})`} />
      <ellipse cx="20" cy="20" rx="14" ry="5.5" fill="none" stroke={`url(#orbit-${id})`} strokeWidth="1.6" transform="rotate(-28 20 20)" />
      <circle cx="31.4" cy="14.2" r="1.7" fill="#FCD34D" />
    </svg>
  );
}
