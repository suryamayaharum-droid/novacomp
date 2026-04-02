"""
NovaComp - Agente Executor de Tarefas
Habilidades de automação e execução segura
"""

import asyncio
import subprocess
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import shlex


class TaskExecutorAgent:
    """
    Agente especializado em execução de tarefas.
    
    Responsabilidades:
    - Executar comandos de forma segura
    - Automatizar tarefas repetitivas
    - Monitorar execução de processos
    - Reportar resultados
    """
    
    def __init__(self, safe_mode: bool = True):
        self.safe_mode = safe_mode
        self.execution_log: List[Dict] = []
        self.allowed_commands = [
            'ls', 'dir', 'pwd', 'echo', 'cat', 'head', 'tail',
            'grep', 'find', 'python', 'pip', 'git', 'curl', 'wget'
        ]
        self.blocked_patterns = [
            'rm -rf', 'sudo', 'chmod 777', 'dd if=', '> /dev/',
            'mkfs', 'fdisk', 'shutdown', 'reboot'
        ]
        
    def _is_command_safe(self, command: str) -> tuple[bool, str]:
        """Verifica se comando é seguro para execução"""
        
        # Verifica padrões bloqueados
        for pattern in self.blocked_patterns:
            if pattern in command.lower():
                return False, f"Comando contém padrão bloqueado: {pattern}"
        
        if self.safe_mode:
            # Extrai comando base
            parts = shlex.split(command)
            if not parts:
                return False, "Comando vazio"
            
            base_command = parts[0]
            
            # Verifica se está na lista de permitidos
            if base_command not in self.allowed_commands:
                return False, f"Comando não permitido: {base_command}"
        
        return True, "Comando seguro"
    
    async def execute(self, 
                     command: str, 
                     timeout: int = 30,
                     cwd: Optional[str] = None) -> Dict:
        """
        Executa comando com segurança.
        
        Args:
            command: Comando a executar
            timeout: Timeout em segundos
            cwd: Diretório de trabalho
        
        Returns:
            Resultado da execução
        """
        
        start_time = datetime.now()
        
        # Verifica segurança
        is_safe, safety_msg = self._is_command_safe(command)
        if not is_safe:
            result = {
                'success': False,
                'error': safety_msg,
                'blocked': True,
                'command': command,
                'timestamp': start_time.isoformat()
            }
            self.execution_log.append(result)
            return result
        
        try:
            # Executa comando
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                result = {
                    'success': process.returncode == 0,
                    'return_code': process.returncode,
                    'stdout': stdout.decode('utf-8', errors='replace'),
                    'stderr': stderr.decode('utf-8', errors='replace'),
                    'duration_seconds': duration,
                    'command': command,
                    'timestamp': start_time.isoformat()
                }
                
            except asyncio.TimeoutError:
                process.kill()
                result = {
                    'success': False,
                    'error': f'Timeout após {timeout} segundos',
                    'command': command,
                    'timestamp': start_time.isoformat()
                }
            
            self.execution_log.append(result)
            return result
            
        except Exception as e:
            result = {
                'success': False,
                'error': str(e),
                'command': command,
                'timestamp': start_time.isoformat()
            }
            self.execution_log.append(result)
            return result
    
    async def run_script(self, 
                        script_path: str, 
                        args: Optional[List[str]] = None) -> Dict:
        """Executa script Python"""
        
        path = Path(script_path)
        if not path.exists():
            return {
                'success': False,
                'error': f'Script não encontrado: {script_path}'
            }
        
        command = f"python {script_path}"
        if args:
            command += " " + " ".join(args)
        
        return await self.execute(command)
    
    async def read_file(self, file_path: str, max_lines: int = 100) -> Dict:
        """Lê conteúdo de arquivo"""
        
        path = Path(file_path)
        if not path.exists():
            return {
                'success': False,
                'error': f'Arquivo não encontrado: {file_path}'
            }
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line)
            
            return {
                'success': True,
                'content': ''.join(lines),
                'lines_read': len(lines),
                'truncated': len(lines) >= max_lines,
                'file_path': str(path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def write_file(self, 
                        file_path: str, 
                        content: str,
                        append: bool = False) -> Dict:
        """Escreve conteúdo em arquivo"""
        
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'file_path': str(path),
                'bytes_written': len(content.encode('utf-8'))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def list_directory(self, dir_path: str = ".") -> Dict:
        """Lista conteúdo de diretório"""
        
        try:
            path = Path(dir_path)
            if not path.exists():
                return {
                    'success': False,
                    'error': f'Diretório não encontrado: {dir_path}'
                }
            
            items = []
            for item in path.iterdir():
                items.append({
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': item.stat().st_size if item.is_file() else 0
                })
            
            return {
                'success': True,
                'directory': str(path.absolute()),
                'items': items,
                'total_items': len(items)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_execution_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de execuções"""
        return self.execution_log[-limit:]
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do agente"""
        
        total_executions = len(self.execution_log)
        successful = sum(1 for log in self.execution_log if log.get('success', False))
        blocked = sum(1 for log in self.execution_log if log.get('blocked', False))
        
        return {
            'total_executions': total_executions,
            'successful': successful,
            'failed': total_executions - successful - blocked,
            'blocked': blocked,
            'success_rate': successful / total_executions if total_executions > 0 else 0,
            'safe_mode': self.safe_mode
        }


class LearningAgent:
    """
    Agente especializado em aprendizado contínuo.
    
    Responsabilidades:
    - Analisar experiências passadas
    - Identificar padrões
    - Sugerir melhorias
    - Consolidar conhecimento
    """
    
    def __init__(self):
        self.learning_sessions: List[Dict] = []
        self.patterns_discovered: List[Dict] = []
        
    async def analyze_experience(self, experience: Dict) -> Dict:
        """Analisa experiência para extrair aprendizado"""
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'experience_type': experience.get('category', 'unknown'),
            'outcome': 'positive' if experience.get('success', False) else 'negative',
            'lessons_learned': [],
            'suggestions': []
        }
        
        # Extrai lições
        if experience.get('success'):
            analysis['lessons_learned'].append(
                "Estratégia bem-sucedida identificada"
            )
        else:
            analysis['lessons_learned'].append(
                "Identificar causa da falha para evitar repetição"
            )
            analysis['suggestions'].append(
                "Revisar abordagem e tentar alternativa"
            )
        
        self.learning_sessions.append(analysis)
        return analysis
    
    async def discover_patterns(self, experiences: List[Dict]) -> List[Dict]:
        """Descobre padrões em experiências"""
        
        patterns = []
        
        # Agrupa por tipo
        by_type = {}
        for exp in experiences:
            exp_type = exp.get('category', 'general')
            if exp_type not in by_type:
                by_type[exp_type] = []
            by_type[exp_type].append(exp)
        
        # Analisa cada grupo
        for exp_type, exps in by_type.items():
            if len(exps) >= 3:
                success_rate = sum(1 for e in exps if e.get('success', False)) / len(exps)
                
                pattern = {
                    'type': exp_type,
                    'occurrences': len(exps),
                    'success_rate': success_rate,
                    'trend': 'improving' if success_rate > 0.6 else 'needs_work',
                    'discovered_at': datetime.now().isoformat()
                }
                
                patterns.append(pattern)
                self.patterns_discovered.append(pattern)
        
        return patterns
    
    def get_learning_stats(self) -> Dict:
        """Retorna estatísticas de aprendizado"""
        
        return {
            'total_sessions': len(self.learning_sessions),
            'patterns_discovered': len(self.patterns_discovered),
            'recent_sessions': self.learning_sessions[-10:]
        }
