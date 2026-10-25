/**
 * Mastery celebration burst in the Aurora palette. Loaded on demand so canvas-confetti never
 * weighs on first paint, and skipped entirely for users who prefer reduced motion.
 */
const COLORS = ["#8B5CF6", "#A78BFA", "#06B6D4", "#67E8F9", "#F59E0B", "#F5F3FF"];

export async function celebrateMastery(origin: { x: number; y: number } = { x: 0.5, y: 0.6 }): Promise<void> {
  if (typeof window === "undefined" || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const { default: confetti } = await import("canvas-confetti");
  const shared = { colors: COLORS, disableForReducedMotion: true, zIndex: 80, ticks: 240 };
  confetti({ ...shared, particleCount: 90, spread: 75, startVelocity: 42, scalar: 0.95, origin });
  window.setTimeout(() => confetti({ ...shared, particleCount: 45, angle: 60, spread: 58, origin: { x: 0, y: 0.75 } }), 170);
  window.setTimeout(() => confetti({ ...shared, particleCount: 45, angle: 120, spread: 58, origin: { x: 1, y: 0.75 } }), 250);
}
