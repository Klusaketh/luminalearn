import {
  BarChart3,
  Binary,
  BookOpen,
  Brain,
  Calculator,
  Code,
  Code2,
  Coffee,
  Cpu,
  Database,
  Dice5,
  Eye,
  FileCode,
  Grid3X3,
  MessageSquare,
  Network,
  Server,
  Sigma,
  Sparkles,
  Terminal,
  Wand2,
  type LucideIcon,
} from "lucide-react";

const ICONS: Record<string, LucideIcon> = {
  "code-2": Code2,
  cpu: Cpu,
  database: Database,
  network: Network,
  binary: Binary,
  server: Server,
  terminal: Terminal,
  code: Code,
  coffee: Coffee,
  "file-code": FileCode,
  brain: Brain,
  sparkles: Sparkles,
  "wand-2": Wand2,
  "message-square": MessageSquare,
  eye: Eye,
  sigma: Sigma,
  "dice-5": Dice5,
  "bar-chart": BarChart3,
  grid: Grid3X3,
  calculator: Calculator,
};

/** The subject's icon from its `icon_key`, with a book as the fallback. */
export function SubjectIcon({ iconKey, className = "h-6 w-6" }: { iconKey: string | null; className?: string }) {
  const Icon = (iconKey && ICONS[iconKey]) || BookOpen;
  return <Icon className={className} aria-hidden="true" />;
}

const DIFFICULTY_STYLE: Record<string, string> = {
  beginner: "bg-emerald-400/10 text-emerald-200 ring-emerald-300/20",
  intermediate: "bg-amber-400/10 text-amber-200 ring-amber-300/20",
  advanced: "bg-rose-400/10 text-rose-200 ring-rose-300/20",
};

export function DifficultyBadge({ level, className = "" }: { level: string; className?: string }) {
  const style = DIFFICULTY_STYLE[level.toLowerCase()] ?? "bg-white/[0.06] text-slate-200 ring-white/10";
  return <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ${style} ${className}`}>{level}</span>;
}
