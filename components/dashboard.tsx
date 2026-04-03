"use client";

import { useState, useEffect, useCallback } from "react";
import useSWR from "swr";
import { Header } from "./header";
import { StatusCard, MetricRow } from "./status-card";
import { SkillBar } from "./skill-bar";
import { ProcessIndicator } from "./process-indicator";
import { LogViewer, type LogEntry } from "./log-viewer";
import { ChatInterface } from "./chat-interface";
import { EvolutionDisplay } from "./evolution-display";
import { SkillsChart } from "./skills-chart";
import { ActionButtons } from "./action-buttons";
import { formatDuration, formatNumber } from "@/lib/utils";
import {
  fetchStatus,
  sendMessage,
  type NovaCompStatus,
  type ChatResponse,
} from "@/lib/api";
import {
  Activity,
  Database,
  MessageSquare,
  Terminal,
  Target,
  Clock,
  HardDrive,
  Network,
  BarChart3,
  Zap,
} from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  confidence?: number;
}

// Mock data para quando a API nao esta disponivel
const mockStatus: NovaCompStatus = {
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

export function Dashboard() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  
  // Fetch status com SWR
  const { data: status, error } = useSWR<NovaCompStatus>(
    "status",
    fetchStatus,
    {
      refreshInterval: 5000,
      onSuccess: () => setIsConnected(true),
      onError: () => setIsConnected(false),
      fallbackData: mockStatus,
    }
  );
  
  const currentStatus = status || mockStatus;
  
  // Adiciona log
  const addLog = useCallback((level: LogEntry["level"], message: string) => {
    const entry: LogEntry = {
      id: crypto.randomUUID(),
      timestamp: new Date().toLocaleTimeString("pt-BR"),
      level,
      message,
    };
    setLogs((prev) => [entry, ...prev].slice(0, 100));
  }, []);
  
  // Inicializa logs
  useEffect(() => {
    addLog("info", "Dashboard inicializado");
    if (error) {
      addLog("warning", "API Python nao disponivel - usando dados de demonstracao");
    }
  }, [addLog, error]);
  
  // Handle action buttons
  const handleAction = useCallback((action: string, result: unknown) => {
    const resultStr = JSON.stringify(result);
    if (action === "evolve") {
      addLog("success", `Evolucao verificada: ${resultStr.substring(0, 50)}`);
    } else if (action === "learn") {
      addLog("success", `Conhecimento ensinado: ${resultStr.substring(0, 50)}`);
    } else if (action === "reflect") {
      addLog("info", `Auto-reflexao realizada: ${resultStr.substring(0, 50)}`);
    }
  }, [addLog]);
  
  // Envia mensagem
  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };
    setMessages((prev) => [...prev, userMessage]);
    addLog("info", `Enviado: ${content.substring(0, 50)}...`);
    
    setIsLoading(true);
    
    try {
      const allMessages = [...messages, userMessage].map((m) => ({
        role: m.role,
        content: m.content,
      }));
      
      const response: ChatResponse = await sendMessage(allMessages);
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.response,
        confidence: response.confidence,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      addLog("success", "Resposta recebida da IA");
    } catch (err) {
      // Fallback response quando API nao esta disponivel
      const fallbackMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: `Recebi sua mensagem: "${content}"\n\nNo momento estou operando em modo de demonstracao. Conecte a API Python para interacao completa com o sistema NovaComp.`,
        confidence: 0.5,
      };
      setMessages((prev) => [...prev, fallbackMessage]);
      addLog("warning", "Usando resposta de demonstracao");
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-background grid-pattern">
      <Header isConnected={isConnected} systemName={currentStatus.name} />
      
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Evolution Level & Actions */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <EvolutionDisplay level={currentStatus.evolution_level} />
          <div className="flex flex-col items-center md:items-end gap-2">
            <p className="text-sm text-muted-foreground flex items-center gap-2">
              <Zap className="w-4 h-4 text-chart-3" />
              Acoes Rapidas
            </p>
            <ActionButtons onAction={handleAction} />
          </div>
        </div>
        
        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          {/* Left Column - Status */}
          <div className="space-y-6">
            {/* System Status */}
            <StatusCard title="Status do Sistema" icon={<Activity className="w-4 h-4" />}>
              <MetricRow label="Estado" value={currentStatus.state} />
              <MetricRow
                label="Tempo ativo"
                value={formatDuration(currentStatus.uptime_hours)}
              />
              <MetricRow
                label="Memorias"
                value={formatNumber(currentStatus.memory_stats.total_memories)}
              />
              <MetricRow
                label="Eventos de aprendizado"
                value={formatNumber(currentStatus.learning_events)}
              />
              <ProcessIndicator currentState={currentStatus.state} />
            </StatusCard>
            
            {/* Memory Stats */}
            <StatusCard title="Memoria TurboQuant" icon={<Database className="w-4 h-4" />}>
              <MetricRow
                label="Total de memorias"
                value={formatNumber(currentStatus.memory_stats.total_memories)}
              />
              <MetricRow
                label="Relacoes"
                value={formatNumber(currentStatus.memory_stats.total_relations)}
              />
              <MetricRow
                label="Cache curto prazo"
                value={formatNumber(currentStatus.memory_stats.short_term_cache_size)}
              />
              <MetricRow
                label="Acessos recentes"
                value={formatNumber(currentStatus.memory_stats.recent_accesses)}
              />
              <MetricRow
                label="Eventos de evolucao"
                value={formatNumber(currentStatus.memory_stats.evolution_events)}
              />
            </StatusCard>
          </div>
          
          {/* Middle Column - Chat */}
          <div className="lg:col-span-1">
            <StatusCard
              title="Interacao"
              icon={<MessageSquare className="w-4 h-4" />}
              className="h-[600px] flex flex-col"
            >
              <div className="flex-1 -mx-5 -mb-5 border-t border-border mt-2">
                <ChatInterface
                  messages={messages}
                  onSendMessage={handleSendMessage}
                  isLoading={isLoading}
                />
              </div>
            </StatusCard>
          </div>
          
          {/* Right Column - Skills & Logs */}
          <div className="space-y-6">
            {/* Skills Radar */}
            <StatusCard title="Mapa de Habilidades" icon={<BarChart3 className="w-4 h-4" />}>
              <SkillsChart skills={currentStatus.skills} />
              <div className="mt-2 pt-4 border-t border-border">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Media geral</span>
                  <span className="font-semibold text-primary">
                    {(currentStatus.average_skill * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </StatusCard>
            
            {/* Skills List */}
            <StatusCard title="Detalhes das Habilidades" icon={<Target className="w-4 h-4" />}>
              {Object.entries(currentStatus.skills).map(([name, value]) => (
                <SkillBar key={name} name={name} value={value} />
              ))}
            </StatusCard>
            
            {/* Logs */}
            <StatusCard title="Logs em Tempo Real" icon={<Terminal className="w-4 h-4" />}>
              <LogViewer logs={logs} />
            </StatusCard>
          </div>
        </div>
        
        {/* Bottom Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-card border border-border rounded-xl p-4 text-center">
            <Clock className="w-5 h-5 mx-auto mb-2 text-primary" />
            <p className="text-2xl font-bold text-foreground">
              {formatDuration(currentStatus.uptime_hours)}
            </p>
            <p className="text-xs text-muted-foreground">Uptime</p>
          </div>
          <div className="bg-card border border-border rounded-xl p-4 text-center">
            <HardDrive className="w-5 h-5 mx-auto mb-2 text-accent" />
            <p className="text-2xl font-bold text-foreground">
              {formatNumber(currentStatus.memory_stats.total_memories)}
            </p>
            <p className="text-xs text-muted-foreground">Memorias</p>
          </div>
          <div className="bg-card border border-border rounded-xl p-4 text-center">
            <Network className="w-5 h-5 mx-auto mb-2 text-chart-3" />
            <p className="text-2xl font-bold text-foreground">
              {formatNumber(currentStatus.memory_stats.total_relations)}
            </p>
            <p className="text-xs text-muted-foreground">Relacoes</p>
          </div>
          <div className="bg-card border border-border rounded-xl p-4 text-center">
            <Activity className="w-5 h-5 mx-auto mb-2 text-chart-4" />
            <p className="text-2xl font-bold text-foreground">
              {formatNumber(currentStatus.learning_events)}
            </p>
            <p className="text-xs text-muted-foreground">Aprendizados</p>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="border-t border-border mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm text-muted-foreground">
            NovaComp - Sistema de Inteligencia Autonoma com Memoria Vetorial TurboQuant
          </p>
        </div>
      </footer>
    </div>
  );
}
