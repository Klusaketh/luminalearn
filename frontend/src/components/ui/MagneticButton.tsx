"use client";

import React, { useRef } from "react";
import Link from "next/link";
import { motion, useMotionValue, useReducedMotion, useSpring } from "framer-motion";
import { cn } from "@/utils/cn";

const MotionLink = motion.create(Link);

type Variant = "primary" | "light" | "outline" | "glass" | "ghost";
type Size = "sm" | "md" | "lg";

// Gradient stops are the 700 shades of teal/cyan/violet so white label text stays above 4.5:1.
const VARIANTS: Record<Variant, string> = {
  primary:
    "text-white bg-[linear-gradient(135deg,#0F766E_0%,#0E7490_45%,#6D28D9_100%)] shadow-glow-teal hover:shadow-[0_0_0_1px_rgba(45,212,191,0.55),0_14px_44px_-10px_rgba(34,211,238,0.6)]",
  light: "bg-white text-space-950 shadow-[0_10px_40px_-12px_rgba(255,255,255,0.45)] hover:bg-slate-50",
  outline: "border border-white/25 text-white hover:border-aurora-teal/70 hover:bg-white/[0.04]",
  glass: "glass text-slate-100 hover:border-white/20",
  ghost: "text-slate-200 hover:text-white hover:bg-white/[0.04]",
};

/** Variants that get the light sweep on hover. */
const SHINE: Record<Variant, boolean> = { primary: true, light: true, outline: true, glass: true, ghost: false };

const SIZES: Record<Size, string> = {
  sm: "h-9 px-4 text-[13px] gap-1.5 rounded-xl",
  md: "h-11 px-5 text-sm gap-2 rounded-2xl",
  lg: "h-14 px-7 text-[15px] gap-2.5 rounded-[1.25rem]",
};

interface BaseProps {
  variant?: Variant;
  size?: Size;
  /** How far (0-1) the button follows the cursor. */
  strength?: number;
  /** Label the custom cursor shows while hovering ("Start", "Open"). */
  cursorLabel?: string;
  className?: string;
  children: React.ReactNode;
}

type NativeButtonProps = Omit<
  React.ButtonHTMLAttributes<HTMLButtonElement>,
  keyof BaseProps | "onDrag" | "onDragStart" | "onDragEnd" | "onAnimationStart"
>;
type ButtonProps = BaseProps & NativeButtonProps & { href?: undefined };
type LinkProps = BaseProps & { href: string; "aria-label"?: string; target?: string };

/**
 * A button (or link) that leans toward the pointer with spring physics while a radial
 * spotlight tracks the cursor across its surface. Falls back to a static button when the
 * user prefers reduced motion, and keeps native focus/keyboard behavior throughout.
 */
export function MagneticButton({
  variant = "primary",
  size = "md",
  strength = 0.22,
  cursorLabel,
  className,
  children,
  ...rest
}: ButtonProps | LinkProps) {
  const reduceMotion = useReducedMotion();
  const ref = useRef<HTMLElement | null>(null);
  const x = useSpring(useMotionValue(0), { stiffness: 260, damping: 18, mass: 0.4 });
  const y = useSpring(useMotionValue(0), { stiffness: 260, damping: 18, mass: 0.4 });

  const onPointerMove = (event: React.PointerEvent<HTMLElement>) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const px = event.clientX - rect.left;
    const py = event.clientY - rect.top;
    el.style.setProperty("--mx", `${px}px`);
    el.style.setProperty("--my", `${py}px`);
    if (!reduceMotion) {
      x.set((px - rect.width / 2) * strength);
      y.set((py - rect.height / 2) * strength);
    }
  };
  const onPointerLeave = () => {
    x.set(0);
    y.set(0);
  };

  const classes = cn(
    "group relative inline-flex select-none items-center justify-center overflow-hidden font-semibold tracking-[-0.005em] outline-none transition-[box-shadow,background-color,border-color,color] duration-300",
    "focus-visible:ring-2 focus-visible:ring-indigo-300 focus-visible:ring-offset-2 focus-visible:ring-offset-space-950",
    "disabled:pointer-events-none disabled:opacity-50",
    VARIANTS[variant],
    SIZES[size],
    className
  );
  const content = (
    <>
      <span
        aria-hidden="true"
        className="spotlight pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
      />
      {SHINE[variant] && !reduceMotion ? (
        <span aria-hidden="true" className="shine-sweep pointer-events-none absolute inset-0" />
      ) : null}
      <span className="relative z-[1] inline-flex items-center gap-[inherit]">{children}</span>
    </>
  );
  const tap = reduceMotion ? undefined : { scale: 0.97 };

  if (typeof rest.href === "string") {
    const linkProps = rest as Omit<LinkProps, keyof BaseProps>;
    return (
      <MotionLink
        ref={(node: HTMLAnchorElement | null) => {
          ref.current = node;
        }}
        href={linkProps.href}
        target={linkProps.target}
        aria-label={linkProps["aria-label"]}
        data-cursor={cursorLabel}
        className={classes}
        style={{ x, y }}
        whileTap={tap}
        onPointerMove={onPointerMove}
        onPointerLeave={onPointerLeave}
      >
        {content}
      </MotionLink>
    );
  }

  const buttonProps = rest as Omit<ButtonProps, keyof BaseProps>;
  return (
    <motion.button
      ref={(node: HTMLButtonElement | null) => {
        ref.current = node;
      }}
      {...buttonProps}
      type={buttonProps.type ?? "button"}
      data-cursor={cursorLabel}
      className={classes}
      style={{ x, y }}
      whileTap={tap}
      onPointerMove={onPointerMove}
      onPointerLeave={onPointerLeave}
    >
      {content}
    </motion.button>
  );
}
