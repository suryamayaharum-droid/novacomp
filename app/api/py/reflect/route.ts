import { NextResponse } from "next/server";

const PYTHON_API = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${PYTHON_API}/api/reflect`, {
      next: { revalidate: 0 },
    });
    
    if (!response.ok) {
      throw new Error("Python API not available");
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json({
      success: true,
      data: {
        timestamp: new Date().toISOString(),
        current_state: "idle",
        evolution_level: 1,
        strongest_skills: [
          ["reasoning", 0.5],
          ["learning", 0.5],
          ["memory_recall", 0.5],
        ],
        weakest_skills: [
          ["self_reflection", 0.3],
          ["adaptation", 0.4],
          ["decision_making", 0.5],
        ],
        total_experiences: 0,
        recommendations: [
          "Focar em melhorar self_reflection atraves de pratica direcionada",
        ],
      },
    });
  }
}
