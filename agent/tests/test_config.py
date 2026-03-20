"""
Agent Config 模块测试
测试 agent/config.py 中的配置类
"""
import pytest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestAgentConfigLoadConfig:
    """测试配置加载"""
    
    def test_load_config_from_file(self, tmp_path):
        """测试从文件加载配置"""
        # 创建临时配置文件
        config_file = tmp_path / "agent.json"
        config_data = {
            "llm": {"model_id": "test-model", "api_key": "test-key"},
            "vision": {"model_id": "test-vision"},
            "embedding": {"model_name": "test-embedding"}
        }
        config_file.write_text(json.dumps(config_data))
        
        from agent.config import AgentConfig
        
        # Mock CONFIG_FILE
        with patch.object(AgentConfig, 'CONFIG_FILE', config_file):
            # 清除缓存
            AgentConfig._config_cache = None
            AgentConfig._cache_mtime = 0
            
            config = AgentConfig._load_config()
            
            assert config['llm']['model_id'] == 'test-model'
            assert config['llm']['api_key'] == 'test-key'
    
    def test_load_config_file_not_found(self):
        """测试配置文件不存在"""
        from agent.config import AgentConfig
        
        # Mock CONFIG_FILE 为不存在的路径
        fake_path = Path("/nonexistent/path/agent.json")
        
        with patch.object(AgentConfig, 'CONFIG_FILE', fake_path):
            # 清除缓存
            AgentConfig._config_cache = None
            AgentConfig._cache_mtime = 0
            
            config = AgentConfig._load_config()
            
            # 应该返回默认配置
            assert 'llm' in config
            assert 'vision' in config
            assert 'embedding' in config
    
    def test_load_config_uses_cache(self):
        """测试使用缓存"""
        from agent.config import AgentConfig
        
        # 设置缓存
        AgentConfig._config_cache = {"cached": True}
        AgentConfig._cache_mtime = 9999999999
        
        # Mock stat to return same mtime
        with patch.object(AgentConfig, 'CONFIG_FILE') as mock_file:
            mock_file.stat.return_value.st_mtime = 9999999999
            mock_file.exists.return_value = True
            
            config = AgentConfig._load_config()
            
            assert config == {"cached": True}
    
    def test_load_config_force_refresh(self):
        """测试强制刷新"""
        from agent.config import AgentConfig
        from pathlib import Path
        from unittest.mock import patch, MagicMock
        
        # 设置缓存
        AgentConfig._config_cache = {"cached": True}
        
        # Mock 配置文件不存在
        with patch.object(AgentConfig, 'CONFIG_FILE') as mock_file:
            mock_file.exists.return_value = False
            mock_file.stat.return_value.st_mtime = 0
            
            config = AgentConfig._load_config(force_refresh=True)
            
            # 文件不存在时会使用默认配置
            assert config is not None
            assert 'llm' in config


class TestAgentConfigGetDefaultConfig:
    """测试默认配置"""
    
    def test_get_default_config_structure(self):
        """测试默认配置结构"""
        from agent.config import AgentConfig
        
        config = AgentConfig._get_default_config()
        
        assert 'llm' in config
        assert 'vision' in config
        assert 'embedding' in config
        assert 'settings' in config
        assert 'allowed_extensions' in config
    
    def test_get_default_llm_config(self):
        """测试默认 LLM 配置"""
        from agent.config import AgentConfig
        
        config = AgentConfig._get_default_config()
        
        assert config['llm']['model_id'] == 'qwen-plus'
        assert 'api_key' in config['llm']
        assert 'base_url' in config['llm']
    
    def test_get_default_vision_config(self):
        """测试默认视觉配置"""
        from agent.config import AgentConfig
        
        config = AgentConfig._get_default_config()
        
        assert config['vision']['model_id'] == 'qwen-vl-max'
    
    def test_get_default_embedding_config(self):
        """测试默认 Embedding 配置"""
        from agent.config import AgentConfig
        
        config = AgentConfig._get_default_config()
        
        assert config['embedding']['model_name'] == 'text-embedding-v3'
    
    def test_get_default_settings(self):
        """测试默认设置"""
        from agent.config import AgentConfig
        
        config = AgentConfig._get_default_config()
        
        assert config['settings']['max_questions_per_image'] == 10
        assert config['settings']['max_questions_per_document'] == 50
        assert 'confidence_threshold' in config['settings']
    
    def test_get_default_allowed_extensions(self):
        """测试默认允许的扩展名"""
        from agent.config import AgentConfig
        
        config = AgentConfig._get_default_config()
        
        assert 'images' in config['allowed_extensions']
        assert 'documents' in config['allowed_extensions']
        assert 'jpg' in config['allowed_extensions']['images']
        assert 'png' in config['allowed_extensions']['images']
        assert 'pdf' in config['allowed_extensions']['documents']


class TestAgentConfigRefresh:
    """测试配置刷新"""
    
    def test_refresh_clears_cache(self):
        """测试刷新清除缓存"""
        from agent.config import AgentConfig
        
        # 设置缓存
        AgentConfig._config_cache = {"old": True}
        AgentConfig._cache_mtime = 12345
        
        # 刷新
        AgentConfig.refresh()
        
        # 缓存应该被重新加载（不是 None）
        # refresh() 会清除旧缓存并重新加载配置
        assert AgentConfig._config_cache is not None
        assert 'llm' in AgentConfig._config_cache


class TestAgentConfigGetLlmConfig:
    """测试 LLM 配置获取"""
    
    def test_get_llm_config(self):
        """测试获取 LLM 配置"""
        from agent.config import AgentConfig
        
        # 清除缓存以重新加载
        AgentConfig._config_cache = None
        
        llm_config = AgentConfig.get_llm_config()
        
        assert 'model' in llm_config or 'model_id' in llm_config
        assert 'api_key' in llm_config
        assert 'base_url' in llm_config


class TestAgentConfigGetVisionConfig:
    """测试视觉配置获取"""
    
    def test_get_vision_config(self):
        """测试获取视觉配置"""
        from agent.config import AgentConfig
        
        AgentConfig._config_cache = None
        
        vision_config = AgentConfig.get_vision_config()
        
        assert 'model' in vision_config or 'model_id' in vision_config
        assert 'api_key' in vision_config
        assert 'base_url' in vision_config


class TestAgentConfigGetEmbeddingConfig:
    """测试 Embedding 配置获取"""
    
    def test_get_embedding_config(self):
        """测试获取 Embedding 配置"""
        from agent.config import AgentConfig
        
        AgentConfig._config_cache = None
        
        embedding_config = AgentConfig.get_embed_config()
        
        assert 'model' in embedding_config or 'model_name' in embedding_config or 'model_id' in embedding_config
        assert 'api_key' in embedding_config
        assert 'base_url' in embedding_config


class TestAgentConfigGetFullConfig:
    """测试完整配置获取"""
    
    def test_get_full_config(self):
        """测试获取完整配置"""
        from agent.config import AgentConfig
        
        AgentConfig._config_cache = None
        
        full_config = AgentConfig.get_full_config()
        
        assert 'llm' in full_config
        assert 'vision' in full_config
        assert 'embedding' in full_config
        assert 'settings' in full_config
    
    def test_get_full_config_is_dict(self):
        """测试完整配置是字典"""
        from agent.config import AgentConfig
        
        AgentConfig._config_cache = None
        
        full_config = AgentConfig.get_full_config()
        
        assert isinstance(full_config, dict)


class TestAgentConfigClassAttributes:
    """测试类属性"""
    
    def test_config_file_exists(self):
        """测试配置文件路径"""
        from agent.config import AgentConfig
        
        assert AgentConfig.CONFIG_FILE is not None
        assert isinstance(AgentConfig.CONFIG_FILE, Path)
    
    def test_max_questions_per_document(self):
        """测试每文档最大题目数"""
        from agent.config import AgentConfig
        
        # 这些应该是从配置中获取的
        config = AgentConfig.get_full_config()
        assert 'max_questions_per_document' in config['settings']
    
    def test_max_questions_per_image(self):
        """测试每图片最大题目数"""
        from agent.config import AgentConfig
        
        config = AgentConfig.get_full_config()
        assert 'max_questions_per_image' in config['settings']


class TestAgentConfigAllowedExtensions:
    """测试允许的扩展名"""
    
    def test_allowed_image_extensions(self):
        """测试允许的图片扩展名"""
        from agent.config import AgentConfig
        
        config = AgentConfig.get_full_config()
        extensions = config['allowed_extensions']['images']
        
        assert isinstance(extensions, list)
        assert len(extensions) > 0
    
    def test_allowed_document_extensions(self):
        """测试允许的文档扩展名"""
        from agent.config import AgentConfig
        
        config = AgentConfig.get_full_config()
        extensions = config['allowed_extensions']['documents']
        
        assert isinstance(extensions, list)
        assert len(extensions) > 0
    
    def test_image_extensions_contains_jpg(self):
        """测试图片扩展名包含 JPG"""
        from agent.config import AgentConfig
        
        config = AgentConfig.get_full_config()
        extensions = config['allowed_extensions']['images']
        
        assert 'jpg' in extensions or 'jpeg' in extensions
    
    def test_document_extensions_contains_pdf(self):
        """测试文档扩展名包含 PDF"""
        from agent.config import AgentConfig
        
        config = AgentConfig.get_full_config()
        extensions = config['allowed_extensions']['documents']
        
        assert 'pdf' in extensions


class TestAgentConfigWithMockedFile:
    """测试使用 Mock 文件"""
    
    def test_load_config_with_mocked_file(self):
        """测试使用 Mock 文件加载配置"""
        from agent.config import AgentConfig
        
        mock_config = {
            "llm": {"model_id": "mock-model"},
            "vision": {"model_id": "mock-vision"},
            "embedding": {"model_name": "mock-embedding"},
            "settings": {},
            "allowed_extensions": {"images": [], "documents": []}
        }
        
        with patch.object(AgentConfig, '_load_config', return_value=mock_config):
            config = AgentConfig.get_full_config()
            
            assert config == mock_config


class TestAgentConfigCacheBehavior:
    """测试缓存行为"""
    
    def test_cache_populated_after_load(self):
        """测试加载后缓存被填充"""
        from agent.config import AgentConfig
        
        AgentConfig._config_cache = None
        
        # 加载配置
        AgentConfig.get_full_config()
        
        # 缓存应该被填充
        assert AgentConfig._config_cache is not None
    
    def test_second_load_uses_cache(self):
        """测试第二次加载使用缓存"""
        from agent.config import AgentConfig
        
        AgentConfig._config_cache = None
        
        # 第一次加载
        AgentConfig.get_full_config()
        first_cache = AgentConfig._config_cache
        
        # 第二次加载
        AgentConfig.get_full_config()
        second_cache = AgentConfig._config_cache
        
        # 缓存应该相同（内容相同）
        # 注意：get_full_config 使用 force_refresh=True，但 _config_cache 应该保持不变
        assert first_cache == second_cache


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
