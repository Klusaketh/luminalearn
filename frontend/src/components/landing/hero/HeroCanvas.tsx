"use client";

import { Component, useCallback, useState, type ReactNode } from "react";
import dynamic from "next/dynamic";
import { useReducedMotion } from "framer-motion";
import { supportsWebGL2, useDeviceTier } from "@/hooks/useDeviceTier";
import { cn } from "@/utils/cn";

// three.js + R3F + postprocessing live in their own chunk, fetched only on the client.
const LuminaCore = dynamic(() => import("./LuminaCore"), { ssr: false });

/** CSS-only stand-in for the particle core: shown instantly, and kept for reduced motion / no WebGL2. */
function CoreFallback() {
  return (
    <div className="absolute inset-0 flex items-center justify-center" aria-hidden="true">
      <div className="relative aspect-square w-[min(72vw,34rem)] -translate-y-[3%] [transform:perspective(900px)_rotateX(58deg)]">
        <div className="absolute inset-0 rounded-full bg-[conic-gradient(from_200deg,rgba(45,212,191,0.55),rgba(34,211,238,0.4),rgba(139,92,246,0.6),rgba(99,102,241,0.45),rgba(45,212,191,0.55))] [mask-image:radial-gradient(closest-side,transparent_44%,black_52%,black_78%,transparent_92%)] blur-[2px]" />
        <div className="absolute inset-[18%] rounded-full bg-[radial-gradient(closest-side,rgba(45,212,191,0.18),transparent)]" />
      </div>
    </div>
  );
}

/** If WebGL context creation or the 3D chunk fails, drop the scene and keep the CSS core. */
class SceneBoundary extends Component<{ children: ReactNode; onError: () => void }, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(error: unknown) {
    console.warn("Hero 3D scene unavailable; showing the static core.", error);
    this.props.onError();
  }

  render() {
    return this.state.failed ? null : this.props.children;
  }
}

/**
 * Full-bleed hero visual. The fallback paints with the first byte of HTML; once mounted on a
 * capable device the WebGL core loads and cross-fades in over it.
 */
export function HeroCanvas({ className }: { className?: string }) {
  const reduceMotion = useReducedMotion();
  const tier = useDeviceTier();
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);
  const onReady = useCallback(() => setReady(true), []);
  const onError = useCallback(() => setFailed(true), []);
  const use3D = tier !== null && !reduceMotion && !failed && supportsWebGL2();

  return (
    <div className={cn("pointer-events-none absolute inset-0", className)}>
      <div className={cn("absolute inset-0 transition-opacity duration-1000", ready && use3D ? "opacity-0" : "opacity-100")}>
        <CoreFallback />
      </div>
      {use3D && (
        <div className={cn("absolute inset-0 transition-opacity duration-700", ready ? "opacity-100" : "opacity-0")}>
          <SceneBoundary onError={onError}>
            <LuminaCore tier={tier} onReady={onReady} className="!absolute inset-0" />
          </SceneBoundary>
        </div>
      )}
    </div>
  );
}
