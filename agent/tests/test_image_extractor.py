"""
ImageExtractor 测试
测试图片题目提取器功能
"""
import pytest
import sys
import os
import json
import ssl
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.extractors.image_extractor import ImageExtractor


class TestImageExtractorInit:
    """ImageExtractor 初始化测试"""
    
    def test_init_with_default_config(self):
        """测试使用默认配置初始化"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                with patch('agent.extractors.image_extractor.AgentConfig.MAX_QUESTIONS_PER_IMAGE', 5):
                    mock_client_instance = Mock()
                    mock_client.return_value = mock_client_instance
                    
                    extractor = ImageExtractor()
                    
                    assert extractor.client is not None
                    assert extractor.max_questions == 5
    
    def test_init_with_custom_config(self):
        """测试使用自定义配置初始化"""
        custom_config = {
            'model': 'gpt-4-vision',
            'api_key': 'custom-key',
            'base_url': 'https://api.openai.com'
        }
        
        with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
            with patch('agent.extractors.image_extractor.AgentConfig.MAX_QUESTIONS_PER_IMAGE', 5):
                mock_client_instance = Mock()
                mock_client.return_value = mock_client_instance
                
                extractor = ImageExtractor(config=custom_config)
                
                assert extractor.client is not None
                mock_client.assert_called_once_with(custom_config)


class TestImageExtractorExtract:
    """图片提取功能测试"""
    
    def test_extract_file_not_found(self):
        """测试文件不存在的情况"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                extractor = ImageExtractor()
                
                with pytest.raises(FileNotFoundError):
                    extractor.extract("/nonexistent/path/image.jpg")
    
    def test_extract_success(self, tmp_path):
        """测试提取成功"""
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")
        
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance._encode_image.return_value = "data:image/jpeg;base64,ZmFrZQ=="
                mock_response = json.dumps({
                    "questions": [{
                        "type": "single_choice",
                        "content": "图片中的题目",
                        "options": ["A. 选项 1", "B. 选项 2"],
                        "answer": "A",
                        "explanation": "解析"
                    }],
                    "total_count": 1,
                    "confidence": 0.95
                })
                mock_client_instance.chat_with_images.return_value = mock_response
                mock_client.return_value = mock_client_instance
                
                extractor = ImageExtractor()
                result = extractor.extract(str(image_path))
                
                assert result['total_count'] == 1
                assert len(result['questions']) == 1
                assert result['source_type'] == 'image'
                assert result['source_file'] == 'test.jpg'
                assert 'extracted_at' in result
                
                # 验证调用了 chat_with_images
                mock_client_instance.chat_with_images.assert_called_once()
    
    def test_extract_multiple_questions(self, tmp_path):
        """测试提取多个题目"""
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")
        
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                with patch('agent.extractors.image_extractor.AgentConfig.MAX_QUESTIONS_PER_IMAGE', 2):
                    mock_config.return_value = {
                        'model': 'qwen-vl',
                        'api_key': 'test-key',
                        'base_url': 'https://api.test.com'
                    }
                    
                    mock_client_instance = Mock()
                    mock_client_instance._encode_image.return_value = "data:image/jpeg;base64,ZmFrZQ=="
                    mock_response = json.dumps({
                        "questions": [
                            {"type": "single_choice", "content": "题目 1", "options": [], "answer": "A", "explanation": ""},
                            {"type": "single_choice", "content": "题目 2", "options": [], "answer": "B", "explanation": ""},
                            {"type": "single_choice", "content": "题目 3", "options": [], "answer": "C", "explanation": ""}
                        ],
                        "total_count": 3,
                        "confidence": 0.9
                    })
                    mock_client_instance.chat_with_images.return_value = mock_response
                    mock_client.return_value = mock_client_instance
                    
                    extractor = ImageExtractor()
                    result = extractor.extract(str(image_path))
                    
                    # 应该限制在 2 个题目
                    assert result['total_count'] == 2
                    assert len(result['questions']) == 2
    
    def test_extract_json_parse_error(self, tmp_path):
        """测试 JSON 解析错误"""
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")
        
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance._encode_image.return_value = "data:image/jpeg;base64,ZmFrZQ=="
                mock_client_instance.chat_with_images.return_value = "这不是 JSON"
                mock_client.return_value = mock_client_instance
                
                extractor = ImageExtractor()
                result = extractor.extract(str(image_path))
                
                assert result['questions'] == []
                assert result['total_count'] == 0
                assert 'error' in result
                # 错误消息可能包含 JSON 解析错误或 OCR 降级信息
                error_msg = result.get('error', '')
                assert 'JSON' in error_msg or '解析' in error_msg or 'OCR' in error_msg
    
    def test_extract_ssl_error(self, tmp_path):
        """测试 SSL 证书错误"""
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")
        
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                with patch('agent.extractors.image_extractor.OcrQuestionExtractor') as mock_ocr_extractor:
                    mock_config.return_value = {
                        'model': 'qwen-vl',
                        'api_key': 'test-key',
                        'base_url': 'https://api.test.com'
                    }
                    
                    # Mock OCR 提取器返回空结果
                    mock_ocr_instance = Mock()
                    mock_ocr_instance.extract.return_value = {'questions': [], 'total_count': 0, 'confidence': 0.0, 'error': 'OCR 失败'}
                    mock_ocr_extractor.return_value = mock_ocr_instance
                    
                    mock_client_instance = Mock()
                    mock_client_instance._encode_image.return_value = "data:image/jpeg;base64,ZmFrZQ=="
                    mock_client_instance.chat_with_images.side_effect = ssl.SSLCertVerificationError("Certificate verify failed")
                    mock_client.return_value = mock_client_instance
                    
                    extractor = ImageExtractor()
                    result = extractor.extract(str(image_path))
                    
                    assert result['questions'] == []
                    assert result['total_count'] == 0
                    # 错误消息可能包含 SSL 或 OCR 降级信息
                    assert 'error' in result
    
    def test_extract_connection_error(self, tmp_path):
        """测试网络连接错误"""
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")
        
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                with patch('agent.extractors.image_extractor.OcrQuestionExtractor') as mock_ocr_extractor:
                    mock_config.return_value = {
                        'model': 'qwen-vl',
                        'api_key': 'test-key',
                        'base_url': 'https://api.test.com'
                    }
                    
                    # Mock OCR 提取器返回空结果
                    mock_ocr_instance = Mock()
                    mock_ocr_instance.extract.return_value = {'questions': [], 'total_count': 0, 'confidence': 0.0, 'error': 'OCR 失败'}
                    mock_ocr_extractor.return_value = mock_ocr_instance
                    
                    mock_client_instance = Mock()
                    mock_client_instance._encode_image.return_value = "data:image/jpeg;base64,ZmFrZQ=="
                    mock_client_instance.chat_with_images.side_effect = Exception("Connection timeout")
                    mock_client.return_value = mock_client_instance
                    
                    extractor = ImageExtractor()
                    result = extractor.extract(str(image_path))
                    
                    assert result['questions'] == []
                    # 错误消息可能包含 OCR 降级信息
                    assert 'error' in result
    
    def test_extract_api_key_error(self, tmp_path):
        """测试 API Key 错误"""
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")
        
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                with patch('agent.extractors.image_extractor.OcrQuestionExtractor') as mock_ocr_extractor:
                    mock_config.return_value = {
                        'model': 'qwen-vl',
                        'api_key': 'test-key',
                        'base_url': 'https://api.test.com'
                    }
                    
                    # Mock OCR 提取器返回空结果
                    mock_ocr_instance = Mock()
                    mock_ocr_instance.extract.return_value = {'questions': [], 'total_count': 0, 'confidence': 0.0, 'error': 'OCR 失败'}
                    mock_ocr_extractor.return_value = mock_ocr_instance
                    
                    mock_client_instance = Mock()
                    mock_client_instance._encode_image.return_value = "data:image/jpeg;base64,ZmFrZQ=="
                    mock_client_instance.chat_with_images.side_effect = Exception("401 Unauthorized")
                    mock_client.return_value = mock_client_instance
                    
                    extractor = ImageExtractor()
                    result = extractor.extract(str(image_path))
                    
                    assert result['questions'] == []
                    # 错误消息可能包含 OCR 降级信息
                    assert 'error' in result
    
    def test_extract_model_not_found_error(self, tmp_path):
        """测试模型不可用错误"""
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")
        
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                with patch('agent.extractors.image_extractor.OcrQuestionExtractor') as mock_ocr_extractor:
                    mock_config.return_value = {
                        'model': 'qwen-vl',
                        'api_key': 'test-key',
                        'base_url': 'https://api.test.com'
                    }
                    
                    # Mock OCR 提取器返回空结果
                    mock_ocr_instance = Mock()
                    mock_ocr_instance.extract.return_value = {'questions': [], 'total_count': 0, 'confidence': 0.0, 'error': 'OCR 失败'}
                    mock_ocr_extractor.return_value = mock_ocr_instance
                    
                    mock_client_instance = Mock()
                    mock_client_instance._encode_image.return_value = "data:image/jpeg;base64,ZmFrZQ=="
                    mock_client_instance.chat_with_images.side_effect = Exception("Model not found")
                    mock_client.return_value = mock_client_instance
                    
                    extractor = ImageExtractor()
                    result = extractor.extract(str(image_path))
                    
                    assert result['questions'] == []
                    # 错误消息可能包含 OCR 降级信息
                    assert 'error' in result
    
    def test_extract_generic_error(self, tmp_path):
        """测试通用错误"""
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake image data")
        
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance._encode_image.return_value = "data:image/jpeg;base64,ZmFrZQ=="
                mock_client_instance.chat_with_images.side_effect = Exception("Unknown error")
                mock_client.return_value = mock_client_instance
                
                extractor = ImageExtractor()
                result = extractor.extract(str(image_path))
                
                assert result['questions'] == []
                # 错误消息可能包含 OCR 降级信息
                assert 'error' in result
                assert '提取失败' in result.get('error', '') or 'OCR' in result.get('error', '')


class TestImageExtractorExtractBatch:
    """批量提取测试"""
    
    def test_extract_batch_success(self, tmp_path):
        """测试批量提取成功"""
        image1 = tmp_path / "test1.jpg"
        image2 = tmp_path / "test2.jpg"
        image1.write_bytes(b"fake image 1")
        image2.write_bytes(b"fake image 2")
        
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance._encode_image.return_value = "data:image/jpeg;base64,ZmFrZQ=="
                
                # 第一次调用返回 1 个题目
                mock_response1 = json.dumps({
                    "questions": [{"type": "single_choice", "content": "题目 1", "options": [], "answer": "A", "explanation": ""}],
                    "total_count": 1,
                    "confidence": 0.9
                })
                # 第二次调用返回 2 个题目
                mock_response2 = json.dumps({
                    "questions": [
                        {"type": "single_choice", "content": "题目 2", "options": [], "answer": "B", "explanation": ""},
                        {"type": "single_choice", "content": "题目 3", "options": [], "answer": "C", "explanation": ""}
                    ],
                    "total_count": 2,
                    "confidence": 0.8
                })
                mock_client_instance.chat_with_images.side_effect = [mock_response1, mock_response2]
                mock_client.return_value = mock_client_instance
                
                extractor = ImageExtractor()
                result = extractor.extract_batch([str(image1), str(image2)])
                
                assert result['total_count'] == 3
                assert len(result['questions']) == 3
                assert result['source_type'] == 'image_batch'
                assert result['source_files'] == ['test1.jpg', 'test2.jpg']
                assert result['error_count'] == 0
    
    def test_extract_batch_partial_failure(self, tmp_path):
        """测试批量提取部分失败"""
        image1 = tmp_path / "test1.jpg"
        image2 = tmp_path / "test2.jpg"
        image1.write_bytes(b"fake image 1")
        image2.write_bytes(b"fake image 2")
        
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance._encode_image.return_value = "data:image/jpeg;base64,ZmFrZQ=="
                
                # 第一次成功，第二次失败
                mock_response1 = json.dumps({
                    "questions": [{"type": "single_choice", "content": "题目 1", "options": [], "answer": "A", "explanation": ""}],
                    "total_count": 1,
                    "confidence": 0.9
                })
                mock_client_instance.chat_with_images.side_effect = [mock_response1, Exception("Error")]
                mock_client.return_value = mock_client_instance
                
                extractor = ImageExtractor()
                result = extractor.extract_batch([str(image1), str(image2)])
                
                assert result['total_count'] == 1
                assert result['error_count'] == 1
    
    def test_extract_batch_empty_list(self):
        """测试空列表的批量提取"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                extractor = ImageExtractor()
                result = extractor.extract_batch([])
                
                assert result['total_count'] == 0
                assert result['questions'] == []
                assert result['average_confidence'] == 0


class TestImageExtractorParseResponse:
    """响应解析测试"""
    
    def test_parse_response_direct_json(self):
        """测试直接解析 JSON"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                extractor = ImageExtractor()
                
                json_str = '{"questions": [], "total_count": 0, "confidence": 0.0}'
                result = extractor._parse_response(json_str)
                
                assert result['total_count'] == 0
    
    def test_parse_response_json_code_block(self):
        """测试解析 JSON 代码块"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                extractor = ImageExtractor()
                
                response = """
```json
{"questions": [{"type": "single_choice", "content": "题目", "options": [], "answer": "A", "explanation": ""}], "total_count": 1, "confidence": 0.9}
```
"""
                result = extractor._parse_response(response)
                
                assert result['total_count'] == 1
    
    def test_parse_response_invalid_json(self):
        """测试解析无效 JSON"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                extractor = ImageExtractor()
                
                response = "这不是有效的 JSON"
                result = extractor._parse_response(response)
                
                assert result['questions'] == []
                assert result['error'] == "无法解析响应为 JSON"


class TestImageExtractorGetFriendlyErrorName:
    """错误名称测试"""
    
    def test_get_friendly_error_name_certificate(self):
        """测试证书错误名称"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {'model': 'qwen-vl', 'api_key': 'key', 'base_url': 'url'}
                mock_client.return_value = Mock()
                
                extractor = ImageExtractor()
                
                error = Exception("CERTIFICATE_VERIFY_FAILED")
                name = extractor._get_friendly_error_name(error)
                assert name == "证书验证失败"
    
    def test_get_friendly_error_name_connection(self):
        """测试连接错误名称"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {'model': 'qwen-vl', 'api_key': 'key', 'base_url': 'url'}
                mock_client.return_value = Mock()
                
                extractor = ImageExtractor()
                
                error = Exception("Connection timeout")
                name = extractor._get_friendly_error_name(error)
                assert name == "网络连接失败"
    
    def test_get_friendly_error_name_auth(self):
        """测试认证错误名称"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {'model': 'qwen-vl', 'api_key': 'key', 'base_url': 'url'}
                mock_client.return_value = Mock()
                
                extractor = ImageExtractor()
                
                error = Exception("401 Unauthorized")
                name = extractor._get_friendly_error_name(error)
                assert name == "认证失败"
    
    def test_get_friendly_error_name_model(self):
        """测试模型错误名称"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {'model': 'qwen-vl', 'api_key': 'key', 'base_url': 'url'}
                mock_client.return_value = Mock()
                
                extractor = ImageExtractor()
                
                error = Exception("Model not found")
                name = extractor._get_friendly_error_name(error)
                assert name == "模型不可用"
    
    def test_get_friendly_error_name_default(self):
        """测试默认错误名称"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {'model': 'qwen-vl', 'api_key': 'key', 'base_url': 'url'}
                mock_client.return_value = Mock()
                
                extractor = ImageExtractor()
                
                error = Exception("Unknown error")
                name = extractor._get_friendly_error_name(error)
                assert name == "提取失败"


class TestImageExtractorClose:
    """资源清理测试"""
    
    def test_close(self):
        """测试关闭客户端"""
        with patch('agent.extractors.image_extractor.AgentConfig.get_vision_config') as mock_config:
            with patch('agent.extractors.image_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-vl',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client_instance = Mock()
                mock_client.return_value = mock_client_instance
                
                extractor = ImageExtractor()
                extractor.close()
                
                mock_client_instance.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
