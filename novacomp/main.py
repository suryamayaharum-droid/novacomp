#!/usr/bin/env python3
"""
NovaComp - Sistema de IA Autônoma Viva
Entry Point Principal
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Adicionar caminho do projeto
sys.path.insert(0, str(Path(__file__).parent))

from core.brain import NovaBrain
from memory.turboquant import TurboQuantMemory


def print_banner():
    """Imprimir banner de boas-vindas"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ███╗   ██╗███████╗██╗    ██╗    ███████╗                ║
    ║   ████╗  ██║██╔════╝██║    ██║    ██╔════╝                ║
    ║   ██╔██╗ ██║█████╗  ██║ █╗ ██║    ███████╗                ║
    ║   ██║╚██╗██║██╔══╝  ██║███╗██║    ╚════██║                ║
    ║   ██║ ╚████║███████╗╚███╔███╔╝    ███████║                ║
    ║   ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝     ╚══════╝                ║
    ║                                                           ║
    ║        SISTEMA DE IA AUTÔNOMA VIVA                        ║
    ║        Versão 1.0 - Evolução Contínua                     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def interactive_mode(brain: NovaBrain):
    """Modo interativo com o usuário"""
    print("\n🤖 Modo Interativo Ativado")
    print("Digite 'sair' para encerrar, 'status' para ver status, 'refletir' para auto-reflexão\n")
    
    while True:
        try:
            user_input = input("\n🧑 Você: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Encerrando NovaComp...")
                break
            
            if user_input.lower() == 'status':
                status = brain.get_status()
                print(f"\n📊 Status do Sistema:")
                print(f"   Nome: {status['name']}")
                print(f"   Estado: {status['state']}")
                print(f"   Nível: {status['evolution_level']}")
                print(f"   XP: {status['experience_points']}")
                print(f"   Memórias: {status['memory_stats']['total_memories']}")
                print(f"   Habilidades: {status['skills']}")
                continue
            
            if user_input.lower() == 'refletir':
                print("\n🤔 NovaComp está refletindo...")
                reflection = brain.reflect()
                print(f"   Pontos fortes: {reflection['strengths']}")
                print(f"   Pontos fracos: {reflection['weaknesses']}")
                print(f"   Insights: {reflection['insights']}")
                continue
            
            # Processar entrada
            print("\n💭 NovaComp está pensando...")
            result = brain.think(user_input)
            
            print(f"\n🧠 Resposta:")
            print(f"   {result['response']}")
            
            if result['next_action']['type'] != 'none':
                print(f"\n⚡ Próxima ação sugerida: {result['next_action']['type']}")
                print(f"   Prioridade: {result['next_action']['priority']:.1%}")
                
                # Perguntar se deve executar
                if result['next_action']['requires_approval']:
                    confirm = input("\n   Executar ação? (s/n): ").strip().lower()
                    if confirm == 's':
                        exec_result = brain.execute_action(
                            result['next_action']['type'],
                            {'input': user_input}
                        )
                        print(f"   Resultado: {exec_result['output']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrompido pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            continue


def demo_mode(brain: NovaBrain):
    """Executar demonstração automática"""
    print("\n🎬 Iniciando Demonstração Automática...\n")
    
    demos = [
        "Como criar um sistema de IA autônomo?",
        "Quero aprender sobre machine learning",
        "Analise este conceito de memória vetorial",
        "Qual a melhor forma de evoluir habilidades?",
        "Execute uma reflexão sobre seu estado atual"
    ]
    
    for i, demo_input in enumerate(demos, 1):
        print(f"\n{'='*60}")
        print(f"📝 Demo {i}: '{demo_input}'")
        print('='*60)
        
        result = brain.think(demo_input)
        
        print(f"Intenção detectada: {result['thought']['intention']['type']}")
        print(f"Confiança: {result['thought']['intention']['confidence']:.1%}")
        print(f"\nResposta:")
        print(f"   {result['response']}")
        
        # Aprender com a interação
        brain.learn({
            'summary': f'Demo: {demo_input}',
            'outcome': 'success'
        })
    
    # Auto-reflexão final
    print(f"\n{'='*60}")
    print("🤔 Auto-Reflexão Final")
    print('='*60)
    
    reflection = brain.reflect()
    print(f"Pontos fortes: {reflection['strengths']}")
    print(f"Insights: {reflection['insights']}")
    
    # Status final
    print(f"\n{'='*60}")
    print("📊 Status Final")
    print('='*60)
    
    status = brain.get_status()
    print(f"Nível de evolução: {status['evolution_level']}")
    print(f"Experiência: {status['experience_points']} XP")
    print(f"Memórias armazenadas: {status['memory_stats']['total_memories']}")
    print(f"Relações criadas: {status['memory_stats']['total_relations']}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='NovaComp - Sistema de IA Autônoma Viva'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Executar modo de demonstração'
    )
    
    parser.add_argument(
        '--name',
        type=str,
        default='NovaComp',
        help='Nome da instância da IA'
    )
    
    parser.add_argument(
        '--safe',
        action='store_true',
        default=True,
        help='Ativar modo de segurança (padrão: ativado)'
    )
    
    parser.add_argument(
        '--autonomy',
        type=float,
        default=0.7,
        help='Nível de autonomia (0.0-1.0, padrão: 0.7)'
    )
    
    args = parser.parse_args()
    
    # Imprimir banner
    print_banner()
    
    print(f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🚀 Inicializando {args.name}...\n")
    
    # Criar instância do cérebro
    brain = NovaBrain(name=args.name)
    brain.safety_mode = args.safe
    brain.autonomy_level = args.autonomy
    
    # Selecionar modo de operação
    if args.demo:
        demo_mode(brain)
    else:
        interactive_mode(brain)
    
    print("\n✅ Sessão encerrada. Até logo!")


if __name__ == "__main__":
    main()
