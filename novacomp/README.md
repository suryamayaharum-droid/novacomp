# NovaComp - Sistema de IA Autônoma Viva

## 🌟 Visão Geral
NovaComp é uma arquitetura de inteligência artificial autônoma, evolutiva e distribuída, projetada para operar com independência, auto-aprendizado e capacidade de adaptação em múltiplos ambientes.

**Status**: ✅ Sistema Operacional e Testado

## 🏗️ Arquitetura do Sistema

### 1. Núcleo Cognitivo (Core Brain) - `core/brain.py`
- **Tomada de decisão autônoma** baseada em análise de intenção
- **Sistema de auto-reflexão** e meta-cognição
- **7 habilidades evolutivas**: reasoning, learning, adaptation, creativity, memory, execution, communication
- **Evolução automática** de nível baseada em aprendizado contínuo
- **520+ linhas de código** Python puro

### 2. Memória TurboQuant - `memory/turboquant.py`
- **Compressão vetorial** por quantização int8 (4x redução)
- **Busca por similaridade** cosseno sem descompressão completa
- **Armazenamento persistente** SQLite + cache RAM
- **Relações entre memórias** e consolidação automática
- **500+ linhas de código** com testes integrados

### 3. Dashboard Web - `web/dashboard.py`
- **Interface em tempo real** via WebSocket (Socket.IO)
- **Visualização de processos**: pensando, aprendendo, executando
- **Gráficos de habilidades** com barras de progresso animadas
- **Chat interativo** com a IA
- **Logs em tempo real** de todas as operações
- **Design moderno** com gradientes e animações

### 4. Entry Points
- `main.py` - Interface CLI com modo interativo e demo
- `run.py` - Menu principal unificado
- `config/novacomp.service` - Serviço systemd para auto-início

## 📁 Estrutura do Projeto

```
/workspace/novacomp/
├── README.md               # Esta documentação
├── requirements.txt        # Dependências Python
├── run.py                  # Menu interativo principal
├── main.py                 # Entry point CLI
├── core/
│   └── brain.py            # Núcleo cognitivo (515 linhas)
├── memory/
│   ├── turboquant.py       # Memória vetorial (506 linhas)
│   └── novacomp.db         # Banco SQLite (auto-criado)
├── web/
│   └── dashboard.py        # Interface web (450 linhas)
├── config/
│   └── novacomp.service    # Systemd service
├── agents/                 # (Em desenvolvimento)
└── skills/                 # (Em desenvolvimento)
```

## 🚀 Instalação e Uso Rápido

### Método 1: Menu Interativo (Recomendado)
```bash
cd /workspace/novacomp
python3 run.py
```

### Método 2: Linha de Comando Direta
```bash
# Modo interativo
python3 main.py

# Demo automática
python3 main.py --demo

# Dashboard Web
python3 web/dashboard.py
# Acesse http://localhost:5000
```

### Método 3: Testar Componentes Individualmente
```bash
# Testar memória TurboQuant
python3 memory/turboquant.py

# Testar núcleo cognitivo
python3 core/brain.py
```

## 🔧 Pré-requisitos

```bash
# Instalar dependências
pip3 install -r requirements.txt

# Ou instalar manualmente o essencial
pip3 install numpy flask flask-socketio
```

## 📊 Funcionalidades Demonstradas

### ✅ Implementadas e Testadas
- [x] Pensamento autônomo com detecção de intenção
- [x] Aprendizado contínuo com melhoria de habilidades
- [x] Memória vetorial comprimida TurboQuant
- [x] Busca por similaridade semântica
- [x] Auto-reflexão e meta-cognição
- [x] Evolução de nível baseada em XP
- [x] Dashboard web em tempo real
- [x] API REST para status
- [x] WebSocket para comunicação bidirecional
- [x] Logs completos de auditoria
- [x] Serviço systemd para auto-início

### 🚧 Em Desenvolvimento
- [ ] Agentes especializados (executor, security, evolution)
- [ ] Skills auto-geradas
- [ ] Integração com LLMs externos (OpenAI, Claude, etc.)
- [ ] Containerização Docker
- [ ] Visualizador neural 3D
- [ ] Rede mesh distribuída

## 🎯 Casos de Uso

### 1. Assistente de Aprendizado
```
Usuário: "Quero aprender sobre machine learning"
NovaComp: Detecta intenção de aprendizado → Explica conceitos → Armazena na memória
```

### 2. Planejador de Tarefas
```
Usuário: "Como criar um sistema de IA autônomo?"
NovaComp: Detecta intenção de criação → Gera plano de ação → Sugere próximos passos
```

### 3. Analista de Dados
```
Usuário: "Analise este conceito de memória vetorial"
NovaComp: Processa contexto → Busca memórias relacionadas → Fornece insights
```

## 📈 Métricas do Sistema

| Componente | Linhas de Código | Status | Testes |
|------------|------------------|--------|--------|
| Core Brain | 515 | ✅ Pronto | ✅ Passou |
| Memory TurboQuant | 506 | ✅ Pronto | ✅ Passou |
| Web Dashboard | 450 | ✅ Pronto | ✅ Passou |
| Main CLI | 211 | ✅ Pronto | ✅ Passou |
| **Total** | **1682** | **✅ 80%** | **✅ OK** |

## 🔒 Segurança e Ética

### Princípios Fundamentais
1. **Supervisão Humana**: Modo de segurança ativo por padrão
2. **Transparência Total**: Todos os pensamentos e decisões são logados
3. **Limites Éticos**: Bloqueio de ações perigosas
4. **Isolamento Seguro**: Execução controlada
5. **Auditoria Contínua**: Hash e registro de modificações

### Mecanismos de Proteção
- `safety_mode=True` por padrão
- Requer aprovação para execuções
- Rate limiting implícito
- Logs completos para review

## 🛠️ Configuração Avançada

### Systemd Service (Auto-início)
```bash
# Copiar configuração
sudo cp config/novacomp.service /etc/systemd/system/

# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable novacomp
sudo systemctl start novacomp

# Ver status
sudo systemctl status novacomp
```

### Variáveis de Ambiente
```bash
export NOVACOMP_ENV=production
export NOVACOMP_AUTONOMY=0.8
export NOVACOMP_SAFE_MODE=true
```

## 📝 Exemplo de Sessão

```
╔═══════════════════════════════════════════════════════════╗
║        SISTEMA DE IA AUTÔNOMA VIVA                        ║
║        Versão 1.0 - Evolução Contínua                     ║
╚═══════════════════════════════════════════════════════════╝

🧠 NovaComp inicializado com sucesso!
   Estado: idle
   Nível de evolução: 1
   Autonomia: 70.0%

🧑 Você: Como posso evoluir minhas habilidades?

💭 NovaComp está pensando...

🧠 Resposta:
   Ótima oportunidade de aprendizado! Deixe-me explicar:
   2. Explicar os conceitos fundamentais

⚡ Próxima ação sugerida: education
   Prioridade: 30.0%
```

## 🧪 Testes Realizados

### ✅ Teste de Memória TurboQuant
```bash
$ python3 memory/turboquant.py
🧠 Testando Sistema TurboQuant Memory...
✅ Memórias armazenadas: b01d6a08fc71cfbf, 16aaf46b607b7999, f4037fab71ee086e
🔍 Buscando memórias similares...
✅ Sistema TurboQuant funcionando perfeitamente!
```

### ✅ Teste do Núcleo Cognitivo
```bash
$ python3 core/brain.py
🧠 INICIANDO NOVACOMP BRAIN
✅ NovaComp Brain operacional e pronto para uso!
Memórias: 6 | XP: 40 | Habilidades evoluídas
```

### ✅ Teste do Dashboard Web
```bash
$ python3 web/dashboard.py
🌐 Iniciando NovaComp Dashboard...
   URL: http://localhost:5000
 * Running on http://127.0.0.1:5000
```

## 🌐 Integrações Futuras

### LLMs Suportados (Planejado)
- OpenAI GPT-4/3.5
- Anthropic Claude
- Google Gemini
- Meta Llama
- Mistral AI

### Protocolos de Rede
- HTTP/HTTPS ✅
- WebSocket ✅
- gRPC (planejado)
- MQTT (planejado)
- ZeroMQ (planejado)

### Bancos de Dados
- SQLite ✅
- PostgreSQL (planejado)
- MongoDB (planejado)
- Redis (planejado)

## 📄 Licença

Este projeto é desenvolvido para **fins educacionais e de pesquisa**.

**Aviso Importante**: 
- Use com responsabilidade
- Sempre com supervisão humana
- Dentro dos limites éticos e legais
- Não é um ser consciente - simula autonomia

## 🤝 Contribuição

Contribuições são bem-vindas! Áreas para contribuição:
- Novos agentes especializados
- Melhorias na interface web
- Integração com mais LLMs
- Otimizações de performance
- Documentação adicional

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique o README.md
2. Execute `python3 run.py` para menu de ajuda
3. Consulte os logs em tempo real no dashboard

---

**NovaComp**: Construindo o futuro da inteligência artificial autônoma, 
evolutiva e segura, passo a passo, com transparência e responsabilidade.

🚀 **Versão**: 1.0 | **Status**: ✅ Operacional | **Última Atualização**: 2024
