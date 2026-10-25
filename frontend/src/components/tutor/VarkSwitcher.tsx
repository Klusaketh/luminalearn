"use client";

import type { ReactNode } from "react";
import { BookOpen, Ear, Eye, Hand } from "lucide-react";
import type { Modality } from "@/services/tutorService";
import { SegmentedControl } from "@/components/ui/SegmentedControl";

export const MODALITY_OPTIONS = [
  { value: "visual", label: "Visual", icon: <Eye className="h-3.5 w-3.5" aria-hidden="true" />, description: "Diagrams and flows" },
  { value: "auditory", label: "Auditory", icon: <Ear className="h-3.5 w-3.5" aria-hidden="true" />, description: "Spoken walkthroughs" },
  { value: "read_write", label: "Read/Write", icon: <BookOpen className="h-3.5 w-3.5" aria-hidden="true" />, description: "Structured notes" },
  { value: "kinesthetic", label: "Hands-on", icon: <Hand className="h-3.5 w-3.5" aria-hidden="true" />, description: "Interactive labs" },
] as const satisfies ReadonlyArray<{ value: Modality; label: string; icon: ReactNode; description: string }>;

/** VARK modality switcher; changing it re-explains the current idea in the new style. */
export function VarkSwitcher({ value, onChange }: { value: Modality; onChange: (modality: Modality) => void }) {
  return <SegmentedControl label="Explanation style" options={MODALITY_OPTIONS} value={value} onChange={onChange} compactOnMobile />;
}
