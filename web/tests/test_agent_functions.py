"""
Web Agent API 单元测试
直接测试 web/api/agent.py 中的各个函数和端点
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


class TestAgentRouterDirect:
    """直接测试 Agent 路由函数"""
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ImageExtractor')
    def test_extract_from_image_success(self, mock_extractor_class, mock_config, mock_qa_repo, mock_staging_repo):
        """测试图片提取成功路径"""
        from web.api.agent import extract_from_image
        
        mock_config.validate = Mock()
        mock_config.ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'png']
        
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            'questions': [{'type': 'single_choice', 'content': '题目', 'options': [], 'answer': 'A', 'explanation': ''}],
            'total_count': 1,
            'confidence': 0.9,
            'source_type': 'image',
            'source_file': 'test.jpg'
        }
        mock_extractor_class.return_value = mock_extractor
        mock_staging_repo.create.return_value = 123  # 返回整数 ID
        
        # 创建 Mock 文件
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read = AsyncMock(return_value=b'fake image data')
        
        import asyncio
        result = asyncio.run(extract_from_image(files=[mock_file]))
        
        assert result.success is True
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ImageExtractor')
    def test_extract_from_image_extraction_error(self, mock_extractor_class, mock_config, mock_qa_repo, mock_staging_repo):
        """测试图片提取错误处理"""
        from web.api.agent import extract_from_image
        
        mock_config.validate = Mock()
        mock_config.ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'png']
        
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            'questions': [],
            'total_count': 0,
            'error': '无法识别'
        }
        mock_extractor_class.return_value = mock_extractor
        
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read = AsyncMock(return_value=b'fake data')
        
        import asyncio
        result = asyncio.run(extract_from_image(files=[mock_file]))
        
        assert result.success is True  # 即使提取失败也返回 success=True，但 data 中包含 error
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ImageExtractor')
    def test_extract_from_image_exception(self, mock_extractor_class, mock_config, mock_qa_repo, mock_staging_repo):
        """测试图片提取异常处理"""
        from web.api.agent import extract_from_image
        
        mock_config.validate = Mock()
        mock_config.ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'png']
        
        mock_extractor = Mock()
        mock_extractor.extract.side_effect = Exception("Unexpected error")
        mock_extractor_class.return_value = mock_extractor
        
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read = AsyncMock(return_value=b'fake data')
        
        import asyncio
        result = asyncio.run(extract_from_image(files=[mock_file]))
        
        assert result.success is False
        assert 'error' in result.data
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.DocumentExtractor')
    def test_extract_from_document_success(self, mock_extractor_class, mock_config, mock_qa_repo, mock_staging_repo):
        """测试文档提取成功"""
        from web.api.agent import extract_from_document
        
        mock_config.validate = Mock()
        mock_config.ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'txt']
        
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            'questions': [{'type': 'short_answer', 'content': '题目', 'options': [], 'answer': '答案', 'explanation': ''}],
            'total_count': 1,
            'confidence': 0.9
        }
        mock_extractor_class.return_value = mock_extractor
        mock_staging_repo.create.return_value = 456  # 返回整数 ID
        
        mock_file = Mock()
        mock_file.filename = 'test.txt'
        mock_file.read = AsyncMock(return_value=b'fake text')
        
        import asyncio
        result = asyncio.run(extract_from_document(files=[mock_file]))
        
        assert result.success is True
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    def test_get_staging_questions(self, mock_config, mock_qa_repo, mock_staging_repo):
        """测试获取预备题目列表"""
        from web.api.agent import get_staging_questions
        
        mock_staging_repo.get_all.return_value = [
            {'id': 1, 'content': '题目 1', 'status': 'pending'}
        ]
        mock_staging_repo.get_count.return_value = 1
        
        import asyncio
        result = asyncio.run(get_staging_questions(status='pending', page=1, limit=10))
        
        assert result.success is True
        assert result.data['total'] == 1
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    def test_get_staging_question_success(self, mock_qa_repo, mock_staging_repo):
        """测试获取单个预备题目"""
        from web.api.agent import get_staging_question
        
        mock_staging_repo.get_by_id.return_value = {'id': 1, 'content': '题目'}
        
        import asyncio
        result = asyncio.run(get_staging_question(question_id=1))
        
        assert result.success is True
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    def test_get_staging_question_not_found(self, mock_qa_repo, mock_staging_repo):
        """测试获取不存在的预备题目"""
        from web.api.agent import get_staging_question
        from fastapi import HTTPException
        
        mock_staging_repo.get_by_id.return_value = None
        
        with pytest.raises(HTTPException):
            import asyncio
            asyncio.run(get_staging_question(question_id=999))
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    def test_update_staging_question(self, mock_qa_repo, mock_staging_repo):
        """测试更新预备题目"""
        from web.api.agent import update_staging_question
        from core.models import StagingQuestionUpdate
        
        mock_staging_repo.get_by_id.side_effect = [
            {'id': 1, 'content': '原题目'},
            {'id': 1, 'content': '新题目'}
        ]
        mock_staging_repo.update = Mock()
        
        update_data = StagingQuestionUpdate(content='新题目')
        
        import asyncio
        result = asyncio.run(update_staging_question(question_id=1, update_data=update_data))
        
        assert result.success is True
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    def test_delete_staging_question(self, mock_qa_repo, mock_staging_repo):
        """测试删除预备题目"""
        from web.api.agent import delete_staging_question
        
        mock_staging_repo.get_by_id.return_value = {'id': 1, 'content': '题目'}
        mock_staging_repo.delete = Mock()
        
        import asyncio
        result = asyncio.run(delete_staging_question(question_id=1))
        
        assert result.success is True
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    def test_reject_staging_question(self, mock_qa_repo, mock_staging_repo):
        """测试拒绝预备题目"""
        from web.api.agent import reject_staging_question
        
        mock_staging_repo.get_by_id.return_value = {'id': 1, 'content': '题目'}
        mock_staging_repo.reject = Mock()
        
        import asyncio
        result = asyncio.run(reject_staging_question(question_id=1))
        
        assert result.success is True
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ExplanationGenerator')
    def test_generate_explanation_success(self, mock_generator_class, mock_config, mock_qa_repo, mock_staging_repo):
        """测试生成解析成功"""
        from web.api.agent import generate_explanation
        from core.models import ExplanationGenerateRequest
        
        mock_config.validate = Mock()
        
        mock_generator = Mock()
        mock_generator.generate.return_value = {
            'success': True,
            'explanation': '解析内容'
        }
        mock_generator_class.return_value = mock_generator
        
        request = ExplanationGenerateRequest(
            content='题目',
            options=['A'],
            answer='A',
            type='single_choice'
        )
        
        import asyncio
        result = asyncio.run(generate_explanation(request=request))
        
        assert result.success is True
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    @patch('web.api.agent.ExplanationGenerator')
    def test_generate_explanation_failure(self, mock_generator_class, mock_config, mock_qa_repo, mock_staging_repo):
        """测试生成解析失败"""
        from web.api.agent import generate_explanation
        from core.models import ExplanationGenerateRequest
        from fastapi import HTTPException
        
        mock_config.validate = Mock()
        
        mock_generator = Mock()
        mock_generator.generate.return_value = {
            'success': False,
            'error': 'API Error'
        }
        mock_generator_class.return_value = mock_generator
        
        request = ExplanationGenerateRequest(
            content='题目',
            options=['A'],
            answer='A'
        )
        
        with pytest.raises(HTTPException):
            import asyncio
            asyncio.run(generate_explanation(request=request))
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    def test_ask_question(self, mock_qa_repo, mock_staging_repo):
        """测试智能问答（占位实现）"""
        from web.api.agent import ask_question
        from core.models import QAAskRequest
        
        request = QAAskRequest(question='什么是 Python？')
        
        import asyncio
        result = asyncio.run(ask_question(request=request))
        
        assert result.success is True
        assert '功能开发中' in result.data['answer']
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    def test_get_qa_logs(self, mock_qa_repo, mock_staging_repo):
        """测试获取问答日志"""
        from web.api.agent import get_qa_logs
        
        mock_qa_repo.get_all.return_value = [
            {'id': 1, 'question': '问题', 'answer': '回答'}
        ]
        
        import asyncio
        result = asyncio.run(get_qa_logs(page=1, limit=10))
        
        assert result.success is True
        assert len(result.data['logs']) == 1
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    def test_get_config(self, mock_config, mock_qa_repo, mock_staging_repo):
        """测试获取配置"""
        from web.api.agent import get_agent_config
        
        mock_config.get_full_config.return_value = {
            'llm': {'model': 'qwen-plus'},
            'vision': {'model': 'qwen-vl'}
        }
        
        import asyncio
        result = asyncio.run(get_agent_config())
        
        assert result.success is True
        assert 'llm' in result.data
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    def test_update_config(self, mock_config, mock_qa_repo, mock_staging_repo):
        """测试更新配置"""
        from web.api.agent import update_agent_config
        from core.models import AgentConfigUpdate
        
        mock_config._load_config.return_value = {'llm': {'model': 'old'}}
        mock_config.save_config.return_value = True
        mock_config.refresh = Mock()
        mock_config.get_full_config.return_value = {'llm': {'model': 'new'}}
        
        config_update = AgentConfigUpdate(llm={'model': 'new'})
        
        import asyncio
        result = asyncio.run(update_agent_config(config_update=config_update))
        
        assert result.success is True
        mock_config.refresh.assert_called_once()
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    def test_update_config_save_failure(self, mock_config, mock_qa_repo, mock_staging_repo):
        """测试更新配置保存失败"""
        from web.api.agent import update_agent_config
        from core.models import AgentConfigUpdate
        from fastapi import HTTPException
        
        mock_config._load_config.return_value = {}
        mock_config.save_config.return_value = False
        
        config_update = AgentConfigUpdate(llm={})
        
        with pytest.raises(HTTPException):
            import asyncio
            asyncio.run(update_agent_config(config_update=config_update))
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    def test_test_config_not_configured(self, mock_config, mock_qa_repo, mock_staging_repo):
        """测试配置未配置"""
        from web.api.agent import test_agent_config
        
        mock_config.LLM_API_KEY = None
        mock_config.VISION_API_KEY = None
        
        import asyncio
        result = asyncio.run(test_agent_config())
        
        assert result.success is False
        assert result.data['status'] == 'not_configured'
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.AgentConfig')
    def test_test_config_success(self, mock_config, mock_qa_repo, mock_staging_repo):
        """测试配置有效"""
        from web.api.agent import test_agent_config
        
        mock_config.LLM_API_KEY = 'key'
        mock_config.VISION_API_KEY = 'key'
        mock_config.LLM_MODEL_ID = 'model'
        mock_config.VISION_MODEL_ID = 'model'
        mock_config.LLM_BASE_URL = 'url'
        
        import asyncio
        result = asyncio.run(test_agent_config())
        
        assert result.success is True
        assert result.data['status'] == 'configured'


class TestValidationErrorFormatting:
    """验证错误格式化函数测试"""
    
    def test_format_validation_error_empty(self):
        """测试空错误列表"""
        from web.api.agent import _format_validation_error
        from pydantic import ValidationError
        
        # 创建 mock ValidationError
        mock_error = Mock(spec=ValidationError)
        mock_error.errors.return_value = []
        
        result = _format_validation_error(mock_error)
        assert result == ""
    
    def test_format_validation_error_string_too_short(self):
        """测试字符串太短错误"""
        from web.api.agent import _format_validation_error
        from pydantic import ValidationError
        
        mock_error = Mock(spec=ValidationError)
        mock_error.errors.return_value = [
            {'loc': ('content',), 'type': 'string_too_short', 'msg': 'String should have at least 1 character'}
        ]
        
        result = _format_validation_error(mock_error)
        assert '题干' in result or '不能为空' in result
    
    def test_format_validation_error_value_error(self):
        """测试值错误"""
        from web.api.agent import _format_validation_error
        from pydantic import ValidationError
        
        mock_error = Mock(spec=ValidationError)
        mock_error.errors.return_value = [
            {'loc': ('answer',), 'type': 'value_error', 'msg': 'Value error'}
        ]
        
        result = _format_validation_error(mock_error)
        assert '答案' in result or '格式不正确' in result
    
    def test_format_validation_error_unknown(self):
        """测试未知错误类型"""
        from web.api.agent import _format_validation_error
        from pydantic import ValidationError
        
        mock_error = Mock(spec=ValidationError)
        mock_error.errors.return_value = [
            {'loc': ('unknown_field',), 'type': 'unknown_error', 'msg': 'Unknown error'}
        ]
        
        result = _format_validation_error(mock_error)
        assert '验证失败' in result


class TestApproveStagingQuestion:
    """审核预备题目测试"""
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.CategoryRepository')
    @patch('web.api.agent.QuestionRepository')
    @patch('web.api.agent.VectorIndex')
    @patch('web.api.agent.get_embedding_service')
    @patch('web.api.agent.get_db_connection')
    def test_approve_staging_success(self, mock_db_conn, mock_embedding_svc, mock_vector_index, 
                                     mock_question_repo, mock_category_repo, mock_qa_repo, mock_staging_repo):
        """测试审核通过成功"""
        from web.api.agent import approve_staging_question
        
        # Mock 预备题目
        mock_staging_repo.get_by_id.return_value = {
            'id': 1,
            'content': '测试题目',
            'options': ['A'],
            'answer': 'A',
            'explanation': '',
            'category_id': None
        }
        
        # Mock 分类
        mock_category = Mock()
        mock_category.id = 1
        mock_category.parent_id = None
        mock_category_repo.return_value.get_all.return_value = [mock_category]
        
        # Mock 题目创建
        mock_created = Mock()
        mock_created.id = 'q123'
        mock_question_repo.return_value.create.return_value = mock_created
        
        # Mock 向量索引
        mock_vector_index.return_value.add = Mock()
        
        # Mock Embedding
        mock_embedding_service = Mock()
        mock_embedding_service.embed.return_value = [0.1, 0.2, 0.3]
        mock_embedding_svc.return_value = mock_embedding_service
        
        import asyncio
        result = asyncio.run(approve_staging_question(question_id=1, reviewed_by="test", force=False))
        
        assert result.success is True
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    def test_approve_staging_not_found(self, mock_qa_repo, mock_staging_repo):
        """测试审核不存在的题目"""
        from web.api.agent import approve_staging_question
        from fastapi import HTTPException
        
        mock_staging_repo.get_by_id.return_value = None
        
        with pytest.raises(HTTPException):
            import asyncio
            asyncio.run(approve_staging_question(question_id=999))
    
    @patch('web.api.agent.StagingQuestionRepository')
    @patch('web.api.agent.QALogRepository')
    @patch('web.api.agent.CategoryRepository')
    def test_approve_staging_no_category(self, mock_category_repo, mock_qa_repo, mock_staging_repo):
        """测试没有可用分类"""
        from web.api.agent import approve_staging_question
        from fastapi import HTTPException
        
        mock_staging_repo.get_by_id.return_value = {
            'id': 1,
            'content': '题目',
            'options': [],
            'answer': 'A',
            'category_id': None
        }
        
        mock_category_repo.return_value.get_all.return_value = []
        
        with pytest.raises(HTTPException):
            import asyncio
            asyncio.run(approve_staging_question(question_id=1))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
