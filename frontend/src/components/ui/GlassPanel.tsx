import React from "react";
import { cn } from "@/utils/cn";

export interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Animated radiant border that travels around the panel. */
  flow?: boolean;
  /** Denser, more opaque glass for surfaces that hold body text. */
  strong?: boolean;
  as?: "div" | "section" | "aside" | "article";
}

/** Frosted VisionOS-style surface: translucent fill, hairline border, deep soft shadow. */
export const GlassPanel = React.forwardRef<HTMLDivElement, GlassPanelProps>(
  ({ className, flow = false, strong = false, as: Tag = "div", ...props }, ref) => (
    <Tag
      ref={ref}
      className={cn(
        "rounded-3xl shadow-glass",
        strong ? "glass-strong" : "glass",
        flow && "gradient-border-flow",
        className
      )}
      {...props}
    />
  )
);

GlassPanel.displayName = "GlassPanel";
