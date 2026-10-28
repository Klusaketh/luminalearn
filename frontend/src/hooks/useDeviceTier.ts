"use client";

import { useEffect, useState } from "react";

/**
 * How much visual effect a device can carry.
 *  - high: desktop-class GPU path (full particle counts + postprocessing)
 *  - mid:  phones, tablets and 4-core / 4 GB machines (reduced counts)
 *  - low:  no WebGL2, 2 cores, 2 GB, or Data Saver (static fallbacks)
 */
export type DeviceTier = "high" | "mid" | "low";

interface NavigatorHints extends Navigator {
  deviceMemory?: number;
  connection?: { saveData?: boolean };
}

let cached: DeviceTier | null = null;
let webgl2: boolean | null = null;

/** three.js r163+ renders through WebGL2 only; without it every 3D scene must use its fallback. */
export function supportsWebGL2(): boolean {
  if (webgl2 !== null) return webgl2;
  try {
    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl2");
    webgl2 = !!gl;
    gl?.getExtension("WEBGL_lose_context")?.loseContext();
  } catch {
    webgl2 = false;
  }
  return webgl2;
}

export function detectDeviceTier(): DeviceTier {
  if (cached) return cached;
  const nav = navigator as NavigatorHints;
  const cores = nav.hardwareConcurrency ?? 4;
  const memory = nav.deviceMemory ?? 8;
  const coarse = window.matchMedia("(pointer: coarse)").matches;
  const narrow = window.matchMedia("(max-width: 767px)").matches;

  if (!supportsWebGL2() || cores <= 2 || memory <= 2 || nav.connection?.saveData) {
    cached = "low";
  } else if (coarse || narrow || cores <= 4 || memory <= 4) {
    cached = "mid";
  } else {
    cached = "high";
  }
  return cached;
}

/**
 * The device tier, measured once on the client. `null` until mounted, so server-rendered markup
 * always shows the lightweight fallback first and upgrades after hydration.
 */
export function useDeviceTier(): DeviceTier | null {
  const [tier, setTier] = useState<DeviceTier | null>(cached);
  useEffect(() => {
    setTier(detectDeviceTier());
  }, []);
  return tier;
}
