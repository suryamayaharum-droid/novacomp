#!/usr/bin/env python3
"""
NovaComp - Script de Inicialização Rápida
Menu interativo para todas as funcionalidades
"""

import sys
import subprocess
from pathlib import Path

def print_header():
    print("\n" + "="*60)
    print("   🚀 NOVACOMP - SISTEMA DE IA AUTÔNOMA VIVA")
    print("="*60)

def show_menu():
    print("\n📋 MENU PRINCIPAL\n")
    print("1. 🧠 Iniciar Brain (Modo Interativo)")
    print("2. 🎬 Executar Demo Automática")
    print("3. 💾 Testar Memória TurboQuant")
    print("4. 📊 Ver Status do Sistema")
    print("5. 🌐 Iniciar Dashboard Web (em desenvolvimento)")
    print("6. 📖 Ver Documentação (README)")
    print("7. 🔧 Instalar Dependências")
    print("8. 🧹 Limpar Banco de Dados")
    print("0. ❌ Sair")
    print()

def run_command(cmd):
    """Executar comando e mostrar saída"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=False, 
            text=True,
            cwd=str(Path(__file__).parent)
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    base_path = Path(__file__).parent
    
    while True:
        print_header()
        show_menu()
        
        choice = input("👉 Escolha uma opção (0-8): ").strip()
        
        if choice == '1':
            print("\n🧠 Iniciando NovaComp Brain (Interativo)...\n")
            run_command(f"python3 {base_path}/main.py")
            
        elif choice == '2':
            print("\n🎬 Executando Demo Automática...\n")
            run_command(f"python3 {base_path}/main.py --demo")
            
        elif choice == '3':
            print("\n💾 Testando Sistema de Memória TurboQuant...\n")
            run_command(f"python3 {base_path}/memory/turboquant.py")
            
        elif choice == '4':
            print("\n📊 Verificando Status do Sistema...\n")
            # Verificar arquivos existentes
            files = {
                'Brain': base_path / 'core' / 'brain.py',
                'Memória': base_path / 'memory' / 'turboquant.py',
                'Main': base_path / 'main.py',
                'Requirements': base_path / 'requirements.txt',
                'README': base_path / 'README.md'
            }
            
            for name, path in files.items():
                status = "✅" if path.exists() else "❌"
                print(f"   {status} {name}: {path.name}")
            
            # Verificar banco de dados
            db_path = base_path / 'memory' / 'novacomp.db'
            if db_path.exists():
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM memories')
                count = cursor.fetchone()[0]
                conn.close()
                print(f"\n   📦 Banco de dados: {count} memórias armazenadas")
            else:
                print(f"\n   📦 Banco de dados: Não criado ainda")
                
        elif choice == '5':
            print("\n🌐 Dashboard Web em desenvolvimento...")
            print("   Em breve: interface visual em tempo real!\n")
            
        elif choice == '6':
            readme_path = base_path / 'README.md'
            if readme_path.exists():
                print("\n📖 Documentação:\n")
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:2000]  # Primeiros 2000 caracteres
                    print(content)
                    print("\n   ... (documento completo em README.md)")
            else:
                print("\n❌ README.md não encontrado\n")
            
        elif choice == '7':
            print("\n🔧 Instalando dependências...\n")
            run_command(f"pip3 install -r {base_path}/requirements.txt")
            
        elif choice == '8':
            print("\n🧹 Limpando banco de dados...")
            db_path = base_path / 'memory' / 'novacomp.db'
            if db_path.exists():
                db_path.unlink()
                print("   ✅ Banco de dados removido!")
            else:
                print("   ℹ️  Nenhum banco de dados para remover")
            
        elif choice == '0':
            print("\n👋 Encerrando NovaComp. Até logo!\n")
            break
            
        else:
            print("\n❌ Opção inválida! Tente novamente.\n")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
