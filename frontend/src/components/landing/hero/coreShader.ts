/**
 * GLSL for the Lumina Core particle field.
 *
 * Vertex stage: each point sits on a torus surface, breathes along its normal with two octaves
 * of 3D simplex noise, converges from a scattered start position during the intro (per-particle
 * delay), and is pushed away from the cursor in world space with a smooth falloff.
 * Fragment stage: a soft round sprite whose colour runs teal -> violet by height + noise,
 * brightest at the silhouette rim. Rendered with additive blending and no depth writes.
 */

// 3D simplex noise: Ashima Arts / Stefan Gustavson (MIT), https://github.com/ashima/webgl-noise
const SIMPLEX_3D = /* glsl */ `
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 permute(vec4 x) { return mod289(((x * 34.0) + 10.0) * x); }
vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

float snoise(vec3 v) {
  const vec2 C = vec2(1.0 / 6.0, 1.0 / 3.0);
  const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
  vec3 i = floor(v + dot(v, C.yyy));
  vec3 x0 = v - i + dot(i, C.xxx);
  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min(g.xyz, l.zxy);
  vec3 i2 = max(g.xyz, l.zxy);
  vec3 x1 = x0 - i1 + C.xxx;
  vec3 x2 = x0 - i2 + C.yyy;
  vec3 x3 = x0 - D.yyy;
  i = mod289(i);
  vec4 p = permute(permute(permute(
            i.z + vec4(0.0, i1.z, i2.z, 1.0))
          + i.y + vec4(0.0, i1.y, i2.y, 1.0))
          + i.x + vec4(0.0, i1.x, i2.x, 1.0));
  float n_ = 0.142857142857;
  vec3 ns = n_ * D.wyz - D.xzx;
  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_);
  vec4 x = x_ * ns.x + ns.yyyy;
  vec4 y = y_ * ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);
  vec4 b0 = vec4(x.xy, y.xy);
  vec4 b1 = vec4(x.zw, y.zw);
  vec4 s0 = floor(b0) * 2.0 + 1.0;
  vec4 s1 = floor(b1) * 2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));
  vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
  vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;
  vec3 p0 = vec3(a0.xy, h.x);
  vec3 p1 = vec3(a0.zw, h.y);
  vec3 p2 = vec3(a1.xy, h.z);
  vec3 p3 = vec3(a1.zw, h.w);
  vec4 norm = taylorInvSqrt(vec4(dot(p0, p0), dot(p1, p1), dot(p2, p2), dot(p3, p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;
  vec4 m = max(0.5 - vec4(dot(x0, x0), dot(x1, x1), dot(x2, x2), dot(x3, x3)), 0.0);
  m = m * m;
  return 105.0 * dot(m * m, vec4(dot(p0, x0), dot(p1, x1), dot(p2, x2), dot(p3, x3)));
}
`;

export const coreVertexShader = /* glsl */ `
uniform float uTime;
uniform vec3 uMouse;
uniform float uMouseStrength;
uniform float uIntro;
uniform float uPixelRatio;
uniform float uSize;

attribute vec3 aNormal;
attribute vec3 aScatter;
attribute float aRandom;

varying float vMix;
varying float vRim;
varying float vFade;

${SIMPLEX_3D}

void main() {
  vec3 p = position;

  // Organic breathing: two noise octaves push each point along its surface normal.
  float n = snoise(p * 1.2 + uTime * 0.15);
  float n2 = snoise(p * 2.7 - uTime * 0.22) * 0.35;
  p += aNormal * (n + n2) * 0.26;

  // Intro: converge from the scattered sphere; later particles start later (power3.out feel).
  float t = clamp(uIntro * 1.4 - aRandom * 0.4, 0.0, 1.0);
  t = 1.0 - pow(1.0 - t, 3.0);
  vec3 swirl = vec3(-aScatter.y, aScatter.x, 0.0) * (1.0 - t) * 0.35;
  p = mix(aScatter + swirl, p, t);

  // Cursor repulsion in world space, so it stays correct while the object rotates.
  vec4 world = modelMatrix * vec4(p, 1.0);
  vec3 away = world.xyz - uMouse;
  float dist = length(away);
  float push = (1.0 - smoothstep(0.0, 0.9, dist)) * uMouseStrength * t;
  world.xyz += (away / max(dist, 1e-4)) * push * 0.6;

  vec4 mv = viewMatrix * world;
  gl_Position = projectionMatrix * mv;
  gl_PointSize = uSize * uPixelRatio * (0.55 + aRandom * 0.9) / -mv.z;

  vec3 viewNormal = normalize(normalMatrix * aNormal);
  vRim = pow(1.0 - abs(viewNormal.z), 1.6);
  vMix = clamp(position.y * 0.32 + 0.5 + n * 0.22, 0.0, 1.0);
  vFade = 0.35 + 0.65 * t;
}
`;

export const coreFragmentShader = /* glsl */ `
uniform vec3 uColorA;
uniform vec3 uColorB;
uniform float uOpacity;

varying float vMix;
varying float vRim;
varying float vFade;

void main() {
  vec2 c = gl_PointCoord - 0.5;
  float d = length(c);
  if (d > 0.5) discard;
  float alpha = pow(smoothstep(0.5, 0.0, d), 1.6);
  vec3 color = mix(uColorA, uColorB, vMix);
  color *= 0.6 + vRim * 1.1;
  gl_FragColor = vec4(color, alpha * (0.32 + vRim * 0.68) * vFade * uOpacity);
  // Uniform colours are linear (three's colour management); convert back to the output space.
  #include <colorspace_fragment>
}
`;
