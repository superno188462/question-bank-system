"""
向量索引服务
用于题目相似度检索（重复检测、智能问答）
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VectorIndex:
    """
    向量索引服务
    使用余弦相似度进行快速检索
    """
    
    def __init__(self, db_connection):
        """
        初始化向量索引
        
        Args:
            db_connection: SQLite 数据库连接
        """
        self.db = db_connection
        self._ensure_table()
    
    def _ensure_table(self):
        """确保向量表存在"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS question_embeddings (
                question_id INTEGER PRIMARY KEY,
                embedding BLOB NOT NULL,
                dimension INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        self.db.commit()
    
    def add(self, question_id: int, embedding: np.ndarray):
        """
        添加题目向量
        
        Args:
            question_id: 题目 ID
            embedding: 向量数组
        """
        now = datetime.now().isoformat()
        embedding_bytes = embedding.astype(np.float32).tobytes()
        dimension = len(embedding)
        
        self.db.execute("""
            INSERT OR REPLACE INTO question_embeddings 
            (question_id, embedding, dimension, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (question_id, embedding_bytes, dimension, now, now))
        self.db.commit()
        
        logger.info(f"添加题目向量：question_id={question_id}, dimension={dimension}")
    
    def delete(self, question_id: int):
        """删除题目向量"""
        self.db.execute(
            "DELETE FROM question_embeddings WHERE question_id = ?",
            (question_id,)
        )
        self.db.commit()
    
    def get(self, question_id: int) -> Optional[np.ndarray]:
        """获取题目向量"""
        cursor = self.db.execute(
            "SELECT embedding, dimension FROM question_embeddings WHERE question_id = ?",
            (question_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        embedding_bytes, dimension = row
        return np.frombuffer(embedding_bytes, dtype=np.float32)
    
    def search_similar(
        self, 
        embedding: np.ndarray, 
        threshold: float = 0.95,
        top_k: int = 10,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        检索相似题目
        
        Args:
            embedding: 查询向量
            threshold: 相似度阈值（0-1，越高越严格）
            top_k: 返回最多结果数
            exclude_ids: 排除的题目 ID 列表
            
        Returns:
            相似题目列表：[{question_id, similarity, content}, ...]
        """
        # 获取所有向量
        query = "SELECT question_id, embedding, dimension FROM question_embeddings"
        params = []
        
        if exclude_ids:
            placeholders = ','.join('?' * len(exclude_ids))
            query += f" WHERE question_id NOT IN ({placeholders})"
            params.extend(exclude_ids)
        
        cursor = self.db.execute(query, params)
        rows = cursor.fetchall()
        
        if not rows:
            return []
        
        # 计算相似度
        similar_questions = []
        query_norm = np.linalg.norm(embedding)
        
        for question_id, emb_bytes, dimension in rows:
            emb = np.frombuffer(emb_bytes, dtype=np.float32)
            
            # 余弦相似度
            emb_norm = np.linalg.norm(emb)
            if emb_norm == 0 or query_norm == 0:
                continue
            
            similarity = np.dot(embedding, emb) / (query_norm * emb_norm)
            
            if similarity >= threshold:
                similar_questions.append({
                    'question_id': question_id,
                    'similarity': float(similarity),
                    'dimension': dimension
                })
        
        # 按相似度排序
        similar_questions.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 限制返回数量
        similar_questions = similar_questions[:top_k]
        
        logger.info(f"检索相似题目：threshold={threshold}, found={len(similar_questions)}")
        
        return similar_questions
    
    def get_stats(self) -> Dict:
        """获取索引统计信息"""
        cursor = self.db.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(dimension) as avg_dimension,
                MIN(created_at) as first_created,
                MAX(created_at) as last_created
            FROM question_embeddings
        """)
        row = cursor.fetchone()
        
        return {
            'total_vectors': row[0] or 0,
            'avg_dimension': row[1] or 0,
            'first_created': row[2],
            'last_created': row[3]
        }
    
    def rebuild_index(self, questions: List[Dict], embedding_service):
        """
        重建索引（批量添加）
        
        Args:
            questions: 题目列表 [{id, content}, ...]
            embedding_service: EmbeddingService 实例
        """
        logger.info(f"开始重建索引，题目数：{len(questions)}")
        
        for i, question in enumerate(questions):
            try:
                embedding = embedding_service.embed(question['content'])
                self.add(question['id'], embedding)
                
                if (i + 1) % 100 == 0:
                    logger.info(f"已处理 {i + 1}/{len(questions)} 题目")
            except Exception as e:
                logger.error(f"处理题目 {question['id']} 失败：{e}")
        
        logger.info(f"索引重建完成，共 {len(questions)} 题目")


# 单例实例（延迟初始化）
_vector_index: Optional[VectorIndex] = None


def get_vector_index(db_connection):
    """获取向量索引单例"""
    global _vector_index
    if _vector_index is None:
        _vector_index = VectorIndex(db_connection)
    return _vector_index
