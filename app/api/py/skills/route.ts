import { NextResponse } from "next/server";

const PYTHON_API = process.env.PYTHON_API_URL || "http://localhost:8000";

const mockSkills = {
  skills: {
    reasoning: 0.5,
    learning: 0.5,
    memory_recall: 0.5,
    pattern_recognition: 0.5,
    decision_making: 0.5,
    self_reflection: 0.3,
    adaptation: 0.4,
  },
  average: 0.457,
  evolution_level: 1,
};

export async function GET() {
  try {
    const response = await fetch(`${PYTHON_API}/api/skills`, {
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
      data: mockSkills,
    });
  }
}
