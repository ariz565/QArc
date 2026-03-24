import { cn } from "../../lib/cn";

type StatusDotVariant =
  | "online"
  | "offline"
  | "processing"
  | "warning"
  | "error";

interface StatusDotProps {
  variant?: StatusDotVariant;
  pulse?: boolean;
  className?: string;
}

const dotColors: Record<StatusDotVariant, string> = {
  online: "bg-emerald-400 shadow-emerald-400/50",
  offline: "bg-slate-600",
  processing: "bg-cyan-400 shadow-cyan-400/50",
  warning: "bg-amber-400 shadow-amber-400/50",
  error: "bg-rose-400 shadow-rose-400/50",
};

export function StatusDot({
  variant = "online",
  pulse = true,
  className,
}: StatusDotProps) {
  return (
    <div
      className={cn(
        "w-2 h-2 rounded-full",
        dotColors[variant],
        pulse && variant !== "offline" && "animate-pulse shadow-[0_0_8px]",
        className,
      )}
    />
  );
}
