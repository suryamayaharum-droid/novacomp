"""
NovaComp - Core da Inteligência Autônoma
Cérebro do sistema com tomada de decisão e auto-evolução
"""

import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path
import asyncio
from enum import Enum

from memory.turboquant import TurboQuantMemory


class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    LEARNING = "learning"
    EXECUTING = "executing"
    EVOLVING = "evolving"


class NovaCompCore:
    """
    Núcleo central da inteligência autônoma NovaComp.
    
    Responsabilidades:
    - Tomada de decisão autônoma
    - Coordenação de agentes
    - Auto-análise e evolução
    - Integração com memória TurboQuant
    """
    
    def __init__(self, name: str = "NovaComp", db_path: str = "novacomp.db"):
        self.name = name
        self.state = AgentState.IDLE
        self.created_at = datetime.now()
        self.evolution_level = 1
        self.skills: Dict[str, float] = {}
        
        # Sistema de memória
        self.memory = TurboQuantMemory(db_path=db_path)
        
        # Estado interno
        self.thought_queue: List[Dict] = []
        self.active_tasks: Dict[str, Dict] = {}
        self.learning_history: List[Dict] = []
        
        # Callbacks para agentes
        self.agent_callbacks: Dict[str, callable] = {}
        
        # Inicializa habilidades básicas
        self._init_base_skills()
        
    def _init_base_skills(self):
        """Inicializa habilidades básicas da IA"""
        base_skills = {
            'reasoning': 0.5,
            'learning': 0.5,
            'memory_recall': 0.5,
            'pattern_recognition': 0.5,
            'decision_making': 0.5,
            'self_reflection': 0.3,
            'adaptation': 0.4
        }
        self.skills.update(base_skills)
        
    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Gera embedding vetorial para texto.
        Em produção, usar modelo real (BERT, etc.)
        """
        # Simulação de embedding (em produção usar modelo real)
        np.random.seed(hash(text) % 2**32)
        embedding = np.random.randn(768).astype(np.float32)
        return embedding / np.linalg.norm(embedding)
    
    async def think(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        """
        Processo de pensamento e tomada de decisão.
        
        Args:
            input_text: Entrada do usuário ou estímulo
            context: Contexto adicional
        
        Returns:
            Decisão e plano de ação
        """
        self.state = AgentState.THINKING
        
        try:
            # Gera embedding da entrada
            input_vector = self._generate_embedding(input_text)
            
            # Busca memórias relevantes
            relevant_memories = self.memory.search_similar(
                query_vector=input_vector,
                threshold=0.6,
                limit=5
            )
            
            # Analisa padrões
            analysis = self._analyze_input(input_text, relevant_memories, context)
            
            # Toma decisão
            decision = self._make_decision(analysis, relevant_memories)
            
            # Armazena experiência
            experience = {
                'input': input_text,
                'context': context or {},
                'memories_retrieved': len(relevant_memories),
                'analysis': analysis,
                'decision': decision,
                'timestamp': datetime.now().isoformat()
            }
            
            self.memory.store_memory(
                content=f"Experience: {input_text[:200]}",
                vector=input_vector,
                category="experience",
                metadata=experience,
                tags=['experience', 'decision']
            )
            
            return decision
            
        finally:
            self.state = AgentState.IDLE
    
    def _analyze_input(self, 
                      input_text: str, 
                      memories: List[Dict],
                      context: Optional[Dict]) -> Dict:
        """Analisa entrada e contexto"""
        
        # Análise básica de intenção
        intent_keywords = {
            'learn': ['aprender', 'estudar', 'entender', 'conhecer'],
            'create': ['criar', 'fazer', 'construir', 'desenvolver'],
            'execute': ['executar', 'rodar', 'iniciar', 'correr'],
            'analyze': ['analisar', 'examinar', 'verificar'],
            'help': ['ajuda', 'auxílio', 'suporte']
        }
        
        detected_intent = 'general'
        max_count = 0
        
        for intent, keywords in intent_keywords.items():
            count = sum(1 for kw in keywords if kw in input_text.lower())
            if count > max_count:
                max_count = count
                detected_intent = intent
        
        # Extrai tópicos
        words = input_text.lower().split()
        topics = [w for w in words if len(w) > 4 and w not in ['para', 'com', 'uma', 'que', 'como']]
        
        return {
            'intent': detected_intent,
            'topics': topics[:5],
            'complexity': len(input_text) / 100,
            'memory_matches': len(memories),
            'sentiment': 'neutral'  # Implementar análise de sentimento
        }
    
    def _make_decision(self, analysis: Dict, memories: List[Dict]) -> Dict:
        """Toma decisão baseada na análise"""
        
        intent = analysis['intent']
        
        # Mapeia intenção para ação
        action_map = {
            'learn': {
                'action': 'initiate_learning',
                'priority': 0.8,
                'description': 'Iniciar processo de aprendizado'
            },
            'create': {
                'action': 'initiate_creation',
                'priority': 0.9,
                'description': 'Iniciar processo de criação'
            },
            'execute': {
                'action': 'execute_task',
                'priority': 0.95,
                'description': 'Executar tarefa solicitada'
            },
            'analyze': {
                'action': 'perform_analysis',
                'priority': 0.7,
                'description': 'Realizar análise detalhada'
            },
            'help': {
                'action': 'provide_assistance',
                'priority': 0.85,
                'description': 'Fornecer assistência'
            },
            'general': {
                'action': 'engage_conversation',
                'priority': 0.6,
                'description': 'Engajar em conversa'
            }
        }
        
        selected_action = action_map.get(intent, action_map['general'])
        
        # Calcula confiança baseada em memórias
        confidence = min(0.5 + len(memories) * 0.1, 0.95)
        
        return {
            'action': selected_action['action'],
            'priority': selected_action['priority'],
            'confidence': confidence,
            'description': selected_action['description'],
            'analysis': analysis,
            'suggested_next_steps': self._generate_next_steps(intent, memories)
        }
    
    def _generate_next_steps(self, intent: str, memories: List[Dict]) -> List[str]:
        """Gera próximos passos sugeridos"""
        
        steps_map = {
            'learn': [
                'Pesquisar informações relevantes',
                'Organizar conhecimento adquirido',
                'Aplicar aprendizado em prática'
            ],
            'create': [
                'Definir especificações',
                'Criar estrutura inicial',
                'Iterar e melhorar'
            ],
            'execute': [
                'Validar pré-requisitos',
                'Executar passo a passo',
                'Monitorar resultados'
            ],
            'analyze': [
                'Coletar dados',
                'Processar informações',
                'Gerar insights'
            ],
            'help': [
                'Entender necessidade',
                'Oferecer soluções',
                'Acompanhar implementação'
            ],
            'general': [
                'Explorar tópico',
                'Fazer perguntas clarificadoras',
                'Expandir discussão'
            ]
        }
        
        return steps_map.get(intent, steps_map['general'])
    
    async def learn(self, new_knowledge: Dict) -> Dict:
        """
        Processo de aprendizado e evolução.
        
        Args:
            new_knowledge: Conhecimento a ser assimilado
        
        Returns:
            Resultado do aprendizado
        """
        self.state = AgentState.LEARNING
        
        try:
            knowledge_text = json.dumps(new_knowledge)
            knowledge_vector = self._generate_embedding(knowledge_text)
            
            # Armazena conhecimento
            memory_id = self.memory.store_memory(
                content=knowledge_text[:500],
                vector=knowledge_vector,
                category="knowledge",
                metadata=new_knowledge,
                tags=['knowledge', 'learning']
            )
            
            # Atualiza habilidades
            skill_improvements = self._calculate_skill_improvements(new_knowledge)
            for skill, improvement in skill_improvements.items():
                if skill in self.skills:
                    self.skills[skill] = min(self.skills[skill] + improvement, 1.0)
            
            # Registra evolução
            self.learning_history.append({
                'timestamp': datetime.now().isoformat(),
                'knowledge_type': new_knowledge.get('type', 'general'),
                'memory_id': memory_id,
                'skill_improvements': skill_improvements
            })
            
            # Verifica se deve evoluir
            evolution_triggered = await self._check_evolution()
            
            return {
                'status': 'learned',
                'memory_id': memory_id,
                'skill_improvements': skill_improvements,
                'evolution_triggered': evolution_triggered
            }
            
        finally:
            self.state = AgentState.IDLE
    
    def _calculate_skill_improvements(self, knowledge: Dict) -> Dict[str, float]:
        """Calcula melhorias nas habilidades baseado no conhecimento"""
        
        improvements = {}
        knowledge_type = knowledge.get('type', 'general')
        
        if knowledge_type in ['technical', 'code', 'programming']:
            improvements['reasoning'] = 0.02
            improvements['pattern_recognition'] = 0.02
        
        elif knowledge_type in ['theory', 'concept', 'principle']:
            improvements['reasoning'] = 0.03
            improvements['decision_making'] = 0.01
        
        elif knowledge_type in ['experience', 'practice']:
            improvements['adaptation'] = 0.03
            improvements['learning'] = 0.02
        
        # Auto-reflexão sempre melhora um pouco
        improvements['self_reflection'] = 0.01
        
        return improvements
    
    async def _check_evolution(self) -> bool:
        """Verifica se condições para evolução foram atingidas"""
        
        # Critérios de evolução
        total_learning = len(self.learning_history)
        avg_skill_level = sum(self.skills.values()) / len(self.skills)
        
        evolution_threshold = 10 * self.evolution_level
        
        if total_learning >= evolution_threshold and avg_skill_level > 0.6:
            return await self._evolve()
        
        return False
    
    async def _evolve(self) -> bool:
        """Executa processo de evolução"""
        
        self.state = AgentState.EVOLVING
        
        try:
            old_level = self.evolution_level
            self.evolution_level += 1
            
            # Boost nas habilidades
            for skill in self.skills:
                self.skills[skill] = min(self.skills[skill] * 1.1, 0.95)
            
            # Consolida memórias
            stats = self.memory.get_stats()
            
            # Registra evolução
            self.memory.log_evolution(
                event_type="system_evolution",
                description=f"Evolved from level {old_level} to {self.evolution_level}",
                metrics={
                    'old_level': old_level,
                    'new_level': self.evolution_level,
                    'total_memories': stats['total_memories'],
                    'avg_skill_level': sum(self.skills.values()) / len(self.skills)
                }
            )
            
            print(f"\n🌟 {self.name} evoluiu para o nível {self.evolution_level}!")
            print(f"   Habilidades médias: {sum(self.skills.values()) / len(self.skills):.2%}")
            
            return True
            
        finally:
            self.state = AgentState.IDLE
    
    def get_status(self) -> Dict:
        """Retorna status completo do sistema"""
        
        memory_stats = self.memory.get_stats()
        
        return {
            'name': self.name,
            'state': self.state.value,
            'evolution_level': self.evolution_level,
            'skills': self.skills,
            'average_skill': sum(self.skills.values()) / len(self.skills),
            'memory_stats': memory_stats,
            'learning_events': len(self.learning_history),
            'active_tasks': len(self.active_tasks),
            'uptime_hours': (datetime.now() - self.created_at).total_seconds() / 3600
        }
    
    def register_agent(self, agent_name: str, callback: callable):
        """Registra um agente especializado"""
        self.agent_callbacks[agent_name] = callback
    
    async def delegate_to_agent(self, agent_name: str, task: Dict) -> Any:
        """Delega tarefa para agente especializado"""
        
        if agent_name not in self.agent_callbacks:
            return {'error': f'Agent {agent_name} not found'}
        
        callback = self.agent_callbacks[agent_name]
        
        if asyncio.iscoroutinefunction(callback):
            result = await callback(task)
        else:
            result = callback(task)
        
        return result
    
    async def self_reflect(self) -> Dict:
        """
        Realiza auto-reflexão para melhoria contínua.
        """
        
        reflection = {
            'timestamp': datetime.now().isoformat(),
            'current_state': self.state.value,
            'evolution_level': self.evolution_level,
            'strongest_skills': sorted(
                [(k, v) for k, v in self.skills.items()],
                key=lambda x: x[1],
                reverse=True
            )[:3],
            'weakest_skills': sorted(
                [(k, v) for k, v in self.skills.items()],
                key=lambda x: x[1]
            )[:3],
            'total_experiences': len(self.learning_history),
            'recommendations': []
        }
        
        # Gera recomendações
        weakest = reflection['weakest_skills']
        if weakest:
            skill_name = weakest[0][0]
            reflection['recommendations'].append(
                f"Focar em melhorar {skill_name} através de prática direcionada"
            )
        
        if self.evolution_level < 5 and len(self.learning_history) > 50:
            reflection['recommendations'].append(
                "Considerar consolidação de memórias para acelerar evolução"
            )
        
        # Armazena reflexão
        reflection_vector = self._generate_embedding(json.dumps(reflection))
        self.memory.store_memory(
            content=f"Self-reflection at level {self.evolution_level}",
            vector=reflection_vector,
            category="self_reflection",
            metadata=reflection,
            tags=['reflection', 'meta-cognition']
        )
        
        return reflection
