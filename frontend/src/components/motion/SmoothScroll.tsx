"use client";

import { createContext, useContext, useEffect, useState } from "react";
import Lenis from "lenis";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useReducedMotion } from "framer-motion";

gsap.registerPlugin(ScrollTrigger);

const LenisContext = createContext<Lenis | null>(null);

/** The active Lenis instance (null under reduced motion or outside the landing page). */
export function useLenis(): Lenis | null {
  return useContext(LenisContext);
}

/**
 * Smooth scrolling for the marketing page only. GSAP's ticker drives Lenis, and every Lenis
 * scroll updates ScrollTrigger, so scrubbed timelines and the smoothed position never drift.
 * In-app pages keep native scrolling: the tutor, lesson TOC and chat rely on it.
 */
export function SmoothScroll({ children }: { children: React.ReactNode }) {
  const reduceMotion = useReducedMotion();
  const [lenis, setLenis] = useState<Lenis | null>(null);

  useEffect(() => {
    if (reduceMotion) return;
    const instance = new Lenis({ lerp: 0.09, smoothWheel: true, wheelMultiplier: 0.9 });
    const tick = (time: number) => instance.raf(time * 1000);
    instance.on("scroll", ScrollTrigger.update);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);
    setLenis(instance);
    return () => {
      gsap.ticker.remove(tick);
      gsap.ticker.lagSmoothing(500, 33);
      instance.destroy();
      setLenis(null);
    };
  }, [reduceMotion]);

  return <LenisContext.Provider value={lenis}>{children}</LenisContext.Provider>;
}
