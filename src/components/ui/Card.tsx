import { cn } from "../../lib/cn";
import type { ReactNode } from "react";

type CardVariant = "default" | "elevated" | "ghost";

interface CardProps {
  children: ReactNode;
  className?: string;
  variant?: CardVariant;
  hover?: boolean;
  padding?: boolean;
}

export function Card({
  children,
  className,
  variant = "default",
  hover,
  padding = true,
}: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border transition-colors",
        variant === "default" && "bg-surface-card border-edge",
        variant === "elevated" &&
          "bg-surface-card border-edge shadow-lg shadow-black/5",
        variant === "ghost" && "bg-transparent border-transparent",
        hover && "card-hover cursor-pointer",
        padding && "p-5",
        className,
      )}
    >
      {children}
    </div>
  );
}
