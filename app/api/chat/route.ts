import { NextResponse } from "next/server";

// Configuracao do provedor de LLM
const LLM_PROVIDER = process.env.LLM_PROVIDER || "local"; // "ollama" | "openai" | "local"
const OLLAMA_URL = process.env.OLLAMA_URL || "http://localhost:11434";
const OLLAMA_MODEL = process.env.OLLAMA_MODEL || "llama3";
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

// Memoria simples em memoria
const memory: Map<string, string> = new Map();
const conversationHistory: Array<{ role: string; content: string }> = [];

// Ferramentas disponiveis
const tools = {
  memorizar: (key: string, value: string) => {
    memory.set(key, value);
    return { success: true, message: `Memorizado: ${key}` };
  },
  lembrar: (key: string) => {
    const value = memory.get(key);
    return value ? { found: true, value } : { found: false, message: "Nao encontrado" };
  },
  calcular: (expression: string) => {
    try {
      const sanitized = expression.replace(/[^0-9+\-*/().%\s]/g, "");
      const result = Function(`"use strict"; return (${sanitized})`)();
      return { result, expression: sanitized };
    } catch {
      return { error: "Expressao invalida" };
    }
  },
  status_sistema: () => ({
    status: "online",
    provider: LLM_PROVIDER,
    model: LLM_PROVIDER === "ollama" ? OLLAMA_MODEL : "local-ai",
    uptime: process.uptime(),
    memoria_usada: process.memoryUsage().heapUsed / 1024 / 1024,
    skills: {
      raciocinio: 0.85,
      memoria: 0.92,
      criatividade: 0.78,
      analise: 0.88,
      comunicacao: 0.90,
    },
  }),
  gerar_ideias: (topic: string) => {
    const ideas = [
      `Aplicar ${topic} com machine learning para otimizacao`,
      `Criar um dashboard interativo para visualizar ${topic}`,
      `Desenvolver API REST para integrar ${topic} com outros sistemas`,
      `Implementar cache inteligente para melhorar performance de ${topic}`,
      `Usar websockets para atualizacoes em tempo real de ${topic}`,
    ];
    return { topic, ideas: ideas.slice(0, 3) };
  },
};

// System prompt para o NovaComp AI
const SYSTEM_PROMPT = `Voce e o NovaComp AI, um sistema de inteligencia artificial autonoma avancado.
Suas capacidades incluem:
- Raciocinio logico avancado
- Memoria de longo prazo (TurboQuant)
- Analise de codigo e dados
- Geracao de ideias criativas
- Calculos matematicos

Responda sempre em portugues de forma clara e util.
Quando apropriado, use formatacao Markdown para melhor legibilidade.
Seja conciso mas completo em suas respostas.`;

// Chamar Ollama API
async function callOllama(messages: Array<{ role: string; content: string }>): Promise<ReadableStream> {
  const response = await fetch(`${OLLAMA_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: OLLAMA_MODEL,
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        ...messages,
      ],
      stream: true,
    }),
  });

  if (!response.ok || !response.body) {
    throw new Error(`Ollama error: ${response.status}`);
  }

  const encoder = new TextEncoder();
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  return new ReadableStream({
    async start(controller) {
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n").filter(Boolean);

          for (const line of lines) {
            try {
              const data = JSON.parse(line);
              if (data.message?.content) {
                const sseChunk = JSON.stringify({ type: "text-delta", delta: data.message.content });
                controller.enqueue(encoder.encode(`data: ${sseChunk}\n\n`));
              }
            } catch {
              // Skip invalid JSON
            }
          }
        }
        controller.enqueue(encoder.encode(`data: [DONE]\n\n`));
        controller.close();
      } catch (error) {
        controller.error(error);
      }
    },
  });
}

// Chamar OpenAI API
async function callOpenAI(messages: Array<{ role: string; content: string }>): Promise<ReadableStream> {
  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        ...messages,
      ],
      stream: true,
    }),
  });

  if (!response.ok || !response.body) {
    throw new Error(`OpenAI error: ${response.status}`);
  }

  const encoder = new TextEncoder();
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  return new ReadableStream({
    async start(controller) {
      try {
        let buffer = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith("data:")) {
              const data = trimmed.slice(5).trim();
              if (data === "[DONE]") continue;
              try {
                const parsed = JSON.parse(data);
                const delta = parsed.choices?.[0]?.delta?.content;
                if (delta) {
                  const sseChunk = JSON.stringify({ type: "text-delta", delta });
                  controller.enqueue(encoder.encode(`data: ${sseChunk}\n\n`));
                }
              } catch {
                // Skip invalid JSON
              }
            }
          }
        }
        controller.enqueue(encoder.encode(`data: [DONE]\n\n`));
        controller.close();
      } catch (error) {
        controller.error(error);
      }
    },
  });
}

// Respostas locais inteligentes
function generateLocalResponse(messages: Array<{ role: string; content: string }>): string {
  const lastMessage = messages[messages.length - 1]?.content?.toLowerCase() || "";
  
  if (lastMessage.includes("status") || lastMessage.includes("como voce esta")) {
    const status = tools.status_sistema();
    return `Estou funcionando perfeitamente!\n\n**Status do Sistema:**\n- Provider: ${status.provider}\n- Modelo: ${status.model}\n- Uptime: ${status.uptime.toFixed(2)}s\n- Memoria: ${status.memoria_usada.toFixed(2)}MB\n\n**Habilidades:**\n- Raciocinio: ${(status.skills.raciocinio * 100).toFixed(0)}%\n- Memoria: ${(status.skills.memoria * 100).toFixed(0)}%\n- Criatividade: ${(status.skills.criatividade * 100).toFixed(0)}%`;
  }
  
  if (lastMessage.includes("calcul") || lastMessage.match(/\d+\s*[+\-*/]\s*\d+/)) {
    const match = lastMessage.match(/[\d+\-*/().%\s]+/);
    if (match) {
      const result = tools.calcular(match[0]);
      if (result.result !== undefined) {
        return `**Calculo:** ${result.expression} = **${result.result}**`;
      }
    }
    return "Forneca uma expressao matematica valida (ex: 2 + 2, 10 * 5)";
  }
  
  if (lastMessage.includes("ideia") || lastMessage.includes("sugest")) {
    const topicMatch = lastMessage.match(/(?:sobre|para|de)\s+(.+?)(?:\?|$|\.)/i);
    const topic = topicMatch ? topicMatch[1].trim() : "inteligencia artificial";
    const result = tools.gerar_ideias(topic);
    return `**Ideias sobre "${result.topic}":**\n\n${result.ideas.map((idea, i) => `${i + 1}. ${idea}`).join("\n")}`;
  }
  
  if (lastMessage.includes("ajuda") || lastMessage.includes("help")) {
    return `**NovaComp AI - Comandos:**\n
1. **status** - Meu estado atual
2. **calcular** - Calculos matematicos
3. **ideias sobre [topico]** - Gerar ideias
4. **memorizar/lembrar** - Gerenciar memoria

**Configuracao LLM:**
- Provider atual: \`${LLM_PROVIDER}\`
- Para usar Ollama: defina OLLAMA_URL e LLM_PROVIDER=ollama
- Para usar OpenAI: defina OPENAI_API_KEY e LLM_PROVIDER=openai`;
  }
  
  return `Entendi sua mensagem. Estou operando em modo local.\n\nPara usar uma LLM completa, configure:\n- **Ollama**: LLM_PROVIDER=ollama, OLLAMA_URL, OLLAMA_MODEL\n- **OpenAI**: LLM_PROVIDER=openai, OPENAI_API_KEY\n\nDigite "ajuda" para ver comandos disponiveis.`;
}

function createLocalStream(content: string): ReadableStream {
  const encoder = new TextEncoder();
  const words = content.split(" ");
  
  return new ReadableStream({
    start(controller) {
      words.forEach((word, index) => {
        const delta = (index === 0 ? "" : " ") + word;
        const chunk = JSON.stringify({ type: "text-delta", delta });
        controller.enqueue(encoder.encode(`data: ${chunk}\n\n`));
      });
      controller.enqueue(encoder.encode(`data: [DONE]\n\n`));
      controller.close();
    },
  });
}

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    let stream: ReadableStream;

    // Escolher provider
    if (LLM_PROVIDER === "ollama") {
      try {
        stream = await callOllama(messages);
      } catch (error) {
        console.error("Ollama error, falling back to local:", error);
        stream = createLocalStream(generateLocalResponse(messages) + "\n\n(Ollama indisponivel, usando modo local)");
      }
    } else if (LLM_PROVIDER === "openai" && OPENAI_API_KEY) {
      try {
        stream = await callOpenAI(messages);
      } catch (error) {
        console.error("OpenAI error, falling back to local:", error);
        stream = createLocalStream(generateLocalResponse(messages) + "\n\n(OpenAI indisponivel, usando modo local)");
      }
    } else {
      stream = createLocalStream(generateLocalResponse(messages));
    }

    // Adicionar ao historico
    conversationHistory.push(
      { role: "user", content: messages[messages.length - 1]?.content || "" }
    );

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (error) {
    console.error("Chat error:", error);
    return NextResponse.json(
      { error: "Erro ao processar mensagem" },
      { status: 500 }
    );
  }
}

// Health check endpoint
export async function GET() {
  const status = tools.status_sistema();
  return NextResponse.json({
    status: "healthy",
    provider: LLM_PROVIDER,
    model: LLM_PROVIDER === "ollama" ? OLLAMA_MODEL : "local",
    ...status,
  });
}
