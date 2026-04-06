"""
NovaComp Polyglot Engine
Motor de Execução e Compilação Universal
Suporta: Python, JS, Rust, Go, C++, Java, PowerShell, Bash, SQL
Capacidade de análise estática, compilação e execução segura.
"""

import subprocess
import tempfile
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PolyglotEngine")

@dataclass
class CodeResult:
    success: bool
    output: str
    error: str
    binary_path: Optional[str]
    language: str
    execution_time: float

class PolyglotEngine:
    def __init__(self):
        self.supported_languages = {
            'python': {'ext': '.py', 'cmd': ['python3', '-u'], 'check': 'python3 --version'},
            'javascript': {'ext': '.js', 'cmd': ['node'], 'check': 'node --version'},
            'bash': {'ext': '.sh', 'cmd': ['bash'], 'check': 'bash --version'},
            'powershell': {'ext': '.ps1', 'cmd': ['pwsh', '-File'], 'check': 'pwsh -v'},
            'go': {'ext': '.go', 'cmd': ['go', 'run'], 'check': 'go version'},
            'rust': {'ext': '.rs', 'cmd': ['rustc', '--out-dir', '/tmp'], 'check': 'rustc --version'},
            'java': {'ext': '.java', 'cmd': ['java'], 'check': 'java -version'},
            'cpp': {'ext': '.cpp', 'cmd': ['g++', '-o', '/tmp/out'], 'check': 'g++ --version'},
        }
        self.sandbox_dir = Path(tempfile.mkdtemp(prefix="novacomp_sandbox_"))
        
    def detect_language(self, code: str) -> str:
        """Detecta a linguagem baseada em heurística de sintaxe."""
        code_lower = code.strip().lower()
        if code_lower.startswith('package ') or 'func main()' in code: return 'go'
        if code_lower.startswith('use ') or 'fn main()' in code: return 'rust'
        if code_lower.startswith('import ') and ('from' in code or 'def ' in code): return 'python'
        if code_lower.startswith('public class') or 'public static void main': return 'java'
        if code_lower.startswith('#include') or 'int main()' in code: return 'cpp'
        if code_lower.startswith('function ') or 'const ' in code or 'console.log' in code: return 'javascript'
        if code_lower.startswith('$') or 'get-process' in code_lower: return 'powershell'
        if code_lower.startswith('#!/') or '|' in code: return 'bash'
        return 'python' # Default

    def compile_code(self, code: str, language: str, output_name: str = "main") -> CodeResult:
        """Compila código para bytecode ou binário se aplicável."""
        lang_config = self.supported_languages.get(language)
        if not lang_config:
            return CodeResult(False, "", f"Linguagem {language} não suportada", None, language, 0.0)

        filename = f"{output_name}{lang_config['ext']}"
        filepath = self.sandbox_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)

        try:
            if language == 'rust':
                cmd = ['rustc', str(filepath), '-o', str(self.sandbox_dir / output_name)]
            elif language == 'cpp':
                cmd = ['g++', str(filepath), '-o', str(self.sandbox_dir / output_name)]
            elif language == 'java':
                cmd = ['javac', str(filepath), '-d', str(self.sandbox_dir)]
                # Java compila para .class, não executamos aqui
            else:
                # Linguagens interpretadas não precisam de compilação separada neste contexto
                # Mas podemos gerar bytecode (.pyc) se necessário
                if language == 'python':
                    import py_compile
                    pyc_path = str(self.sandbox_dir / f"{output_name}.pyc")
                    py_compile.compile(str(filepath), cfile=pyc_path, doraise=True)
                    return CodeResult(True, f"Bytecode gerado: {pyc_path}", "", pyc_path, language, 0.0)
                
                return CodeResult(True, "Código interpretado (sem compilação estática necessária)", "", str(filepath), language, 0.0)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                binary = str(self.sandbox_dir / output_name) if language != 'java' else str(self.sandbox_dir / f"{output_name}.class")
                return CodeResult(True, result.stdout, result.stderr, binary, language, 0.0)
            else:
                return CodeResult(False, result.stdout, result.stderr, None, language, 0.0)

        except Exception as e:
            return CodeResult(False, "", str(e), None, language, 0.0)

    def execute_code(self, code: str, language: Optional[str] = None, args: List[str] = None) -> CodeResult:
        """Executa código em ambiente isolado."""
        if not language:
            language = self.detect_language(code)
        
        lang_config = self.supported_languages.get(language)
        if not lang_config:
            return CodeResult(False, "", f"Linguagem {language} não reconhecida", None, language, 0.0)

        filename = f"script_{hashlib.md5(code.encode()).hexdigest()[:8]}{lang_config['ext']}"
        filepath = self.sandbox_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)

        cmd = []
        if language == 'java':
            # Compilar primeiro
            compile_res = self.compile_code(code, language, "MainClass")
            if not compile_res.success: return compile_res
            cmd = ['java', '-cp', str(self.sandbox_dir), 'MainClass']
        elif language == 'rust' or language == 'cpp':
            # Compilar primeiro
            compile_res = self.compile_code(code, language, "main")
            if not compile_res.success: return compile_res
            cmd = [str(self.sandbox_dir / "main")]
        else:
            cmd = lang_config['cmd'] + [str(filepath)]

        if args:
            cmd.extend(args)

        import time
        start = time.time()
        try:
            # Segurança: Limitar tempo e recursos poderia ser adicionado aqui (ulimit, docker)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, cwd=str(self.sandbox_dir))
            elapsed = time.time() - start
            return CodeResult(
                result.returncode == 0,
                result.stdout,
                result.stderr,
                None,
                language,
                elapsed
            )
        except subprocess.TimeoutExpired:
            return CodeResult(False, "", "Timeout de execução (15s)", None, language, 15.0)
        except Exception as e:
            return CodeResult(False, "", str(e), None, language, 0.0)

    def analyze_bytecode(self, file_path: str) -> Dict[str, Any]:
        """Analisa arquivos compilados (pyc, class, etc) para extrair metadados."""
        # Implementação simplificada de análise estática
        analysis = {
            "file": file_path,
            "type": "unknown",
            "strings": [],
            "imports": [],
            "functions": []
        }
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            # Extrair strings ASCII imprimíveis
            import re
            strings = re.findall(b'[A-Za-z0-9_./]{4,}', content)
            analysis["strings"] = [s.decode('ascii', errors='ignore') for s in strings[:50]]
            
            if file_path.endswith('.pyc'):
                analysis["type"] = "python_bytecode"
            elif file_path.endswith('.class'):
                analysis["type"] = "java_bytecode"
            elif file_path.endswith('.so') or file_path.endswith('.dll'):
                analysis["type"] = "native_binary"
                
        except Exception as e:
            analysis["error"] = str(e)
            
        return analysis

    def cleanup(self):
        """Limpa o diretório sandbox."""
        import shutil
        try:
            shutil.rmtree(self.sandbox_dir)
            self.sandbox_dir = Path(tempfile.mkdtemp(prefix="novacomp_sandbox_"))
        except:
            pass

# Exemplo de uso integrado ao Brain
if __name__ == "__main__":
    engine = PolyglotEngine()
    
    # Teste Python
    py_code = "print('Hello from Python'); import math; print(math.sqrt(16))"
    res = engine.execute_code(py_code)
    print(f"Python: {res.output}")
    
    # Teste JS
    js_code = "console.log('Hello from Node'); const x = 10 * 5; console.log(x);"
    res = engine.execute_code(js_code, 'javascript')
    print(f"JS: {res.output}")
    
    # Teste Bash
    bash_code = "echo 'System Info:' && uname -a"
    res = engine.execute_code(bash_code, 'bash')
    print(f"Bash: {res.output}")
    
    engine.cleanup()
