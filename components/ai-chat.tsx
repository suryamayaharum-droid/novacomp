"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { cn } from "@/lib/utils";
import { Send, Bot, User, Sparkles, Loader2, Wrench } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolCalls?: Array<{ name: string; status: "running" | "complete"; result?: string }>;
}

export function AIChat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setStreamingContent("");

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, userMessage].map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error("Erro na resposta");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      const toolCalls: Message["toolCalls"] = [];

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith("data:")) {
              const data = trimmed.slice(5).trim();
              if (data === "[DONE]") continue;
              
              try {
                const parsed = JSON.parse(data);
                
                if (parsed.type === "text-delta" && parsed.delta) {
                  fullContent += parsed.delta;
                  setStreamingContent(fullContent);
                } else if (parsed.type === "tool-call") {
                  toolCalls.push({
                    name: parsed.toolName || "ferramenta",
                    status: "running",
                  });
                } else if (parsed.type === "tool-result") {
                  const existing = toolCalls.find((t) => t.name === parsed.toolName);
                  if (existing) {
                    existing.status = "complete";
                    existing.result = JSON.stringify(parsed.result).substring(0, 100);
                  }
                }
              } catch {
                // Skip invalid JSON
              }
            }
          }
        }
      }

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: fullContent || "Processado com sucesso.",
        toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setStreamingContent("");
    } catch {
      const demoResponses = [
        "Sou o NovaComp AI, um sistema de inteligencia artificial autonoma. Estou operando com todas as minhas habilidades ativas.",
        "Analisando sua solicitacao... Posso ajudar com analise de codigo, calculos matematicos, geracao de ideias e muito mais.",
        "Meu sistema de memoria TurboQuant esta funcionando normalmente. Todas as habilidades estao em nivel otimo.",
      ];
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: demoResponses[Math.floor(Math.random() * demoResponses.length)] + "\n\n(Modo Demo - Configure LLM_PROVIDER para usar Ollama ou OpenAI)",
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
      setStreamingContent("");
    } finally {
      setIsLoading(false);
    }
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    sendMessage(input);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 p-3 border-b border-border bg-card/50">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-chart-3 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-primary-foreground" />
        </div>
        <div>
          <h3 className="text-sm font-medium">NovaComp AI</h3>
          <p className="text-xs text-muted-foreground">
            {isLoading ? "Pensando..." : "Online - LLM Integrada"}
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !streamingContent ? (
          <div className="text-center text-muted-foreground py-12">
            <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="font-medium">NovaComp AI - LLM Integrada</p>
            <p className="text-sm mt-2">Sistema de IA autonoma com ferramentas integradas</p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center max-w-sm mx-auto">
              {["Qual seu status?", "Analise este codigo", "Gere ideias sobre IA"].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                  className="text-xs px-3 py-1.5 rounded-full bg-secondary hover:bg-secondary/80 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={cn(
                  "flex gap-3",
                  msg.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-chart-3 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-primary-foreground" />
                  </div>
                )}
                <div
                  className={cn(
                    "max-w-[80%] rounded-xl",
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground px-4 py-3"
                      : "bg-secondary text-foreground"
                  )}
                >
                  {msg.toolCalls && msg.toolCalls.length > 0 && (
                    <div className="px-4 py-2 border-b border-border/50">
                      <div className="flex flex-wrap gap-1">
                        {msg.toolCalls.map((tool, i) => (
                          <span
                            key={i}
                            className={cn(
                              "inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full",
                              tool.status === "complete"
                                ? "bg-chart-2/20 text-chart-2"
                                : "bg-chart-3/20 text-chart-3"
                            )}
                          >
                            <Wrench className="w-3 h-3" />
                            {tool.name}
                            {tool.status === "running" && (
                              <Loader2 className="w-3 h-3 animate-spin" />
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <p className={cn(
                    "text-sm whitespace-pre-wrap",
                    msg.role === "assistant" && "px-4 py-3"
                  )}>
                    {msg.content}
                  </p>
                </div>
                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-accent" />
                  </div>
                )}
              </div>
            ))}
            
            {streamingContent && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-chart-3 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-4 h-4 text-primary-foreground animate-pulse" />
                </div>
                <div className="max-w-[80%] bg-secondary text-foreground rounded-xl px-4 py-3">
                  <p className="text-sm whitespace-pre-wrap">{streamingContent}</p>
                </div>
              </div>
            )}
          </>
        )}
        
        {isLoading && !streamingContent && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-chart-3 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-primary-foreground animate-pulse" />
            </div>
            <div className="bg-secondary rounded-xl px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-primary" />
                <span className="text-sm text-muted-foreground">Processando...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-border">
        <div className="flex gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Converse com NovaComp AI..."
            className={cn(
              "flex-1 bg-secondary border border-border rounded-xl px-4 py-3",
              "text-sm text-foreground placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary",
              "resize-none min-h-[48px] max-h-32"
            )}
            rows={1}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={cn(
              "px-4 py-3 bg-gradient-to-r from-primary to-chart-3 text-primary-foreground rounded-xl",
              "hover:opacity-90 transition-opacity",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "flex items-center justify-center gap-2"
            )}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          Suporta Ollama e OpenAI - Configure via variaveis de ambiente
        </p>
      </form>
    </div>
  );
}
