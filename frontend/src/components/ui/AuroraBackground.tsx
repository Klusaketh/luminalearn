/**
 * Ambient deep-space backdrop: drifting teal / violet / indigo aurora fields, sparse twinkling
 * stars, a fading hairline grid and film grain. Transform/opacity-only animation on soft radial
 * gradients (no blur filters) keeps it GPU-cheap, and the global reduced-motion rule freezes it
 * for users who ask for less motion.
 */
const GRAIN =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E\")";

/** Deterministic PRNG so server and client render identical star fields. */
function mulberry32(seed: number) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const STARS = (() => {
  const rand = mulberry32(20261028);
  return Array.from({ length: 46 }, () => ({
    left: `${(rand() * 100).toFixed(2)}%`,
    top: `${(rand() * 100).toFixed(2)}%`,
    size: rand() < 0.82 ? 1 : 2,
    delay: `${(-rand() * 8).toFixed(2)}s`,
    duration: `${(3 + rand() * 5).toFixed(2)}s`,
  }));
})();

export function AuroraBackground() {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-space-950">
      <div className="absolute -left-[15%] -top-[35%] h-[85vh] w-[80vw] animate-aurora-drift rounded-full bg-[radial-gradient(closest-side,rgba(45,212,191,0.16),rgba(34,211,238,0.05)_55%,transparent)] will-change-transform" />
      <div className="absolute -right-[20%] -top-[25%] h-[70vh] w-[70vw] animate-aurora-drift rounded-full bg-[radial-gradient(closest-side,rgba(139,92,246,0.22),rgba(139,92,246,0.06)_55%,transparent)] will-change-transform [animation-delay:-9s] [animation-duration:34s]" />
      <div className="absolute -bottom-[40%] left-[15%] h-[70vh] w-[70vw] animate-aurora-drift rounded-full bg-[radial-gradient(closest-side,rgba(99,102,241,0.14),transparent)] will-change-transform [animation-delay:-18s] [animation-duration:40s]" />
      <div className="absolute inset-0">
        {STARS.map((star, index) => (
          <span
            key={index}
            className="absolute animate-twinkle rounded-full bg-white"
            style={{
              left: star.left,
              top: star.top,
              width: star.size,
              height: star.size,
              animationDelay: star.delay,
              animationDuration: star.duration,
            }}
          />
        ))}
      </div>
      <div className="absolute inset-0 opacity-40 [background-image:linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] [background-size:72px_72px] [mask-image:radial-gradient(ellipse_70%_55%_at_50%_0%,black,transparent)]" />
      <div className="absolute inset-0 opacity-[0.07] mix-blend-overlay" style={{ backgroundImage: GRAIN }} />
    </div>
  );
}
