"""
EmbeddingService 测试
测试 Embedding 服务功能
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.services.embedding_service import EmbeddingService, get_embedding_service


class TestEmbeddingServiceInit:
    """EmbeddingService 初始化测试"""
    
    @patch('openai.OpenAI')
    def test_init_with_default_config(self, mock_openai):
        """测试使用默认配置初始化"""
        config = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        service = EmbeddingService(config)
        
        assert service.model_name == 'text-embedding-v3'
        assert service.api_key == 'test-key'
        assert service.base_url == 'https://api.test.com'
        mock_openai.assert_called_once_with(
            api_key='test-key',
            base_url='https://api.test.com'
        )
    
    @patch('openai.OpenAI')
    def test_init_with_custom_config(self, mock_openai):
        """测试使用自定义配置初始化"""
        config = {
            'model_name': 'ollama/nomic-embed-text',
            'api_key': 'ollama',
            'base_url': 'http://localhost:11434/v1'
        }
        
        service = EmbeddingService(config)
        
        assert service.model_name == 'ollama/nomic-embed-text'
        assert service.api_key == 'ollama'
        assert service.base_url == 'http://localhost:11434/v1'
    
    @patch('openai.OpenAI')
    def test_init_with_minimal_config(self, mock_openai):
        """测试使用最小配置初始化"""
        config = {}
        
        service = EmbeddingService(config)
        
        assert service.model_name == 'text-embedding-v3'
        assert service.api_key == ''
        assert service.base_url == ''


class TestEmbeddingServiceEmbed:
    """Embedding 计算测试"""
    
    @patch('openai.OpenAI')
    def test_embed_success(self, mock_openai):
        """测试单文本 Embedding 成功"""
        config = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        # Mock OpenAI 客户端
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Mock embeddings 响应
        mock_embedding = Mock()
        mock_embedding.embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_response = Mock()
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response
        
        service = EmbeddingService(config)
        result = service.embed("测试文本")
        
        assert isinstance(result, np.ndarray)
        assert len(result) == 5
        assert np.array_equal(result, np.array([0.1, 0.2, 0.3, 0.4, 0.5]))
        
        # 验证 API 调用
        mock_client.embeddings.create.assert_called_once_with(
            model='text-embedding-v3',
            input='测试文本'
        )
    
    @patch('openai.OpenAI')
    def test_embed_with_different_text_lengths(self, mock_openai):
        """测试不同长度文本的 Embedding"""
        config = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_embedding = Mock()
        mock_embedding.embedding = [0.1] * 768  # 常见维度
        mock_response = Mock()
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response
        
        service = EmbeddingService(config)
        
        # 短文本
        result_short = service.embed("短")
        assert len(result_short) == 768
        
        # 长文本
        long_text = "这是一段很长的文本" * 100
        result_long = service.embed(long_text)
        assert len(result_long) == 768
    
    @patch('openai.OpenAI')
    def test_embed_api_error(self, mock_openai):
        """测试 API 错误处理"""
        config = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.embeddings.create.side_effect = Exception("API Error")
        
        service = EmbeddingService(config)
        
        with pytest.raises(Exception):
            service.embed("测试文本")


class TestEmbeddingServiceEmbedBatch:
    """批量 Embedding 测试"""
    
    @patch('openai.OpenAI')
    def test_embed_batch_success(self, mock_openai):
        """测试批量 Embedding 成功"""
        config = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Mock 批量响应
        mock_embeddings = [
            Mock(embedding=[0.1, 0.2]),
            Mock(embedding=[0.3, 0.4]),
            Mock(embedding=[0.5, 0.6])
        ]
        mock_response = Mock()
        mock_response.data = mock_embeddings
        mock_client.embeddings.create.return_value = mock_response
        
        service = EmbeddingService(config)
        texts = ["文本 1", "文本 2", "文本 3"]
        results = service.embed_batch(texts)
        
        assert len(results) == 3
        assert all(isinstance(r, np.ndarray) for r in results)
        assert len(results[0]) == 2
        
        # 验证 API 调用
        mock_client.embeddings.create.assert_called_once_with(
            model='text-embedding-v3',
            input=texts
        )
    
    @patch('openai.OpenAI')
    def test_embed_batch_with_batch_size(self, mock_openai):
        """测试批量 Embedding 的批次大小"""
        config = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Mock 响应 - 为每个文本返回一个 embedding
        def create_embedding_response(*args, **kwargs):
            # 获取输入文本数量
            input_texts = kwargs.get('input', args[0] if args else [])
            num_texts = len(input_texts) if isinstance(input_texts, list) else 1
            
            mock_response = Mock()
            mock_response.data = [Mock(embedding=[0.1, 0.2]) for _ in range(num_texts)]
            return mock_response
        
        mock_client.embeddings.create.side_effect = create_embedding_response
        
        service = EmbeddingService(config)
        texts = ["文本"] * 10  # 10 个文本
        
        # 使用小批次大小
        results = service.embed_batch(texts, batch_size=3)
        
        assert len(results) == 10
        # 应该调用 4 次 API (10/3 = 3.33, 向上取整)
        assert mock_client.embeddings.create.call_count == 4
    
    @patch('openai.OpenAI')
    def test_embed_batch_empty_list(self, mock_openai):
        """测试空列表的批量 Embedding"""
        config = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        service = EmbeddingService(config)
        results = service.embed_batch([])
        
        assert results == []
        mock_client.embeddings.create.assert_not_called()
    
    @patch('openai.OpenAI')
    def test_embed_batch_api_error(self, mock_openai):
        """测试批量 Embedding 的 API 错误"""
        config = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.embeddings.create.side_effect = Exception("Batch API Error")
        
        service = EmbeddingService(config)
        
        with pytest.raises(Exception):
            service.embed_batch(["文本 1", "文本 2"])


class TestEmbeddingServiceGetModelVersion:
    """模型版本获取测试"""
    
    @patch('openai.OpenAI')
    def test_get_model_version(self, mock_openai):
        """测试获取模型版本"""
        config = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        mock_openai.return_value = Mock()
        
        service = EmbeddingService(config)
        version = service.get_model_version()
        
        assert version == 'text-embedding-v3'
    
    @patch('openai.OpenAI')
    def test_get_model_version_ollama(self, mock_openai):
        """测试获取 Ollama 模型版本"""
        config = {
            'model_name': 'ollama/nomic-embed-text',
            'api_key': 'ollama',
            'base_url': 'http://localhost:11434/v1'
        }
        
        mock_openai.return_value = Mock()
        
        service = EmbeddingService(config)
        version = service.get_model_version()
        
        assert version == 'ollama/nomic-embed-text'


class TestGetEmbeddingService:
    """单例获取函数测试"""
    
    @patch('openai.OpenAI')
    def test_get_embedding_service_creates_new_instance(self, mock_openai):
        """测试创建新实例"""
        # 重置全局状态
        import agent.services.embedding_service as es_module
        es_module._embedding_service = None
        es_module._last_config_hash = ""
        
        config = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        mock_openai.return_value = Mock()
        
        service1 = get_embedding_service(config)
        
        assert service1 is not None
        assert isinstance(service1, EmbeddingService)
    
    @patch('openai.OpenAI')
    def test_get_embedding_service_returns_cached_instance(self, mock_openai):
        """测试返回缓存实例"""
        # 重置全局状态
        import agent.services.embedding_service as es_module
        es_module._embedding_service = None
        es_module._last_config_hash = ""
        
        config = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        mock_openai.return_value = Mock()
        
        service1 = get_embedding_service(config)
        service2 = get_embedding_service(config)
        
        # 应该返回同一个实例
        assert service1 is service2
    
    @patch('openai.OpenAI')
    def test_get_embedding_service_recreates_on_config_change(self, mock_openai):
        """测试配置变化时重新创建实例"""
        # 重置全局状态
        import agent.services.embedding_service as es_module
        es_module._embedding_service = None
        es_module._last_config_hash = ""
        
        config1 = {
            'model_name': 'text-embedding-v3',
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        config2 = {
            'model_name': 'text-embedding-v2',  # 不同的模型
            'api_key': 'test-key',
            'base_url': 'https://api.test.com'
        }
        
        mock_openai.return_value = Mock()
        
        service1 = get_embedding_service(config1)
        service2 = get_embedding_service(config2)
        
        # 配置不同，应该返回不同实例
        assert service1 is not service2
        assert service1.model_name == 'text-embedding-v3'
        assert service2.model_name == 'text-embedding-v2'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
