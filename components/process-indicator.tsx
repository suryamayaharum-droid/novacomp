"use client";

import { cn } from "@/lib/utils";
import { Brain, BookOpen, Zap } from "lucide-react";

interface ProcessIndicatorProps {
  currentState: string;
}

const processes = [
  { id: "thinking", label: "Pensando", icon: Brain },
  { id: "learning", label: "Aprendendo", icon: BookOpen },
  { id: "executing", label: "Executando", icon: Zap },
];

export function ProcessIndicator({ currentState }: ProcessIndicatorProps) {
  return (
    <div className="flex gap-2 mt-4">
      {processes.map((process) => {
        const Icon = process.icon;
        const isActive = currentState === process.id;
        
        return (
          <div
            key={process.id}
            className={cn(
              "flex-1 flex flex-col items-center gap-1.5 p-3 rounded-lg transition-all duration-300",
              isActive
                ? "bg-accent/10 border border-accent/30"
                : "bg-secondary/50 border border-transparent"
            )}
          >
            <Icon
              className={cn(
                "w-4 h-4 transition-colors",
                isActive ? "text-accent" : "text-muted-foreground"
              )}
            />
            <span
              className={cn(
                "text-xs font-medium",
                isActive ? "text-accent" : "text-muted-foreground"
              )}
            >
              {process.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
