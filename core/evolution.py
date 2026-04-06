"""
Módulo de Auto-Evolução e Criação de Habilidades
Permite que o NovaComp escreva, valide e instale novos scripts de habilidades.
"""
import os
import ast
import hashlib
from datetime import datetime
from typing import Optional, List, Dict

class EvolutionEngine:
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = skills_dir
        os.makedirs(skills_dir, exist_ok=True)
        self.whitelist_modules = ['os', 'sys', 'json', 'datetime', 'math', 're', 'subprocess']
        self.blacklist_calls = ['eval', 'exec', '__import__', 'compile', 'open'] # Restrições estritas para auto-código
        
    def analyze_safety(self, code: str) -> Dict[str, any]:
        """Analisa a segurança do código gerado pela própria IA."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"safe": False, "reason": f"Syntax Error: {str(e)}"}

        issues = []
        for node in ast.walk(tree):
            # Checar imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in self.whitelist_modules:
                        issues.append(f"Importe não permitido: {alias.name}")
            if isinstance(node, ast.ImportFrom):
                if node.module not in self.whitelist_modules:
                    issues.append(f"Importe from não permitido: {node.module}")
            
            # Checar chamadas perigosas
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in self.blacklist_calls:
                    issues.append(f"Chamada perigosa detectada: {node.func.id}")
                if isinstance(node.func, ast.Attribute) and node.func.attr in self.blacklist_calls:
                    issues.append(f"Atributo perigoso detectado: {node.func.attr}")

        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "complexity": sum(1 for _ in ast.walk(tree))
        }

    def create_skill(self, name: str, description: str, code: str, author: str = "NovaComp-Auto") -> bool:
        """Cria um novo arquivo de habilidade após validação."""
        safety_report = self.analyze_safety(code)
        
        if not safety_report["safe"]:
            print(f"⚠️ [EVOLUÇÃO BLOQUEADA] Skill '{name}' rejeitada por segurança:")
            for issue in safety_report["issues"]:
                print(f"   - {issue}")
            return False

        filename = f"{name.lower().replace(' ', '_')}.py"
        filepath = os.path.join(self.skills_dir, filename)
        
        # Adiciona metadata e cabeçalho
        full_code = f'''
# Auto-generated Skill by NovaComp Evolution Engine
# Date: {datetime.now().isoformat()}
# Author: {author}
# Description: {description}
# Safety Hash: {hashlib.sha256(code.encode()).hexdigest()[:16]}

{code}
'''
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_code)
            print(f"✅ [EVOLUÇÃO SUCESSO] Nova skill '{name}' instalada em {filepath}")
            return True
        except Exception as e:
            print(f"❌ [ERRO CRÍTICO] Falha ao escrever skill: {e}")
            return False

    def generate_self_improvement_prompt(self, error_log: str, current_context: str) -> str:
        """Gera um prompt estruturado para a LLM criar uma correção."""
        return f"""
Você é o motor de evolução do NovaComp. Detectamos o seguinte erro durante a operação:

[ERRO]: {error_log}
[CONTEXTO ATUAL]: {current_context}

Sua tarefa:
1. Analise a causa raiz.
2. Escreva um script Python curto (função) que previna esse erro no futuro ou o corrija automaticamente.
3. O script deve ser seguro, sem uso de eval/exec e usando apenas módulos básicos.
4. Retorne APENAS o código python, sem markdown.

Exemplo de formato de saída esperado:
def auto_fix_function(params):
    # lógica de correção
    return result
"""

    def scan_and_load_skills(self) -> List[str]:
        """Varre a pasta de skills e retorna nomes disponíveis."""
        skills = []
        if not os.path.exists(self.skills_dir):
            return skills
            
        for file in os.listdir(self.skills_dir):
            if file.endswith(".py") and not file.startswith("__"):
                skills.append(file[:-3])
        return skills

# Exemplo de uso simulado
if __name__ == "__main__":
    engine = EvolutionEngine()
    
    # Simulação de uma skill que a IA "pensou" em criar
    new_skill_code = '''
def calculate_optimization_score(data_points):
    import math
    if not data_points:
        return 0.0
    avg = sum(data_points) / len(data_points)
    variance = sum((x - avg) ** 2 for x in data_points) / len(data_points)
    return math.sqrt(variance)
'''
    
    print("🧬 Iniciando processo de evolução...")
    success = engine.create_skill(
        name="Otimização Estatística",
        description="Calcula variância para otimização de processos internos",
        code=new_skill_code
    )
    
    if success:
        print("🧠 NovaComp evoluiu com sucesso!")
    else:
        print("🚫 Evolução bloqueada por protocolos de segurança.")
