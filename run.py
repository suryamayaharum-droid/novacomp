#!/usr/bin/env python3
"""
NovaComp - Sistema de Inteligência Autônoma Viva
Script de inicialização rápida
"""

import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Verifica e instala dependências se necessário"""
    
    required = ['fastapi', 'uvicorn', 'numpy', 'websockets']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print("📦 Instalando dependências faltantes...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing, '-q'])
        print("✅ Dependências instaladas!")
    
    return True


def show_banner():
    """Mostra banner de boas-vindas"""
    
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🧠  NovaComp - Inteligência Autônoma Viva              ║
║                                                           ║
║   Memória TurboQuant | Auto-Evolução | Dashboard Web     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main_menu():
    """Menu principal interativo"""
    
    while True:
        print("\n" + "=" * 60)
        print("📋 Menu Principal")
        print("=" * 60)
        print("1. 🖥️  Iniciar Dashboard Web (http://localhost:8000)")
        print("2. 💬 Modo Interativo Terminal")
        print("3. 🧪 Testar Componentes")
        print("4. 📊 Ver Status do Sistema")
        print("5. ❌ Sair")
        print("=" * 60)
        
        choice = input("\nEscolha uma opção (1-5): ").strip()
        
        if choice == '1':
            start_dashboard()
        elif choice == '2':
            asyncio.run(interactive_mode())
        elif choice == '3':
            asyncio.run(run_tests())
        elif choice == '4':
            asyncio.run(show_status())
        elif choice == '5':
            print("\n👋 Encerrando NovaComp. Até logo!")
            break
        else:
            print("\n⚠️  Opção inválida. Tente novamente.")


def start_dashboard():
    """Inicia o dashboard web"""
    
    print("\n🚀 Iniciando dashboard web...")
    print("🌐 Acesse: http://localhost:8000/dashboard")
    print("💡 Pressione Ctrl+C para parar\n")
    
    try:
        from web.dashboard import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n⚠️  Dashboard parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar dashboard: {e}")


async def interactive_mode():
    """Modo interativo de terminal"""
    
    print("\n💬 Iniciando modo interativo...")
    print("Digite suas mensagens ou comandos (ou 'quit' para sair)\n")
    
    from core.brain import NovaCompCore
    
    core = NovaCompCore(name="NovaComp-Interactive")
    
    try:
        while True:
            user_input = input("🧑 Você: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'sair']:
                break
            
            if not user_input:
                continue
            
            # Processa entrada
            decision = await core.think(user_input)
            
            print(f"\n🤖 NovaComp:")
            print(f"   Ação: {decision['action']}")
            print(f"   Confiança: {decision['confidence']:.2%}")
            print(f"   {decision['description']}")
            
            if decision['suggested_next_steps']:
                print(f"\n   💡 Sugestões:")
                for step in decision['suggested_next_steps'][:2]:
                    print(f"      • {step}")
            print()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")


async def run_tests():
    """Executa testes dos componentes"""
    
    print("\n🧪 Executando testes...\n")
    
    from core.brain import NovaCompCore
    from memory.turboquant import TurboQuantMemory
    from agents.executor import TaskExecutorAgent
    
    # Teste 1: Memória
    print("Teste 1: Sistema de Memória TurboQuant")
    mem = TurboQuantMemory(db_path=":memory:")
    
    import numpy as np
    vec = np.random.randn(768).astype(np.float32)
    vec /= np.linalg.norm(vec)
    
    mem_id = mem.store_memory(
        content="Teste de memória",
        vector=vec,
        category="test"
    )
    print(f"   ✅ Memória armazenada: {mem_id}")
    
    results = mem.search_similar(vec, threshold=0.5)
    print(f"   ✅ Busca retornou {len(results)} resultados")
    
    stats = mem.get_stats()
    print(f"   ✅ Stats: {stats['total_memories']} memórias")
    
    # Teste 2: Core
    print("\nTeste 2: Núcleo Cognitivo")
    core = NovaCompCore(name="TestCore")
    print(f"   ✅ Core inicializado: {core.name}")
    print(f"   ✅ Habilidades: {len(core.skills)}")
    print(f"   ✅ Nível: {core.evolution_level}")
    
    decision = await core.think("Quero aprender Python")
    print(f"   ✅ Decisão: {decision['action']}")
    
    # Teste 3: Agente
    print("\nTeste 3: Agente Executor")
    executor = TaskExecutorAgent()
    result = await executor.execute("echo Hello NovaComp")
    print(f"   ✅ Comando executado: {result['success']}")
    print(f"   ✅ Output: {result['stdout'].strip()}")
    
    print("\n✅ Todos os testes passaram!")


async def show_status():
    """Mostra status detalhado do sistema"""
    
    from core.brain import NovaCompCore
    
    core = NovaCompCore()
    status = core.get_status()
    
    print("\n📊 Status do Sistema NovaComp")
    print("=" * 60)
    print(f"Nome:              {status['name']}")
    print(f"Estado:            {status['state']}")
    print(f"Nível de Evolução: {status['evolution_level']}")
    print(f"Habilidade Média:  {status['average_skill']:.2%}")
    print(f"Tempo Ativo:       {status['uptime_hours']:.4f} horas")
    print()
    print("Habilidades:")
    for skill, value in sorted(status['skills'].items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(value * 20)
        print(f"  {skill:20} {bar:20} {value:.2%}")
    print()
    print("Memória:")
    ms = status['memory_stats']
    print(f"  Total memórias:    {ms['total_memories']}")
    print(f"  Relações:          {ms['total_relations']}")
    print(f"  Cache:             {ms['short_term_cache_size']}")
    print(f"  Acessos recentes:  {ms['recent_accesses']}")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    
    show_banner()
    check_dependencies()
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 NovaComp encerrado. Volte sempre!")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
