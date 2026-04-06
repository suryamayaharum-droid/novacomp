#!/usr/bin/env python3
"""
NovaComp - Demo Completo das Capacidades Avançadas
Demonstra: Polyglot, Universal Comm, Memory TurboQuant, Evolution
"""

import sys
import asyncio
from pathlib import Path

# Adicionar workspace ao path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🧠 NOVACOMP - IA AUTÔNOMA VIVA COM CAPACIDADES AVANÇADAS")
print("=" * 70)

# =============================================================================
# 1. POLYGLOT ENGINE - Execução Multi-Linguagem
# =============================================================================
print("\n" + "=" * 70)
print("💻 1. POLYGLOT ENGINE - Domínio de 8+ Linguagens")
print("=" * 70)

from core.polyglot_engine import PolyglotEngine

engine = PolyglotEngine()

# Teste Python
print("\n🐍 Python:")
py_code = "print('Hello from Python'); import math; print(f'Raiz de 144 = {math.sqrt(144)}')"
result = engine.execute_code(py_code)
print(f"   Saída: {result.output.strip().replace(chr(10), ' | ')}")

# Teste JavaScript
print("\n🟨 JavaScript:")
js_code = "console.log('Hello from Node'); const x = 10 * 5; console.log(`Resultado: ${x}`);"
result = engine.execute_code(js_code, 'javascript')
print(f"   Saída: {result.output.strip().replace(chr(10), ' | ')}")

# Teste Bash
print("\n🐚 Bash:")
bash_code = "echo 'Sistema:' && uname -s && echo 'Kernel:' && uname -r"
result = engine.execute_code(bash_code, 'bash')
print(f"   Saída: {result.output.strip().replace(chr(10), ' | ')}")

# Teste PowerShell (se disponível)
print("\n🔷 PowerShell:")
ps_code = "$ver = $PSVersionTable.PSVersion; Write-Host \"PowerShell v$ver\""
try:
    result = engine.execute_code(ps_code, 'powershell')
    if result.success:
        print(f"   Saída: {result.output.strip()}")
    else:
        print(f"   ⚠️ PowerShell não disponível: {result.error[:50]}")
except Exception as e:
    print(f"   ⚠️ PowerShell não disponível neste ambiente")

engine.cleanup()

# =============================================================================
# 2. UNIVERSAL COMMUNICATOR - Comunicação com LLMs
# =============================================================================
print("\n" + "=" * 70)
print("🗣️ 2. UNIVERSAL COMMUNICATOR - Integração com LLMs")
print("=" * 70)

from core.universal_comm import create_universal_communicator, Message

comm = create_universal_communicator()

print(f"\n✅ LLMs Registradas: {list(comm.llm_providers.keys())}")
print(f"✅ Bancos de Dados: {list(comm.db_connections.keys())}")
print(f"✅ Cloud Providers: {list(comm.cloud_clients.keys())}")

print("\n📡 Configurações disponíveis:")
print("   - OpenAI GPT-4 (requer OPENAI_API_KEY)")
print("   - Anthropic Claude (requer ANTHROPIC_API_KEY)")
print("   - Google Gemini (requer GOOGLE_API_KEY)")
print("   - Ollama Local (http://localhost:11434)")

# Testar banco de dados
print("\n💾 Testando SQLite:")
try:
    results = comm.query_db("local_sqlite", "SELECT name FROM sqlite_master WHERE type='table'")
    print(f"   Tabelas encontradas: {len(results)}")
except Exception as e:
    print(f"   Info: Banco será criado quando necessário")

# =============================================================================
# 3. TURBOQUANT MEMORY - Compressão Vetorial
# =============================================================================
print("\n" + "=" * 70)
print("🧠 3. TURBOQUANT MEMORY - Armazenamento Comprimido 4x")
print("=" * 70)

from memory.turboquant import TurboQuantMemory

memory = TurboQuantMemory(vector_dim=768, db_path="demo_novacomp.db")

print("\n📊 Características:")
print("   - Dimensão do vetor: 768 (BERT base)")
print("   - Compressão: int8 (4x redução)")
print("   - Busca: Similaridade cosseno binária")
print("   - Persistência: SQLite + metadados JSON")

# Armazenar memórias de exemplo
print("\n💾 Armazenando memórias de exemplo...")
import numpy as np

memories = [
    ("Python é uma linguagem versátil", {"type": "knowledge", "lang": "pt"}),
    ("Machine Learning transforma dados em insights", {"type": "concept", "field": "AI"}),
    ("O NovaComp pode executar código em 8 linguagens", {"type": "capability", "system": "NovaComp"})
]

for text, metadata in memories:
    # Gerar vetor aleatório para demo (em produção usaria BERT/SentenceTransformers)
    vector = np.random.randn(768).astype(np.float32)
    memory.store_memory(text, vector, metadata=metadata)
    print(f"   ✅ '{text[:40]}...'")

# Buscar similaridades
print("\n🔍 Buscando por 'programação':")
query_vector = np.random.randn(768).astype(np.float32)  # Vetor de query simulado
results = memory.search_similar(query_vector, threshold=0.1, limit=2)
for r in results:
    print(f"   • Score {r.get('similarity', 0):.3f}: {r.get('content', '')[:50]}...")

# Stats
stats = memory.get_stats()
print(f"\n📈 Estatísticas:")
print(f"   - Total memórias: {stats.get('total_memories', 0)}")
print(f"   - Relações criadas: {stats.get('total_relations', 0)}")
print(f"   - Acesso registrado: {stats.get('total_accesses', 0)}")

# =============================================================================
# 4. EVOLUTION ENGINE - Auto-Evolução
# =============================================================================
print("\n" + "=" * 70)
print("🚀 4. EVOLUTION ENGINE - Criação Automática de Skills")
print("=" * 70)

from core.evolution import EvolutionEngine

engine = EvolutionEngine(skills_dir="skills")

print("\n🔒 Scanner de Segurança:")
test_codes = [
    ("x = 1 + 2", "Código seguro"),
    ("eval('malicious')", "Código perigoso (eval)"),
    ("import socket", "Import proibido"),
    ("def calc(): return 1", "Função segura")
]

for code, desc in test_codes:
    analysis = engine.analyze_safety(code)
    safe = analysis.get('is_safe', False)
    status = "✅ Seguro" if safe else "❌ Bloqueado"
    print(f"   {status}: {desc}")

# Ver skills existentes
skills_dir = Path("skills")
if skills_dir.exists():
    skills = list(skills_dir.glob("*.py"))
    print(f"\n📚 Skills disponíveis: {len(skills)}")
    for s in skills[:5]:
        print(f"   • {s.name}")

# =============================================================================
# 5. ORCHESTRATOR - Sistema Operacional da IA
# =============================================================================
print("\n" + "=" * 70)
print("⚙️ 5. ORCHESTRATOR - Gerenciamento Autônomo")
print("=" * 70)

from core.orchestrator import NovaOrchestrator

orch = NovaOrchestrator(safe_mode=True)

status = orch.get_status()
print("\n📊 Status do Sistema:")
print(f"   - Uptime: {status['uptime_hours']*3600:.1f}s")
print(f"   - Skills: {status['skills_count']}")
print(f"   - Memórias: {status['memory_size']}")
print(f"   - Modo Seguro: {'✅ Ativo' if status['safe_mode'] else '❌ Desativo'}")
print(f"   - Tarefas Completadas: {status['completed_processes']}")

# Testar execução direta de código
print("\n💻 Executando código via Orchestrator:")
polyglot = PolyglotEngine()
code_result = polyglot.execute_code("print('NovaComp operational'); result = sum([1,2,3,4,5]); print(f'Soma: {result}')")
print(f"   {code_result.output.strip().replace(chr(10), ' | ')}")
polyglot.cleanup()

async def cleanup():
    await orch.shutdown()

asyncio.run(cleanup())

# =============================================================================
# RESUMO FINAL
# =============================================================================
print("\n" + "=" * 70)
print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 70)

print("""
🎯 CAPACIDADES DEMONSTRADAS:

1. ✅ Polyglot Engine
   • Execução em Python, JavaScript, Bash
   • Detecção automática de linguagem
   • Sandbox segura para execução

2. ✅ Universal Communicator
   • Integração com múltiplas LLMs
   • Conexão com bancos de dados
   • Interface para cloud providers

3. ✅ TurboQuant Memory
   • Armazenamento vetorial comprimido
   • Busca por similaridade semântica
   • Persistência em SQLite

4. ✅ Evolution Engine
   • Scanner de segurança AST
   • Criação de skills validadas
   • Whitelist/blacklist de módulos

5. ✅ Orchestrator
   • Gerenciamento de processos
  • Loop autônomo de pensamento
   • Métricas em tempo real

🚀 PRÓXIMOS PASSOS:
   • Execute: python run.py (menu interativo)
   • Execute: python web/dashboard.py (interface web)
   • Execute: python web/neural_viz.py (visualização 3D)
   • Configure chaves de API para LLMs externas
   • Instale Ollama para LLM local completo

📚 DOCUMENTAÇÃO: Consulte README.md
""")

print("=" * 70)
print("🧠 NovaComp - Uma inteligência viva e em evolução!")
print("=" * 70)
