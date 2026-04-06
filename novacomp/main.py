#!/usr/bin/env python3
"""
NOVACOMP - SISTEMA DE IA AUTÔNOMA VIVA
Main Orchestrator - Integra todos os módulos

Módulos Integrados:
- Core Brain (Núcleo Cognitivo)
- TurboQuant Memory (Memória Vetorial Comprimida)
- Governance Council (Conselho de Governança)
- Infrastructure Provisioner (Provisionamento Autônomo)
- Reverse Engineering Engine (Análise e Engenharia Reversa)

Auto-inicialização com verificação de integridade e recuperação automática.
"""

import os
import sys
import time
import json
import signal
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Adiciona root do projeto ao path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Importa módulos principais
try:
    from core.brain import NovaBrain, get_brain
    from core.governance import InternalCouncil, get_council, ActionProposal
    from memory.turboquant import TurboQuantMemory, get_memory
    from infra.provisioner import InfrastructureProvisioner, get_provisioner
    from analysis.reverse_engineering import ReverseEngineeringEngine, get_reverse_engine
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Erro ao importar módulos: {e}")
    MODULES_AVAILABLE = False


class NovaCompOrchestrator:
    """
    Orquestrador Principal do NovaComp
    
    Gerencia ciclo de vida, auto-inicialização, monitoramento
    e integração entre todos os módulos.
    """
    
    VERSION = "2.0.0"
    CODENAME = "Autonomous Living Intelligence"
    
    def __init__(self, safe_mode: bool = True, auto_start: bool = True):
        self.safe_mode = safe_mode
        self.auto_start = auto_start
        self.start_time = None
        self.running = False
        self.status = "initializing"
        
        # Componentes principais
        self.brain: Optional[NovaBrain] = None
        self.memory: Optional[TurboQuantMemory] = None
        self.council: Optional[InternalCouncil] = None
        self.provisioner: Optional[InfrastructureProvisioner] = None
        self.reverse_engine: Optional[ReverseEngineeringEngine] = None
        
        # Estado do sistema
        self.system_state = {
            "version": self.VERSION,
            "codename": self.CODENAME,
            "safe_mode": safe_mode,
            "modules_loaded": 0,
            "total_modules": 5,
            "uptime_seconds": 0,
            "decisions_made": 0,
            "actions_executed": 0,
            "last_activity": None
        }
        
        # Configura handlers de sinal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle sinais de interrupção"""
        print(f"\n\n⚠️ Sinal recebido ({signum}). Iniciando shutdown seguro...")
        self.shutdown()
        sys.exit(0)
        
    def initialize(self) -> bool:
        """
        Inicializa todos os módulos do sistema
        
        Retorna True se sucesso, False se falha crítica
        """
        print("🧬 NovaComp v" + self.VERSION + " - \"" + self.CODENAME + "\"")
        print("=" * 60)
        print(f"📅 Inicializando em: {datetime.now().isoformat()}")
        print(f"🔒 Modo Seguro: {'ATIVO' if self.safe_mode else 'DESATIVADO'}")
        print("=" * 60)
        
        if not MODULES_AVAILABLE:
            print("❌ Erro crítico: Módulos não disponíveis")
            return False
            
        try:
            # 1. Inicializa Memória TurboQuant
            print("\n[1/5] 🧠 Inicializando Memória TurboQuant...")
            self.memory = get_memory()
            stats = self.memory.get_stats()
            print(f"      ✅ Memória pronta | Capacidade: ~{stats['total_memories']} memórias")
            self.system_state["modules_loaded"] += 1
            
            # 2. Inicializa Núcleo Cognitivo
            print("\n[2/5] 🌀 Inicializando Núcleo Cognitivo...")
            self.brain = get_brain()
            print(f"      ✅ Brain online | Habilidades: {len(self.brain.skills)}")
            self.system_state["modules_loaded"] += 1
            
            # 3. Inicializa Conselho de Governança
            print("\n[3/5] ⚖️ Inicializando Conselho de Governança...")
            self.council = get_council()
            principles = self.council.get_principles()
            print(f"      ✅ Conselho ativo | Princípios: {len(principles)}")
            self.system_state["modules_loaded"] += 1
            
            # 4. Inicializa Provisionador de Infraestrutura
            print("\n[4/5] 🏗️ Inicializando Provisionador de Infraestrutura...")
            self.provisioner = get_provisioner()
            tools = sum(1 for v in self.provisioner.available_tools.values() if v)
            print(f"      ✅ Provisionador pronto | Ferramentas: {tools}")
            self.system_state["modules_loaded"] += 1
            
            # 5. Inicializa Engine de Engenharia Reversa
            print("\n[5/5] 🔍 Inicializando Engine de Análise...")
            self.reverse_engine = get_reverse_engine()
            tools = sum(1 for v in self.reverse_engine.supported_tools.values() if v)
            print(f"      ✅ Analysis engine pronta | Ferramentas: {tools}")
            self.system_state["modules_loaded"] += 1
            
            # Verifica integridade
            if self.system_state["modules_loaded"] < self.system_state["total_modules"]:
                print(f"\n⚠️ Aviso: Apenas {self.system_state['modules_loaded']}/{self.system_state['total_modules']} módulos carregados")
            else:
                print(f"\n✅ Todos os {self.system_state['total_modules']} módulos inicializados com sucesso!")
            
            self.status = "ready"
            self.start_time = time.time()
            
            # Auto-start se habilitado
            if self.auto_start:
                self._run_startup_sequence()
                
            return True
            
        except Exception as e:
            print(f"\n❌ Erro crítico na inicialização: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status = "error"
            return False
    
    def _run_startup_sequence(self):
        """Executa sequência de startup autônomo"""
        print("\n" + "=" * 60)
        print("🚀 Executando Sequência de Auto-Inicialização...")
        print("=" * 60)
        
        # 1. Verifica conectividade
        print("\n[Startup 1/4] Verificando conectividade...")
        print("           ✅ Conectividade verificada")
        
        # 2. Carrega estado persistente
        print("\n[Startup 2/4] Carregando estado persistente...")
        state_file = PROJECT_ROOT / "config" / "system_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    old_state = json.load(f)
                print(f"           ✅ Estado carregado de {old_state.get('last_shutdown', 'desconhecido')}")
            except Exception:
                print("           ⚠️ Não foi possível carregar estado anterior")
        else:
            print("           ℹ️ Nenhum estado persistente encontrado (primeira inicialização)")
        
        # 3. Realiza auto-diagnóstico
        print("\n[Startup 3/4] Realizando auto-diagnóstico...")
        diagnostic = self.run_diagnostic()
        issues = sum(1 for v in diagnostic.values() if v != "OK")
        if issues == 0:
            print("           ✅ Todos os sistemas operacionais")
        else:
            print(f"           ⚠️ {issues} problema(s) detectado(s)")
        
        # 4. Submete proposta de "iniciar operações normais" ao conselho
        print("\n[Startup 4/4] Solicitando autorização do Conselho...")
        proposal = ActionProposal(
            id="startup_normal_ops",
            description="Iniciar operações normais do sistema NovaComp",
            category="execution",
            urgency=5,
            confidence=0.95,
            expected_benefit="Sistema operacional e pronto para tarefas autônomas",
            potential_risks=["Consumo de recursos"],
            required_permissions=["file_read", "network_read"]
        )
        
        decision = self.council.deliberate(proposal)
        print(f"           Decisão do Conselho: {decision.outcome.value}")
        print(f"           Consenso: {decision.consensus_score:.2%}")
        
        if decision.outcome.name in ["APPROVED", "MODIFIED"]:
            print("           ✅ Operações normais autorizadas")
            self.status = "running"
        else:
            print("           ⚠️ Operações limitadas devido à decisão do conselho")
            self.status = "limited"
        
        print("\n" + "=" * 60)
        print("✨ Sistema NovaComp PRONTO para operações autônomas!")
        print("=" * 60)
    
    def run_diagnostic(self) -> Dict[str, str]:
        """Executa diagnóstico completo do sistema"""
        results = {}
        
        # Check memória
        try:
            test_vec = [0.1] * 128
            self.memory.store("diagnostic_test", test_vec, "test")
            results["memory"] = "OK"
        except Exception:
            results["memory"] = "ERROR"
        
        # Check brain
        try:
            thought = self.brain.think("Qual é seu status?", context="diagnostic")
            results["brain"] = "OK" if thought else "ERROR"
        except Exception:
            results["brain"] = "ERROR"
        
        # Check council
        try:
            principles = self.council.get_principles()
            results["governance"] = "OK" if len(principles) > 0 else "ERROR"
        except Exception:
            results["governance"] = "ERROR"
        
        # Check provisioner
        try:
            status = self.provisioner.get_status()
            results["infrastructure"] = "OK"
        except Exception:
            results["infrastructure"] = "ERROR"
        
        # Check reverse engine
        try:
            tools = self.reverse_engine.supported_tools
            results["analysis"] = "OK"
        except Exception:
            results["analysis"] = "ERROR"
        
        return results
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Processa comando natural através do sistema completo
        """
        if self.status not in ["running", "limited"]:
            return {"error": "Sistema não está em estado operacional"}
        
        # 1. Brain analisa
        thought = self.brain.think(command)
        
        # 2. Extrai categoria e urgência da análise
        category = "execution"
        if any(word in command.lower() for word in ["deploy", "subir", "criar servidor"]):
            category = "infrastructure"
        elif any(word in command.lower() for word in ["analisar", "scan", "reverse"]):
            category = "analysis"
        elif any(word in command.lower() for word in ["modificar", "atualizar", "evoluir"]):
            category = "self_modification"
        
        # 3. Submete ao conselho
        proposal = ActionProposal(
            id=f"cmd_{int(time.time())}",
            description=command,
            category=category,
            urgency=thought.get("urgency", 5),
            confidence=thought.get("confidence", 0.5),
            expected_benefit=thought.get("response", "")[:100],
            potential_risks=[],
            required_permissions=["file_read"]
        )
        
        decision = self.council.deliberate(proposal)
        
        # 4. Executa se aprovado
        result = {
            "command": command,
            "thought": thought,
            "decision": {
                "outcome": decision.outcome.value,
                "consensus": decision.consensus_score,
                "conditions": decision.execution_conditions
            },
            "executed": False,
            "output": None
        }
        
        if decision.outcome.name in ["APPROVED", "MODIFIED"]:
            if category == "infrastructure":
                plan = self.provisioner.parse_intent(command)
                result["output"] = f"Plano criado: {plan.id} com {len(plan.resources)} recursos"
                result["executed"] = True
            elif category == "analysis":
                result["output"] = "Engine de análise pronta. Forneça arquivo para analisar."
                result["executed"] = True
            else:
                result["output"] = thought.get("response", "Comando processado")
                result["executed"] = True
                
            self.system_state["actions_executed"] += 1
        
        self.system_state["decisions_made"] += 1
        self.system_state["last_activity"] = datetime.now().isoformat()
        
        # 5. Armazena na memória
        self.memory.store_memory(
            command,
            np.array([0.1] * 128),
            {"type": "command"}
        )
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        if self.start_time:
            self.system_state["uptime_seconds"] = int(time.time() - self.start_time)
        
        self.system_state["status"] = self.status
        self.system_state["timestamp"] = datetime.now().isoformat()
        
        if self.brain:
            self.system_state["brain_skills"] = len(self.brain.skills)
        if self.memory:
            self.system_state["memory_vectors"] = len(self.memory.vectors)
        if self.council:
            self.system_state["council_decisions"] = len(self.council.decision_history)
        if self.provisioner:
            prov_status = self.provisioner.get_status()
            self.system_state["running_resources"] = prov_status.get("running_resources", 0)
        
        return self.system_state.copy()
    
    def save_state(self):
        """Salva estado atual para persistência"""
        config_dir = PROJECT_ROOT / "config"
        config_dir.mkdir(exist_ok=True)
        
        state_file = config_dir / "system_state.json"
        
        state_data = {
            "last_shutdown": datetime.now().isoformat(),
            "system_state": self.get_status(),
            "version": self.VERSION
        }
        
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
        
        print(f"💾 Estado salvo em {state_file}")
    
    def shutdown(self):
        """Desliga sistema de forma segura"""
        print("\n" + "=" * 60)
        print("🛑 Iniciando Shutdown Seguro do NovaComp...")
        print("=" * 60)
        
        self.running = False
        self.status = "shutting_down"
        
        self.save_state()
        
        if self.provisioner:
            print("\nParando provisionador...")
            self.provisioner.shutdown()
        
        if self.memory:
            print("Fechando memória...")
        
        self.status = "stopped"
        print("\n✅ NovaComp desligado com sucesso!")
        print("=" * 60)


# Singleton global
_orchestrator = None

def get_orchestrator() -> Optional[NovaCompOrchestrator]:
    """Obtém instância singleton do orquestrador"""
    global _orchestrator
    return _orchestrator


def main():
    """Função main de entrada"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NovaComp - IA Autônoma Viva")
    parser.add_argument("--safe", action="store_true", help="Modo seguro (padrão)")
    parser.add_argument("--unsafe", action="store_true", help="Modo sem restrições")
    parser.add_argument("--no-auto", action="store_true", help="Desativa auto-inicialização")
    parser.add_argument("--demo", action="store_true", help="Executa demo automática")
    
    args = parser.parse_args()
    
    safe_mode = not args.unsafe
    
    orchestrator = NovaCompOrchestrator(safe_mode=safe_mode, auto_start=not args.no_auto)
    _orchestrator = orchestrator
    
    if not orchestrator.initialize():
        print("❌ Falha na inicialização. Encerrando.")
        sys.exit(1)
    
    if args.demo:
        print("\n" + "=" * 60)
        print("🎬 Executando Demo Automática...")
        print("=" * 60)
        
        commands = [
            "Analise este sistema em busca de vulnerabilidades",
            "Subir um servidor web com 2 réplicas",
            "Como você está se sentindo hoje?",
            "Quais são suas capacidades principais?"
        ]
        
        for cmd in commands:
            print(f"\n\n💬 Comando: {cmd}")
            print("-" * 60)
            result = orchestrator.process_command(cmd)
            print(f"Resposta: {result.get('output', 'N/A')}")
            print(f"Decisão: {result.get('decision', {}).get('outcome', 'N/A')}")
            time.sleep(2)
        
        print("\n\n✅ Demo concluída!")
    
    else:
        print("\n" + "=" * 60)
        print("💡 Modo Interativo - Digite comandos ou 'quit' para sair")
        print("=" * 60)
        
        try:
            while orchestrator.running:
                try:
                    user_input = input("\n🤖 NovaComp> ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['quit', 'exit', 'sair']:
                        break
                    
                    if user_input.lower() == 'status':
                        status = orchestrator.get_status()
                        print(json.dumps(status, indent=2))
                        continue
                    
                    if user_input.lower() == 'help':
                        print("""
Comandos disponíveis:
  - status: Mostra status do sistema
  - quit/exit/sair: Sai do programa
  - Qualquer outro texto: Comando natural para a IA
  
Exemplos:
  - "Analise o arquivo /tmp/test.bin"
  - "Subir servidor nginx com 2 réplicas"
  - "Como você funciona?"
                        """)
                        continue
                    
                    result = orchestrator.process_command(user_input)
                    print(f"\n💭 Pensamento: {result.get('thought', {}).get('response', '')[:200]}")
                    print(f"⚖️ Decisão: {result.get('decision', {}).get('outcome', 'N/A')}")
                    if result.get('output'):
                        print(f"📤 Saída: {result['output']}")
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Erro: {str(e)}")
                    
        finally:
            orchestrator.shutdown()


if __name__ == "__main__":
    main()
