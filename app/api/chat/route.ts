import { NextResponse } from "next/server";

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
      // Avaliacao segura de expressoes matematicas
      const sanitized = expression.replace(/[^0-9+\-*/().%\s]/g, "");
      const result = Function(`"use strict"; return (${sanitized})`)();
      return { result, expression: sanitized };
    } catch {
      return { error: "Expressao invalida" };
    }
  },
  status_sistema: () => ({
    status: "online",
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

// Respostas inteligentes baseadas no contexto
function generateResponse(messages: Array<{ role: string; content: string }>): string {
  const lastMessage = messages[messages.length - 1]?.content?.toLowerCase() || "";
  
  // Detectar intencao
  if (lastMessage.includes("status") || lastMessage.includes("como voce esta")) {
    const status = tools.status_sistema();
    return `Estou funcionando perfeitamente!\n\n**Status do Sistema:**\n- Uptime: ${status.uptime.toFixed(2)}s\n- Memoria: ${status.memoria_usada.toFixed(2)}MB\n\n**Habilidades:**\n- Raciocinio: ${(status.skills.raciocinio * 100).toFixed(0)}%\n- Memoria: ${(status.skills.memoria * 100).toFixed(0)}%\n- Criatividade: ${(status.skills.criatividade * 100).toFixed(0)}%\n- Analise: ${(status.skills.analise * 100).toFixed(0)}%\n- Comunicacao: ${(status.skills.comunicacao * 100).toFixed(0)}%`;
  }
  
  if (lastMessage.includes("calcul") || lastMessage.match(/\d+\s*[+\-*/]\s*\d+/)) {
    const match = lastMessage.match(/[\d+\-*/().%\s]+/);
    if (match) {
      const result = tools.calcular(match[0]);
      if (result.result !== undefined) {
        return `**Calculo:** ${result.expression} = **${result.result}**`;
      }
    }
    return "Por favor, forneca uma expressao matematica valida (ex: 2 + 2, 10 * 5, etc.)";
  }
  
  if (lastMessage.includes("memor") || lastMessage.includes("lembr")) {
    if (lastMessage.includes("guardar") || lastMessage.includes("salvar")) {
      return "Para memorizar algo, diga: 'memorize [chave]: [valor]'\nExemplo: memorize meu_nome: João";
    }
    return `Tenho ${memory.size} itens na memoria. Posso guardar ou lembrar informacoes para voce.`;
  }
  
  if (lastMessage.includes("ideia") || lastMessage.includes("sugest")) {
    const topicMatch = lastMessage.match(/(?:sobre|para|de)\s+(.+?)(?:\?|$|\.)/i);
    const topic = topicMatch ? topicMatch[1].trim() : "inteligencia artificial";
    const result = tools.gerar_ideias(topic);
    return `**Ideias sobre "${result.topic}":**\n\n${result.ideas.map((idea, i) => `${i + 1}. ${idea}`).join("\n")}`;
  }
  
  if (lastMessage.includes("codigo") || lastMessage.includes("analis")) {
    return "Posso analisar codigo para voce! Cole o codigo que deseja analisar e direi:\n- Complexidade estimada\n- Possiveis melhorias\n- Boas praticas aplicaveis";
  }
  
  if (lastMessage.includes("ajuda") || lastMessage.includes("help")) {
    return `**Comandos disponiveis:**\n
1. **Status** - Pergunta sobre meu estado atual
2. **Calcular** - Faco calculos matematicos (ex: "calcule 15 * 8")
3. **Ideias** - Gero ideias sobre um topico (ex: "ideias sobre automacao")
4. **Memoria** - Posso guardar e lembrar informacoes
5. **Analise** - Analiso codigo ou textos

Sou o NovaComp AI, um sistema de IA autonoma com capacidades avancadas!`;
  }
  
  // Resposta generica inteligente
  const responses = [
    `Entendi sua mensagem sobre "${lastMessage.substring(0, 30)}...". Como posso ajudar mais especificamente?`,
    `Interessante! Posso ajudar com calculos, gerar ideias, analisar codigo ou memorizar informacoes. O que prefere?`,
    `Estou processando sua solicitacao. Posso executar diversas tarefas - pergunte "ajuda" para ver todas as opcoes.`,
  ];
  
  return responses[Math.floor(Math.random() * responses.length)];
}

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    
    // Gerar resposta
    const response = generateResponse(messages);
    
    // Adicionar ao historico
    conversationHistory.push(
      { role: "user", content: messages[messages.length - 1]?.content || "" },
      { role: "assistant", content: response }
    );
    
    // Criar stream SSE
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        // Simular streaming palavra por palavra
        const words = response.split(" ");
        let currentText = "";
        
        words.forEach((word, index) => {
          currentText += (index === 0 ? "" : " ") + word;
          const chunk = JSON.stringify({ type: "text-delta", delta: (index === 0 ? "" : " ") + word });
          controller.enqueue(encoder.encode(`data: ${chunk}\n\n`));
        });
        
        controller.enqueue(encoder.encode(`data: [DONE]\n\n`));
        controller.close();
      },
    });

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
