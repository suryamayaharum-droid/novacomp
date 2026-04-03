"use client";

import { useState, useRef, useEffect } from "react";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { cn } from "@/lib/utils";
import { Send, Bot, User, Sparkles, Loader2, Wrench } from "lucide-react";

export function AIChat() {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { messages, sendMessage, status } = useChat({
    transport: new DefaultChatTransport({ api: "/api/chat" }),
  });

  const isLoading = status === "streaming" || status === "submitted";

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    sendMessage({ text: input });
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Helper para extrair texto das mensagens
  const getMessageText = (parts: Array<{ type: string; text?: string }> | undefined): string => {
    if (!parts || !Array.isArray(parts)) return "";
    return parts
      .filter((p): p is { type: "text"; text: string } => p.type === "text" && !!p.text)
      .map((p) => p.text)
      .join("");
  };

  // Helper para detectar tool calls
  const getToolCalls = (parts: Array<{ type: string; toolName?: string; state?: string }> | undefined) => {
    if (!parts || !Array.isArray(parts)) return [];
    return parts.filter((p) => p.type === "tool-invocation");
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-2 p-3 border-b border-border bg-card/50">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-chart-3 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-primary-foreground" />
        </div>
        <div>
          <h3 className="text-sm font-medium">NovaComp AI</h3>
          <p className="text-xs text-muted-foreground">
            {isLoading ? "Pensando..." : "Online - LLM Nativa"}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-muted-foreground py-12">
            <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="font-medium">NovaComp AI - LLM Nativa</p>
            <p className="text-sm mt-2">Sistema de IA autonoma com ferramentas integradas</p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center max-w-sm mx-auto">
              {["Qual seu status?", "Analise este codigo", "Gere ideias sobre IA"].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setInput(suggestion);
                  }}
                  className="text-xs px-3 py-1.5 rounded-full bg-secondary hover:bg-secondary/80 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => {
            const text = getMessageText(msg.parts);
            const toolCalls = getToolCalls(msg.parts);
            
            return (
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
                  {/* Tool calls indicators */}
                  {toolCalls.length > 0 && (
                    <div className="px-4 py-2 border-b border-border/50">
                      <div className="flex flex-wrap gap-1">
                        {toolCalls.map((tool, i) => (
                          <span
                            key={i}
                            className={cn(
                              "inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full",
                              tool.state === "output-available"
                                ? "bg-chart-2/20 text-chart-2"
                                : "bg-chart-3/20 text-chart-3"
                            )}
                          >
                            <Wrench className="w-3 h-3" />
                            {tool.toolName}
                            {tool.state !== "output-available" && (
                              <Loader2 className="w-3 h-3 animate-spin" />
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Message text */}
                  {text && (
                    <p className={cn(
                      "text-sm whitespace-pre-wrap",
                      msg.role === "assistant" && "px-4 py-3"
                    )}>
                      {text}
                    </p>
                  )}
                </div>
                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-accent" />
                  </div>
                )}
              </div>
            );
          })
        )}
        
        {/* Loading indicator */}
        {isLoading && messages[messages.length - 1]?.role !== "assistant" && (
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

      {/* Input */}
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
          LLM Nativa com ferramentas: memoria, analise, calculos e mais
        </p>
      </form>
    </div>
  );
}
