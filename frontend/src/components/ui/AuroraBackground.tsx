/**
 * Ambient deep-space backdrop: three slow aurora fields, a fading hairline grid and film grain.
 * Transform-only animation on soft radial gradients (no blur filters) keeps it GPU-cheap,
 * and the global reduced-motion rule freezes it for users who ask for less motion.
 */
const GRAIN =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E\")";

export function AuroraBackground() {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-space-950">
      <div className="absolute -left-[15%] -top-[35%] h-[85vh] w-[80vw] animate-aurora-drift rounded-full bg-[radial-gradient(closest-side,rgba(139,92,246,0.24),rgba(139,92,246,0.06)_55%,transparent)] will-change-transform" />
      <div className="absolute -right-[20%] -top-[25%] h-[70vh] w-[70vw] animate-aurora-drift rounded-full bg-[radial-gradient(closest-side,rgba(6,182,212,0.15),rgba(6,182,212,0.04)_55%,transparent)] will-change-transform [animation-delay:-9s]" />
      <div className="absolute -bottom-[40%] left-[15%] h-[70vh] w-[70vw] animate-aurora-drift rounded-full bg-[radial-gradient(closest-side,rgba(245,158,11,0.09),transparent)] will-change-transform [animation-delay:-18s]" />
      <div className="absolute inset-0 opacity-40 [background-image:linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] [background-size:72px_72px] [mask-image:radial-gradient(ellipse_70%_55%_at_50%_0%,black,transparent)]" />
      <div className="absolute inset-0 opacity-[0.07] mix-blend-overlay" style={{ backgroundImage: GRAIN }} />
    </div>
  );
}
