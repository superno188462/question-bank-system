"""
VectorIndex 测试
测试向量索引服务功能
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.services.vector_index import VectorIndex, get_vector_index


class MockDBConnection:
    """Mock 数据库连接用于测试"""
    
    def __init__(self):
        self.executed_queries = []
        self.fetch_one_result = None
        self.fetch_all_result = []
    
    def execute(self, query, params=None):
        self.executed_queries.append((query, params))
        return Mock()
    
    def fetch_one(self, query, params=None):
        self.executed_queries.append((query, params))
        return self.fetch_one_result
    
    def fetch_all(self, query, params=None):
        self.executed_queries.append((query, params))
        return self.fetch_all_result


class TestVectorIndexInit:
    """VectorIndex 初始化测试"""
    
    def test_init_creates_columns(self):
        """测试初始化时创建列"""
        mock_db = MockDBConnection()
        
        index = VectorIndex(mock_db)
        
        # 验证执行了 ALTER TABLE 语句
        assert len(mock_db.executed_queries) > 0
        
        # 验证尝试创建 embedding 相关列
        queries = [q[0] for q in mock_db.executed_queries]
        assert any('embedding' in q for q in queries)
    
    def test_init_handles_existing_columns(self):
        """测试处理已存在的列"""
        mock_db = MockDBConnection()
        
        # 模拟列已存在的情况（execute 抛出异常）
        def raise_exception(*args, **kwargs):
            raise Exception("Column already exists")
        
        mock_db.execute = raise_exception
        
        # 不应该抛出异常
        index = VectorIndex(mock_db)
        assert index is not None
    
    def test_init_stores_db_connection(self):
        """测试存储数据库连接"""
        mock_db = MockDBConnection()
        
        index = VectorIndex(mock_db)
        
        assert index.db is mock_db


class TestVectorIndexComputeContentHash:
    """内容哈希计算测试"""
    
    def test_compute_hash_with_content_only(self):
        """测试仅内容计算哈希"""
        mock_db = MockDBConnection()
        index = VectorIndex(mock_db)
        
        hash1 = index._compute_content_hash("测试题目")
        hash2 = index._compute_content_hash("测试题目")
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 哈希长度
    
    def test_compute_hash_with_options(self):
        """测试带选项计算哈希"""
        mock_db = MockDBConnection()
        index = VectorIndex(mock_db)
        
        hash1 = index._compute_content_hash("测试题目", '["A", "B"]')
        hash2 = index._compute_content_hash("测试题目", '["A", "B"]')
        hash3 = index._compute_content_hash("测试题目", '["C", "D"]')
        
        assert hash1 == hash2
        assert hash1 != hash3  # 选项不同，哈希不同
    
    def test_compute_hash_strips_whitespace(self):
        """测试去除空白"""
        mock_db = MockDBConnection()
        index = VectorIndex(mock_db)
        
        hash1 = index._compute_content_hash("  测试题目  ")
        hash2 = index._compute_content_hash("测试题目")
        
        assert hash1 == hash2
    
    def test_compute_hash_case_sensitive(self):
        """测试大小写敏感"""
        mock_db = MockDBConnection()
        index = VectorIndex(mock_db)
        
        hash1 = index._compute_content_hash("测试题目")
        hash2 = index._compute_content_hash("测试题目")  # 相同内容
        
        assert hash1 == hash2  # 相同内容哈希相同


class TestVectorIndexNeedsReembedding:
    """重新向量化检测测试"""
    
    def test_needs_reembedding_new_question(self):
        """测试新题目需要向量化"""
        mock_db = MockDBConnection()
        mock_db.fetch_one_result = None  # 题目不存在
        
        index = VectorIndex(mock_db)
        
        needs, reason = index.needs_reembedding(
            question_id="q1",
            content="测试题目",
            options='["A", "B"]',
            current_model_version="v1"
        )
        
        assert needs is True
        assert "不存在" in reason
    
    def test_needs_reembedding_never_embedded(self):
        """测试从未向量化的题目"""
        mock_db = MockDBConnection()
        mock_db.fetch_one_result = {
            'content_hash': None,
            'embedding_version': None,
            'embedding_updated_at': None
        }
        
        index = VectorIndex(mock_db)
        
        needs, reason = index.needs_reembedding(
            question_id="q1",
            content="测试题目",
            options='["A", "B"]',
            current_model_version="v1"
        )
        
        assert needs is True
        assert "从未" in reason
    
    def test_needs_reembedding_content_changed(self):
        """测试内容变更需要重新向量化"""
        mock_db = MockDBConnection()
        mock_db.fetch_one_result = {
            'content_hash': 'old_hash',
            'embedding_version': 'v1',
            'embedding_updated_at': '2024-01-01'
        }
        # 第二次调用返回 embedding
        mock_db.fetch_all_result = [{'embedding': b'\x00' * 128}]
        
        index = VectorIndex(mock_db)
        
        needs, reason = index.needs_reembedding(
            question_id="q1",
            content="新的测试题目",  # 内容不同
            options='["A", "B"]',
            current_model_version="v1"
        )
        
        assert needs is True
        assert "变更" in reason
    
    def test_needs_reembedding_model_version_changed(self):
        """测试模型版本变更需要重新向量化"""
        mock_db = MockDBConnection()
        content = "测试题目"
        options = '["A", "B"]'
        old_hash = MockDBConnection()  # 先创建实例计算哈希
        old_hash_val = VectorIndex._compute_content_hash(MockDBConnection(), content, options)
        
        mock_db.fetch_one_result = {
            'content_hash': old_hash_val,
            'embedding_version': 'v1',
            'embedding_updated_at': '2024-01-01'
        }
        
        # Mock embedding 存在
        def fetch_one_side_effect(query, params=None):
            if 'embedding' in query and 'content_hash' not in query:
                return {'embedding': b'\x00' * 128}
            return mock_db.fetch_one_result
        
        mock_db.fetch_one = fetch_one_side_effect
        
        index = VectorIndex(mock_db)
        
        needs, reason = index.needs_reembedding(
            question_id="q1",
            content=content,
            options=options,
            current_model_version="v2"  # 版本不同
        )
        
        assert needs is True
        assert "模型版本" in reason
    
    def test_needs_reembedding_no_changes(self):
        """测试无变更不需要重新向量化"""
        from core.services.vector_index import VectorIndex
        
        mock_db = MockDBConnection()
        content = "测试题目"
        options = '["A", "B"]'
        
        # 先创建 index 实例
        index = VectorIndex(mock_db)
        content_hash = index._compute_content_hash(content, options)
        
        mock_db.fetch_one_result = {
            'content_hash': content_hash,
            'embedding_version': 'v1',
            'embedding_updated_at': '2024-01-01'
        }
        
        # Mock embedding 存在
        def fetch_one_side_effect(query, params=None):
            if 'embedding' in query and 'content_hash' not in query:
                return {'embedding': b'\x00' * 128}
            return mock_db.fetch_one_result
        
        mock_db.fetch_one = fetch_one_side_effect
        
        needs, reason = index.needs_reembedding(
            question_id="q1",
            content=content,
            options=options,
            current_model_version="v1"
        )
        
        assert needs is False
        assert "无需" in reason or "不需要" in reason
    
    def test_needs_reembedding_embedding_missing(self):
        """测试向量丢失需要重新向量化"""
        from core.services.vector_index import VectorIndex
        
        mock_db = MockDBConnection()
        content = "测试题目"
        options = '["A", "B"]'
        
        # 先创建 index 实例
        index = VectorIndex(mock_db)
        content_hash = index._compute_content_hash(content, options)
        
        mock_db.fetch_one_result = {
            'content_hash': content_hash,
            'embedding_version': 'v1',
            'embedding_updated_at': '2024-01-01'
        }
        
        # Mock embedding 不存在
        def fetch_one_side_effect(query, params=None):
            if 'embedding' in query and 'content_hash' not in query:
                return None
            return mock_db.fetch_one_result
        
        mock_db.fetch_one = fetch_one_side_effect
        
        needs, reason = index.needs_reembedding(
            question_id="q1",
            content=content,
            options=options,
            current_model_version="v1"
        )
        
        assert needs is True
        assert "丢失" in reason or "不存在" in reason


class TestVectorIndexUpdateEmbedding:
    """向量更新测试"""
    
    def test_update_embedding_success(self):
        """测试更新向量成功"""
        mock_db = MockDBConnection()
        index = VectorIndex(mock_db)
        
        embedding = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        
        index.update_embedding(
            question_id="q1",
            embedding=embedding,
            model_version="v1",
            content="测试题目",
            options='["A", "B"]'
        )
        
        # 验证执行了 UPDATE 语句
        assert len(mock_db.executed_queries) > 0
        
        # 验证参数正确
        update_query = mock_db.executed_queries[-1]
        assert 'UPDATE' in update_query[0]
        assert update_query[1][4] == "q1"  # question_id
    
    def test_update_embedding_without_options(self):
        """测试不带选项更新向量"""
        mock_db = MockDBConnection()
        index = VectorIndex(mock_db)
        
        embedding = np.array([0.1, 0.2, 0.3])
        
        index.update_embedding(
            question_id="q1",
            embedding=embedding,
            model_version="v1",
            content="测试题目"
        )
        
        # 应该成功执行
        assert len(mock_db.executed_queries) > 0
    
    def test_update_embedding_stores_bytes(self):
        """测试向量以字节存储"""
        mock_db = MockDBConnection()
        index = VectorIndex(mock_db)
        
        embedding = np.array([0.1, 0.2, 0.3], dtype=np.float64)
        
        index.update_embedding(
            question_id="q1",
            embedding=embedding,
            model_version="v1",
            content="测试题目"
        )
        
        # 验证存储的是 float32 字节
        update_params = mock_db.executed_queries[-1][1]
        embedding_bytes = update_params[0]
        assert isinstance(embedding_bytes, bytes)


class TestVectorIndexGetEmbedding:
    """获取向量测试"""
    
    def test_get_embedding_success(self):
        """测试获取向量成功"""
        mock_db = MockDBConnection()
        
        # 创建测试向量
        original_embedding = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=np.float32)
        embedding_bytes = original_embedding.tobytes()
        
        mock_db.fetch_one_result = {'embedding': embedding_bytes}
        
        index = VectorIndex(mock_db)
        result = index.get_embedding("q1")
        
        assert result is not None
        assert isinstance(result, np.ndarray)
        assert len(result) == 5
        assert np.allclose(result, original_embedding)
    
    def test_get_embedding_not_found(self):
        """测试向量不存在"""
        mock_db = MockDBConnection()
        mock_db.fetch_one_result = None
        
        index = VectorIndex(mock_db)
        result = index.get_embedding("q1")
        
        assert result is None
    
    def test_get_embedding_empty(self):
        """测试向量为空"""
        mock_db = MockDBConnection()
        mock_db.fetch_one_result = {'embedding': None}
        
        index = VectorIndex(mock_db)
        result = index.get_embedding("q1")
        
        assert result is None


class TestVectorIndexSearchSimilar:
    """相似题目搜索测试"""
    
    def test_search_similar_no_results(self):
        """测试没有相似题目"""
        mock_db = MockDBConnection()
        mock_db.fetch_all_result = []
        
        index = VectorIndex(mock_db)
        embedding = np.array([0.1, 0.2, 0.3])
        
        results = index.search_similar(embedding)
        
        assert results == []
    
    def test_search_similar_with_high_similarity(self):
        """测试高相似度匹配"""
        mock_db = MockDBConnection()
        
        # 创建相似向量
        query_embedding = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        similar_embedding = np.array([0.99, 0.01, 0.0], dtype=np.float32)
        
        mock_db.fetch_all_result = [
            {
                'id': 'q1',
                'content': '相似题目',
                'embedding': similar_embedding.tobytes()
            }
        ]
        
        index = VectorIndex(mock_db)
        results = index.search_similar(query_embedding, threshold=0.9)
        
        assert len(results) > 0
        assert results[0]['question_id'] == 'q1'
        assert results[0]['similarity'] > 0.9
    
    def test_search_similar_with_low_similarity(self):
        """测试低相似度不匹配"""
        mock_db = MockDBConnection()
        
        query_embedding = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        different_embedding = np.array([0.0, 1.0, 0.0], dtype=np.float32)  # 正交向量
        
        mock_db.fetch_all_result = [
            {
                'id': 'q1',
                'content': '不同题目',
                'embedding': different_embedding.tobytes()
            }
        ]
        
        index = VectorIndex(mock_db)
        results = index.search_similar(query_embedding, threshold=0.9)
        
        assert results == []  # 相似度为 0，低于阈值
    
    def test_search_similar_exclude_ids(self):
        """测试排除指定题目"""
        from core.services.vector_index import VectorIndex
        
        mock_db = MockDBConnection()
        
        query_embedding = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        similar_embedding = np.array([0.99, 0.01, 0.0], dtype=np.float32)
        
        # 设置 mock 返回 q2（q1 应该被 SQL 排除）
        mock_db.fetch_all_result = [
            {
                'id': 'q2',
                'content': '题目 2',
                'embedding': similar_embedding.tobytes()
            }
        ]
        
        index = VectorIndex(mock_db)
        results = index.search_similar(query_embedding, exclude_ids=['q1'])
        
        # 验证 SQL 查询包含 NOT IN
        queries = [q[0] for q in mock_db.executed_queries]
        assert any('NOT IN' in q for q in queries)
        
        # 验证参数包含排除的 ID
        for query, params in mock_db.executed_queries:
            if 'NOT IN' in query:
                assert 'q1' in params
    
    def test_search_similar_respects_top_k(self):
        """测试限制返回数量"""
        mock_db = MockDBConnection()
        
        query_embedding = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        similar_embedding = np.array([0.99, 0.01, 0.0], dtype=np.float32)
        
        # 创建 10 个相似题目
        mock_db.fetch_all_result = [
            {
                'id': f'q{i}',
                'content': f'题目{i}',
                'embedding': similar_embedding.tobytes()
            }
            for i in range(10)
        ]
        
        index = VectorIndex(mock_db)
        results = index.search_similar(query_embedding, top_k=3)
        
        assert len(results) <= 3
    
    def test_search_similar_sorted_by_similarity(self):
        """测试按相似度排序"""
        mock_db = MockDBConnection()
        
        query_embedding = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        
        # 创建不同相似度的向量
        mock_db.fetch_all_result = [
            {
                'id': 'q1',
                'content': '题目 1',
                'embedding': np.array([0.7, 0.3, 0.0], dtype=np.float32).tobytes()
            },
            {
                'id': 'q2',
                'content': '题目 2',
                'embedding': np.array([0.9, 0.1, 0.0], dtype=np.float32).tobytes()
            },
            {
                'id': 'q3',
                'content': '题目 3',
                'embedding': np.array([0.5, 0.5, 0.0], dtype=np.float32).tobytes()
            }
        ]
        
        index = VectorIndex(mock_db)
        results = index.search_similar(query_embedding, threshold=0.5)
        
        # 验证按相似度降序排列
        similarities = [r['similarity'] for r in results]
        assert similarities == sorted(similarities, reverse=True)
    
    def test_search_similar_zero_norm_handling(self):
        """测试零范数处理"""
        mock_db = MockDBConnection()
        
        query_embedding = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        zero_embedding = np.array([0.0, 0.0, 0.0], dtype=np.float32)  # 零向量
        
        mock_db.fetch_all_result = [
            {
                'id': 'q1',
                'content': '零向量题目',
                'embedding': zero_embedding.tobytes()
            }
        ]
        
        index = VectorIndex(mock_db)
        results = index.search_similar(query_embedding)
        
        # 零向量应该被跳过
        assert results == []


class TestVectorIndexGetStats:
    """统计信息测试"""
    
    def test_get_stats_success(self):
        """测试获取统计信息"""
        mock_db = MockDBConnection()
        
        mock_db.fetch_one = lambda q, p=None: {'total': 100} if 'COUNT(*)' in q and 'WHERE' not in q else {'total': 80}
        mock_db.fetch_all_result = [
            {'embedding_version': 'v1', 'total': 50, 'last_updated': '2024-01-01'},
            {'embedding_version': 'v2', 'total': 30, 'last_updated': '2024-01-02'}
        ]
        
        index = VectorIndex(mock_db)
        stats = index.get_stats()
        
        assert 'total_questions' in stats
        assert 'with_embedding' in stats
        assert 'without_embedding' in stats
        assert 'versions' in stats
        
        assert stats['total_questions'] == 100
        assert stats['with_embedding'] == 80
        assert stats['without_embedding'] == 20
    
    def test_get_stats_empty_database(self):
        """测试空数据库统计"""
        mock_db = MockDBConnection()
        
        mock_db.fetch_one = lambda q, p=None: {'total': 0}
        mock_db.fetch_all_result = []
        
        index = VectorIndex(mock_db)
        stats = index.get_stats()
        
        assert stats['total_questions'] == 0
        assert stats['with_embedding'] == 0
        assert stats['without_embedding'] == 0


class TestVectorIndexGetMissingEmbeddings:
    """获取未向量化题目测试"""
    
    def test_get_missing_embeddings_success(self):
        """测试获取未向量化题目"""
        mock_db = MockDBConnection()
        mock_db.fetch_all_result = [
            {'id': 'q1', 'content': '题目 1', 'category_id': 'cat1', 'created_at': '2024-01-01'},
            {'id': 'q2', 'content': '题目 2', 'category_id': 'cat1', 'created_at': '2024-01-02'}
        ]
        
        index = VectorIndex(mock_db)
        results = index.get_missing_embeddings()
        
        assert len(results) == 2
        assert results[0]['id'] == 'q1'
        
        # 验证查询包含 WHERE embedding IS NULL
        queries = [q[0] for q in mock_db.executed_queries]
        assert any('embedding IS NULL' in q for q in queries)
    
    def test_get_missing_embeddings_empty(self):
        """测试没有未向量化的题目"""
        mock_db = MockDBConnection()
        mock_db.fetch_all_result = []
        
        index = VectorIndex(mock_db)
        results = index.get_missing_embeddings()
        
        assert results == []


class TestVectorIndexGetMismatchedEmbeddings:
    """获取版本不匹配题目测试"""
    
    def test_get_mismatched_embeddings_success(self):
        """测试获取版本不匹配题目"""
        mock_db = MockDBConnection()
        mock_db.fetch_all_result = [
            {
                'id': 'q1',
                'content': '题目 1',
                'category_id': 'cat1',
                'embedding_version': 'v1',
                'embedding_updated_at': '2024-01-01'
            }
        ]
        
        index = VectorIndex(mock_db)
        results = index.get_mismatched_embeddings('v2')
        
        assert len(results) == 1
        assert results[0]['embedding_version'] == 'v1'
        
        # 验证查询参数包含新版本号
        params = mock_db.executed_queries[-1][1]
        assert 'v2' in params
    
    def test_get_mismatched_embeddings_empty(self):
        """测试没有版本不匹配的题目"""
        mock_db = MockDBConnection()
        mock_db.fetch_all_result = []
        
        index = VectorIndex(mock_db)
        results = index.get_mismatched_embeddings('v2')
        
        assert results == []


class TestVectorIndexRebuildAll:
    """重建所有向量测试"""
    
    def test_rebuild_all_success(self):
        """测试重建所有向量成功"""
        mock_db = MockDBConnection()
        mock_db.fetch_all_result = [
            {'id': 'q1', 'content': '题目 1', 'options': '["A", "B"]'},
            {'id': 'q2', 'content': '题目 2', 'options': '["C", "D"]'}
        ]
        
        # Mock embedding service
        mock_embedding_service = Mock()
        mock_embedding_service.embed.return_value = np.array([0.1, 0.2, 0.3])
        
        index = VectorIndex(mock_db)
        result = index.rebuild_all(mock_embedding_service, 'v1', batch_size=1)
        
        assert result['total'] == 2
        assert result['processed'] == 2
        assert result['errors'] == 0
        
        # 验证调用了 embedding service
        assert mock_embedding_service.embed.call_count == 2
    
    def test_rebuild_all_with_errors(self):
        """测试重建过程中有错误"""
        mock_db = MockDBConnection()
        mock_db.fetch_all_result = [
            {'id': 'q1', 'content': '题目 1', 'options': '["A", "B"]'},
            {'id': 'q2', 'content': '题目 2', 'options': '["C", "D"]'}
        ]
        
        # Mock embedding service 第一次成功，第二次失败
        mock_embedding_service = Mock()
        mock_embedding_service.embed.side_effect = [
            np.array([0.1, 0.2, 0.3]),
            Exception("Embedding failed")
        ]
        
        index = VectorIndex(mock_db)
        result = index.rebuild_all(mock_embedding_service, 'v1')
        
        assert result['total'] == 2
        assert result['processed'] == 1
        assert result['errors'] == 1
    
    def test_rebuild_all_empty_database(self):
        """测试空数据库重建"""
        mock_db = MockDBConnection()
        mock_db.fetch_all_result = []
        
        mock_embedding_service = Mock()
        
        index = VectorIndex(mock_db)
        result = index.rebuild_all(mock_embedding_service, 'v1')
        
        assert result['total'] == 0
        assert result['processed'] == 0
        assert result['errors'] == 0


class TestGetVectorIndex:
    """单例获取函数测试"""
    
    def test_get_vector_index_creates_instance(self):
        """测试创建实例"""
        # 重置单例
        import core.services.vector_index as vi_module
        vi_module._vector_index = None
        
        mock_db = MockDBConnection()
        
        index = get_vector_index(mock_db)
        
        assert index is not None
        assert isinstance(index, VectorIndex)
    
    def test_get_vector_index_returns_same_instance(self):
        """测试返回同一实例"""
        # 重置单例
        import core.services.vector_index as vi_module
        vi_module._vector_index = None
        
        mock_db = MockDBConnection()
        
        index1 = get_vector_index(mock_db)
        index2 = get_vector_index(mock_db)
        
        # 应该返回同一个实例
        assert index1 is index2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
