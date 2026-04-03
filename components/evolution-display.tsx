"use client";

import { cn } from "@/lib/utils";
import { Sparkles } from "lucide-react";

interface EvolutionDisplayProps {
  level: number;
  className?: string;
}

export function EvolutionDisplay({ level, className }: EvolutionDisplayProps) {
  return (
    <div className={cn("text-center py-6", className)}>
      <div className="inline-flex items-center gap-3">
        <Sparkles className="w-6 h-6 text-chart-3" />
        <div>
          <p className="text-sm text-muted-foreground uppercase tracking-wide">
            Nivel de Evolucao
          </p>
          <p className="text-5xl font-bold bg-gradient-to-r from-chart-3 via-primary to-accent bg-clip-text text-transparent">
            {level}
          </p>
        </div>
        <Sparkles className="w-6 h-6 text-chart-3" />
      </div>
    </div>
  );
}
