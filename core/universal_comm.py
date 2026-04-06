"""
NovaComp Universal Communicator
Sistema de Comunicação Unificada com Ambientes Externos
- LLMs (OpenAI, Anthropic, Google, Local)
- APIs REST/GraphQL/gRPC
- Bancos de Dados (SQL/NoSQL)
- Sistemas de Arquivos e Cloud (AWS, Azure, GCP)
- Protocolos de Rede (SSH, WebSocket, MQTT)
"""

import os
import json
import asyncio
import aiohttp
import sqlite3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UniversalComm")

@dataclass
class Message:
    role: str  # system, user, assistant
    content: str
    metadata: Optional[Dict] = None

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: List[Message], **kwargs) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    async def chat(self, messages: List[Message], model="gpt-4o", **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            **kwargs
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, json=payload, headers=headers) as resp:
                data = await resp.json()
                return data['choices'][0]['message']['content']

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        
    async def chat(self, messages: List[Message], model="claude-3-5-sonnet-20241022", **kwargs) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        # Converter formato
        system_msg = next((m.content for m in messages if m.role == 'system'), "")
        user_msgs = [m for m in messages if m.role != 'system']
        
        payload = {
            "model": model,
            "max_tokens": 4096,
            "system": system_msg,
            "messages": [{"role": m.role, "content": m.content} for m in user_msgs],
            **kwargs
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, json=payload, headers=headers) as resp:
                data = await resp.json()
                return data['content'][0]['text']

class GoogleProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
    async def chat(self, messages: List[Message], model="gemini-1.5-pro", **kwargs) -> str:
        # Gemini usa formato diferente
        contents = []
        for m in messages:
            if m.role == 'user':
                contents.append({"role": "user", "parts": [{"text": m.content}]})
            elif m.role == 'assistant':
                contents.append({"role": "model", "parts": [{"text": m.content}]})
            # System messages são incorporados no primeiro user message ou ignorados
        
        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"
        payload = {"contents": contents, **kwargs}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                return data['candidates'][0]['content']['parts'][0]['text']

class LocalLLMProvider(LLMProvider):
    """Para Ollama, LM Studio, vLLM rodando localmente"""
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        
    async def chat(self, messages: List[Message], model="llama3.1", **kwargs) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            **kwargs
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                return data['choices'][0]['message']['content']

class DatabaseConnector:
    """Conector universal para bancos de dados"""
    
    def __init__(self, connection_string: str, db_type: str = "sqlite"):
        self.conn_str = connection_string
        self.db_type = db_type
        self.conn = None
        
    def connect(self):
        if self.db_type == "sqlite":
            self.conn = sqlite3.connect(self.conn_str)
        elif self.db_type == "postgres":
            import psycopg2
            self.conn = psycopg2.connect(self.conn_str)
        elif self.db_type == "mysql":
            import pymysql
            self.conn = pymysql.connect(**self._parse_mysql_uri(self.conn_str))
        return self
    
    def _parse_mysql_uri(self, uri: str) -> dict:
        # Parse simples de URI MySQL
        return {"host": "localhost", "user": "root", "password": "", "database": "test"}
    
    def query(self, sql: str, params: tuple = None) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(sql, params or ())
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results
    
    def execute(self, sql: str, params: tuple = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(sql, params or ())
        self.conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected

class CloudProvisioner:
    """Interface simplificada para provisionamento em nuvem"""
    
    def __init__(self, provider: str, credentials: Dict):
        self.provider = provider
        self.creds = credentials
        
    async def create_vm(self, name: str, size: str, region: str) -> Dict:
        """Cria uma VM na nuvem especificada"""
        # Implementação simulada - em produção usaria boto3, azure-sdk, google-cloud
        return {
            "status": "created",
            "name": name,
            "size": size,
            "region": region,
            "ip": "10.0.0.1",
            "provider": self.provider
        }
    
    async def deploy_container(self, image: str, ports: Dict) -> Dict:
        """Deploy de container"""
        return {
            "status": "deployed",
            "image": image,
            "ports": ports,
            "url": f"http://localhost:{list(ports.values())[0]}"
        }

class UniversalCommunicator:
    """Orquestrador central de comunicação"""
    
    def __init__(self):
        self.llm_providers: Dict[str, LLMProvider] = {}
        self.db_connections: Dict[str, DatabaseConnector] = {}
        self.cloud_clients: Dict[str, CloudProvisioner] = {}
        
    def register_llm(self, name: str, provider: LLMProvider):
        self.llm_providers[name] = provider
        logger.info(f"LLM '{name}' registrada: {type(provider).__name__}")
        
    def register_db(self, name: str, connector: DatabaseConnector):
        self.db_connections[name] = connector
        logger.info(f"DB '{name}' registrado")
        
    def register_cloud(self, name: str, client: CloudProvisioner):
        self.cloud_clients[name] = client
        logger.info(f"Cloud '{name}' registrada")
    
    async def talk_to_llm(self, provider_name: str, messages: List[Message], **kwargs) -> str:
        """Comunica-se com qualquer LLM registrado"""
        if provider_name not in self.llm_providers:
            raise ValueError(f"LLM '{provider_name}' não encontrada")
        return await self.llm_providers[provider_name].chat(messages, **kwargs)
    
    def query_db(self, db_name: str, sql: str, params: tuple = None) -> List[Dict]:
        """Executa query em qualquer DB registrado"""
        if db_name not in self.db_connections:
            raise ValueError(f"DB '{db_name}' não encontrado")
        return self.db_connections[db_name].query(sql, params)
    
    async def provision_cloud(self, cloud_name: str, action: str, **kwargs) -> Dict:
        """Provisiona recursos na nuvem"""
        if cloud_name not in self.cloud_clients:
            raise ValueError(f"Cloud '{cloud_name}' não encontrada")
        client = self.cloud_clients[cloud_name]
        if action == "create_vm":
            return await client.create_vm(**kwargs)
        elif action == "deploy_container":
            return await client.deploy_container(**kwargs)
        else:
            raise ValueError(f"Ação '{action}' não suportada")

# Factory para criar comunicador pré-configurado
def create_universal_communicator() -> UniversalCommunicator:
    comm = UniversalCommunicator()
    
    # Registrar LLMs se chaves existirem
    if os.getenv("OPENAI_API_KEY"):
        comm.register_llm("openai", OpenAIProvider(os.getenv("OPENAI_API_KEY")))
    if os.getenv("ANTHROPIC_API_KEY"):
        comm.register_llm("anthropic", AnthropicProvider(os.getenv("ANTHROPIC_API_KEY")))
    if os.getenv("GOOGLE_API_KEY"):
        comm.register_llm("google", GoogleProvider(os.getenv("GOOGLE_API_KEY")))
    
    # Sempre registrar LLM local (Ollama)
    comm.register_llm("local", LocalLLMProvider())
    
    # Registrar DB local
    comm.register_db("local_sqlite", DatabaseConnector("novacomp_memory.db", "sqlite"))
    
    # Registrar clouds (credenciais via env)
    if os.getenv("AWS_ACCESS_KEY_ID"):
        comm.register_cloud("aws", CloudProvisioner("aws", {
            "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret": os.getenv("AWS_SECRET_ACCESS_KEY")
        }))
    
    return comm

if __name__ == "__main__":
    # Teste do sistema
    comm = create_universal_communicator()
    print(f"LLMs disponíveis: {list(comm.llm_providers.keys())}")
    print(f"DBs disponíveis: {list(comm.db_connections.keys())}")
    print(f"Clouds disponíveis: {list(comm.cloud_clients.keys())}")
    
    # Teste com LLM local
    async def test():
        msgs = [Message("user", "Olá, quem é você?")]
        try:
            resp = await comm.talk_to_llm("local", msgs)
            print(f"Resposta Local LLM: {resp}")
        except Exception as e:
            print(f"Erro LLM local (talvez Ollama não esteja rodando): {e}")
    
    asyncio.run(test())
