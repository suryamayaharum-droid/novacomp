"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Sparkles, BookOpen, Brain, RefreshCw } from "lucide-react";
import { triggerEvolution, teachKnowledge, triggerReflection } from "@/lib/api";

interface ActionButtonsProps {
  onAction: (action: string, result: unknown) => void;
}

export function ActionButtons({ onAction }: ActionButtonsProps) {
  const [loading, setLoading] = useState<string | null>(null);

  const handleAction = async (
    actionName: string,
    actionFn: () => Promise<unknown>
  ) => {
    setLoading(actionName);
    try {
      const result = await actionFn();
      onAction(actionName, result);
    } catch (error) {
      onAction(actionName, { error: String(error) });
    } finally {
      setLoading(null);
    }
  };

  const actions = [
    {
      id: "evolve",
      label: "Evoluir",
      icon: Sparkles,
      color: "text-chart-3",
      bgColor: "bg-chart-3/10 hover:bg-chart-3/20",
      action: () => triggerEvolution(),
    },
    {
      id: "learn",
      label: "Ensinar",
      icon: BookOpen,
      color: "text-accent",
      bgColor: "bg-accent/10 hover:bg-accent/20",
      action: () =>
        teachKnowledge({
          type: "experience",
          content: "Novo conhecimento adquirido via dashboard",
          source: "user_interaction",
        }),
    },
    {
      id: "reflect",
      label: "Refletir",
      icon: Brain,
      color: "text-primary",
      bgColor: "bg-primary/10 hover:bg-primary/20",
      action: () => triggerReflection(),
    },
  ];

  return (
    <div className="flex gap-2 flex-wrap">
      {actions.map((action) => {
        const Icon = action.icon;
        const isLoading = loading === action.id;

        return (
          <button
            key={action.id}
            onClick={() => handleAction(action.id, action.action)}
            disabled={loading !== null}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg transition-all",
              "border border-transparent",
              action.bgColor,
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
          >
            {isLoading ? (
              <RefreshCw className={cn("w-4 h-4 animate-spin", action.color)} />
            ) : (
              <Icon className={cn("w-4 h-4", action.color)} />
            )}
            <span className={cn("text-sm font-medium", action.color)}>
              {action.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}
