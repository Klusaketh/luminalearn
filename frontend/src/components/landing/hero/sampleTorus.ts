/**
 * Point sampling for the Lumina Core: an area-uniform sample of a torus surface (lumpy via a
 * small tube-radius jitter), plus the scattered start positions used by the intro.
 * Pure functions of (count, seed), so a given tier always builds identical buffers.
 */

export interface CoreBuffers {
  positions: Float32Array;
  normals: Float32Array;
  scatter: Float32Array;
  random: Float32Array;
}

function mulberry32(seed: number) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function sampleCore(count: number, radius = 1.6, tube = 0.75, seed = 7): CoreBuffers {
  const rand = mulberry32(seed);
  const positions = new Float32Array(count * 3);
  const normals = new Float32Array(count * 3);
  const scatter = new Float32Array(count * 3);
  const random = new Float32Array(count);

  let i = 0;
  while (i < count) {
    const u = rand() * Math.PI * 2;
    const v = rand() * Math.PI * 2;
    // Rejection keeps density uniform by area: the outer rim has more surface than the inner one.
    if (rand() > (radius + tube * Math.cos(v)) / (radius + tube)) continue;
    const r = tube * (0.9 + rand() * 0.2);
    const ring = radius + r * Math.cos(v);
    const o = i * 3;
    positions[o] = ring * Math.cos(u);
    positions[o + 1] = ring * Math.sin(u);
    positions[o + 2] = r * Math.sin(v);
    normals[o] = Math.cos(v) * Math.cos(u);
    normals[o + 1] = Math.cos(v) * Math.sin(u);
    normals[o + 2] = Math.sin(v);

    // Start inside a wide sphere (cube-root radius = uniform by volume).
    const theta = rand() * Math.PI * 2;
    const phi = Math.acos(2 * rand() - 1);
    const s = 7 * Math.cbrt(rand());
    scatter[o] = s * Math.sin(phi) * Math.cos(theta);
    scatter[o + 1] = s * Math.sin(phi) * Math.sin(theta);
    scatter[o + 2] = s * Math.cos(phi);

    random[i] = rand();
    i += 1;
  }
  return { positions, normals, scatter, random };
}

export const PARTICLES_BY_TIER = { high: 40000, mid: 18000, low: 6000 } as const;
