# NovaComp - Inteligência Autônoma Viva

## 🧠 Arquitetura da IA Autônoma

NovaComp é uma inteligência artificial autônoma com:
- **Memória Vetorial Comprimida (TurboQuant)**: Armazenamento eficiente de embeddings sem descompressão completa para buscas
- **Auto-Evolução**: Capacidade de aprender e melhorar continuamente através de experiências
- **Renderização em Tempo Real**: Dashboard web para monitoramento de processos via WebSocket
- **Agentes Autônomos**: Habilidades de automação e execução segura de tarefas

## 🚀 Funcionalidades Principais

### Núcleo Cognitivo (`core/brain.py`)
- Tomada de decisão autônoma baseada em análise de intenção
- Sistema de habilidades evolutivas (reasoning, learning, adaptation, etc.)
- Auto-reflexão para melhoria contínua
- Detecção automática de evolução de nível

### Memória TurboQuant (`memory/turboquant.py`)
- **Compressão vetorial**: Quantização para int8 (4x redução)
- **Busca sem descompressão completa**: Cálculo de similaridade otimizado
- **Memória de curto e longo prazo**: Cache + SQLite persistente
- **Relações entre memórias**: Grafo de conhecimento conectado
- **Consolidação automática**: Fusão de memórias relacionadas

### Agentes Especializados (`agents/executor.py`)
- **TaskExecutorAgent**: Execução segura de comandos com whitelist
- **LearningAgent**: Análise de padrões e aprendizado contínuo
- Modo seguro bloqueando comandos perigosos

### Dashboard Web (`web/dashboard.py`)
- Interface em tempo real via WebSocket
- Visualização de processos ativos (pensando, aprendendo, executando)
- Gráficos de habilidades e evolução
- Logs em tempo real
- Chat interativo com a IA

## 📦 Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Ou instalar individualmente
pip install fastapi uvicorn websockets numpy scipy pydantic aiofiles httpx apscheduler
```

## 🎯 Uso

### 1. Interface de Linha de Comando

```bash
python main.py
```

Interaja diretamente com a IA através do terminal.

### 2. Dashboard Web

```bash
python web/dashboard.py
```

Acesse em: **http://localhost:8000/dashboard**

### 3. Uso Programático

```python
import asyncio
from core.brain import NovaCompCore
from agents.executor import TaskExecutorAgent

async def main():
    # Inicializa
    core = NovaCompCore(name="MinhaIA")
    executor = TaskExecutorAgent()
    
    # Pensar sobre algo
    decision = await core.think("Quero criar um projeto Python")
    print(f"Ação: {decision['action']}")
    
    # Ensinar novo conhecimento
    await core.learn({
        'type': 'technical',
        'content': 'Python usa indentação para blocos'
    })
    
    # Executar comando seguro
    result = await executor.execute("ls -la")
    print(result['stdout'])
    
    # Auto-reflexão
    reflection = await core.self_reflect()
    print(f"Habilidade mais forte: {reflection['strongest_skills'][0]}")
    
    # Status completo
    status = core.get_status()
    print(f"Nível de evolução: {status['evolution_level']}")

asyncio.run(main())
```

## 🔄 Sistema de Evolução

A IA evolui automaticamente quando:
- Atinge threshold de experiências aprendidas
- Média de habilidades > 60%
- Cada evolução aumenta todas as habilidades em 10%

**Níveis de evolução:**
- Nível 1: Básico (50% skills base)
- Nível 2+: Skills aumentam progressivamente até 95%

## 🧠 Habilidades

| Habilidade | Descrição |
|------------|-----------|
| `reasoning` | Capacidade de raciocínio lógico |
| `learning` | Velocidade e eficiência de aprendizado |
| `memory_recall` | Recuperação de memórias relevantes |
| `pattern_recognition` | Identificação de padrões |
| `decision_making` | Qualidade das decisões |
| `self_reflection` | Meta-cognição e auto-análise |
| `adaptation` | Adaptação a novos contextos |

## 🔒 Segurança

O sistema opera em **modo seguro por padrão**:
- Whitelist de comandos permitidos
- Bloqueio de padrões perigosos (rm -rf, sudo, etc.)
- Timeout em execuções
- Logging completo de todas as ações

## 📊 Arquitetura de Memória

```
┌─────────────────────────────────────────────┐
│         Short-Term Cache (RAM)              │
│   - Acesso ultra-rápido                     │
│   - Últimas memórias acessadas              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      TurboQuant Storage (SQLite)            │
│   - Vetores comprimidos (int8)              │
│   - Busca por similaridade                  │
│   - Relações entre memórias                 │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│       Evolution Log                         │
│   - Histórico de aprendizado                │
│   - Eventos de evolução                     │
│   - Métricas de performance                 │
└─────────────────────────────────────────────┘
```

## 🌐 API Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Dashboard web |
| `/api/think` | POST | Processa entrada e retorna decisão |
| `/api/learn` | POST | Ensina novo conhecimento |
| `/api/status` | GET | Status completo do sistema |
| `/api/execute` | POST | Executa comando seguro |
| `/ws` | WebSocket | Atualizações em tempo real |

## 📈 Roadmap

- [ ] Integração com LLMs reais (BERT, GPT, etc.)
- [ ] Embeddings persistentes de alta qualidade
- [ ] Multi-agente colaborativo
- [ ] Aprendizado por reforço profundo
- [ ] Export/import de personalidade
- [ ] Plugins e extensões

## ⚠️ Considerações Importantes

1. **Não é uma IA consciente**: O sistema simula comportamento autônomo mas não possui consciência real
2. **Supervisão humana necessária**: Sempre opere com supervisão, especialmente em produção
3. **Segurança primeiro**: Nunca desative o modo seguro em ambientes não confiáveis
4. **Privacidade**: Dados são armazenados localmente, proteja o banco de dados

## 📄 Licença

MIT License - Use livremente para projetos pessoais e comerciais.

---

**🚀 NovaComp - Uma nova forma de inteligência digital viva**

*Construído com ❤️ para explorar os limites da autonomia artificial segura*
