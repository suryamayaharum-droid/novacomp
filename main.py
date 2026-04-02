"""
NovaComp - Main Entry Point
Ponto de entrada principal da IA Autônoma
"""

import asyncio
import sys
from pathlib import Path

# Adiciona root ao path
sys.path.insert(0, str(Path(__file__).parent))


async def main():
    """Função principal"""
    
    print("=" * 60)
    print("🧠 NovaComp - Inteligência Autônoma Viva")
    print("=" * 60)
    print()
    
    # Importa módulos principais
    from core.brain import NovaCompCore
    from memory.turboquant import TurboQuantMemory
    from agents.executor import TaskExecutorAgent
    
    # Inicializa sistema
    print("📦 Inicializando componentes...")
    
    core = NovaCompCore(name="NovaComp-Alpha")
    executor = TaskExecutorAgent(safe_mode=True)
    
    print("✅ Núcleo inicializado")
    print(f"   - Nível de evolução: {core.evolution_level}")
    print(f"   - Habilidades: {len(core.skills)}")
    
    print("✅ Memória TurboQuant pronta")
    print(f"   - Database: {core.memory.db_path}")
    
    print("✅ Agente Executor pronto")
    print(f"   - Modo seguro: {executor.safe_mode}")
    
    print()
    print("🚀 Sistema pronto!")
    print()
    
    # Demonstra capacidades
    print("📊 Status inicial:")
    status = core.get_status()
    print(f"   - Estado: {status['state']}")
    print(f"   - Habilidades médias: {status['average_skill']:.2%}")
    print(f"   - Memórias: {status['memory_stats']['total_memories']}")
    print()
    
    # Exemplo de uso
    print("💡 Exemplos de uso:")
    print()
    print("1. Pensar sobre um tópico:")
    print("   decision = await core.think('Quero aprender Python')")
    print()
    print("2. Ensinar novo conhecimento:")
    print("   await core.learn({'type': 'technical', 'content': 'Python é...'})")
    print()
    print("3. Executar comando seguro:")
    print("   result = await executor.execute('ls -la')")
    print()
    print("4. Auto-reflexão:")
    print("   reflection = await core.self_reflect()")
    print()
    print("5. Dashboard web:")
    print("   python web/dashboard.py")
    print()
    
    # Loop interativo (opcional)
    try:
        while True:
            print("\n" + "=" * 60)
            user_input = input("💬 Digite (ou 'quit' para sair): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'sair']:
                break
            
            if not user_input:
                continue
            
            # Processa entrada
            decision = await core.think(user_input)
            
            print(f"\n🤔 Decisão: {decision['action']}")
            print(f"   Confiança: {decision['confidence']:.2%}")
            print(f"   Descrição: {decision['description']}")
            
            if decision['suggested_next_steps']:
                print("\n📋 Próximos passos sugeridos:")
                for i, step in enumerate(decision['suggested_next_steps'], 1):
                    print(f"   {i}. {step}")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
    
    print("\n👋 Encerrando NovaComp...")
    
    # Status final
    final_status = core.get_status()
    print(f"\n📊 Resumo da sessão:")
    print(f"   - Tempo ativo: {final_status['uptime_hours']:.2f} horas")
    print(f"   - Eventos de aprendizado: {final_status['learning_events']}")
    print(f"   - Memórias totais: {final_status['memory_stats']['total_memories']}")
    print(f"   - Nível de evolução: {final_status['evolution_level']}")


if __name__ == "__main__":
    asyncio.run(main())
