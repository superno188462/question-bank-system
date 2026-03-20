"""
ModelClient 测试
测试通用模型客户端功能
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.services.model_client import ModelClient


class TestModelClientInit:
    """ModelClient 初始化测试"""
    
    def test_init_with_default_config(self):
        """测试使用默认配置初始化"""
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-plus',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com'
            }
            client = ModelClient()
            
            assert client.model == 'qwen-plus'
            assert client.api_key == 'test-key'
            assert client.base_url == 'https://api.test.com'
    
    def test_init_with_custom_config(self):
        """测试使用自定义配置初始化"""
        custom_config = {
            'model': 'gpt-4',
            'api_key': 'custom-key',
            'base_url': 'https://api.openai.com'
        }
        client = ModelClient(config=custom_config)
        
        assert client.model == 'gpt-4'
        assert client.api_key == 'custom-key'
        assert client.base_url == 'https://api.openai.com'
    
    def test_init_with_partial_config(self):
        """测试使用部分配置初始化"""
        custom_config = {
            'model': 'deepseek-chat'
        }
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-plus',
                'api_key': 'default-key',
                'base_url': 'https://api.test.com'
            }
            client = ModelClient(config=custom_config)
            
            assert client.model == 'deepseek-chat'
            # 其他配置应该使用自定义配置中的值（如果提供）或默认值
            assert client.api_key == ''
            assert client.base_url == ''
    
    def test_init_with_proxy(self):
        """测试使用代理配置初始化"""
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.services.model_client.AgentConfig.HTTP_PROXY', 'http://proxy:8080'):
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                client = ModelClient()
                
                assert client.http_client is not None
    
    def test_init_with_ssl_verify_disabled(self):
        """测试禁用 SSL 验证初始化"""
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            with patch.dict(os.environ, {'VERIFY_SSL': 'false'}):
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                client = ModelClient()
                
                assert client.http_client is not None


class TestModelClientEncodeImage:
    """图片编码测试"""
    
    def test_encode_image_jpeg(self, tmp_path):
        """测试编码 JPEG 图片"""
        # 创建测试图片文件
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")
        
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-plus',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com'
            }
            client = ModelClient()
            
            result = client._encode_image(str(image_path))
            
            assert result.startswith("data:image/jpeg;base64,")
            assert "ZmFrZSBpbWFnZSBkYXRh" in result  # base64 of "fake image data"
    
    def test_encode_image_png(self, tmp_path):
        """测试编码 PNG 图片"""
        image_path = tmp_path / "test.png"
        image_path.write_bytes(b"fake png data")
        
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-plus',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com'
            }
            client = ModelClient()
            
            result = client._encode_image(str(image_path))
            
            assert result.startswith("data:image/png;base64,")
    
    def test_encode_image_unknown_type(self, tmp_path):
        """测试编码未知类型图片"""
        image_path = tmp_path / "test.xyz"
        image_path.write_bytes(b"fake data")
        
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-plus',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com'
            }
            client = ModelClient()
            
            result = client._encode_image(str(image_path))
            
            # 未知类型会返回空 mime_type，然后使用默认 jpeg
            assert 'base64,' in result


class TestModelClientChat:
    """聊天功能测试"""
    
    def test_chat_success(self):
        """测试聊天成功"""
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-plus',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com'
            }
            client = ModelClient()
            
            # Mock HTTP 响应
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{
                    "message": {"content": "这是 AI 的回答"}
                }]
            }
            mock_response.raise_for_status = Mock()
            
            with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
                messages = [{"role": "user", "content": "你好"}]
                result = client.chat(messages)
                
                assert result == "这是 AI 的回答"
                mock_post.assert_called_once()
                
                # 验证请求参数
                call_args = mock_post.call_args
                assert "Authorization" in call_args.kwargs["headers"]
                assert call_args.kwargs["json"]["model"] == "qwen-plus"
                assert call_args.kwargs["json"]["messages"] == messages
    
    def test_chat_with_custom_params(self):
        """测试带自定义参数的聊天"""
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-plus',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com'
            }
            client = ModelClient()
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{
                    "message": {"content": "回答"}
                }]
            }
            mock_response.raise_for_status = Mock()
            
            with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
                messages = [{"role": "user", "content": "你好"}]
                result = client.chat(messages, temperature=0.9, max_tokens=1000)
                
                # 验证参数传递
                assert mock_post.call_args.kwargs["json"]["temperature"] == 0.9
                assert mock_post.call_args.kwargs["json"]["max_tokens"] == 1000
    
    def test_chat_with_base_url_trailing_slash(self):
        """测试 base_url 带斜杠的情况"""
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-plus',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com/'
            }
            client = ModelClient()
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{
                    "message": {"content": "回答"}
                }]
            }
            mock_response.raise_for_status = Mock()
            
            with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
                messages = [{"role": "user", "content": "你好"}]
                client.chat(messages)
                
                # 验证 URL 正确处理（没有双斜杠）
                url = mock_post.call_args.args[0]
                assert url == "https://api.test.com/chat/completions"
    
    def test_chat_http_error(self):
        """测试 HTTP 错误处理"""
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-plus',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com'
            }
            client = ModelClient()
            
            mock_response = Mock()
            mock_response.raise_for_status = Mock(side_effect=Exception("HTTP Error"))
            
            with patch.object(client.http_client, 'post', return_value=mock_response):
                messages = [{"role": "user", "content": "你好"}]
                
                with pytest.raises(Exception):
                    client.chat(messages)


class TestModelClientChatWithImages:
    """多模态聊天测试"""
    
    def test_chat_with_images_success(self):
        """测试带图片的聊天成功"""
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-vl',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com'
            }
            client = ModelClient()
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{
                    "message": {"content": "这是一张图片"}
                }]
            }
            mock_response.raise_for_status = Mock()
            
            with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
                messages = [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "这是什么？"},
                        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,xxx"}}
                    ]
                }]
                result = client.chat_with_images(messages)
                
                assert result == "这是一张图片"
                mock_post.assert_called_once()
                
                # 验证 max_tokens 默认值更大
                assert mock_post.call_args.kwargs["json"]["max_tokens"] == 4096
    
    def test_chat_with_images_custom_params(self):
        """测试带自定义参数的多模态聊天"""
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-vl',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com'
            }
            client = ModelClient()
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{
                    "message": {"content": "回答"}
                }]
            }
            mock_response.raise_for_status = Mock()
            
            with patch.object(client.http_client, 'post', return_value=mock_response) as mock_post:
                messages = [{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,xxx"}}
                    ]
                }]
                client.chat_with_images(messages, temperature=0.5, max_tokens=2048)
                
                assert mock_post.call_args.kwargs["json"]["temperature"] == 0.5
                assert mock_post.call_args.kwargs["json"]["max_tokens"] == 2048


class TestModelClientContextManager:
    """上下文管理器测试"""
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-plus',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com'
            }
            
            with ModelClient() as client:
                assert client is not None
                assert hasattr(client, 'http_client')
    
    def test_close_method(self):
        """测试 close 方法"""
        with patch('agent.services.model_client.AgentConfig.get_llm_config') as mock_config:
            mock_config.return_value = {
                'model': 'qwen-plus',
                'api_key': 'test-key',
                'base_url': 'https://api.test.com'
            }
            client = ModelClient()
            
            # 验证 close 方法存在且可调用
            assert hasattr(client, 'close')
            client.close()  # 不应该抛出异常


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
