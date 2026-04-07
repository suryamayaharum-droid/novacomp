"use client";

import { cn } from "@/lib/utils";
import { useRef, useEffect } from "react";

export interface LogEntry {
  id: string;
  timestamp: string;
  level: "info" | "success" | "warning" | "error";
  message: string;
}

interface LogViewerProps {
  logs: LogEntry[];
  className?: string;
}

const levelColors = {
  info: "text-primary",
  success: "text-accent",
  warning: "text-chart-3",
  error: "text-destructive",
};

export function LogViewer({ logs, className }: LogViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = 0;
    }
  }, [logs.length]);
  
  return (
    <div
      ref={containerRef}
      className={cn(
        "bg-background rounded-lg p-4 h-80 overflow-y-auto font-mono text-sm",
        "border border-border",
        className
      )}
    >
      {logs.length === 0 ? (
        <div className="text-muted-foreground text-center py-8">
          Aguardando logs...
        </div>
      ) : (
        logs.map((log) => (
          <div
            key={log.id}
            className="py-1.5 border-b border-border/30 last:border-0"
          >
            <span className="text-muted-foreground">[{log.timestamp}]</span>{" "}
            <span className={levelColors[log.level]}>{log.message}</span>
          </div>
        ))
      )}
    </div>
  );
}
