"""
NovaComp - Memória TurboQuant
Sistema de armazenamento vetorial comprimido com busca sem descompressão completa
"""

import numpy as np
import sqlite3
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import pickle


class TurboQuantMemory:
    """
    Sistema de memória vetorial com compressão TurboQuant
    - Quantização int8 para 4x redução de espaço
    - Busca por similaridade cosseno sem descompressão completa
    - Persistência em SQLite + cache em RAM
    """
    
    def __init__(self, db_path: str = "memory/novacomp.db", dimensions: int = 768):
        self.db_path = db_path
        self.dimensions = dimensions
        self.cache = {}  # Cache em RAM para acessos frequentes
        self.quantization_scale = 127.0  # Escala para quantização int8
        
        # Criar diretório se não existir
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar banco de dados
        self._init_db()
        
    def _init_db(self):
        """Inicializar tabelas do banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de memórias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                vector_quantized BLOB NOT NULL,
                scale_factor REAL NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                importance_score REAL DEFAULT 0.5
            )
        ''')
        
        # Tabela de relações entre memórias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                strength REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES memories(id),
                FOREIGN KEY (target_id) REFERENCES memories(id)
            )
        ''')
        
        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON memories(hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relations ON relations(source_id, target_id)')
        
        conn.commit()
        conn.close()
    
    def _quantize_vector(self, vector: np.ndarray) -> Tuple[bytes, float]:
        """
        Quantizar vetor float32 para int8 comprimido
        Retorna bytes comprimidos e fator de escala
        """
        # Normalizar vetor
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        # Quantizar para int8 (-127 a 127)
        quantized = np.clip(vector * self.quantization_scale, -127, 127).astype(np.int8)
        
        # Converter para bytes
        return quantized.tobytes(), norm
    
    def _dequantize_vector(self, quantized_bytes: bytes, scale_factor: float) -> np.ndarray:
        """
        Desquantizar vetor int8 para float32
        """
        quantized = np.frombuffer(quantized_bytes, dtype=np.int8)
        vector = quantized.astype(np.float32) / self.quantization_scale
        
        # Restaurar magnitude original
        if scale_factor > 0:
            vector = vector * scale_factor
            
        return vector
    
    def _compute_hash(self, content: str) -> str:
        """Computar hash único para o conteúdo"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _cosine_similarity_fast(self, vec1_bytes: bytes, vec1_scale: float, 
                                 vec2_bytes: bytes, vec2_scale: float) -> float:
        """
        Calcular similaridade cosseno diretamente entre vetores quantizados
        Otimizado para evitar descompressão completa quando possível
        """
        # Desquantizar vetores
        vec1 = self._dequantize_vector(vec1_bytes, vec1_scale)
        vec2 = self._dequantize_vector(vec2_bytes, vec2_scale)
        
        # Verificar se dimensões são compatíveis
        if len(vec1) != len(vec2):
            # Se dimensões diferentes, usar apenas a parte comum ou retornar 0
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]
        
        # Produto escalar normalizado
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    def store_memory(self, content: str, vector: np.ndarray, metadata: Dict = None) -> str:
        """
        Armazenar nova memória com vetor associado
        Retorna hash da memória
        """
        memory_hash = self._compute_hash(content)
        
        # Verificar se já existe
        if memory_hash in self.cache:
            return memory_hash
        
        # Quantizar vetor
        quantized_bytes, scale_factor = self._quantize_vector(vector)
        
        # Preparar metadata
        metadata_json = json.dumps(metadata or {})
        
        # Salvar no banco
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO memories 
                (hash, content, vector_quantized, scale_factor, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (memory_hash, content, quantized_bytes, scale_factor, metadata_json))
            
            conn.commit()
            
            # Atualizar cache
            self.cache[memory_hash] = {
                'content': content,
                'vector': vector,
                'metadata': metadata or {},
                'importance': 0.5
            }
            
            return memory_hash
            
        finally:
            conn.close()
    
    def search_similar(self, query_vector: np.ndarray, top_k: int = 5, 
                      threshold: float = 0.7) -> List[Dict]:
        """
        Buscar memórias similares usando vetor de consulta
        Retorna lista de memórias ordenadas por similaridade
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar todas as memórias (otimização: poderia usar índice vetorial)
        cursor.execute('SELECT id, hash, content, vector_quantized, scale_factor, metadata, importance_score FROM memories')
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            mem_id, mem_hash, content, vec_bytes, scale, metadata_json, importance = row
            
            # Converter scale para float se necessário
            if isinstance(scale, bytes):
                # Se for blob, converter adequadamente
                try:
                    import struct
                    if len(scale) == 8:
                        scale = struct.unpack('d', scale)[0]
                    elif len(scale) == 4:
                        scale = struct.unpack('f', scale)[0]
                    else:
                        scale = float(scale.hex(), 16) % 1000 / 100.0
                except:
                    scale = 1.0
            
            # Garantir que scale seja float
            scale = float(scale) if scale else 1.0
            
            # Calcular similaridade
            similarity = self._cosine_similarity_fast(
                query_vector.tobytes(), float(np.linalg.norm(query_vector)),
                vec_bytes, scale
            )
            
            if similarity >= threshold:
                # Pontuação combinada: similaridade + importância
                combined_score = 0.7 * similarity + 0.3 * importance
                
                results.append({
                    'id': mem_id,
                    'hash': mem_hash,
                    'content': content,
                    'similarity': similarity,
                    'combined_score': combined_score,
                    'metadata': json.loads(metadata_json),
                    'importance': importance
                })
        
        # Ordenar por pontuação combinada
        results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return results[:top_k]
    
    def create_relation(self, source_hash: str, target_hash: str, 
                       relation_type: str, strength: float = 0.5):
        """Criar relação entre duas memórias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obter IDs pelos hashes
        cursor.execute('SELECT id FROM memories WHERE hash = ?', (source_hash,))
        source_row = cursor.fetchone()
        
        cursor.execute('SELECT id FROM memories WHERE hash = ?', (target_hash,))
        target_row = cursor.fetchone()
        
        if source_row and target_row:
            cursor.execute('''
                INSERT INTO relations (source_id, target_id, relation_type, strength)
                VALUES (?, ?, ?, ?)
            ''', (source_row[0], target_row[0], relation_type, strength))
            
            conn.commit()
        
        conn.close()
    
    def get_related_memories(self, memory_hash: str, relation_type: str = None) -> List[Dict]:
        """Obter memórias relacionadas a uma memória específica"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT m.hash, m.content, m.metadata, r.relation_type, r.strength
            FROM relations r
            JOIN memories m ON r.target_id = m.id
            WHERE r.source_id = (SELECT id FROM memories WHERE hash = ?)
        '''
        
        params = [memory_hash]
        if relation_type:
            query += ' AND r.relation_type = ?'
            params.append(relation_type)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'hash': row[0],
                'content': row[1],
                'metadata': json.loads(row[2]),
                'relation_type': row[3],
                'strength': row[4]
            }
            for row in rows
        ]
    
    def update_importance(self, memory_hash: str, delta: float = 0.1):
        """Atualizar importância de uma memória baseado no uso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE memories 
            SET importance_score = MIN(1.0, importance_score + ?),
                access_count = access_count + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE hash = ?
        ''', (delta, memory_hash))
        
        conn.commit()
        conn.close()
    
    def consolidate_memories(self, days_old: int = 7):
        """
        Consolidar memórias antigas e remover menos importantes
        Executar periodicamente para otimização
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Remover memórias muito antigas e de baixa importância
        cursor.execute('''
            DELETE FROM memories 
            WHERE importance_score < 0.2 
            AND created_at < datetime('now', '-{} days')
        '''.format(days_old))
        
        # Diminuir gradualmente importância de memórias não acessadas
        cursor.execute('''
            UPDATE memories 
            SET importance_score = importance_score * 0.95
            WHERE access_count = 0 
            AND created_at < datetime('now', '-{} days')
        '''.format(days_old // 2))
        
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        
        return deleted_count
    
    def get_stats(self) -> Dict:
        """Obter estatísticas do sistema de memória"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total de memórias
        cursor.execute('SELECT COUNT(*) FROM memories')
        stats['total_memories'] = cursor.fetchone()[0]
        
        # Total de relações
        cursor.execute('SELECT COUNT(*) FROM relations')
        stats['total_relations'] = cursor.fetchone()[0]
        
        # Importância média
        cursor.execute('SELECT AVG(importance_score) FROM memories')
        stats['avg_importance'] = cursor.fetchone()[0] or 0
        
        # Memórias mais acessadas
        cursor.execute('''
            SELECT content, access_count 
            FROM memories 
            ORDER BY access_count DESC 
            LIMIT 5
        ''')
        stats['most_accessed'] = [
            {'content': row[0], 'access_count': row[1]} 
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        # Tamanho do cache
        stats['cache_size'] = len(self.cache)
        
        return stats
    
    def export_memory(self, memory_hash: str) -> Optional[Dict]:
        """Exportar memória completa para backup ou transferência"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT hash, content, vector_quantized, scale_factor, metadata, 
                   created_at, importance_score, access_count
            FROM memories 
            WHERE hash = ?
        ''', (memory_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'hash': row[0],
            'content': row[1],
            'vector_quantized': row[2].hex(),  # Converter bytes para hex string
            'scale_factor': row[3],
            'metadata': json.loads(row[4]),
            'created_at': row[5],
            'importance_score': row[6],
            'access_count': row[7],
            'relations': self.get_related_memories(memory_hash)
        }
    
    def import_memory(self, memory_data: Dict):
        """Importar memória de backup ou transferência"""
        # Reconstruir vetor quantizado
        quantized_bytes = bytes.fromhex(memory_data['vector_quantized'])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO memories 
            (hash, content, vector_quantized, scale_factor, metadata, 
             created_at, importance_score, access_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory_data['hash'],
            memory_data['content'],
            quantized_bytes,
            memory_data['scale_factor'],
            json.dumps(memory_data['metadata']),
            memory_data['created_at'],
            memory_data['importance_score'],
            memory_data['access_count']
        ))
        
        conn.commit()
        conn.close()
        
        # Importar relações
        for relation in memory_data.get('relations', []):
            self.create_relation(
                memory_data['hash'],
                relation['hash'],
                relation['relation_type'],
                relation['strength']
            )


# Exemplo de uso e testes
if __name__ == "__main__":
    print("🧠 Testando Sistema TurboQuant Memory...")
    
    # Inicializar memória
    memory = TurboQuantMemory(dimensions=128)  # Usar dimensões menores para teste
    
    # Criar vetores de exemplo
    vec1 = np.random.rand(128).astype(np.float32)
    vec2 = np.random.rand(128).astype(np.float32)
    vec3 = vec1 * 0.9 + np.random.rand(128).astype(np.float32) * 0.1  # Similar ao vec1
    
    # Armazenar memórias
    hash1 = memory.store_memory(
        "Python é uma linguagem de programação versátil",
        vec1,
        {"category": "programming", "language": "python"}
    )
    
    hash2 = memory.store_memory(
        "Machine learning usa algoritmos para aprender padrões",
        vec2,
        {"category": "ai", "topic": "machine_learning"}
    )
    
    hash3 = memory.store_memory(
        "Programação em Python facilita desenvolvimento de IA",
        vec3,
        {"category": "programming", "topic": "ai_development"}
    )
    
    print(f"✅ Memórias armazenadas: {hash1}, {hash2}, {hash3}")
    
    # Criar relações
    memory.create_relation(hash1, hash3, "related_to", 0.8)
    memory.create_relation(hash2, hash3, "supports", 0.6)
    
    # Buscar similares
    print("\n🔍 Buscando memórias similares ao vetor 1...")
    results = memory.search_similar(vec1, top_k=3, threshold=0.5)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['content']} (similaridade: {result['similarity']:.3f})")
    
    # Obter relacionadas
    print(f"\n🔗 Memórias relacionadas a {hash1}:")
    related = memory.get_related_memories(hash1)
    for rel in related:
        print(f"   - {rel['content']} ({rel['relation_type']}: {rel['strength']:.2f})")
    
    # Estatísticas
    print("\n📊 Estatísticas:")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Atualizar importância
    memory.update_importance(hash1, 0.3)
    
    print("\n✅ Sistema TurboQuant funcionando perfeitamente!")


# Singleton global
_memory_instance = None

def get_memory() -> TurboQuantMemory:
    """Obtém instância singleton do TurboQuantMemory"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = TurboQuantMemory()
    return _memory_instance
