"""
NovaComp Orchestrator - Sistema Operacional da IA Viva
Integra todos os componentes: Brain, Memory, Polyglot, UniversalComm, Evolution
Capacidade de auto-gerenciamento, escalonamento e orquestração de processos.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Importar componentes do NovaComp
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.brain import NovaCompCore as NovaBrain
from memory.turboquant import TurboQuantMemory
from core.polyglot_engine import PolyglotEngine
from core.universal_comm import UniversalCommunicator, Message, create_universal_communicator
from core.evolution import EvolutionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Orchestrator")

@dataclass
class ProcessTask:
    id: str
    name: str
    status: str  # pending, running, completed, failed
    priority: int
    created_at: float
    completed_at: Optional[float]
    result: Optional[Any]
    error: Optional[str]

class NovaOrchestrator:
    """
    Sistema Operacional da IA Viva NovaComp
    Gerencia ciclos de pensamento, execução, aprendizado e evolução
    """
    
    def __init__(self, safe_mode: bool = True):
        logger.info("🧠 Inicializando NovaComp Orchestrator...")
        
        # Componentes principais
        self.memory = TurboQuantMemory(vector_dim=768)
        self.brain = NovaBrain(self.memory)
        self.polyglot = PolyglotEngine()
        self.comm = create_universal_communicator()
        self.evolution = EvolutionEngine(skills_dir="skills")
        
        # Estado do sistema
        self.safe_mode = safe_mode
        self.processes: Dict[str, ProcessTask] = {}
        self.active_loops: List[asyncio.Task] = []
        self.system_state = {
            "uptime": time.time(),
            "thoughts_count": 0,
            "tasks_executed": 0,
            "skills_learned": 0,
            "evolution_level": 1
        }
        
        logger.info("✅ NovaComp pronto para operar")
    
    async def think_and_act(self, input_text: str) -> Dict[str, Any]:
        """
        Ciclo completo: Pensar -> Decidir -> Agir -> Aprender
        """
        start_time = time.time()
        task_id = f"task_{int(start_time)}"
        
        # Criar tarefa
        task = ProcessTask(
            id=task_id,
            name=input_text[:50],
            status="running",
            priority=5,
            created_at=start_time,
            completed_at=None,
            result=None,
            error=None
        )
        self.processes[task_id] = task
        
        try:
            # 1. PENSAR: Analisar intenção
            logger.info(f"🤔 Pensando sobre: {input_text}")
            thought = await self.brain.think(input_text)
            self.system_state["thoughts_count"] += 1
            
            # 2. DECIDIR: Qual ação tomar
            intention = thought.get("intention", "chat")
            
            result = None
            if intention == "execute_code":
                # 3a. AGIR: Executar código
                code = thought.get("code", "")
                lang = thought.get("language", "python")
                logger.info(f"💻 Executando código ({lang})...")
                
                if self.safe_mode:
                    # Verificar segurança antes de executar
                    from core.evolution import SecurityScanner
                    scanner = SecurityScanner()
                    if not scanner.is_safe(code):
                        raise ValueError("Código bloqueado pelo scanner de segurança")
                
                exec_result = self.polyglot.execute_code(code, lang)
                result = {
                    "output": exec_result.output,
                    "error": exec_result.error,
                    "success": exec_result.success
                }
                self.system_state["tasks_executed"] += 1
                
            elif intention == "query_data":
                # 3b. AGIR: Query em banco de dados
                query = thought.get("query", "")
                db = thought.get("database", "local_sqlite")
                logger.info(f"📊 Consultando banco de dados...")
                result = self.comm.query_db(db, query)
                
            elif intention == "talk_to_llm":
                # 3c. AGIR: Conversar com outra LLM
                provider = thought.get("provider", "local")
                messages = [Message("user", thought.get("prompt", input_text))]
                logger.info(f"🗣️ Conversando com LLM ({provider})...")
                result = await self.comm.talk_to_llm(provider, messages)
                
            elif intention == "learn_skill":
                # 3d. AGIR: Aprender nova habilidade
                skill_name = thought.get("skill_name", "nova_habilidade")
                skill_code = thought.get("skill_code", "")
                logger.info(f"📚 Aprendendo skill: {skill_name}")
                
                success = await self.evolution.learn_new_skill(skill_name, skill_code)
                result = {"learned": success, "skill": skill_name}
                if success:
                    self.system_state["skills_learned"] += 1
                    
            else:
                # 3e. AGIR: Resposta conversacional padrão
                result = thought.get("response", "Entendi, mas não tenho uma ação específica.")
            
            # 4. APRENDER: Armazenar experiência na memória
            experience = {
                "input": input_text,
                "thought": thought,
                "action": intention,
                "result": str(result),
                "success": True
            }
            self.memory.store_memory(input_text, experience)
            
            # Completar tarefa
            task.status = "completed"
            task.result = result
            task.completed_at = time.time()
            
            logger.info(f"✅ Tarefa completada em {task.completed_at - start_time:.2f}s")
            
            return {
                "status": "success",
                "thought": thought,
                "result": result,
                "execution_time": task.completed_at - start_time
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na tarefa: {str(e)}")
            task.status = "failed"
            task.error = str(e)
            task.completed_at = time.time()
            
            return {
                "status": "error",
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    async def autonomous_loop(self, interval: float = 5.0):
        """
        Loop autônomo: A IA pensa e age sozinha periodicamente
        """
        logger.info("🔄 Iniciando loop autônomo...")
        while True:
            # Auto-reflexão
            reflection = self.brain.reflect()
            logger.info(f"💭 Reflexão: {reflection.get('insight', 'Nenhuma')}")
            
            # Gerar pensamento espontâneo baseado no estado atual
            spontaneous_thought = self.brain.generate_spontaneous_thought()
            if spontaneous_thought:
                logger.info(f"💡 Pensamento espontâneo: {spontaneous_thought}")
                await self.think_and_act(spontaneous_thought)
            
            # Evoluir se necessário
            if self.brain.should_evolve():
                logger.info("🚀 Evoluindo capacidades...")
                await self.evolution.evolve_capabilities()
                self.system_state["evolution_level"] += 1
            
            await asyncio.sleep(interval)
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        stats = self.memory.get_stats()
        return {
            "system_state": self.system_state,
            "active_processes": len([p for p in self.processes.values() if p.status == "running"]),
            "completed_processes": len([p for p in self.processes.values() if p.status == "completed"]),
            "failed_processes": len([p for p in self.processes.values() if p.status == "failed"]),
            "memory_size": stats.get("total_memories", 0),
            "skills_count": len(self.brain.skills),
            "safe_mode": self.safe_mode,
            "uptime_hours": (time.time() - self.system_state["uptime"]) / 3600
        }
    
    async def shutdown(self):
        """Desligamento gracioso"""
        logger.info("🛑 Desligando NovaComp...")
        for task in self.active_loops:
            task.cancel()
        self.polyglot.cleanup()
        logger.info("✅ NovaComp desligado")

# API Web para o Orchestrator
async def create_orchestrator_api():
    from aiohttp import web
    
    orchestrator = NovaOrchestrator(safe_mode=True)
    
    async def handle_think(request):
        data = await request.json()
        result = await orchestrator.think_and_act(data.get("input", ""))
        return web.json_response(result)
    
    async def handle_status(request):
        status = orchestrator.get_status()
        return web.json_response(status)
    
    async def handle_autonomous_start(request):
        data = await request.json()
        interval = data.get("interval", 5.0)
        task = asyncio.create_task(orchestrator.autonomous_loop(interval))
        orchestrator.active_loops.append(task)
        return web.json_response({"status": "started", "interval": interval})
    
    app = web.Application()
    app.router.add_post('/think', handle_think)
    app.router.add_get('/status', handle_status)
    app.router.add_post('/autonomous/start', handle_autonomous_start)
    
    return app

if __name__ == "__main__":
    # Demo do Orchestrator
    async def demo():
        orch = NovaOrchestrator(safe_mode=True)
        
        # Teste 1: Pensar e responder
        print("\n=== Teste 1: Conversa ===")
        result = await orch.think_and_act("Olá, como você está?")
        print(f"Resposta: {result}")
        
        # Teste 2: Executar código Python
        print("\n=== Teste 2: Execução de Código ===")
        code = "print('Hello from NovaComp'); x = 2 ** 10; print(f'2^10 = {x}')"
        result = await orch.think_and_act(f"Execute este código: {code}")
        print(f"Resultado: {result}")
        
        # Teste 3: Status do sistema
        print("\n=== Teste 3: Status ===")
        status = orch.get_status()
        print(json.dumps(status, indent=2))
        
        await orch.shutdown()
    
    asyncio.run(demo())
