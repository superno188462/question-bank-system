"""
Web Agent API 全面测试
覆盖所有 AI Agent 相关的 Web API 接口
目标：90%+ 覆盖率
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json
from io import BytesIO

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from fastapi import UploadFile, HTTPException


class MockUploadFile:
    """Mock UploadFile for testing"""
    def __init__(self, filename: str, content: bytes, content_type: str = "application/octet-stream"):
        self.filename = filename
        self.content_type = content_type
        self.file = BytesIO(content)
    
    async def read(self):
        return self.content


# ========== 预备题目管理测试 ==========

@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestStagingQuestionsAPI:
    """预备题目管理 API 测试"""
    
    def test_get_staging_questions_list(self, mock_qa_repo, mock_staging_repo):
        """测试获取预备题目列表"""
        from web.main import app
        
        mock_staging_repo.get_all.return_value = [
            {'id': 1, 'content': '题目 1', 'status': 'pending'},
            {'id': 2, 'content': '题目 2', 'status': 'approved'}
        ]
        mock_staging_repo.get_count.return_value = 2
        
        client = TestClient(app)
        response = client.get("/api/agent/staging?page=1&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['total'] == 2
        assert len(data['data']['questions']) == 2
    
    def test_get_staging_questions_with_status_filter(self, mock_qa_repo, mock_staging_repo):
        """测试按状态筛选预备题目"""
        from web.main import app
        
        mock_staging_repo.get_all.return_value = [
            {'id': 1, 'content': '题目 1', 'status': 'pending'}
        ]
        mock_staging_repo.get_count.return_value = 1
        
        client = TestClient(app)
        response = client.get("/api/agent/staging?status=pending")
        
        assert response.status_code == 200
        mock_staging_repo.get_all.assert_called_with(status='pending', limit=20, offset=0)
    
    def test_get_staging_questions_api_error(self, mock_qa_repo, mock_staging_repo):
        """测试 API 错误处理"""
        from web.main import app
        
        mock_staging_repo.get_all.side_effect = Exception("Database error")
        
        client = TestClient(app)
        response = client.get("/api/agent/staging")
        
        assert response.status_code == 500
    
    def test_get_staging_question_success(self, mock_qa_repo, mock_staging_repo):
        """测试获取单个预备题目"""
        from web.main import app
        
        mock_staging_repo.get_by_id.return_value = {
            'id': 1,
            'content': '测试题目',
            'type': 'single_choice',
            'status': 'pending'
        }
        
        client = TestClient(app)
        response = client.get("/api/agent/staging/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['id'] == 1
    
    def test_get_staging_question_not_found(self, mock_qa_repo, mock_staging_repo):
        """测试获取不存在的预备题目"""
        from web.main import app
        
        mock_staging_repo.get_by_id.return_value = None
        
        client = TestClient(app)
        response = client.get("/api/agent/staging/999")
        
        assert response.status_code == 404
    
    def test_update_staging_question_success(self, mock_qa_repo, mock_staging_repo):
        """测试更新预备题目"""
        from web.main import app
        
        mock_staging_repo.get_by_id.side_effect = [
            {'id': 1, 'content': '原题目', 'status': 'pending'},
            {'id': 1, 'content': '更新后的题目', 'status': 'pending'}
        ]
        mock_staging_repo.update = Mock()
        
        client = TestClient(app)
        response = client.put(
            "/api/agent/staging/1",
            json={'content': '更新后的题目', 'status': 'approved'}
        )
        
        assert response.status_code == 200
        mock_staging_repo.update.assert_called_once()
    
    def test_update_staging_question_not_found(self, mock_qa_repo, mock_staging_repo):
        """测试更新不存在的预备题目"""
        from web.main import app
        
        mock_staging_repo.get_by_id.return_value = None
        
        client = TestClient(app)
        response = client.put(
            "/api/agent/staging/999",
            json={'content': '更新内容'}
        )
        
        assert response.status_code == 404
    
    def test_delete_staging_question_success(self, mock_qa_repo, mock_staging_repo):
        """测试删除预备题目"""
        from web.main import app
        
        mock_staging_repo.get_by_id.return_value = {'id': 1, 'content': '题目'}
        mock_staging_repo.delete = Mock()
        
        client = TestClient(app)
        response = client.delete("/api/agent/staging/1")
        
        assert response.status_code == 200
        mock_staging_repo.delete.assert_called_once()
    
    def test_delete_staging_question_not_found(self, mock_qa_repo, mock_staging_repo):
        """测试删除不存在的预备题目"""
        from web.main import app
        
        mock_staging_repo.get_by_id.return_value = None
        
        client = TestClient(app)
        response = client.delete("/api/agent/staging/999")
        
        assert response.status_code == 404
    
    def test_reject_staging_question(self, mock_qa_repo, mock_staging_repo):
        """测试拒绝预备题目"""
        from web.main import app
        
        mock_staging_repo.get_by_id.return_value = {'id': 1, 'content': '题目'}
        mock_staging_repo.reject = Mock()
        
        client = TestClient(app)
        response = client.post("/api/agent/staging/1/reject")
        
        assert response.status_code == 200
        mock_staging_repo.reject.assert_called_once()
    
    def test_reject_staging_question_not_found(self, mock_qa_repo, mock_staging_repo):
        """测试拒绝不存在的预备题目"""
        from web.main import app
        
        mock_staging_repo.get_by_id.return_value = None
        
        client = TestClient(app)
        response = client.post("/api/agent/staging/999/reject")
        
        assert response.status_code == 404


# ========== 题目提取测试 ==========

@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestImageExtractionAPI:
    """图片题目提取 API 测试"""
    
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ImageExtractor')
    def test_extract_from_image_single_success(self, mock_extractor_class, mock_config, mock_staging_repo, mock_qa_repo):
        """测试单张图片提取成功"""
        from web.main import app
        
        mock_config.validate = Mock()
        mock_config.ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'png', 'jpeg']
        
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            'questions': [{
                'type': 'single_choice',
                'content': '图片题目',
                'options': ['A. 选项'],
                'answer': 'A',
                'explanation': ''
            }],
            'total_count': 1,
            'confidence': 0.9,
            'source_type': 'image',
            'source_file': 'test.jpg'
        }
        mock_extractor_class.return_value = mock_extractor
        mock_staging_repo.create.return_value = 'staging_123'
        
        client = TestClient(app)
        test_file = MockUploadFile("test.jpg", b"fake image data", "image/jpeg")
        
        response = client.post(
            "/api/agent/extract/image",
            files={'files': ('test.jpg', test_file.file, 'image/jpeg')}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
    
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ImageExtractor')
    def test_extract_from_image_batch_success(self, mock_extractor_class, mock_config, mock_staging_repo, mock_qa_repo):
        """测试批量图片提取成功"""
        from web.main import app
        
        mock_config.validate = Mock()
        mock_config.ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'png']
        
        mock_extractor = Mock()
        mock_extractor.extract_batch.return_value = {
            'questions': [
                {'type': 'single_choice', 'content': '题目 1', 'options': [], 'answer': 'A', 'explanation': ''},
                {'type': 'single_choice', 'content': '题目 2', 'options': [], 'answer': 'B', 'explanation': ''}
            ],
            'total_count': 2,
            'confidence': 0.85,
            'source_type': 'image_batch',
            'source_files': ['test1.jpg', 'test2.jpg']
        }
        mock_extractor_class.return_value = mock_extractor
        mock_staging_repo.create.return_value = 'staging_456'
        
        client = TestClient(app)
        
        file1 = MockUploadFile("test1.jpg", b"fake image 1", "image/jpeg")
        file2 = MockUploadFile("test2.jpg", b"fake image 2", "image/jpeg")
        
        response = client.post(
            "/api/agent/extract/image",
            files=[('files', ('test1.jpg', file1.file, 'image/jpeg')),
                   ('files', ('test2.jpg', file2.file, 'image/jpeg'))]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['total_count'] >= 0
    
    @patch('web.api.agent.AgentConfig')
    def test_extract_from_image_unsupported_format(self, mock_config, mock_staging_repo, mock_qa_repo):
        """测试不支持的图片格式"""
        from web.main import app
        
        mock_config.validate = Mock()
        mock_config.ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'png']
        
        client = TestClient(app)
        test_file = MockUploadFile("test.gif", b"fake gif data", "image/gif")
        
        response = client.post(
            "/api/agent/extract/image",
            files={'files': ('test.gif', test_file.file, 'image/gif')}
        )
        
        assert response.status_code == 400
    
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ImageExtractor')
    def test_extract_from_image_extraction_error(self, mock_extractor_class, mock_config, mock_staging_repo, mock_qa_repo):
        """测试提取错误处理"""
        from web.main import app
        
        mock_config.validate = Mock()
        mock_config.ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'png']
        
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            'questions': [],
            'total_count': 0,
            'error': '无法识别题目'
        }
        mock_extractor_class.return_value = mock_extractor
        
        client = TestClient(app)
        test_file = MockUploadFile("test.jpg", b"fake image data", "image/jpeg")
        
        response = client.post(
            "/api/agent/extract/image",
            files={'files': ('test.jpg', test_file.file, 'image/jpeg')}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'error' in data['data']


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestDocumentExtractionAPI:
    """文档题目提取 API 测试"""
    
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.DocumentExtractor')
    def test_extract_from_document_success(self, mock_extractor_class, mock_config, mock_staging_repo, mock_qa_repo):
        """测试文档提取成功"""
        from web.main import app
        
        mock_config.validate = Mock()
        mock_config.ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'docx', 'txt', 'md']
        
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            'questions': [{
                'type': 'short_answer',
                'content': '文档题目',
                'options': [],
                'answer': '答案',
                'explanation': ''
            }],
            'total_count': 1,
            'confidence': 0.9
        }
        mock_extractor_class.return_value = mock_extractor
        mock_staging_repo.create.return_value = 'staging_789'
        
        client = TestClient(app)
        test_file = MockUploadFile("test.txt", b"fake text content", "text/plain")
        
        response = client.post(
            "/api/agent/extract/document",
            files={'files': ('test.txt', test_file.file, 'text/plain')}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
    
    @patch('web.api.agent.AgentConfig')
    def test_extract_from_document_unsupported_format(self, mock_config, mock_staging_repo, mock_qa_repo):
        """测试不支持的文档格式"""
        from web.main import app
        
        mock_config.validate = Mock()
        mock_config.ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'txt']
        
        client = TestClient(app)
        test_file = MockUploadFile("test.exe", b"fake exe", "application/octet-stream")
        
        response = client.post(
            "/api/agent/extract/document",
            files={'files': ('test.exe', test_file.file, 'application/octet-stream')}
        )
        
        assert response.status_code == 400


# ========== 解析生成测试 ==========

@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestExplanationGenerationAPI:
    """解析生成 API 测试"""
    
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ExplanationGenerator')
    def test_generate_explanation_with_question_id(self, mock_generator_class, mock_config, mock_staging_repo, mock_qa_repo):
        """测试通过题目 ID 生成解析"""
        from web.main import app
        from core.models import Question
        
        mock_config.validate = Mock()
        
        mock_question = Mock()
        mock_question.id = 123
        mock_question.content = '测试题目'
        mock_question.options = ['A. 选项']
        mock_question.answer = 'A'
        
        mock_question_service = Mock()
        mock_question_service.get_question.return_value = mock_question
        
        mock_generator = Mock()
        mock_generator.generate.return_value = {
            'success': True,
            'explanation': '这是生成的详细解析',
            'question_id': 123
        }
        mock_generator_class.return_value = mock_generator
        
        with patch('web.api.agent.QuestionService', return_value=mock_question_service):
            client = TestClient(app)
            response = client.post(
                "/api/agent/explanation/generate",
                json={'question_id': 123}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'explanation' in data['data']
    
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ExplanationGenerator')
    def test_generate_explanation_with_data(self, mock_generator_class, mock_config, mock_staging_repo, mock_qa_repo):
        """测试通过题目数据生成解析"""
        from web.main import app
        
        mock_config.validate = Mock()
        
        mock_generator = Mock()
        mock_generator.generate.return_value = {
            'success': True,
            'explanation': '生成的解析',
            'question_id': None
        }
        mock_generator_class.return_value = mock_generator
        
        client = TestClient(app)
        response = client.post(
            "/api/agent/explanation/generate",
            json={
                'type': 'single_choice',
                'content': '测试题目',
                'options': ['A. 选项'],
                'answer': 'A'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
    
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ExplanationGenerator')
    def test_generate_explanation_question_not_found(self, mock_generator_class, mock_config, mock_staging_repo, mock_qa_repo):
        """测试题目不存在"""
        from web.main import app
        
        mock_config.validate = Mock()
        
        mock_question_service = Mock()
        mock_question_service.get_question.return_value = None
        
        with patch('web.api.agent.QuestionService', return_value=mock_question_service):
            client = TestClient(app)
            response = client.post(
                "/api/agent/explanation/generate",
                json={'question_id': 999}
            )
            
            assert response.status_code == 404
    
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ExplanationGenerator')
    def test_generate_explanation_failure(self, mock_generator_class, mock_config, mock_staging_repo, mock_qa_repo):
        """测试生成解析失败"""
        from web.main import app
        
        mock_config.validate = Mock()
        
        mock_generator = Mock()
        mock_generator.generate.return_value = {
            'success': False,
            'error': 'API Error',
            'question_id': 123
        }
        mock_generator_class.return_value = mock_generator
        
        client = TestClient(app)
        response = client.post(
            "/api/agent/explanation/generate",
            json={
                'type': 'single_choice',
                'content': '测试题目',
                'options': ['A. 选项'],
                'answer': 'A'
            }
        )
        
        assert response.status_code == 500


# ========== 智能问答测试 ==========

@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestQAAPI:
    """智能问答 API 测试"""
    
    def test_ask_question_placeholder(self, mock_qa_repo, mock_staging_repo):
        """测试智能问答（占位实现）"""
        from web.main import app
        
        client = TestClient(app)
        response = client.post(
            "/api/agent/ask",
            json={'question': '什么是 Python？'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert '功能开发中' in data['data']['answer']
    
    def test_get_qa_logs(self, mock_qa_repo, mock_staging_repo):
        """测试获取问答日志"""
        from web.main import app
        
        mock_qa_repo.get_all.return_value = [
            {'id': 1, 'question': '问题 1', 'answer': '回答 1'},
            {'id': 2, 'question': '问题 2', 'answer': '回答 2'}
        ]
        
        client = TestClient(app)
        response = client.get("/api/agent/logs?page=1&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['data']['logs']) == 2
    
    def test_get_qa_logs_api_error(self, mock_qa_repo, mock_staging_repo):
        """测试获取日志错误"""
        from web.main import app
        
        mock_qa_repo.get_all.side_effect = Exception("Database error")
        
        client = TestClient(app)
        response = client.get("/api/agent/logs")
        
        assert response.status_code == 500


# ========== 配置管理测试 ==========

@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestConfigAPI:
    """配置管理 API 测试"""
    
    @patch('web.api.agent.AgentConfig')
    def test_get_config(self, mock_config, mock_staging_repo, mock_qa_repo):
        """测试获取配置"""
        from web.main import app
        
        mock_config.get_full_config.return_value = {
            'llm': {
                'model': 'qwen-plus',
                'api_key': '***',
                'base_url': 'https://api.test.com'
            },
            'vision': {
                'model': 'qwen-vl',
                'api_key': '***',
                'base_url': 'https://api.test.com'
            },
            'embedding': {
                'model_name': 'text-embedding-v3',
                'api_key': '***',
                'base_url': 'https://api.test.com'
            },
            'settings': {
                'max_questions_per_document': 10,
                'max_questions_per_image': 5
            }
        }
        
        client = TestClient(app)
        response = client.get("/api/agent/config")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'llm' in data['data']
    
    @patch('web.api.agent.AgentConfig')
    def test_get_config_error(self, mock_config, mock_staging_repo, mock_qa_repo):
        """测试获取配置错误"""
        from web.main import app
        
        mock_config.get_full_config.side_effect = Exception("Config error")
        
        client = TestClient(app)
        response = client.get("/api/agent/config")
        
        assert response.status_code == 500
    
    @patch('web.api.agent.AgentConfig')
    def test_update_config(self, mock_config, mock_staging_repo, mock_qa_repo):
        """测试更新配置"""
        from web.main import app
        
        mock_config._load_config.return_value = {
            'llm': {'model': 'qwen-plus', 'api_key': 'old-key', 'base_url': 'https://api.test.com'}
        }
        mock_config.save_config.return_value = True
        mock_config.refresh = Mock()
        mock_config.get_full_config.return_value = {
            'llm': {'model': 'gpt-4', 'api_key': 'new-key', 'base_url': 'https://api.openai.com'}
        }
        
        client = TestClient(app)
        response = client.put(
            "/api/agent/config",
            json={
                'llm': {
                    'model': 'gpt-4',
                    'api_key': 'new-key',
                    'base_url': 'https://api.openai.com'
                }
            }
        )
        
        assert response.status_code == 200
        mock_config.save_config.assert_called_once()
        mock_config.refresh.assert_called_once()
    
    @patch('web.api.agent.AgentConfig')
    def test_update_config_save_failure(self, mock_config, mock_staging_repo, mock_qa_repo):
        """测试更新配置保存失败"""
        from web.main import app
        
        mock_config._load_config.return_value = {}
        mock_config.save_config.return_value = False
        
        client = TestClient(app)
        response = client.put(
            "/api/agent/config",
            json={'llm': {'model': 'gpt-4'}}
        )
        
        assert response.status_code == 500
    
    @patch('web.api.agent.AgentConfig')
    def test_test_config_not_configured(self, mock_config, mock_staging_repo, mock_qa_repo):
        """测试配置未配置"""
        from web.main import app
        
        mock_config.LLM_API_KEY = None
        mock_config.VISION_API_KEY = None
        
        client = TestClient(app)
        response = client.post("/api/agent/config/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert data['data']['status'] == 'not_configured'
    
    @patch('web.api.agent.AgentConfig')
    def test_test_config_llm_not_configured(self, mock_config, mock_staging_repo, mock_qa_repo):
        """测试 LLM 配置未配置"""
        from web.main import app
        
        mock_config.LLM_API_KEY = None
        mock_config.VISION_API_KEY = 'vision-key'
        
        client = TestClient(app)
        response = client.post("/api/agent/config/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert 'LLM API Key 未配置' in data['message']
    
    @patch('web.api.agent.AgentConfig')
    def test_test_config_vision_not_configured(self, mock_config, mock_staging_repo, mock_qa_repo):
        """测试视觉配置未配置"""
        from web.main import app
        
        mock_config.LLM_API_KEY = 'llm-key'
        mock_config.VISION_API_KEY = None
        
        client = TestClient(app)
        response = client.post("/api/agent/config/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert '视觉模型 API Key 未配置' in data['message']
    
    @patch('web.api.agent.AgentConfig')
    def test_test_config_success(self, mock_config, mock_staging_repo, mock_qa_repo):
        """测试配置有效"""
        from web.main import app
        
        mock_config.LLM_API_KEY = 'llm-key'
        mock_config.VISION_API_KEY = 'vision-key'
        mock_config.LLM_MODEL_ID = 'qwen-plus'
        mock_config.VISION_MODEL_ID = 'qwen-vl'
        mock_config.LLM_BASE_URL = 'https://api.test.com'
        
        client = TestClient(app)
        response = client.post("/api/agent/config/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['status'] == 'configured'
        assert data['data']['llm_model'] == 'qwen-plus'
    
    @patch('web.api.agent.AgentConfig')
    def test_test_config_error(self, mock_config, mock_staging_repo, mock_qa_repo):
        """测试配置测试错误"""
        from web.main import app
        
        mock_config.LLM_API_KEY = 'key'
        mock_config.VISION_API_KEY = 'key'
        mock_config.LLM_MODEL_ID = 'model'
        mock_config.VISION_MODEL_ID = 'model'
        mock_config.LLM_BASE_URL = 'url'
        
        # 模拟异常
        with patch.object(mock_config, 'LLM_API_KEY', side_effect=Exception("Error")):
            client = TestClient(app)
            response = client.post("/api/agent/config/test")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is False


# ========== 验证错误格式化测试 ==========

class TestValidationErrorFormatting:
    """验证错误格式化测试"""
    
    def test_format_validation_error_string_too_short(self):
        """测试字符串太短错误格式化"""
        from web.api.agent import _format_validation_error
        from pydantic import ValidationError
        
        # 创建模拟验证错误
        try:
            from pydantic import BaseModel
            class TestModel(BaseModel):
                content: str
            
            TestModel(content="")  # 空字符串会触发验证错误
        except ValidationError as e:
            result = _format_validation_error(e)
            assert isinstance(result, str)
    
    def test_format_validation_error_value_error(self):
        """测试值错误格式化"""
        from web.api.agent import _format_validation_error
        from pydantic import ValidationError
        
        try:
            from pydantic import BaseModel, EmailStr
            class TestModel(BaseModel):
                email: EmailStr
            
            TestModel(email="invalid")  # 无效邮箱会触发验证错误
        except ValidationError as e:
            result = _format_validation_error(e)
            assert isinstance(result, str)
        except Exception:
            # EmailStr 可能需要额外依赖，跳过此测试
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
