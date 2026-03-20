"""
向量索引服务
用于题目相似度检索（重复检测、智能问答）
支持智能检测：只有题目变更或模型变更时才重新向量化
"""
import numpy as np
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VectorIndex:
    """
    向量索引服务
    使用余弦相似度进行快速检索
    向量直接存储在 questions 表中
    """
    
    def __init__(self, db_connection):
        """
        初始化向量索引
        
        Args:
            db_connection: SQLite 数据库连接
        """
        self.db = db_connection
        self._ensure_columns()
    
    def _ensure_columns(self):
        """确保向量相关列存在"""
        columns = ['embedding', 'embedding_version', 'content_hash', 'embedding_updated_at']
        for col in columns:
            try:
                self.db.execute(f"ALTER TABLE questions ADD COLUMN {col} TEXT")
            except:
                pass  # 列已存在
        # embedding 是 BLOB 类型，需要单独处理
        try:
            self.db.execute("ALTER TABLE questions ADD COLUMN embedding BLOB")
        except:
            pass  # 列已存在
    
    def _compute_content_hash(self, content: str, options: str = None) -> str:
        """
        计算题目内容的哈希值
        
        Args:
            content: 题干内容
            options: 选项（JSON 字符串）
            
        Returns:
            MD5 哈希值
        """
        hash_content = content.strip()
        if options:
            hash_content += f"|{options}"
        return hashlib.md5(hash_content.encode('utf-8')).hexdigest()
    
    def needs_reembedding(self, question_id: str, content: str, options: str, current_model_version: str) -> Tuple[bool, str]:
        """
        检查题目是否需要重新向量化
        
        Args:
            question_id: 题目 ID
            content: 题干内容
            options: 选项（JSON 字符串）
            current_model_version: 当前模型版本
            
        Returns:
            (是否需要重新向量化，原因)
        """
        # 获取题目当前的向量化信息
        row = self.db.fetch_one("""
            SELECT content_hash, embedding_version, embedding_updated_at
            FROM questions
            WHERE id = ?
        """, (question_id,))
        
        if not row:
            return True, "题目不存在"
        
        content_hash = row.get('content_hash')
        embedding_version = row.get('embedding_version')
        embedding_updated_at = row.get('embedding_updated_at')
        
        # 1. 检查是否有向量
        if content_hash is None or embedding_version is None:
            return True, "从未向量化"
        
        # 2. 计算当前内容哈希
        current_hash = self._compute_content_hash(content, options)
        
        # 3. 检查内容是否变更
        if content_hash != current_hash:
            return True, "题目内容已变更"
        
        # 检查模型版本是否变更
        if embedding_version != current_model_version:
            return True, f"模型版本变更（{embedding_version} → {current_model_version}）"
        
        # 检查向量是否存在
        embedding_row = self.db.fetch_one(
            "SELECT embedding FROM questions WHERE id = ?",
            (question_id,)
        )
        if not embedding_row or not embedding_row.get('embedding'):
            return True, "向量数据丢失"
        
        return False, "无需重新向量化"
    
    def update_embedding(self, question_id: str, embedding: np.ndarray, model_version: str, content: str, options: str = None):
        """
        更新题目向量
        
        Args:
            question_id: 题目 ID
            embedding: 向量数组
            model_version: 模型版本标识
            content: 题干内容
            options: 选项（JSON 字符串）
        """
        now = datetime.now().isoformat()
        embedding_bytes = embedding.astype(np.float32).tobytes()
        content_hash = self._compute_content_hash(content, options)
        
        self.db.execute("""
            UPDATE questions
            SET embedding = ?,
                embedding_version = ?,
                content_hash = ?,
                embedding_updated_at = ?
            WHERE id = ?
        """, (embedding_bytes, model_version, content_hash, now, question_id))
        
        logger.info(f"更新题目向量：question_id={question_id}, model_version={model_version}, dimension={len(embedding)}")
    
    def get_embedding(self, question_id: str) -> Optional[np.ndarray]:
        """获取题目向量"""
        row = self.db.fetch_one(
            "SELECT embedding FROM questions WHERE id = ?",
            (question_id,)
        )
        
        if not row or not row.get('embedding'):
            return None
        
        embedding_bytes = row['embedding']
        return np.frombuffer(embedding_bytes, dtype=np.float32)
    
    def search_similar(
        self, 
        embedding: np.ndarray, 
        threshold: float = 0.95,
        top_k: int = 10,
        exclude_ids: Optional[List[str]] = None
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
        # 获取所有有向量的题目
        query = """
            SELECT id, content, embedding 
            FROM questions 
            WHERE embedding IS NOT NULL
        """
        params = []
        
        if exclude_ids:
            placeholders = ','.join('?' * len(exclude_ids))
            query += f" AND id NOT IN ({placeholders})"
            params.extend(exclude_ids)
        
        rows = self.db.fetch_all(query, params)
        
        if not rows:
            return []
        
        # 计算相似度
        similar_questions = []
        query_norm = np.linalg.norm(embedding)
        
        for row in rows:
            question_id = row['id']
            content = row['content']
            emb_bytes = row['embedding']
            
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
                    'content': content
                })
        
        # 按相似度排序
        similar_questions.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 限制返回数量
        similar_questions = similar_questions[:top_k]
        
        logger.info(f"检索相似题目：threshold={threshold}, found={len(similar_questions)}")
        
        return similar_questions
    
    def get_stats(self) -> Dict:
        """获取索引统计信息"""
        total = self.db.fetch_one("SELECT COUNT(*) as total FROM questions")['total']
        with_embedding = self.db.fetch_one("SELECT COUNT(*) as total FROM questions WHERE embedding IS NOT NULL")['total']
        
        # 获取版本分布
        version_rows = self.db.fetch_all("""
            SELECT 
                embedding_version,
                COUNT(*) as total,
                MAX(embedding_updated_at) as last_updated
            FROM questions
            WHERE embedding_version IS NOT NULL
            GROUP BY embedding_version
        """)
        
        return {
            'total_questions': total,
            'with_embedding': with_embedding,
            'without_embedding': total - with_embedding,
            'versions': [
                {
                    'version': row['embedding_version'] or 'unknown',
                    'count': row['total'],
                    'last_updated': row['last_updated']
                }
                for row in version_rows if row['embedding_version']
            ]
        }
    
    def get_missing_embeddings(self) -> List[Dict]:
        """获取未向量化的题目列表"""
        return self.db.fetch_all("""
            SELECT id, content, category_id, created_at
            FROM questions
            WHERE embedding IS NULL
            ORDER BY created_at
        """)
    
    def get_mismatched_embeddings(self, current_model_version: str) -> List[Dict]:
        """获取模型版本不匹配的题目列表"""
        return self.db.fetch_all("""
            SELECT id, content, category_id, embedding_version, embedding_updated_at
            FROM questions
            WHERE embedding IS NOT NULL
            AND (embedding_version IS NULL OR embedding_version != ?)
            ORDER BY embedding_updated_at
        """, (current_model_version,))
    
    def rebuild_all(self, embedding_service, model_version: str, batch_size: int = 100):
        """
        重建所有题目的向量
        
        Args:
            embedding_service: EmbeddingService 实例
            model_version: 模型版本标识
            batch_size: 批次大小
        """
        logger.info("开始重建所有题目向量...")
        
        # 获取所有题目
        all_questions = self.db.fetch_all("""
            SELECT id, content, options
            FROM questions
            ORDER BY created_at
        """)
        
        total = len(all_questions)
        processed = 0
        errors = 0
        
        for i, question in enumerate(all_questions):
            try:
                embedding = embedding_service.embed(question['content'])
                self.update_embedding(
                    question['id'],
                    embedding,
                    model_version,
                    question['content'],
                    question['options']
                )
                processed += 1
                
                if (i + 1) % batch_size == 0:
                    logger.info(f"进度：{i + 1}/{total} ({(i + 1) / total * 100:.1f}%)")
                    
            except Exception as e:
                logger.error(f"处理题目 {question['id']} 失败：{e}")
                errors += 1
        
        logger.info(f"重建完成：成功={processed}, 失败={errors}, 总计={total}")
        
        return {
            'total': total,
            'processed': processed,
            'errors': errors
        }


# 单例实例（延迟初始化）
_vector_index: Optional[VectorIndex] = None


def get_vector_index(db_connection):
    """获取向量索引单例"""
    global _vector_index
    if _vector_index is None:
        _vector_index = VectorIndex(db_connection)
    return _vector_index
