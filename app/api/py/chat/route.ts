import { NextRequest, NextResponse } from "next/server";

const PYTHON_API = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${PYTHON_API}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      throw new Error("Python API not available");
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    // Fallback response quando Python API nao esta disponivel
    const messages = (await request.clone().json()).messages || [];
    const lastUserMessage = messages.findLast((m: { role: string }) => m.role === "user");
    
    return NextResponse.json({
      success: true,
      data: {
        response: `Recebi: "${lastUserMessage?.content || "sua mensagem"}"\n\nEstou em modo de demonstracao. A API Python nao esta conectada.`,
        decision: {
          action: "engage_conversation",
          confidence: 0.5,
          description: "Resposta de demonstracao",
        },
        confidence: 0.5,
      },
    });
  }
}
