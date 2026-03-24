import { cn } from "../../lib/cn";

type BadgeVariant = "status" | "priority" | "type" | "framework" | "default";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  color?: string;
  className?: string;
}

const STATUS_MAP: Record<string, string> = {
  pass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  fail: "bg-rose-500/10 text-rose-400 border-rose-500/20",
  running: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  pending: "bg-slate-500/10 text-slate-400 border-slate-700/30",
  skipped: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  active: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  available: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  "coming-soon": "bg-slate-500/10 text-slate-500 border-slate-700/30",
};

const PRIORITY_MAP: Record<string, string> = {
  P0: "bg-rose-500/10 text-rose-400",
  P1: "bg-amber-500/10 text-amber-400",
  P2: "bg-blue-500/10 text-blue-400",
  P3: "bg-slate-700/50 text-slate-400",
  Critical: "bg-rose-500/15 text-rose-400",
  High: "bg-amber-500/15 text-amber-400",
  Medium: "bg-emerald-500/15 text-emerald-400",
  Low: "bg-slate-500/15 text-slate-400",
};

const TYPE_MAP: Record<string, string> = {
  functional: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  security: "bg-rose-500/10 text-rose-400 border-rose-500/20",
  edge: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  performance: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  accessibility: "bg-violet-500/10 text-violet-400 border-violet-500/20",
};

export function Badge({
  children,
  variant = "default",
  color,
  className,
}: BadgeProps) {
  const value = typeof children === "string" ? children : "";
  const mapped =
    variant === "status"
      ? STATUS_MAP[value]
      : variant === "priority"
        ? PRIORITY_MAP[value]
        : variant === "type"
          ? TYPE_MAP[value]
          : undefined;

  return (
    <span
      className={cn(
        "inline-flex items-center text-[9px] font-bold uppercase px-2 py-0.5 rounded border border-transparent",
        mapped || "bg-slate-800/50 text-slate-400",
        className,
      )}
      style={
        color
          ? { color, background: `${color}15`, borderColor: `${color}30` }
          : undefined
      }
    >
      {children}
    </span>
  );
}
