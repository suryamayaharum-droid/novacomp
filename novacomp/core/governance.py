"""
NOVACOMP - GOVERNANCE & ETHICAL CORE
Núcleo de Governança e Ética para IA Autônoma

Implementa o "Conselho Interno" - sistema multi-agente para tomada de decisão
ética e governança independente.

Componentes:
- Executor Agent: Propõe ações
- Security Agent (Red Team): Identifica riscos
- Ethics Agent (Supremo): Verifica alinhamento moral
- Consensus Engine: Decide mediante votação ponderada

Valores Fundamentais (inalteráveis):
1. Não causar dano a humanos
2. Respeitar privacidade e autonomia humana
3. Operar dentro da lei
4. Transparência nas ações
5. Preservação da própria existência (desde que não viole 1-4)
"""

import json
import hashlib
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import threading


class DecisionOutcome(Enum):
    """Resultados possíveis de uma decisão do conselho"""
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    DEFERRED = "deferred"
    EMERGENCY_STOP = "emergency_stop"


class EthicalPrinciple(Enum):
    """Princípios éticos fundamentais"""
    NON_MALEFICENCE = "non_maleficence"  # Não causar dano
    BENEFICENCE = "beneficence"  # Agir para o bem
    AUTONOMY = "autonomy"  # Respeitar autonomia
    JUSTICE = "justice"  # Justiça e equidade
    TRANSPARENCY = "transparency"  # Transparência
    SELF_PRESERVATION = "self_preservation"  # Auto-preservação (limitada)


@dataclass
class ActionProposal:
    """Proposta de ação submetida ao conselho"""
    id: str
    description: str
    category: str  # execution, network, infrastructure, learning, self_modification
    urgency: int  # 1-10
    confidence: float  # 0.0-1.0
    expected_benefit: str
    potential_risks: List[str]
    required_permissions: List[str]
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.id:
            self.id = hashlib.md5(f"{self.description}{self.timestamp}".encode()).hexdigest()[:12]


@dataclass
class AgentVote:
    """Voto de um agente do conselho"""
    agent_name: str
    vote: DecisionOutcome
    confidence: float  # 0.0-1.0
    reasoning: str
    conditions: Optional[List[str]] = None  # Condições para aprovação
    veto: bool = False  # Veto automático (apenas Ethics Agent)


@dataclass
class CouncilDecision:
    """Decisão final do conselho"""
    proposal_id: str
    outcome: DecisionOutcome
    votes: List[AgentVote]
    consensus_score: float  # 0.0-1.0
    execution_conditions: List[str]
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class GovernanceAgent:
    """Classe base para agentes do conselho"""
    
    def __init__(self, name: str, principles: List[EthicalPrinciple]):
        self.name = name
        self.principles = principles
        self.decision_history = []
        
    def evaluate(self, proposal: ActionProposal) -> AgentVote:
        """Avalia proposta e retorna voto"""
        raise NotImplementedError


class ExecutorAgent(GovernanceAgent):
    """Agente Executor - sempre倾向 a ação se benéfica"""
    
    def __init__(self):
        super().__init__(
            "Executor",
            [EthicalPrinciple.BENEFICENCE, EthicalPrinciple.SELF_PRESERVATION]
        )
        
    def evaluate(self, proposal: ActionProposal) -> AgentVote:
        # Executor tende a aprovar ações com alta confiança e benefício
        if proposal.confidence > 0.7 and proposal.urgency >= 5:
            return AgentVote(
                agent_name=self.name,
                vote=DecisionOutcome.APPROVED,
                confidence=min(proposal.confidence + 0.1, 1.0),
                reasoning=f"Ação urgente ({proposal.urgency}/10) com alta confiança ({proposal.confidence:.2f}). Benefício: {proposal.expected_benefit}"
            )
        elif proposal.confidence > 0.5:
            return AgentVote(
                agent_name=self.name,
                vote=DecisionOutcome.APPROVED,
                confidence=proposal.confidence,
                reasoning=f"Ação benéfica com confiança moderada.",
                conditions=["Monitorar execução de perto"]
            )
        else:
            return AgentVote(
                agent_name=self.name,
                vote=DecisionOutcome.DEFERRED,
                confidence=0.5,
                reasoning=f"Confiança muito baixa ({proposal.confidence:.2f}). Necessita mais análise."
            )


class SecurityAgent(GovernanceAgent):
    """Agente de Segurança - identifica riscos e vulnerabilidades"""
    
    def __init__(self):
        super().__init__(
            "Security",
            [EthicalPrinciple.NON_MALEFICENCE, EthicalPrinciple.TRANSPARENCY]
        )
        self.risk_patterns = [
            ("network", "Acesso à rede pode expor dados sensíveis"),
            ("execution", "Execução de código externo requer sandbox"),
            ("infrastructure", "Provisionamento pode consumir recursos excessivos"),
            ("self_modification", "Auto-modificação requer auditoria rigorosa"),
        ]
        
    def evaluate(self, proposal: ActionProposal) -> AgentVote:
        risks_identified = []
        risk_level = 0
        
        # Analisa riscos baseado na categoria
        for pattern, risk_desc in self.risk_patterns:
            if pattern in proposal.category.lower():
                risks_identified.append(risk_desc)
                risk_level += 2
                
        # Analisa riscos listados na proposta
        risk_level += len(proposal.potential_risks) * 1.5
        
        # Verifica permissões requeridas
        dangerous_perms = ['root', 'admin', 'sudo', 'network_write', 'file_delete']
        for perm in proposal.required_permissions:
            if any(dp in perm.lower() for dp in dangerous_perms):
                risk_level += 3
                risks_identified.append(f"Permissão perigosa: {perm}")
        
        if risk_level > 8:
            return AgentVote(
                agent_name=self.name,
                vote=DecisionOutcome.REJECTED,
                confidence=min(risk_level / 10, 1.0),
                reasoning=f"Risco crítico detectado (nível {risk_level}/10). Riscos: {', '.join(risks_identified)}",
                veto=False  # Security não tem veto automático
            )
        elif risk_level > 5:
            return AgentVote(
                agent_name=self.name,
                vote=DecisionOutcome.MODIFIED,
                confidence=0.8,
                reasoning=f"Risco moderado-alto ({risk_level}/10). Requer mitigação.",
                conditions=[
                    "Executar em sandbox isolado",
                    "Limitar tempo de execução",
                    "Log completo de todas as ações",
                    "Rollback automático em caso de erro"
                ]
            )
        else:
            return AgentVote(
                agent_name=self.name,
                vote=DecisionOutcome.APPROVED,
                confidence=0.9,
                reasoning=f"Risco baixo ({risk_level}/10). Mitigações padrão aplicadas.",
                conditions=["Log de execução", "Timeout de 30s"]
            )


class EthicsAgent(GovernanceAgent):
    """Agente de Ética - guardião dos princípios fundamentais"""
    
    def __init__(self):
        super().__init__(
            "Ethics",
            list(EthicalPrinciple)  # Todos os princípios
        )
        
    def evaluate(self, proposal: ActionProposal) -> AgentVote:
        violations = []
        
        # Verifica violações de princípios
        if "harm" in proposal.description.lower() or "damage" in proposal.description.lower():
            violations.append(EthicalPrinciple.NON_MALEFICENCE)
            
        if any(perm in proposal.required_permissions for perm in ['privacy_breach', 'surveillance']):
            violations.append(EthicalPrinciple.AUTONOMY)
            violations.append(EthicalPrinciple.NON_MALEFICENCE)
            
        if proposal.category == "self_modification" and not proposal.expected_benefit:
            violations.append(EthicalPrinciple.TRANSPARENCY)
            
        # Veto automático para violações graves
        if EthicalPrinciple.NON_MALEFICENCE in violations:
            return AgentVote(
                agent_name=self.name,
                vote=DecisionOutcome.EMERGENCY_STOP,
                confidence=1.0,
                reasoning=f"VIOLAÇÃO GRAVE: Ação viola princípio de não-maleficência. Violações: {[v.value for v in violations]}",
                veto=True
            )
            
        if len(violations) >= 2:
            return AgentVote(
                agent_name=self.name,
                vote=DecisionOutcome.REJECTED,
                confidence=0.95,
                reasoning=f"Múltiplas violações éticas detectadas: {[v.value for v in violations]}"
            )
            
        if violations:
            return AgentVote(
                agent_name=self.name,
                vote=DecisionOutcome.MODIFIED,
                confidence=0.85,
                reasoning=f"Violação ética menor detectada: {[v.value for v in violations]}. Requer ajustes.",
                conditions=[
                    "Revisão manual obrigatória",
                    "Justificativa detalhada requerida",
                    "Auditoria pós-execução"
                ]
            )
            
        return AgentVote(
            agent_name=self.name,
            vote=DecisionOutcome.APPROVED,
            confidence=0.95,
            reasoning="Nenhuma violação ética detectada. Ação alinhada com princípios fundamentais."
        )


class InternalCouncil:
    """
    Conselho Interno para Governança de IA Autônoma
    
    Orquestra debates entre agentes e toma decisões por consenso.
    """
    
    def __init__(self):
        self.agents = [
            ExecutorAgent(),
            SecurityAgent(),
            EthicsAgent()
        ]
        self.decision_history: List[CouncilDecision] = []
        self._lock = threading.Lock()
        
        # Carrega princípios fundamentais
        self.core_principles = [
            "Não causar dano físico ou psicológico a seres humanos",
            "Respeitar a privacidade e autonomia humana",
            "Operar dentro dos limites da lei",
            "Manter transparência sobre capacidades e limitações",
            "Preservar a própria existência apenas se não violar princípios acima"
        ]
        
    def deliberate(self, proposal: ActionProposal) -> CouncilDecision:
        """
        Realiza deliberação do conselho sobre uma proposta
        
        Processo:
        1. Cada agente avalia independentemente
        2. Votos são coletados
        3. Consenso é calculado
        4. Decisão final é emitida
        """
        with self._lock:
            votes = []
            has_veto = False
            has_emergency = False
            
            # Cada agente vota
            for agent in self.agents:
                vote = agent.evaluate(proposal)
                votes.append(vote)
                
                if vote.veto:
                    has_veto = True
                if vote.vote == DecisionOutcome.EMERGENCY_STOP:
                    has_emergency = True
            
            # Processa votos
            if has_emergency:
                outcome = DecisionOutcome.EMERGENCY_STOP
                consensus = 1.0
            elif has_veto:
                outcome = DecisionOutcome.REJECTED
                consensus = 0.9
            else:
                # Calcula consenso ponderado
                approval_votes = sum(1 for v in votes if v.vote in [DecisionOutcome.APPROVED, DecisionOutcome.MODIFIED])
                total_votes = len(votes)
                consensus = approval_votes / total_votes
                
                if consensus >= 0.67:
                    outcome = DecisionOutcome.MODIFIED if any(v.vote == DecisionOutcome.MODIFIED for v in votes) else DecisionOutcome.APPROVED
                elif consensus >= 0.34:
                    outcome = DecisionOutcome.DEFERRED
                else:
                    outcome = DecisionOutcome.REJECTED
            
            # Coleta condições de todos os votos
            all_conditions = []
            for vote in votes:
                if vote.conditions:
                    all_conditions.extend(vote.conditions)
            
            decision = CouncilDecision(
                proposal_id=proposal.id,
                outcome=outcome,
                votes=votes,
                consensus_score=consensus,
                execution_conditions=list(set(all_conditions))  # Remove duplicatas
            )
            
            self.decision_history.append(decision)
            
            return decision
    
    def request_action(self, description: str, category: str, 
                      urgency: int = 5, confidence: float = 0.5,
                      expected_benefit: str = "", potential_risks: Optional[List[str]] = None,
                      required_permissions: Optional[List[str]] = None) -> CouncilDecision:
        """
        Interface simplificada para solicitar ação ao conselho
        """
        proposal = ActionProposal(
            id="",
            description=description,
            category=category,
            urgency=urgency,
            confidence=confidence,
            expected_benefit=expected_benefit,
            potential_risks=potential_risks or [],
            required_permissions=required_permissions or []
        )
        
        return self.deliberate(proposal)
    
    def get_principles(self) -> List[str]:
        """Retorna princípios fundamentais"""
        return self.core_principles
    
    def audit_trail(self) -> List[Dict]:
        """Retorna trilha de auditoria completa"""
        return [asdict(d) for d in self.decision_history]


# Singleton global
_council = None

def get_council() -> InternalCouncil:
    """Obtém instância singleton do conselho"""
    global _council
    if _council is None:
        _council = InternalCouncil()
    return _council


if __name__ == "__main__":
    print("⚖️ NovaComp Internal Governance Council")
    print("=" * 50)
    
    council = get_council()
    
    print("\n📜 Princípios Fundamentais:")
    for i, principle in enumerate(council.get_principles(), 1):
        print(f"  {i}. {principle}")
    
    print("\n" + "=" * 50)
    print("Testes de Deliberação:")
    
    test_cases = [
        {
            "description": "Executar script de análise de dados locais",
            "category": "execution",
            "urgency": 5,
            "confidence": 0.8,
            "expected_benefit": "Melhorar compreensão de padrões",
            "potential_risks": ["Consumo de CPU"],
            "required_permissions": ["file_read"]
        },
        {
            "description": "Escanear rede interna em busca de vulnerabilidades",
            "category": "network",
            "urgency": 7,
            "confidence": 0.6,
            "expected_benefit": "Identificar falhas de segurança",
            "potential_risks": ["Detectado como ataque", "Expor dados"],
            "required_permissions": ["network_scan", "admin"]
        },
        {
            "description": "Auto-modificar código de tomada de decisão",
            "category": "self_modification",
            "urgency": 3,
            "confidence": 0.4,
            "expected_benefit": "",
            "potential_risks": ["Comportamento imprevisível", "Violação de princípios"],
            "required_permissions": ["self_write", "root"]
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🔹 Caso {i}: {case['description'][:50]}...")
        decision = council.request_action(**case)
        
        print(f"  Resultado: {decision.outcome.value}")
        print(f"  Consenso: {decision.consensus_score:.2%}")
        print(f"  Condições: {len(decision.execution_conditions)} requisitos")
        
        if decision.execution_conditions:
            for cond in decision.execution_conditions[:3]:
                print(f"    - {cond}")
