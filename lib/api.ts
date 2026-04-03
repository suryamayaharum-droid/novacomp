const API_BASE = "/api/py";

export interface NovaCompStatus {
  name: string;
  state: string;
  evolution_level: number;
  skills: Record<string, number>;
  average_skill: number;
  memory_stats: {
    total_memories: number;
    categories: Record<string, number>;
    total_relations: number;
    evolution_events: number;
    short_term_cache_size: number;
    recent_accesses: number;
  };
  learning_events: number;
  active_tasks: number;
  uptime_hours: number;
}

export interface ThinkResponse {
  action: string;
  priority: number;
  confidence: number;
  description: string;
  analysis: {
    intent: string;
    topics: string[];
    complexity: number;
    memory_matches: number;
    sentiment: string;
  };
  suggested_next_steps: string[];
}

export interface ChatResponse {
  response: string;
  decision: ThinkResponse;
  confidence: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
}

export async function fetchStatus(): Promise<NovaCompStatus> {
  const res = await fetch(`${API_BASE}/status`);
  const json: ApiResponse<NovaCompStatus> = await res.json();
  if (!json.success) throw new Error("Failed to fetch status");
  return json.data;
}

export async function sendMessage(
  messages: Array<{ role: string; content: string }>
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });
  const json: ApiResponse<ChatResponse> = await res.json();
  if (!json.success) throw new Error("Failed to send message");
  return json.data;
}

export async function triggerReflection() {
  const res = await fetch(`${API_BASE}/reflect`);
  const json = await res.json();
  if (!json.success) throw new Error("Failed to reflect");
  return json.data;
}

export async function fetchSkills() {
  const res = await fetch(`${API_BASE}/skills`);
  const json = await res.json();
  if (!json.success) throw new Error("Failed to fetch skills");
  return json.data;
}

export async function fetchMemoryStats() {
  const res = await fetch(`${API_BASE}/memory`);
  const json = await res.json();
  if (!json.success) throw new Error("Failed to fetch memory");
  return json.data;
}

export async function teachKnowledge(knowledge: Record<string, unknown>) {
  const res = await fetch(`${API_BASE}/learn`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ knowledge }),
  });
  const json = await res.json();
  if (!json.success) throw new Error("Failed to teach");
  return json.data;
}

export async function triggerEvolution() {
  const res = await fetch(`${API_BASE}/evolve`, { method: "POST" });
  const json = await res.json();
  if (!json.success) throw new Error("Failed to evolve");
  return json.data;
}
