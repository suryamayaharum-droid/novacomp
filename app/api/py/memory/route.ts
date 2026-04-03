import { NextResponse } from "next/server";

const PYTHON_API = process.env.PYTHON_API_URL || "http://localhost:8000";

const mockMemory = {
  total_memories: 0,
  categories: {},
  total_relations: 0,
  evolution_events: 0,
  short_term_cache_size: 0,
  recent_accesses: 0,
};

export async function GET() {
  try {
    const response = await fetch(`${PYTHON_API}/api/memory`, {
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
      data: mockMemory,
    });
  }
}
