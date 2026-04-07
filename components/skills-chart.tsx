"use client";

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
} from "recharts";

interface SkillsChartProps {
  skills: Record<string, number>;
}

export function SkillsChart({ skills }: SkillsChartProps) {
  const data = Object.entries(skills).map(([name, value]) => ({
    skill: name.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
    value: value * 100,
    fullMark: 100,
  }));

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
          <PolarGrid stroke="hsl(var(--color-border))" />
          <PolarAngleAxis
            dataKey="skill"
            tick={{ fill: "hsl(var(--color-muted-foreground))", fontSize: 10 }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={{ fill: "hsl(var(--color-muted-foreground))", fontSize: 10 }}
          />
          <Radar
            name="Habilidades"
            dataKey="value"
            stroke="hsl(var(--color-primary))"
            fill="hsl(var(--color-primary))"
            fillOpacity={0.3}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
