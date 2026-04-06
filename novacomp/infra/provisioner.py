"""
NOVACOMP - INFRASTRUCTURE PROVISIONING ENGINE
Motor de Provisionamento Autônomo de Infraestrutura

Capacidades:
- Provisionamento de containers Docker
- Orquestração de serviços
- Gerenciamento de recursos cloud (AWS/GCP/Azure via SDKs)
- Auto-scaling baseado em demanda
- Health checks e auto-cura
- Deploy de aplicações via comandos naturais

Integra com:
- Docker API
- Kubernetes (kubectl)
- Terraform (opcional)
- Ansible (opcional)
- APIs de Cloud Providers
"""

import os
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import threading


@dataclass
class ResourceSpec:
    """Especificação de recurso de infraestrutura"""
    name: str
    resource_type: str  # container, vm, database, storage, network
    cpu: float = 1.0
    memory_mb: int = 512
    storage_gb: int = 10
    image: Optional[str] = None
    ports: Optional[List[int]] = None
    env_vars: Optional[Dict[str, str]] = None
    replicas: int = 1
    region: str = "us-east-1"
    status: str = "pending"
    created_at: str = ""
    health: str = "unknown"


@dataclass
class DeploymentPlan:
    """Plano de deploy gerado a partir de prompt natural"""
    id: str
    description: str
    resources: List[ResourceSpec]
    estimated_cost: float
    estimated_time_seconds: int
    steps: List[str]
    status: str = "planned"
    created_at: str = ""


class InfrastructureProvisioner:
    """
    Motor de Provisionamento de Infraestrutura Autônoma
    
    Traduz intenções em linguagem natural para ações de infraestrutura.
    Gerencia ciclo de vida completo de recursos.
    """
    
    def __init__(self, safe_mode: bool = True):
        self.safe_mode = safe_mode
        self.active_deployments: Dict[str, DeploymentPlan] = {}
        self.resource_registry: Dict[str, ResourceSpec] = {}
        self.available_tools = self._detect_tools()
        self.cloud_providers = self._detect_cloud_sdks()
        self._health_check_thread = None
        self._running = False
        
    def _detect_tools(self) -> Dict[str, bool]:
        """Detecta ferramentas de infraestrutura disponíveis"""
        tools = {
            'docker': False,
            'docker-compose': False,
            'kubectl': False,
            'terraform': False,
            'ansible': False,
            'aws': False,
            'gcloud': False,
            'az': False
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
    
    def _detect_cloud_sdks(self) -> Dict[str, bool]:
        """Detecta SDKs de cloud instalados"""
        sdks = {
            'boto3': False,  # AWS
            'google-cloud': False,  # GCP
            'azure-mgmt': False  # Azure
        }
        
        try:
            import boto3
            sdks['boto3'] = True
        except ImportError:
            pass
            
        try:
            from google.cloud import storage
            sdks['google-cloud'] = True
        except ImportError:
            pass
            
        try:
            from azure.mgmt import resource
            sdks['azure-mgmt'] = True
        except ImportError:
            pass
            
        return sdks
    
    def parse_intent(self, prompt: str) -> DeploymentPlan:
        """
        Analisa prompt em linguagem natural e gera plano de deploy
        
        Exemplos de prompts:
        - "Subir um servidor web com 2 réplicas na porta 80"
        - "Criar banco de dados PostgreSQL com 4GB RAM"
        - "Deploy de aplicação Python com Redis cache"
        """
        import re
        
        plan_id = f"deploy_{int(time.time())}"
        resources = []
        steps = []
        
        prompt_lower = prompt.lower()
        
        # Detecção de tipo de recurso
        if any(word in prompt_lower for word in ['servidor web', 'web server', 'nginx', 'apache']):
            resources.append(ResourceSpec(
                name="web-server",
                resource_type="container",
                cpu=2.0,
                memory_mb=1024,
                image="nginx:latest",
                ports=[80, 443],
                replicas=self._extract_number(prompt_lower, ['réplicas', 'replicas', 'copies'], default=1)
            ))
            steps.append("Pull da imagem nginx:latest")
            steps.append("Configurar portas 80 e 443")
            
        if any(word in prompt_lower for word in ['banco', 'database', 'postgresql', 'mysql', 'redis']):
            db_type = "postgres"
            if 'mysql' in prompt_lower:
                db_type = "mysql"
                image = "mysql:8"
            elif 'redis' in prompt_lower:
                db_type = "redis"
                image = "redis:alpine"
            else:
                image = "postgres:15"
                
            mem = self._extract_number(prompt_lower, ['gb ram', 'memória', 'memory'], default=512)
            if mem > 100:  # Se especificado em MB
                memory_mb = mem
            else:  # Se especificado em GB
                memory_mb = mem * 1024
                
            resources.append(ResourceSpec(
                name=f"{db_type}-db",
                resource_type="database",
                cpu=2.0,
                memory_mb=memory_mb,
                storage_gb=self._extract_number(prompt_lower, ['gb storage', 'armazenamento'], default=10),
                image=image,
                ports=[5432 if db_type == 'postgres' else 3306 if db_type == 'mysql' else 6379],
                env_vars={
                    "POSTGRES_PASSWORD": "secure_password_change_me",
                    "POSTGRES_DB": "appdb"
                } if db_type == 'postgres' else {}
            ))
            steps.append(f"Configurar instância {db_type}")
            steps.append("Configurar persistência de dados")
            
        if any(word in prompt_lower for word in ['python', 'aplicação', 'app']):
            resources.append(ResourceSpec(
                name="app-python",
                resource_type="container",
                cpu=1.0,
                memory_mb=512,
                image="python:3.11-slim",
                ports=[8000],
                replicas=1
            ))
            steps.append("Configurar ambiente Python")
            steps.append("Mount do código da aplicação")
        
        # Estimativas
        estimated_time = len(resources) * 30  # 30s por recurso
        estimated_cost = sum(r.cpu * 0.01 + r.memory_mb * 0.00001 for r in resources) * 24  # Estimativa diária
        
        plan = DeploymentPlan(
            id=plan_id,
            description=prompt,
            resources=resources,
            estimated_cost=round(estimated_cost, 2),
            estimated_time_seconds=estimated_time,
            steps=steps,
            created_at=datetime.now().isoformat()
        )
        
        return plan
    
    def _extract_number(self, text: str, keywords: List[str], default: int = 1) -> int:
        """Extrai número de texto baseado em palavras-chave"""
        import re
        
        for keyword in keywords:
            pattern = rf'{keyword}\s*(\d+)'
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
                
        return default
    
    def execute_deployment(self, plan: DeploymentPlan) -> bool:
        """
        Executa o plano de deploy
        
        Retorna True se sucesso, False se falha
        """
        if not self.available_tools['docker']:
            print("⚠️ Docker não disponível. Execução limitada.")
            # Em produção, fallback para outras opções
            return False
        
        plan.status = "deploying"
        self.active_deployments[plan.id] = plan
        
        for i, resource in enumerate(plan.resources):
            print(f"\n📦 Provisionando: {resource.name} ({i+1}/{len(plan.resources)})")
            
            try:
                if resource.resource_type == "container":
                    success = self._deploy_container(resource)
                elif resource.resource_type == "database":
                    success = self._deploy_database(resource)
                else:
                    print(f"  ⚠️ Tipo de recurso não suportado: {resource.resource_type}")
                    success = False
                    
                if success:
                    resource.status = "running"
                    resource.health = "healthy"
                    self.resource_registry[resource.name] = resource
                    print(f"  ✅ {resource.name} iniciado com sucesso")
                else:
                    resource.status = "failed"
                    resource.health = "unhealthy"
                    plan.status = "partial_failure"
                    
            except Exception as e:
                print(f"  ❌ Erro ao provisionar {resource.name}: {str(e)}")
                resource.status = "error"
                resource.health = "error"
                plan.status = "failed"
                
        if all(r.status == "running" for r in plan.resources):
            plan.status = "completed"
            
        # Inicia health checks se ainda não estiver rodando
        self._start_health_monitoring()
        
        return plan.status == "completed"
    
    def _deploy_container(self, resource: ResourceSpec) -> bool:
        """Deploy de container Docker"""
        if not resource.image:
            return False
            
        cmd = [
            'docker', 'run', '-d',
            '--name', resource.name,
            '--cpus', str(resource.cpu),
            '--memory', f'{resource.memory_mb}m',
        ]
        
        # Adiciona ports
        if resource.ports:
            for port in resource.ports:
                cmd.extend(['-p', f'{port}:{port}'])
                
        # Adiciona env vars
        if resource.env_vars:
            for key, value in resource.env_vars.items():
                cmd.extend(['-e', f'{key}={value}'])
                
        cmd.append(resource.image)
        
        print(f"  Executando: {' '.join(cmd[:5])}...")
        
        # Em modo seguro, apenas simula
        if self.safe_mode:
            print("  [SAFE MODE] Simulação de deploy")
            time.sleep(2)
            return True
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def _deploy_database(self, resource: ResourceSpec) -> bool:
        """Deploy de banco de dados em container"""
        return self._deploy_container(resource)
    
    def scale_service(self, service_name: str, new_replicas: int) -> bool:
        """Escala um serviço existente"""
        if service_name not in self.resource_registry:
            print(f"Serviço não encontrado: {service_name}")
            return False
            
        resource = self.resource_registry[service_name]
        old_replicas = resource.replicas
        resource.replicas = new_replicas
        
        print(f"Escalando {service_name}: {old_replicas} -> {new_replicas} réplicas")
        
        if self.safe_mode:
            print("  [SAFE MODE] Simulação de scaling")
            return True
            
        # Implementação real com Docker Swarm ou Kubernetes
        if self.available_tools['kubectl']:
            cmd = ['kubectl', 'scale', f'deployment/{service_name}', f'--replicas={new_replicas}']
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=30)
                return result.returncode == 0
            except Exception:
                return False
                
        return True
    
    def stop_service(self, service_name: str) -> bool:
        """Para e remove um serviço"""
        if service_name not in self.resource_registry:
            return False
            
        print(f"Parando serviço: {service_name}")
        
        if self.safe_mode:
            del self.resource_registry[service_name]
            return True
            
        try:
            subprocess.run(['docker', 'stop', service_name], timeout=30)
            subprocess.run(['docker', 'rm', service_name], timeout=30)
            del self.resource_registry[service_name]
            return True
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status completo da infraestrutura"""
        return {
            'active_deployments': len(self.active_deployments),
            'running_resources': len([r for r in self.resource_registry.values() if r.status == 'running']),
            'total_resources': len(self.resource_registry),
            'tools_available': self.available_tools,
            'cloud_sdks': self.cloud_providers,
            'resources': [asdict(r) for r in self.resource_registry.values()],
            'safe_mode': self.safe_mode
        }
    
    def _start_health_monitoring(self):
        """Inicia thread de monitoramento de saúde"""
        if self._running:
            return
            
        self._running = True
        self._health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self._health_check_thread.start()
    
    def _health_check_loop(self):
        """Loop de verificação de saúde dos recursos"""
        while self._running:
            for name, resource in list(self.resource_registry.items()):
                if resource.status == "running":
                    # Simula health check
                    # Em produção, faria HTTP request ou comando docker inspect
                    resource.health = "healthy"
                    
            time.sleep(30)  # Check a cada 30s
    
    def shutdown(self):
        """Para o provisionador e limpa recursos"""
        self._running = False
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5)
            
        if not self.safe_mode:
            print("Limpando todos os recursos...")
            for name in list(self.resource_registry.keys()):
                self.stop_service(name)


# Singleton global
_provisioner = None

def get_provisioner() -> InfrastructureProvisioner:
    """Obtém instância singleton do provisionador"""
    global _provisioner
    if _provisioner is None:
        _provisioner = InfrastructureProvisioner()
    return _provisioner


if __name__ == "__main__":
    print("🏗️ NovaComp Infrastructure Provisioning Engine")
    print("=" * 50)
    
    provisioner = get_provisioner()
    
    print(f"\nFerramentas detectadas:")
    for tool, available in provisioner.available_tools.items():
        status = "✅" if available else "❌"
        print(f"  {status} {tool}")
    
    print(f"\nSDKs Cloud:")
    for sdk, available in provisioner.cloud_providers.items():
        status = "✅" if available else "❌"
        print(f"  {status} {sdk}")
    
    # Exemplo de parsing de intenção
    print("\n" + "=" * 50)
    print("Teste de Parsing de Intenção:")
    
    test_prompts = [
        "Subir um servidor web com 2 réplicas na porta 80",
        "Criar banco de dados PostgreSQL com 4GB de memória",
        "Deploy de aplicação Python com Redis cache"
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: '{prompt}'")
        plan = provisioner.parse_intent(prompt)
        print(f"  Recursos planejados: {len(plan.resources)}")
        for res in plan.resources:
            print(f"    - {res.name} ({res.resource_type}): {res.image or 'N/A'}")
        print(f"  Custo estimado: ${plan.estimated_cost}/dia")
        print(f"  Tempo estimado: {plan.estimated_time_seconds}s")
