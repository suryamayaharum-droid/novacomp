import { createAgentUIStreamResponse } from "ai";
import { novaCompAgent, addToHistory } from "@/lib/novacomp-agent";

export async function POST(req: Request) {
  const { messages, userId, contextLevel } = await req.json();

  // Adiciona a ultima mensagem ao historico
  const lastUserMessage = messages
    .filter((m: { role: string }) => m.role === "user")
    .pop();
  
  if (lastUserMessage?.parts?.[0]?.text) {
    addToHistory(lastUserMessage.parts[0].text, "");
  }

  // Usa createAgentUIStreamResponse para streaming
  // IMPORTANTE: usar 'uiMessages' e NAO 'messages'
  return createAgentUIStreamResponse({
    agent: novaCompAgent,
    uiMessages: messages,
    options: {
      userId: userId || "anonymous",
      contextLevel: contextLevel || "avancado",
    },
  });
}
