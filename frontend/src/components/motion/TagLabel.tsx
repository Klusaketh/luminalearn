import { cn } from "@/utils/cn";

/** Mono uppercase "[ TEXT ]" tag. The brackets are decorative and hidden from screen readers. */
export function TagLabel({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={cn("tag-label inline-flex items-center gap-[0.6em] whitespace-nowrap", className)}>
      <span aria-hidden="true">[</span>
      <span>{children}</span>
      <span aria-hidden="true">]</span>
    </span>
  );
}
