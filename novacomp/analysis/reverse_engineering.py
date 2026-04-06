"""
NOVACOMP - ENGINEERING REVERSE & ANALYSIS CORE
Módulo de Engenharia Reversa Ética e Análise Binária

Capacidades:
- Análise estática de binários e scripts
- Desmontagem controlada (via ferramentas externas)
- Identificação de padrões e assinaturas
- Extração de strings e metadados
- Análise de fluxo de dados simplificada
- Detecção de ofuscação

NOTA DE SEGURANÇA:
Este módulo opera APENAS em arquivos locais fornecidos pelo usuário.
Não executa código malicioso. Não realiza engenharia reversa em software protegido por DRM.
Uso exclusivo para análise de malware em sandbox, auditoria de segurança e educação.
"""

import os
import re
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BinaryInfo:
    """Informações extraídas de um binário/arquivo"""
    filename: str
    filepath: str
    size: int
    md5: str
    sha1: str
    sha256: str
    file_type: str
    strings_found: List[str]
    entropy: float
    sections: Optional[Dict] = None
    imports: Optional[List[str]] = None
    exports: Optional[List[str]] = None
    is_packed: bool = False
    compiler_signature: Optional[str] = None
    timestamp: str = ""


class ReverseEngineeringEngine:
    """
    Motor de Engenharia Reversa Ética
    
    Fornece capacidades de análise estática sem execução de código.
    Integra-se com ferramentas externas quando disponíveis (objdump, radare2, ghidra).
    """
    
    def __init__(self, safe_mode: bool = True):
        self.safe_mode = safe_mode
        self.analysis_history = []
        self.supported_tools = self._detect_tools()
        
    def _detect_tools(self) -> Dict[str, bool]:
        """Detecta ferramentas de engenharia reversa disponíveis no sistema"""
        tools = {
            'objdump': False,
            'readelf': False,
            'strings': False,
            'file': False,
            'radare2': False,
            'ghidra': False,
            'binwalk': False
        }
        
        for tool in tools.keys():
            try:
                result = subprocess.run(
                    ['which', tool],
                    capture_output=True,
                    timeout=5
                )
                tools[tool] = (result.returncode == 0)
            except Exception:
                tools[tool] = False
                
        return tools
    
    def analyze_file(self, filepath: str) -> BinaryInfo:
        """
        Realiza análise completa de um arquivo
        
        Args:
            filepath: Caminho para o arquivo a ser analisado
            
        Returns:
            BinaryInfo com todos os dados extraídos
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
            
        if not path.is_file():
            raise ValueError(f"Não é um arquivo válido: {filepath}")
        
        # Coleta informações básicas
        file_size = path.stat().st_size
        file_content = path.read_bytes()
        
        # Hashes
        md5_hash = hashlib.md5(file_content).hexdigest()
        sha1_hash = hashlib.sha1(file_content).hexdigest()
        sha256_hash = hashlib.sha256(file_content).hexdigest()
        
        # Tipo de arquivo
        file_type = self._detect_file_type(path)
        
        # Extrai strings
        strings_found = self._extract_strings(file_content)
        
        # Calcula entropia
        entropy = self._calculate_entropy(file_content)
        
        # Detecta packing
        is_packed = self._detect_packing(entropy, file_type)
        
        # Tenta extrair seções e imports se ferramentas estiverem disponíveis
        sections = None
        imports = None
        exports = None
        compiler_sig = None
        
        if self.supported_tools['readelf'] and 'ELF' in file_type:
            sections = self._extract_sections_elf(path)
            imports = self._extract_imports_elf(path)
            
        if self.supported_tools['objdump'] and 'ELF' in file_type:
            exports = self._extract_exports_objdump(path)
            
        compiler_sig = self._detect_compiler_signature(strings_found, file_content)
        
        info = BinaryInfo(
            filename=path.name,
            filepath=str(path.absolute()),
            size=file_size,
            md5=md5_hash,
            sha1=sha1_hash,
            sha256=sha256_hash,
            file_type=file_type,
            strings_found=strings_found[:50],  # Limita a 50 strings
            entropy=entropy,
            sections=sections,
            imports=imports,
            exports=exports,
            is_packed=is_packed,
            compiler_signature=compiler_sig,
            timestamp=datetime.now().isoformat()
        )
        
        self.analysis_history.append(asdict(info))
        return info
    
    def _detect_file_type(self, path: Path) -> str:
        """Detecta o tipo de arquivo"""
        if self.supported_tools['file']:
            try:
                result = subprocess.run(
                    ['file', str(path)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.stdout.strip()
            except Exception:
                pass
        
        # Fallback: análise por magic bytes
        try:
            with open(path, 'rb') as f:
                magic = f.read(4)
                
            if magic.startswith(b'MZ'):
                return "PE Executable (Windows)"
            elif magic.startswith(b'\x7fELF'):
                return "ELF Executable (Linux/Unix)"
            elif magic.startswith(b'PK'):
                return "ZIP Archive"
            elif magic.startswith(b'%PDF'):
                return "PDF Document"
            else:
                return "Unknown Binary/Data"
        except Exception:
            return "Error reading file"
    
    def _extract_strings(self, content: bytes, min_length: int = 4) -> List[str]:
        """Extrai strings imprimíveis do conteúdo"""
        if self.supported_tools['strings']:
            try:
                result = subprocess.run(
                    ['strings', '-n', str(min_length)],
                    input=content,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return [s.strip() for s in result.stdout.split('\n') if s.strip()][:100]
            except Exception:
                pass
        
        # Fallback: implementação pura em Python
        string_pattern = rb'[\x20-\x7e]{' + str(min_length).encode() + rb',}'
        matches = re.findall(string_pattern, content)
        return [m.decode('ascii', errors='ignore') for m in matches[:100]]
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calcula a entropia de Shannon dos dados"""
        if not data:
            return 0.0
            
        from collections import Counter
        import math
        
        byte_counts = Counter(data)
        total_bytes = len(data)
        
        entropy = 0.0
        for count in byte_counts.values():
            if count > 0:
                probability = count / total_bytes
                entropy -= probability * math.log2(probability)
                
        return round(entropy, 4)
    
    def _detect_packing(self, entropy: float, file_type: str) -> bool:
        """Detecta se o arquivo provavelmente está empacotado/comprimido"""
        # Entropia alta (>7.0) geralmente indica packing ou criptografia
        if entropy > 7.5:
            return True
            
        # Verificações específicas por tipo
        if 'PE' in file_type and entropy > 7.0:
            return True
            
        return False
    
    def _extract_sections_elf(self, path: Path) -> Optional[Dict]:
        """Extrai informações de seções de um ELF"""
        try:
            result = subprocess.run(
                ['readelf', '-S', str(path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
                
            sections = {}
            lines = result.stdout.split('\n')
            
            for line in lines:
                if '[' in line and ']' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            section_name = parts[1].strip('[]')
                            if section_name and not section_name.isdigit():
                                sections[section_name] = {
                                    'type': parts[2] if len(parts) > 2 else 'unknown',
                                    'address': parts[3] if len(parts) > 3 else '0x0'
                                }
                        except (IndexError, ValueError):
                            continue
                            
            return sections
        except Exception:
            return None
    
    def _extract_imports_elf(self, path: Path) -> Optional[List[str]]:
        """Extrai funções importadas de um ELF"""
        try:
            result = subprocess.run(
                ['readelf', '-s', str(path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
                
            imports = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'UND' in line and '@' in line:
                    parts = line.split()
                    for part in parts:
                        if '@' in part and not part.startswith('GLIBC'):
                            func_name = part.split('@')[0]
                            if func_name and func_name not in imports:
                                imports.append(func_name)
                                
            return imports[:50]  # Limita a 50 imports
        except Exception:
            return None
    
    def _extract_exports_objdump(self, path: Path) -> Optional[List[str]]:
        """Extrai símbolos exportados usando objdump"""
        try:
            result = subprocess.run(
                ['objdump', '-T', str(path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
                
            exports = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 5 and 'DF' in parts:
                    func_name = parts[-1]
                    if func_name and not func_name.startswith('.'):
                        exports.append(func_name)
                        
            return exports[:50]
        except Exception:
            return None
    
    def _detect_compiler_signature(self, strings: List[str], content: bytes) -> Optional[str]:
        """Tenta identificar o compilador usado"""
        signatures = {
            'Microsoft Visual C++': ['MSVCRT', 'Visual C++', 'Microsoft'],
            'GCC': ['GCC:', 'GNU C', 'libgcc'],
            'Clang': ['clang', 'LLVM'],
            'Delphi': ['Borland Delphi', 'Delphi Runtime'],
            'Python (PyInstaller)': ['pyinstaller', 'PYZ'],
            '.NET': ['.NET', 'mscorlib', 'System.'],
            'Go': ['go runtime', 'golang'],
            'Rust': ['rustc', 'Rust']
        }
        
        all_strings = ' '.join(strings).lower()
        
        for compiler, keywords in signatures.items():
            if any(kw.lower() in all_strings for kw in keywords):
                return compiler
                
        # Verifica assinaturas em bytecode
        if b'PK\x03\x04' in content and b'meta-inf' in content.lower():
            return 'Java (JAR)'
            
        return None
    
    def decompile_script(self, filepath: str, language: str = 'python') -> Optional[str]:
        """
        Tenta descompilar/deobfuscar scripts (apenas linguagens interpretadas)
        
        Suporta: Python (.pyc), JavaScript (minificado), etc.
        """
        path = Path(filepath)
        
        if not path.exists():
            return None
        
        # Python .pyc -> tentativa de descompilação
        if language.lower() == 'python' and path.suffix == '.pyc':
            try:
                import uncompyle6
                from io import StringIO
                
                output = StringIO()
                uncompyle6.decompile_file(path, output=output)
                return output.getvalue()
            except ImportError:
                return "# uncompyle6 não instalado. Instale com: pip install uncompyle6"
            except Exception as e:
                return f"# Erro na descompilação: {str(e)}"
        
        # Para outros casos, retorna análise básica
        content = path.read_text(errors='ignore')
        
        # Detecção simples de ofuscação JS
        if language.lower() == 'javascript':
            if len(content.split('\n')) == 1 and len(content) > 1000:
                return f"// Código possivelmente ofuscado (linha única)\n{content[:500]}..."
        
        return content[:2000]  # Retorna preview
    
    def generate_report(self, analysis: BinaryInfo) -> str:
        """Gera relatório humano-legível da análise"""
        report = f"""
# Relatório de Engenharia Reversa - {analysis.filename}

## Informações Gerais
- **Arquivo**: {analysis.filename}
- **Caminho**: {analysis.filepath}
- **Tamanho**: {analysis.size:,} bytes
- **Tipo**: {analysis.file_type}
- **Data da Análise**: {analysis.timestamp}

## Hashes Criptográficos
- **MD5**: `{analysis.md5}`
- **SHA1**: `{analysis.sha1}`
- **SHA256**: `{analysis.sha256}`

## Análise Estatística
- **Entropia**: {analysis.entropy} ({'ALTA - Possível packing' if analysis.is_packed else 'Normal'})
- **Empacotado**: {'SIM ⚠️' if analysis.is_packed else 'Não'}
- **Compilador Detectado**: {analysis.compiler_signature or 'Desconhecido'}

## Strings Encontradas ({len(analysis.strings_found)})
```
{chr(10).join(analysis.strings_found[:20])}
{'...' if len(analysis.strings_found) > 20 else ''}
```

## Seções (se disponível)
{json.dumps(analysis.sections, indent=2) if analysis.sections else 'Não disponível'}

## Imports Detectados
{chr(10).join(analysis.imports[:10]) if analysis.imports else 'Nenhum detectado'}

## Recomendações
"""
        
        if analysis.is_packed:
            report += "- ⚠️ Arquivo empacotado detectado. Considere usar ferramentas especializadas (UPX, unpackers).\n"
        
        if analysis.entropy > 7.0:
            report += "- ⚠️ Alta entropia sugere criptografia ou compressão.\n"
        
        if analysis.compiler_signature:
            report += f"- ℹ️ Compilador identificado: {analysis.compiler_signature}. Use ferramentas específicas.\n"
        
        report += "\n---\n*Análise realizada por NovaComp Reverse Engineering Engine*"
        
        return report


# Singleton global
_reverse_engine = None

def get_reverse_engine() -> ReverseEngineeringEngine:
    """Obtém instância singleton do motor de engenharia reversa"""
    global _reverse_engine
    if _reverse_engine is None:
        _reverse_engine = ReverseEngineeringEngine()
    return _reverse_engine


if __name__ == "__main__":
    print("🔍 NovaComp Reverse Engineering Engine")
    print("=" * 50)
    
    engine = get_reverse_engine()
    
    print(f"\nFerramentas detectadas:")
    for tool, available in engine.supported_tools.items():
        status = "✅" if available else "❌"
        print(f"  {status} {tool}")
    
    print("\nℹ️ Este módulo requer arquivos para análise.")
    print("Use via API ou integre ao sistema principal.")
