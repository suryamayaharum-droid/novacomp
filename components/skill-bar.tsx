"use client";

import { cn } from "@/lib/utils";
import { formatPercentage } from "@/lib/utils";

interface SkillBarProps {
  name: string;
  value: number;
  className?: string;
}

export function SkillBar({ name, value, className }: SkillBarProps) {
  const percentage = value * 100;
  
  return (
    <div className={cn("mb-3", className)}>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-sm text-foreground capitalize">
          {name.replace(/_/g, " ")}
        </span>
        <span className="text-sm font-semibold text-accent">
          {formatPercentage(value)}
        </span>
      </div>
      <div className="h-2 bg-secondary rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-primary to-accent rounded-full transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
