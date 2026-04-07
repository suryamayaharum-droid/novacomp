"use client";

import { cn } from "@/lib/utils";

interface StatusCardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
  icon?: React.ReactNode;
}

export function StatusCard({ title, children, className, icon }: StatusCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-card p-5",
        "transition-all duration-200 hover:border-primary/30",
        className
      )}
    >
      <div className="flex items-center gap-2 mb-4">
        {icon && <span className="text-primary">{icon}</span>}
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          {title}
        </h3>
      </div>
      {children}
    </div>
  );
}

interface MetricRowProps {
  label: string;
  value: string | number;
  valueColor?: string;
}

export function MetricRow({ label, value, valueColor = "text-accent" }: MetricRowProps) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className={cn("text-sm font-semibold", valueColor)}>{value}</span>
    </div>
  );
}
