import { cn } from "../../lib/cn";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import type { ElementType } from "react";

interface MetricCardProps {
  icon: ElementType;
  label: string;
  value: string | number;
  change?: string;
  trend?: "up" | "down";
  color: string;
  bgColor: string;
  borderColor?: string;
  className?: string;
}

export function MetricCard({
  icon: Icon,
  label,
  value,
  change,
  trend,
  color,
  bgColor,
  borderColor,
  className,
}: MetricCardProps) {
  return (
    <div
      className={cn(
        "bg-surface-card border rounded-xl p-5 card-hover transition-colors",
        borderColor || "border-edge",
        className,
      )}
    >
      <div className="flex items-center justify-between mb-3">
        <div
          className={cn(
            "w-9 h-9 rounded-lg flex items-center justify-center",
            bgColor,
          )}
        >
          <Icon className={cn("w-4.5 h-4.5", color)} />
        </div>
        {trend && (
          <div
            className={cn(
              "flex items-center gap-1 text-[11px] font-mono",
              trend === "up" ? "text-emerald-400" : "text-rose-400",
            )}
          >
            {trend === "up" ? (
              <ArrowUpRight className="w-3 h-3" />
            ) : (
              <ArrowDownRight className="w-3 h-3" />
            )}
          </div>
        )}
      </div>
      <div className={cn("text-2xl font-black mb-1", color)}>{value}</div>
      <div className="text-[11px] text-slate-500">{label}</div>
      {change && (
        <div className="text-[10px] text-slate-600 mt-1">{change}</div>
      )}
    </div>
  );
}
