import { NextResponse } from "next/server";

const PYTHON_API = process.env.PYTHON_API_URL || "http://localhost:8000";

// Mock data para desenvolvimento
const mockStatus = {
  name: "NovaComp-Alpha",
  state: "idle",
  evolution_level: 1,
  skills: {
    reasoning: 0.5,
    learning: 0.5,
    memory_recall: 0.5,
    pattern_recognition: 0.5,
    decision_making: 0.5,
    self_reflection: 0.3,
    adaptation: 0.4,
  },
  average_skill: 0.457,
  memory_stats: {
    total_memories: 0,
    categories: {},
    total_relations: 0,
    evolution_events: 0,
    short_term_cache_size: 0,
    recent_accesses: 0,
  },
  learning_events: 0,
  active_tasks: 0,
  uptime_hours: 0,
};

export async function GET() {
  try {
    const response = await fetch(`${PYTHON_API}/api/status`, {
      next: { revalidate: 0 },
    });
    
    if (!response.ok) {
      throw new Error("Python API not available");
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    // Retorna mock data quando Python API nao esta disponivel
    return NextResponse.json({
      success: true,
      data: mockStatus,
    });
  }
}
