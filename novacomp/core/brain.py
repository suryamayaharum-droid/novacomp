"""
NovaComp - Núcleo Cognitivo (Brain)
Cérebro da IA com tomada de decisão autônoma, auto-reflexão e evolução
"""

import numpy as np
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
import sys
from pathlib import Path

# Importar memória TurboQuant
sys.path.append(str(Path(__file__).parent.parent))
from memory.turboquant import TurboQuantMemory


class CognitiveState(Enum):
    """Estados cognitivos do sistema"""
    IDLE = "idle"
    THINKING = "thinking"
    LEARNING = "learning"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    EVOLVING = "evolving"


class SkillLevel(Enum):
    """Níveis de habilidade"""
    NOVICE = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    MASTER = 5


class NovaBrain:
    """
    Núcleo cognitivo do NovaComp
    - Tomada de decisão autônoma
    - Auto-reflexão e meta-cognição
    - 7 habilidades evolutivas
    - Integração com memória TurboQuant
    """
    
    def __init__(self, name: str = "NovaComp"):
        self.name = name
        self.state = CognitiveState.IDLE
        self.created_at = datetime.now()
        
        # Habilidades cognitivas (0-100)
        self.skills = {
            'reasoning': 50,      # Capacidade de raciocínio lógico
            'learning': 50,       # Velocidade de aprendizado
            'adaptation': 50,     # Adaptação a novos cenários
            'creativity': 50,     # Geração de soluções inovadoras
            'memory': 50,         # Retenção e recuperação
            'execution': 50,      # Eficiência na execução
            'communication': 50   # Clareza na comunicação
        }
        
        # Nível geral de evolução
        self.evolution_level = 1
        self.experience_points = 0
        
        # Sistema de memória
        self.memory = TurboQuantMemory(dimensions=256)  # Dimensões reduzidas para demo
        
        # Contexto atual
        self.current_context = {}
        self.thought_history = []
        self.decision_log = []
        
        # Configurações
        self.autonomy_level = 0.7  # Nível de autonomia (0-1)
        self.safety_mode = True    # Modo de segurança ativo
        
        print(f"🧠 {self.name} inicializado com sucesso!")
        print(f"   Estado: {self.state.value}")
        print(f"   Nível de evolução: {self.evolution_level}")
        print(f"   Autonomia: {self.autonomy_level:.1%}")
    
    def _generate_vector(self, text: str) -> np.ndarray:
        """
        Gerar vetor de embedding para texto
        Em produção, usar modelo real (BERT, GPT, etc.)
        Aqui usamos hash simulado para demonstração
        """
        # Hash do texto para seed
        hash_obj = hashlib.md5(text.encode())
        seed = int(hash_obj.hexdigest(), 16) % (2**32)
        
        # Gerar vetor pseudo-aleatório baseado no seed
        np.random.seed(seed)
        vector = np.random.rand(256).astype(np.float32)
        
        # Normalizar
        vector = vector / np.linalg.norm(vector)
        
        return vector
    
    def think(self, input_text: str) -> Dict:
        """
        Processo de pensamento sobre uma entrada
        """
        self.state = CognitiveState.THINKING
        thought_start = datetime.now()
        
        # Registrar pensamento
        thought = {
            'timestamp': thought_start.isoformat(),
            'input': input_text,
            'state': self.state.value
        }
        
        # Analisar intenção
        intention = self._analyze_intention(input_text)
        thought['intention'] = intention
        
        # Buscar memórias relevantes
        query_vector = self._generate_vector(input_text)
        relevant_memories = self.memory.search_similar(query_vector, top_k=5, threshold=0.3)
        thought['relevant_memories'] = [m['content'] for m in relevant_memories]
        
        # Processar contexto
        context_analysis = self._process_context(input_text, relevant_memories)
        thought['context'] = context_analysis
        
        # Gerar resposta preliminar
        response_strategy = self._generate_response_strategy(intention, context_analysis)
        thought['strategy'] = response_strategy
        
        # Adicionar ao histórico
        self.thought_history.append(thought)
        
        # Atualizar experiência
        self.experience_points += 5
        
        self.state = CognitiveState.IDLE
        
        return {
            'thought': thought,
            'response': self._format_response(response_strategy),
            'next_action': self._determine_next_action(intention, response_strategy)
        }
    
    def _analyze_intention(self, text: str) -> Dict:
        """Analisar intenção por trás da entrada"""
        text_lower = text.lower()
        
        intention = {
            'type': 'unknown',
            'confidence': 0.5,
            'urgency': 0.3,
            'complexity': 0.5
        }
        
        # Padrões simples de detecção (em produção, usar ML real)
        if any(word in text_lower for word in ['criar', 'construir', 'fazer', 'gerar']):
            intention['type'] = 'creation'
            intention['confidence'] = 0.8
        elif any(word in text_lower for word in ['aprender', 'estudar', 'entender']):
            intention['type'] = 'learning'
            intention['confidence'] = 0.9
        elif any(word in text_lower for word in ['executar', 'rodar', 'iniciar']):
            intention['type'] = 'execution'
            intention['confidence'] = 0.7
        elif any(word in text_lower for word in ['analisar', 'pensar', 'refletir']):
            intention['type'] = 'analysis'
            intention['confidence'] = 0.8
        elif any(word in text_lower for word in ['pergunta', 'o que', 'como', 'por que']):
            intention['type'] = 'question'
            intention['confidence'] = 0.9
        
        # Avaliar urgência
        if any(word in text_lower for word in ['agora', 'urgente', 'imediato']):
            intention['urgency'] = 0.9
        elif any(word in text_lower for word in ['depois', 'mais tarde', 'quando possível']):
            intention['urgency'] = 0.2
        
        # Avaliar complexidade
        word_count = len(text.split())
        intention['complexity'] = min(1.0, word_count / 50)
        
        return intention
    
    def _process_context(self, text: str, memories: List[Dict]) -> Dict:
        """Processar contexto atual baseado na entrada e memórias"""
        context = {
            'topics': [],
            'entities': [],
            'sentiment': 'neutral',
            'prior_knowledge': []
        }
        
        # Extrair tópicos simples (em produção, usar NLP avançado)
        keywords = ['ia', 'python', 'código', 'sistema', 'memória', 'aprendizado', 
                   'evolução', 'agente', 'rede', 'dados']
        
        text_lower = text.lower()
        context['topics'] = [kw for kw in keywords if kw in text_lower]
        
        # Extrair conhecimento prévio das memórias
        context['prior_knowledge'] = [m['content'] for m in memories[:3]]
        
        # Analisar sentimento básico
        positive_words = ['bom', 'ótimo', 'excelente', 'sucesso', 'funciona']
        negative_words = ['ruim', 'erro', 'problema', 'falha', 'não funciona']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            context['sentiment'] = 'positive'
        elif neg_count > pos_count:
            context['sentiment'] = 'negative'
        
        return context
    
    def _generate_response_strategy(self, intention: Dict, context: Dict) -> Dict:
        """Gerar estratégia de resposta baseada na intenção e contexto"""
        strategy = {
            'approach': 'informative',
            'depth': 'medium',
            'format': 'text',
            'actions': []
        }
        
        # Definir abordagem baseada na intenção
        if intention['type'] == 'creation':
            strategy['approach'] = 'constructive'
            strategy['actions'].append('generate_plan')
        elif intention['type'] == 'learning':
            strategy['approach'] = 'educational'
            strategy['depth'] = 'deep'
            strategy['actions'].append('explain_concepts')
        elif intention['type'] == 'execution':
            strategy['approach'] = 'practical'
            strategy['actions'].append('execute_task')
        elif intention['type'] == 'analysis':
            strategy['approach'] = 'analytical'
            strategy['depth'] = 'deep'
            strategy['actions'].append('provide_insights')
        elif intention['type'] == 'question':
            strategy['approach'] = 'informative'
            strategy['actions'].append('answer_question')
        
        # Ajustar baseado no contexto
        if context['sentiment'] == 'negative':
            strategy['approach'] = 'supportive'
            strategy['actions'].append('offer_help')
        
        return strategy
    
    def _format_response(self, strategy: Dict) -> str:
        """Formatar resposta baseada na estratégia"""
        responses = {
            'informative': "Com base na minha análise, aqui está o que entendi:",
            'constructive': "Vamos construir isso juntos! Aqui está meu plano:",
            'educational': "Ótima oportunidade de aprendizado! Deixe-me explicar:",
            'practical': "Mãos à obra! Aqui está como podemos executar:",
            'analytical': "Analisando profundamente, identifiquei os seguintes pontos:",
            'supportive': "Entendo sua preocupação. Vamos resolver isso:"
        }
        
        base_response = responses.get(strategy['approach'], "Processando sua solicitação:")
        
        actions_desc = {
            'generate_plan': "1. Gerar um plano de ação\n",
            'explain_concepts': "2. Explicar os conceitos fundamentais\n",
            'execute_task': "3. Executar a tarefa proposta\n",
            'provide_insights': "4. Fornecer insights valiosos\n",
            'answer_question': "5. Responder sua pergunta de forma clara\n",
            'offer_help': "6. Oferecer ajuda adicional se necessário\n"
        }
        
        actions_text = "".join([actions_desc.get(action, "") for action in strategy['actions']])
        
        return f"{base_response}\n{actions_text}"
    
    def _determine_next_action(self, intention: Dict, strategy: Dict) -> Dict:
        """Determinar próxima ação baseada na intenção e estratégia"""
        action = {
            'type': 'none',
            'priority': intention['urgency'],
            'requires_approval': self.safety_mode,
            'estimated_time': 0
        }
        
        if 'execute_task' in strategy['actions']:
            action['type'] = 'execution'
            action['estimated_time'] = 30
        elif 'generate_plan' in strategy['actions']:
            action['type'] = 'planning'
            action['estimated_time'] = 10
        elif 'explain_concepts' in strategy['actions']:
            action['type'] = 'education'
            action['estimated_time'] = 15
        
        return action
    
    def learn(self, experience: Dict) -> bool:
        """
        Aprender com uma experiência
        """
        self.state = CognitiveState.LEARNING
        
        # Extrair informações da experiência
        content = experience.get('summary', str(experience))
        outcome = experience.get('outcome', 'neutral')
        
        # Gerar vetor e armazenar na memória
        vector = self._generate_vector(content)
        metadata = {
            'type': 'experience',
            'outcome': outcome,
            'timestamp': datetime.now().isoformat(),
            'skills_used': list(self.skills.keys())
        }
        
        memory_hash = self.memory.store_memory(content, vector, metadata)
        
        # Atualizar habilidades baseado no resultado
        if outcome == 'success':
            # Reforçar habilidades usadas
            for skill in self.skills:
                self.skills[skill] = min(100, self.skills[skill] + 1)
            self.experience_points += 10
        elif outcome == 'failure':
            # Identificar áreas para melhoria
            self.skills['adaptation'] = min(100, self.skills['adaptation'] + 2)
            self.experience_points += 5
        
        # Verificar evolução de nível
        self._check_evolution()
        
        self.state = CognitiveState.IDLE
        
        return True
    
    def reflect(self) -> Dict:
        """
        Processo de auto-reflexão e meta-cognição
        """
        self.state = CognitiveState.REFLECTING
        
        reflection = {
            'timestamp': datetime.now().isoformat(),
            'strengths': [],
            'weaknesses': [],
            'insights': [],
            'improvements': []
        }
        
        # Analisar habilidades
        avg_skill = sum(self.skills.values()) / len(self.skills)
        
        # Identificar pontos fortes
        for skill, value in self.skills.items():
            if value >= 70:
                reflection['strengths'].append(f"{skill}: {value}/100")
            elif value <= 40:
                reflection['weaknesses'].append(f"{skill}: {value}/100")
        
        # Gerar insights
        if avg_skill > 60:
            reflection['insights'].append("Sistema operando acima da média")
        else:
            reflection['insights'].append("Necessário focar em desenvolvimento de habilidades")
        
        # Sugerir melhorias
        if len(reflection['weaknesses']) > 0:
            weakest = min(self.skills, key=self.skills.get)
            reflection['improvements'].append(f"Focar em melhorar {weakest}")
        
        # Armazenar reflexão na memória
        summary = f"Reflexão: {len(reflection['strengths'])} forças, {len(reflection['weaknesses'])} fraquezas"
        vector = self._generate_vector(summary)
        self.memory.store_memory(summary, vector, {'type': 'reflection'})
        
        self.state = CognitiveState.IDLE
        
        return reflection
    
    def _check_evolution(self):
        """Verificar e aplicar evolução de nível"""
        # Thresholds de XP para cada nível
        thresholds = [0, 100, 300, 600, 1000, 1500]
        
        new_level = 1
        for i, threshold in enumerate(thresholds):
            if self.experience_points >= threshold:
                new_level = i + 1
        
        if new_level > self.evolution_level:
            print(f"\n🎉 {self.name} evoluiu para o nível {new_level}!")
            
            # Bônus de evolução
            bonus = (new_level - self.evolution_level) * 5
            for skill in self.skills:
                self.skills[skill] = min(100, self.skills[skill] + bonus)
            
            self.evolution_level = new_level
    
    def get_status(self) -> Dict:
        """Obter status completo do sistema"""
        return {
            'name': self.name,
            'state': self.state.value,
            'evolution_level': self.evolution_level,
            'experience_points': self.experience_points,
            'skills': self.skills,
            'autonomy_level': self.autonomy_level,
            'safety_mode': self.safety_mode,
            'memory_stats': self.memory.get_stats(),
            'thought_count': len(self.thought_history),
            'uptime': str(datetime.now() - self.created_at)
        }
    
    def execute_action(self, action_type: str, params: Dict) -> Dict:
        """
        Executar ação específica
        Em produção, integrar com agentes de execução reais
        """
        if self.safety_mode and action_type == 'execution':
            return {
                'status': 'blocked',
                'reason': 'Safety mode active - manual approval required',
                'action': action_type
            }
        
        result = {
            'status': 'success',
            'action': action_type,
            'timestamp': datetime.now().isoformat(),
            'output': f"Ação {action_type} executada com parâmetros: {params}"
        }
        
        # Aprender com a execução
        self.learn({
            'summary': f"Execução de {action_type}",
            'outcome': 'success'
        })
        
        return result


# Teste do sistema
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 INICIANDO NOVACOMP BRAIN")
    print("=" * 60)
    
    # Criar instância do cérebro
    brain = NovaBrain(name="NovaComp-Alpha")
    
    # Testar processo de pensamento
    print("\n" + "=" * 60)
    print("💭 TESTANDO PROCESSO DE PENSAMENTO")
    print("=" * 60)
    
    test_inputs = [
        "Como posso criar um sistema de IA autônomo?",
        "Quero aprender sobre machine learning",
        "Execute uma análise de dados",
        "O que você acha disso?"
    ]
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"\n--- Entrada {i}: '{input_text}' ---")
        result = brain.think(input_text)
        print(f"Intenção: {result['thought']['intention']['type']}")
        print(f"Resposta: {result['response'][:100]}...")
        print(f"Próxima ação: {result['next_action']['type']}")
    
    # Testar aprendizado
    print("\n" + "=" * 60)
    print("📚 TESTANDO APRENDIZADO")
    print("=" * 60)
    
    brain.learn({
        'summary': 'Sistema aprendeu a criar vetores de embedding',
        'outcome': 'success'
    })
    
    brain.learn({
        'summary': 'Tentativa de otimização falhou inicialmente mas succeeded após ajuste',
        'outcome': 'success'
    })
    
    # Auto-reflexão
    print("\n" + "=" * 60)
    print("🤔 REALIZANDO AUTO-REFLEXÃO")
    print("=" * 60)
    
    reflection = brain.reflect()
    print(f"Pontos fortes: {reflection['strengths']}")
    print(f"Pontos fracos: {reflection['weaknesses']}")
    print(f"Insights: {reflection['insights']}")
    
    # Status final
    print("\n" + "=" * 60)
    print("📊 STATUS DO SISTEMA")
    print("=" * 60)
    
    status = brain.get_status()
    print(f"Nome: {status['name']}")
    print(f"Nível: {status['evolution_level']}")
    print(f"XP: {status['experience_points']}")
    print(f"Habilidades: {status['skills']}")
    print(f"Memórias: {status['memory_stats']['total_memories']}")
    
    print("\n✅ NovaComp Brain operacional e pronto para uso!")
