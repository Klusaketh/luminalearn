"use client";

import { useEffect, useMemo, useRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Bloom, EffectComposer, Vignette } from "@react-three/postprocessing";
import { gsap } from "gsap";
import * as THREE from "three";
import type { DeviceTier } from "@/hooks/useDeviceTier";
import { coreFragmentShader, coreVertexShader } from "./coreShader";
import { PARTICLES_BY_TIER, sampleCore } from "./sampleTorus";

const TEAL = new THREE.Color("#2DD4BF");
const VIOLET = new THREE.Color("#8B5CF6");
// ~46deg tilt: steep enough to read as 3D, shallow enough that the ring's hole stays visible.
const BASE_TILT_X = -0.8;

/** Pointer position in NDC, tracked on window so overlaying hero text never blocks it. */
function usePointer() {
  const pointer = useRef({ x: 0, y: 0, active: false });
  const { gl } = useThree();
  useEffect(() => {
    const onMove = (event: PointerEvent) => {
      const rect = gl.domElement.getBoundingClientRect();
      pointer.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      pointer.current.active = event.clientY >= rect.top && event.clientY <= rect.bottom;
    };
    const onLeave = () => {
      pointer.current.active = false;
    };
    window.addEventListener("pointermove", onMove, { passive: true });
    document.documentElement.addEventListener("pointerleave", onLeave);
    return () => {
      window.removeEventListener("pointermove", onMove);
      document.documentElement.removeEventListener("pointerleave", onLeave);
    };
  }, [gl]);
  return pointer;
}

function CoreParticles({ tier, onReady }: { tier: DeviceTier; onReady: () => void }) {
  const group = useRef<THREE.Group>(null);
  const points = useRef<THREE.Points>(null);
  const { camera, size } = useThree();
  const pointer = usePointer();
  const buffers = useMemo(() => sampleCore(PARTICLES_BY_TIER[tier]), [tier]);

  // Reused every frame: no allocation inside useFrame.
  const scratch = useMemo(
    () => ({
      raycaster: new THREE.Raycaster(),
      ndc: new THREE.Vector2(),
      plane: new THREE.Plane(new THREE.Vector3(0, 0, 1), 0),
      hit: new THREE.Vector3(),
      mouse: new THREE.Vector3(0, 0, 50),
    }),
    []
  );

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uMouse: { value: new THREE.Vector3(0, 0, 50) },
      uMouseStrength: { value: 0 },
      uIntro: { value: 0 },
      uPixelRatio: { value: 1 },
      // Small, dim sprites so the core reads as distinct dots rather than a solid glowing band.
      uSize: { value: tier === "high" ? 19 : tier === "mid" ? 25 : 32 },
      uColorA: { value: TEAL.clone() },
      uColorB: { value: VIOLET.clone() },
      uOpacity: { value: tier === "high" ? 0.5 : tier === "mid" ? 0.62 : 0.8 },
    }),
    [tier]
  );

  // Intro: scattered dust converges into the core over ~2.2s.
  useEffect(() => {
    const tween = gsap.to(uniforms.uIntro, { value: 1, duration: 2.2, ease: "power3.out", delay: 0.15 });
    return () => {
      tween.kill();
    };
  }, [uniforms]);
  const announced = useRef(false);

  // Narrow screens: pull the camera back until the ~4.7-unit ring (plus margin) fits horizontally.
  // Visible width at distance z with fov 35 is 2 * z * tan(17.5deg) * aspect = 0.6306 * z * aspect.
  useEffect(() => {
    const aspect = size.width / size.height;
    camera.position.set(0, 0, Math.max(9.5, 5.8 / (0.6306 * aspect)));
    camera.updateProjectionMatrix();
  }, [camera, size]);

  useFrame((state, delta) => {
    // The first drawn frame is the cue to cross-fade the static fallback out.
    if (!announced.current) {
      announced.current = true;
      onReady();
    }
    const u = uniforms;
    u.uTime.value += delta;
    u.uPixelRatio.value = state.gl.getPixelRatio();

    const p = pointer.current;
    if (p.active) {
      scratch.ndc.set(p.x, p.y);
      scratch.raycaster.setFromCamera(scratch.ndc, camera);
      if (scratch.raycaster.ray.intersectPlane(scratch.plane, scratch.hit)) {
        scratch.mouse.lerp(scratch.hit, 0.12);
      }
    }
    u.uMouse.value.copy(scratch.mouse);
    u.uMouseStrength.value += ((p.active ? 1 : 0) - u.uMouseStrength.value) * 0.06;

    if (points.current) points.current.rotation.z += delta * 0.07;
    if (group.current) {
      const tx = BASE_TILT_X + (p.active ? p.y * 0.12 : 0);
      const ty = p.active ? p.x * 0.18 : 0;
      group.current.rotation.x += (tx - group.current.rotation.x) * 0.04;
      group.current.rotation.y += (ty - group.current.rotation.y) * 0.04;
    }
  });

  return (
    <group ref={group} rotation={[BASE_TILT_X, 0, 0]} position={[0.15, -0.42, 0]} scale={0.76}>
      <points ref={points} frustumCulled={false}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[buffers.positions, 3]} />
          <bufferAttribute attach="attributes-aNormal" args={[buffers.normals, 3]} />
          <bufferAttribute attach="attributes-aScatter" args={[buffers.scatter, 3]} />
          <bufferAttribute attach="attributes-aRandom" args={[buffers.random, 1]} />
        </bufferGeometry>
        <shaderMaterial
          vertexShader={coreVertexShader}
          fragmentShader={coreFragmentShader}
          uniforms={uniforms}
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </points>
    </group>
  );
}

interface LuminaCoreProps {
  tier: DeviceTier;
  /** Called once the scene has mounted, so the static fallback can fade out. */
  onReady: () => void;
  className?: string;
}

/** Full-bleed WebGL canvas for the hero. Loaded client-side only (next/dynamic, ssr: false). */
export default function LuminaCore({ tier, onReady, className }: LuminaCoreProps) {
  return (
    <Canvas
      className={className}
      camera={{ fov: 35, position: [0, 0, 9.5], near: 0.1, far: 60 }}
      dpr={[1, tier === "high" ? 1.75 : 1.4]}
      gl={{ antialias: false, alpha: true, powerPreference: "high-performance" }}
      aria-hidden="true"
    >
      <CoreParticles tier={tier} onReady={onReady} />
      {tier !== "low" && (
        <EffectComposer multisampling={0}>
          <Bloom intensity={0.8} luminanceThreshold={0.2} luminanceSmoothing={0.3} mipmapBlur />
          <Vignette offset={0.3} darkness={0.55} />
        </EffectComposer>
      )}
    </Canvas>
  );
}
