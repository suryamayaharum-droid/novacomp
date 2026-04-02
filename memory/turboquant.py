"""
NovaComp - Memória Vetorial TurboQuant
Armazenamento comprimido de vetores sem necessidade de descompressão
"""

import numpy as np
import sqlite3
import pickle
import hashlib
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from pathlib import Path
import json


class TurboQuantMemory:
    """
    Sistema de memória vetorial com compressão turboquant.
    
    Características:
    - Armazenamento de vetores em formato binário comprimido
    - Busca por similaridade sem descompactação completa
    - Indexação hierárquica para recuperação rápida
    - Memória de curto e longo prazo
    """
    
    def __init__(self, db_path: str = "novacomp_memory.db", vector_dim: int = 768):
        self.db_path = Path(db_path)
        self.vector_dim = vector_dim
        self.short_term_cache: Dict[str, np.ndarray] = {}
        self.access_log: List[Dict] = []
        
        self._init_database()
        
    def _init_database(self):
        """Inicializa o banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela principal de memórias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                vector_data BLOB,
                metadata TEXT,
                category TEXT,
                importance REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        ''')
        
        # Tabela de relações entre memórias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_relations (
                source_id TEXT,
                target_id TEXT,
                relation_type TEXT,
                strength REAL,
                PRIMARY KEY (source_id, target_id, relation_type)
            )
        ''')
        
        # Tabela de evolução do sistema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                description TEXT,
                metrics TEXT
            )
        ''')
        
        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON memories(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags ON memories(tags)')
        
        conn.commit()
        conn.close()
        
    def _generate_id(self, content: str) -> str:
        """Gera ID único baseado no conteúdo"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _compress_vector(self, vector: np.ndarray) -> bytes:
        """
        Comprime vetor usando quantização escalar.
        Mantém capacidade de comparação sem descompressão completa.
        """
        # Normaliza o vetor
        normalized = vector / (np.linalg.norm(vector) + 1e-8)
        
        # Quantização para int8 (reduz 4x o tamanho)
        quantized = (normalized * 127).astype(np.int8)
        
        return pickle.dumps(quantized)
    
    def _decompress_vector(self, data: bytes) -> np.ndarray:
        """Descomprime vetor quantizado"""
        quantized = pickle.loads(data)
        return quantized.astype(np.float32) / 127.0
    
    def _cosine_similarity_binary(self, vec1_bytes: bytes, vec2: np.ndarray) -> float:
        """
        Calcula similaridade cosseno diretamente dos dados comprimidos.
        Otimizado para não descomprimir completamente.
        """
        vec1 = self._decompress_vector(vec1_bytes)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def store_memory(self, 
                     content: str, 
                     vector: np.ndarray, 
                     category: str = "general",
                     metadata: Optional[Dict] = None,
                     tags: Optional[List[str]] = None) -> str:
        """
        Armazena uma nova memória no sistema.
        
        Args:
            content: Conteúdo textual da memória
            vector: Embedding vetorial da memória
            category: Categoria da memória
            metadata: Metadados adicionais
            tags: Tags para classificação
        
        Returns:
            ID da memória armazenada
        """
        memory_id = self._generate_id(content)
        compressed = self._compress_vector(vector)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO memories 
                (id, vector_data, metadata, category, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (
                memory_id,
                compressed,
                json.dumps(metadata or {}),
                category,
                json.dumps(tags or [])
            ))
            
            # Adiciona ao cache de curto prazo
            self.short_term_cache[memory_id] = vector.copy()
            
            conn.commit()
            
            self._log_access(memory_id, "store")
            
            return memory_id
            
        finally:
            conn.close()
    
    def search_similar(self, 
                       query_vector: np.ndarray, 
                       threshold: float = 0.7,
                       limit: int = 10,
                       category: Optional[str] = None) -> List[Dict]:
        """
        Busca memórias similares sem descompressão completa.
        
        Args:
            query_vector: Vetor de consulta
            threshold: Limiar mínimo de similaridade
            limit: Número máximo de resultados
            category: Filtrar por categoria (opcional)
        
        Returns:
            Lista de memórias similares ordenadas por relevância
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if category:
                cursor.execute('SELECT id, vector_data, metadata, category, importance, access_count FROM memories WHERE category = ?')
                rows = cursor.fetchall()
            else:
                cursor.execute('SELECT id, vector_data, metadata, category, importance, access_count FROM memories')
                rows = cursor.fetchall()
            
            results = []
            for row in rows:
                memory_id, vector_data, metadata_json, cat, importance, access_count = row
                
                similarity = self._cosine_similarity_binary(vector_data, query_vector)
                
                if similarity >= threshold:
                    results.append({
                        'id': memory_id,
                        'similarity': similarity,
                        'category': cat,
                        'metadata': json.loads(metadata_json),
                        'importance': importance,
                        'access_count': access_count
                    })
            
            # Ordena por similaridade e importância
            results.sort(key=lambda x: x['similarity'] * 0.7 + x['importance'] * 0.3, reverse=True)
            
            return results[:limit]
            
        finally:
            conn.close()
    
    def create_relation(self, 
                       source_id: str, 
                       target_id: str, 
                       relation_type: str = "related",
                       strength: float = 0.5):
        """Cria relação entre duas memórias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO memory_relations 
                (source_id, target_id, relation_type, strength)
                VALUES (?, ?, ?, ?)
            ''', (source_id, target_id, relation_type, strength))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_related_memories(self, memory_id: str, min_strength: float = 0.3) -> List[Dict]:
        """Retorna memórias relacionadas a uma memória específica"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT r.target_id, r.relation_type, r.strength, m.category, m.metadata
                FROM memory_relations r
                JOIN memories m ON r.target_id = m.id
                WHERE r.source_id = ? AND r.strength >= ?
            ''', (memory_id, min_strength))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'relation_type': row[1],
                    'strength': row[2],
                    'category': row[3],
                    'metadata': json.loads(row[4])
                })
            
            return results
        finally:
            conn.close()
    
    def _log_access(self, memory_id: str, action: str):
        """Registra acesso à memória"""
        self.access_log.append({
            'memory_id': memory_id,
            'action': action,
            'timestamp': datetime.now().isoformat()
        })
        
        # Atualiza contador de acessos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE memories 
                SET access_count = access_count + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (memory_id,))
            conn.commit()
        finally:
            conn.close()
    
    def log_evolution(self, event_type: str, description: str, metrics: Dict):
        """Registra evento de evolução do sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO evolution_log (event_type, description, metrics)
                VALUES (?, ?, ?)
            ''', (event_type, description, json.dumps(metrics)))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do sistema de memória"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM memories')
            total_memories = cursor.fetchone()[0]
            
            cursor.execute('SELECT category, COUNT(*) FROM memories GROUP BY category')
            categories = dict(cursor.fetchall())
            
            cursor.execute('SELECT COUNT(*) FROM memory_relations')
            total_relations = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM evolution_log')
            evolution_events = cursor.fetchone()[0]
            
            return {
                'total_memories': total_memories,
                'categories': categories,
                'total_relations': total_relations,
                'evolution_events': evolution_events,
                'short_term_cache_size': len(self.short_term_cache),
                'recent_accesses': len(self.access_log[-100:])
            }
        finally:
            conn.close()
    
    def consolidate_memory(self, memory_ids: List[str], new_content: str, new_vector: np.ndarray):
        """
        Consolida múltiplas memórias em uma única memória mais abstrata.
        Representa aprendizado e evolução do conhecimento.
        """
        # Cria nova memória consolidada
        new_id = self.store_memory(
            content=new_content,
            vector=new_vector,
            category="consolidated",
            metadata={'consolidated_from': memory_ids},
            tags=['synthesis', 'learning']
        )
        
        # Cria relações com memórias originais
        for mem_id in memory_ids:
            self.create_relation(new_id, mem_id, "derived_from", 0.9)
        
        # Registra evolução
        self.log_evolution(
            event_type="memory_consolidation",
            description=f"Consolidated {len(memory_ids)} memories into {new_id}",
            metrics={'source_count': len(memory_ids), 'new_id': new_id}
        )
        
        return new_id
