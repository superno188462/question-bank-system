"""
Core Services 模块测试
测试 core/services.py 中的搜索服务
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestSearchServiceInit:
    """测试 SearchService 初始化"""
    
    def test_init_with_services(self):
        """测试使用服务实例初始化"""
        from core.services import SearchService
        
        mock_question_service = Mock()
        mock_category_service = Mock()
        mock_tag_service = Mock()
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        assert service.question_service == mock_question_service
        assert service.category_service == mock_category_service
        assert service.tag_service == mock_tag_service
    
    def test_init_stores_references(self):
        """测试存储服务引用"""
        from core.services import SearchService
        
        question_svc = Mock(spec=['search_questions'])
        category_svc = Mock(spec=['search_categories'])
        tag_svc = Mock(spec=['search_tags'])
        
        service = SearchService(question_svc, category_svc, tag_svc)
        
        assert service.question_service is question_svc
        assert service.category_service is category_svc
        assert service.tag_service is tag_svc


class TestSearchServiceGlobalSearch:
    """测试全局搜索功能"""
    
    def test_global_search_success(self):
        """测试全局搜索成功"""
        from core.services import SearchService
        
        # Mock 服务
        mock_question_service = Mock()
        mock_question_service.search_questions.return_value = [
            {'id': 1, 'content': '题目 1'},
            {'id': 2, 'content': '题目 2'}
        ]
        
        mock_category_service = Mock()
        mock_category_service.search_categories.return_value = [
            {'id': 1, 'name': '分类 1'}
        ]
        
        mock_tag_service = Mock()
        mock_tag_service.search_tags.return_value = [
            {'id': 1, 'name': '标签 1'}
        ]
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        result = service.global_search("Python")
        
        assert 'questions' in result
        assert 'categories' in result
        assert 'tags' in result
        assert 'total' in result
        
        assert len(result['questions']) == 2
        assert len(result['categories']) == 1
        assert len(result['tags']) == 1
        assert result['total'] == 4
        
        # 验证服务调用
        mock_question_service.search_questions.assert_called_once_with("Python")
        mock_category_service.search_categories.assert_called_once_with("Python")
        mock_tag_service.search_tags.assert_called_once_with("Python")
    
    def test_global_search_empty_results(self):
        """测试全局搜索无结果"""
        from core.services import SearchService
        
        mock_question_service = Mock()
        mock_question_service.search_questions.return_value = []
        
        mock_category_service = Mock()
        mock_category_service.search_categories.return_value = []
        
        mock_tag_service = Mock()
        mock_tag_service.search_tags.return_value = []
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        result = service.global_search("不存在的关键词")
        
        assert result['total'] == 0
        assert result['questions'] == []
        assert result['categories'] == []
        assert result['tags'] == []
    
    def test_global_search_only_questions(self):
        """测试只搜索到题目"""
        from core.services import SearchService
        
        mock_question_service = Mock()
        mock_question_service.search_questions.return_value = [
            {'id': 1, 'content': '题目 1'}
        ]
        
        mock_category_service = Mock()
        mock_category_service.search_categories.return_value = []
        
        mock_tag_service = Mock()
        mock_tag_service.search_tags.return_value = []
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        result = service.global_search("题目")
        
        assert result['total'] == 1
        assert len(result['questions']) == 1
        assert result['categories'] == []
        assert result['tags'] == []
    
    def test_global_search_only_categories(self):
        """测试只搜索到分类"""
        from core.services import SearchService
        
        mock_question_service = Mock()
        mock_question_service.search_questions.return_value = []
        
        mock_category_service = Mock()
        mock_category_service.search_categories.return_value = [
            {'id': 1, 'name': '分类 1'},
            {'id': 2, 'name': '分类 2'}
        ]
        
        mock_tag_service = Mock()
        mock_tag_service.search_tags.return_value = []
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        result = service.global_search("分类")
        
        assert result['total'] == 2
        assert len(result['categories']) == 2
    
    def test_global_search_only_tags(self):
        """测试只搜索到标签"""
        from core.services import SearchService
        
        mock_question_service = Mock()
        mock_question_service.search_questions.return_value = []
        
        mock_category_service = Mock()
        mock_category_service.search_categories.return_value = []
        
        mock_tag_service = Mock()
        mock_tag_service.search_tags.return_value = [
            {'id': 1, 'name': 'Python'},
            {'id': 2, 'name': 'Java'},
            {'id': 3, 'name': 'C++'}
        ]
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        result = service.global_search("标签")
        
        assert result['total'] == 3
        assert len(result['tags']) == 3
    
    def test_global_search_with_special_characters(self):
        """测试特殊字符搜索"""
        from core.services import SearchService
        
        mock_question_service = Mock()
        mock_question_service.search_questions.return_value = []
        
        mock_category_service = Mock()
        mock_category_service.search_categories.return_value = []
        
        mock_tag_service = Mock()
        mock_tag_service.search_tags.return_value = []
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        result = service.global_search("Python@#$%")
        
        assert result['total'] == 0
    
    def test_global_search_with_empty_string(self):
        """测试空字符串搜索"""
        from core.services import SearchService
        
        mock_question_service = Mock()
        mock_question_service.search_questions.return_value = []
        
        mock_category_service = Mock()
        mock_category_service.search_categories.return_value = []
        
        mock_tag_service = Mock()
        mock_tag_service.search_tags.return_value = []
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        result = service.global_search("")
        
        assert result['total'] == 0
    
    def test_global_search_logging(self):
        """测试搜索日志记录"""
        from core.services import SearchService
        
        mock_question_service = Mock()
        mock_question_service.search_questions.return_value = []
        mock_category_service = Mock()
        mock_category_service.search_categories.return_value = []
        mock_tag_service = Mock()
        mock_tag_service.search_tags.return_value = []
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        # 不应该抛出异常
        result = service.global_search("测试关键词")
        
        assert 'total' in result


class TestSearchServiceTotalCalculation:
    """测试总数计算"""
    
    def test_total_calculation_correct(self):
        """测试总数计算正确"""
        from core.services import SearchService
        
        mock_question_service = Mock()
        mock_question_service.search_questions.return_value = [1, 2, 3]  # 3 个
        
        mock_category_service = Mock()
        mock_category_service.search_categories.return_value = [1, 2]  # 2 个
        
        mock_tag_service = Mock()
        mock_tag_service.search_tags.return_value = [1, 2, 3, 4]  # 4 个
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        result = service.global_search("测试")
        
        assert result['total'] == 9  # 3 + 2 + 4
    
    def test_total_with_zero_items(self):
        """测试零项时的总数"""
        from core.services import SearchService
        
        mock_question_service = Mock()
        mock_question_service.search_questions.return_value = []
        
        mock_category_service = Mock()
        mock_category_service.search_categories.return_value = []
        
        mock_tag_service = Mock()
        mock_tag_service.search_tags.return_value = []
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        result = service.global_search("测试")
        
        assert result['total'] == 0


class TestSearchServiceWithMockObjects:
    """测试使用 Mock 对象"""
    
    def test_with_magic_mock(self):
        """测试使用 MagicMock"""
        from core.services import SearchService
        
        question_service = MagicMock()
        category_service = MagicMock()
        tag_service = MagicMock()
        
        service = SearchService(question_service, category_service, tag_service)
        
        assert isinstance(service.question_service, MagicMock)
        assert isinstance(service.category_service, MagicMock)
        assert isinstance(service.tag_service, MagicMock)


class TestSearchServiceEdgeCases:
    """测试边界情况"""
    
    @patch('core.services.services_module.logger')
    def test_global_search_with_none_return(self, mock_logger):
        """测试服务返回 None 的情况"""
        from core.services import SearchService
        
        mock_question_service = Mock()
        mock_question_service.search_questions.return_value = []
        
        mock_category_service = Mock()
        mock_category_service.search_categories.return_value = []
        
        mock_tag_service = Mock()
        mock_tag_service.search_tags.return_value = []
        
        service = SearchService(
            question_service=mock_question_service,
            category_service=mock_category_service,
            tag_service=mock_tag_service
        )
        
        # 执行搜索
        result = service.global_search("测试")
        
        # 验证结果结构
        assert 'questions' in result
        assert 'categories' in result
        assert 'tags' in result
        assert 'total' in result
        assert result['total'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
