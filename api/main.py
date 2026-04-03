"""
NovaComp - API Principal
Backend FastAPI para a IA Autonoma
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import sys
from pathlib import Path

# Adiciona root ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.brain import NovaCompCore
from memory.turboquant import TurboQuantMemory
from agents.executor import TaskExecutorAgent, LearningAgent


# FastAPI app
app = FastAPI(
    title="NovaComp API",
    description="API da Inteligencia Autonoma NovaComp",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Instancias globais
nova_core: Optional[NovaCompCore] = None
executor_agent: Optional[TaskExecutorAgent] = None
learning_agent: Optional[LearningAgent] = None


def get_or_init_core() -> NovaCompCore:
    """Obtem ou inicializa o core"""
    global nova_core, executor_agent, learning_agent
    
    if nova_core is None:
        nova_core = NovaCompCore(name="NovaComp-Alpha", db_path="/tmp/novacomp.db")
        executor_agent = TaskExecutorAgent(safe_mode=True)
        learning_agent = LearningAgent()
        nova_core.register_agent("executor", executor_agent.execute)
    
    return nova_core


# Modelos Pydantic
class ThinkRequest(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = None


class LearnRequest(BaseModel):
    knowledge: Dict[str, Any]


class ExecuteRequest(BaseModel):
    command: str
    timeout: Optional[int] = 30


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


# Rotas
@app.get("/")
async def root():
    """Rota raiz"""
    return {
        "name": "NovaComp API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "status": "/api/status",
            "think": "/api/think",
            "learn": "/api/learn",
            "execute": "/api/execute",
            "chat": "/api/chat",
            "reflect": "/api/reflect",
            "skills": "/api/skills",
            "memory": "/api/memory"
        }
    }


@app.get("/api/status")
async def get_status():
    """Retorna status completo do sistema"""
    core = get_or_init_core()
    status = core.get_status()
    
    return {
        "success": True,
        "data": status
    }


@app.post("/api/think")
async def think(request: ThinkRequest):
    """Processa pensamento da IA"""
    core = get_or_init_core()
    
    try:
        decision = await core.think(request.input, request.context)
        return {
            "success": True,
            "data": decision
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/learn")
async def learn(request: LearnRequest):
    """Ensina novo conhecimento"""
    core = get_or_init_core()
    
    try:
        result = await core.learn(request.knowledge)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/execute")
async def execute(request: ExecuteRequest):
    """Executa comando seguro"""
    core = get_or_init_core()
    
    if executor_agent is None:
        raise HTTPException(status_code=500, detail="Executor not initialized")
    
    try:
        result = await executor_agent.execute(request.command, request.timeout)
        return {
            "success": result.get("success", False),
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Endpoint de chat conversacional"""
    core = get_or_init_core()
    
    try:
        # Pega ultima mensagem do usuario
        last_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                last_message = msg.content
                break
        
        if not last_message:
            return {
                "success": True,
                "data": {
                    "response": "Ola! Como posso ajudar?",
                    "action": "greeting"
                }
            }
        
        # Processa com contexto das mensagens anteriores
        context = {
            "conversation_history": [
                {"role": m.role, "content": m.content} 
                for m in request.messages[:-1]
            ]
        }
        
        decision = await core.think(last_message, context)
        
        # Gera resposta baseada na decisao
        response_templates = {
            "initiate_learning": f"Entendi! Vou aprender sobre isso. {decision.get('description', '')}",
            "initiate_creation": f"Vou criar isso para voce. {decision.get('description', '')}",
            "execute_task": f"Executando a tarefa solicitada. {decision.get('description', '')}",
            "perform_analysis": f"Analisando... {decision.get('description', '')}",
            "provide_assistance": f"Estou aqui para ajudar! {decision.get('description', '')}",
            "engage_conversation": f"Interessante! {decision.get('description', '')}"
        }
        
        action = decision.get("action", "engage_conversation")
        response_text = response_templates.get(action, decision.get('description', 'Processando...'))
        
        # Adiciona proximos passos se houver
        next_steps = decision.get("suggested_next_steps", [])
        if next_steps:
            response_text += "\n\nProximos passos sugeridos:\n"
            for i, step in enumerate(next_steps, 1):
                response_text += f"{i}. {step}\n"
        
        return {
            "success": True,
            "data": {
                "response": response_text,
                "decision": decision,
                "confidence": decision.get("confidence", 0.5)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reflect")
async def reflect():
    """Realiza auto-reflexao"""
    core = get_or_init_core()
    
    try:
        reflection = await core.self_reflect()
        return {
            "success": True,
            "data": reflection
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skills")
async def get_skills():
    """Retorna habilidades da IA"""
    core = get_or_init_core()
    
    skills = core.skills
    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "success": True,
        "data": {
            "skills": dict(sorted_skills),
            "average": sum(skills.values()) / len(skills) if skills else 0,
            "evolution_level": core.evolution_level
        }
    }


@app.get("/api/memory")
async def get_memory_stats():
    """Retorna estatisticas de memoria"""
    core = get_or_init_core()
    
    stats = core.memory.get_stats()
    
    return {
        "success": True,
        "data": stats
    }


@app.post("/api/memory/search")
async def search_memory(query: Dict[str, Any]):
    """Busca na memoria"""
    core = get_or_init_core()
    
    try:
        query_text = query.get("query", "")
        limit = query.get("limit", 10)
        threshold = query.get("threshold", 0.6)
        
        # Gera embedding da query
        query_vector = core._generate_embedding(query_text)
        
        results = core.memory.search_similar(
            query_vector=query_vector,
            threshold=threshold,
            limit=limit
        )
        
        return {
            "success": True,
            "data": {
                "query": query_text,
                "results": results,
                "count": len(results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def get_history():
    """Retorna historico de aprendizado"""
    core = get_or_init_core()
    
    return {
        "success": True,
        "data": {
            "learning_history": core.learning_history[-50:],
            "total_events": len(core.learning_history)
        }
    }


@app.post("/api/evolve")
async def trigger_evolution():
    """Tenta disparar evolucao"""
    core = get_or_init_core()
    
    try:
        evolved = await core._check_evolution()
        
        return {
            "success": True,
            "data": {
                "evolved": evolved,
                "current_level": core.evolution_level,
                "skills": core.skills
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
