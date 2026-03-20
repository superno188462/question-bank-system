"""
Web Agent API 测试
测试 AI Agent 相关的 Web API 接口
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json
from io import BytesIO

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from fastapi import UploadFile


class MockUploadFile:
    """Mock UploadFile for testing"""
    def __init__(self, filename: str, content: bytes, content_type: str = "application/octet-stream"):
        self.filename = filename
        self.content_type = content_type
        self.file = BytesIO(content)
    
    async def read(self):
        return self.content


# 需要 patch 数据库和外部依赖后才能导入 app
@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_get_staging_questions(mock_qa_repo, mock_staging_repo):
    """测试获取预备题目列表"""
    from web.main import app
    
    # Mock 数据
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
    assert len(data['data']['questions']) == 2
    assert data['data']['total'] == 2


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_get_staging_question_not_found(mock_qa_repo, mock_staging_repo):
    """测试获取不存在的预备题目"""
    from web.main import app
    
    mock_staging_repo.get_by_id.return_value = None
    
    client = TestClient(app)
    response = client.get("/api/agent/staging/999")
    
    assert response.status_code == 404


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_get_staging_question_success(mock_qa_repo, mock_staging_repo):
    """测试获取预备题目成功"""
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


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_update_staging_question(mock_qa_repo, mock_staging_repo):
    """测试更新预备题目"""
    from web.main import app
    
    # Mock 第一次查询返回题目
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


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_update_staging_question_not_found(mock_qa_repo, mock_staging_repo):
    """测试更新不存在的预备题目"""
    from web.main import app
    
    mock_staging_repo.get_by_id.return_value = None
    
    client = TestClient(app)
    response = client.put(
        "/api/agent/staging/999",
        json={'content': '更新内容'}
    )
    
    assert response.status_code == 404


@patch('web.api.agent.AgentConfig')
@patch('web.api.agent.ImageExtractor')
@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_extract_from_image_success(mock_qa_repo, mock_staging_repo, mock_extractor_class, mock_config):
    """测试从图片提取题目成功"""
    from web.main import app
    
    # Mock 配置验证
    mock_config.validate = Mock()
    mock_config.ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'png', 'jpeg']
    
    # Mock 提取器
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
    
    # Mock 保存预备题目
    mock_staging_repo.create.return_value = 'staging_123'
    
    client = TestClient(app)
    
    # 创建测试文件
    test_file = MockUploadFile("test.jpg", b"fake image data", "image/jpeg")
    
    response = client.post(
        "/api/agent/extract/image",
        files={'files': ('test.jpg', test_file.file, 'image/jpeg')}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['data']['total_count'] >= 0


@patch('web.api.agent.AgentConfig')
@patch('web.api.agent.ImageExtractor')
@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_extract_from_image_unsupported_format(mock_qa_repo, mock_staging_repo, mock_extractor_class, mock_config):
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
@patch('web.api.agent.DocumentExtractor')
@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_extract_from_document_success(mock_qa_repo, mock_staging_repo, mock_extractor_class, mock_config):
    """测试从文档提取题目成功"""
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
    
    mock_staging_repo.create.return_value = 'staging_456'
    
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
@patch('web.api.agent.DocumentExtractor')
@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_extract_from_document_unsupported_format(mock_qa_repo, mock_staging_repo, mock_extractor_class, mock_config):
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


@patch('web.api.agent.AgentConfig')
@patch('web.api.agent.ExplanationGenerator')
@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_generate_explanation_success(mock_qa_repo, mock_staging_repo, mock_generator_class, mock_config):
    """测试生成解析成功"""
    from web.main import app
    
    mock_config.validate = Mock()
    
    mock_generator = Mock()
    mock_generator.generate.return_value = {
        'success': True,
        'explanation': '这是生成的详细解析',
        'question_id': 123
    }
    mock_generator_class.return_value = mock_generator
    
    client = TestClient(app)
    
    response = client.post(
        "/api/agent/explanation/generate",
        json={
            'question_id': 123,
            'type': 'single_choice',
            'content': '测试题目',
            'options': ['A. 选项'],
            'answer': 'A'
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'explanation' in data['data']


@patch('web.api.agent.AgentConfig')
@patch('web.api.agent.ExplanationGenerator')
@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_generate_explanation_failure(mock_qa_repo, mock_staging_repo, mock_generator_class, mock_config):
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
            'question_id': 123,
            'type': 'single_choice',
            'content': '测试题目',
            'options': ['A. 选项'],
            'answer': 'A'
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is False
    assert 'error' in data['data']


@patch('web.api.agent.AgentConfig')
@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_get_config(mock_qa_repo, mock_staging_repo, mock_config):
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
    assert 'vision' in data['data']


@patch('web.api.agent.AgentConfig')
@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_update_config(mock_qa_repo, mock_staging_repo, mock_config):
    """测试更新配置"""
    from web.main import app
    
    mock_config.update_config = Mock()
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
    mock_config.update_config.assert_called_once()


@patch('web.api.agent.AgentConfig')
@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_validate_config_success(mock_qa_repo, mock_staging_repo, mock_config):
    """测试验证配置成功"""
    from web.main import app
    
    mock_config.validate = Mock()
    
    client = TestClient(app)
    response = client.post("/api/agent/config/validate")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True


@patch('web.api.agent.AgentConfig')
@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_validate_config_failure(mock_qa_repo, mock_staging_repo, mock_config):
    """测试验证配置失败"""
    from web.main import app
    
    mock_config.validate = Mock(side_effect=Exception("配置错误"))
    
    client = TestClient(app)
    response = client.post("/api/agent/config/validate")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is False
    assert 'error' in data['data']


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_delete_staging_question(mock_qa_repo, mock_staging_repo):
    """测试删除预备题目"""
    from web.main import app
    
    mock_staging_repo.get_by_id.return_value = {'id': 1, 'content': '题目'}
    mock_staging_repo.delete = Mock()
    
    client = TestClient(app)
    response = client.delete("/api/agent/staging/1")
    
    assert response.status_code == 200
    mock_staging_repo.delete.assert_called_once()


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
def test_delete_staging_question_not_found(mock_qa_repo, mock_staging_repo):
    """测试删除不存在的预备题目"""
    from web.main import app
    
    mock_staging_repo.get_by_id.return_value = None
    
    client = TestClient(app)
    response = client.delete("/api/agent/staging/999")
    
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
