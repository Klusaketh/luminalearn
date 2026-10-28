import { Bug, Compass, Lightbulb, Shapes } from "lucide-react";
import type { AgentName } from "@/services/tutorService";

/** Visual identity of each faculty specialist (shared by badges, roster and voice stage). */
export const AGENT_STYLE: Record<AgentName, { label: string; icon: typeof Compass; tone: string; dot: string }> = {
  socratic_tutor: { label: "Socratic Tutor", icon: Compass, tone: "text-indigo-200 bg-indigo-500/15 ring-indigo-400/30", dot: "bg-indigo-400" },
  concept_explainer: { label: "Concept Explainer", icon: Shapes, tone: "text-cyan-200 bg-cyan-500/15 ring-cyan-400/30", dot: "bg-cyan-400" },
  analogy_specialist: { label: "Analogy Specialist", icon: Lightbulb, tone: "text-amber-200 bg-amber-500/15 ring-amber-400/30", dot: "bg-amber-400" },
  code_diagnostic: { label: "Code Diagnostic", icon: Bug, tone: "text-rose-200 bg-rose-500/15 ring-rose-400/30", dot: "bg-rose-400" },
};
