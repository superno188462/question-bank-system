"""
QuestionService 测试
测试题目管理服务的功能
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.models import Question, QuestionCreate, QuestionUpdate, Category, Tag, CategoryCreate, TagCreate
from core.services.question_service import QuestionService
from core.database.repositories import QuestionRepository, CategoryRepository, TagRepository


@pytest.fixture
def mock_repos():
    """创建模拟的仓库对象"""
    question_repo = Mock(spec=QuestionRepository)
    category_repo = Mock(spec=CategoryRepository)
    tag_repo = Mock(spec=TagRepository)
    return question_repo, category_repo, tag_repo


@pytest.fixture
def question_service(mock_repos):
    """创建 QuestionService 实例"""
    question_repo, category_repo, tag_repo = mock_repos
    return QuestionService(question_repo, category_repo, tag_repo)


class TestQuestionServiceCreate:
    """测试 QuestionService.create_question 方法"""
    
    def test_create_question_success(self, question_service, mock_repos):
        """测试成功创建题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        # 准备数据
        category = Category(id="cat-1", name="测试分类", description="测试", parent_id=None)
        category_repo.get_by_id.return_value = category
        
        created_question = Question(
            id="q-1",
            content="测试题目内容",
            options=["A. 选项 1", "B. 选项 2"],
            answer="A",
            explanation="这是解析",
            category_id="cat-1",
            category_name="测试分类"
        )
        question_repo.create.return_value = created_question
        question_repo.get_question_tags.return_value = []
        question_repo.get_by_id.return_value = created_question
        
        question_data = QuestionCreate(
            content="测试题目内容",
            options=["A. 选项 1", "B. 选项 2"],
            answer="A",
            explanation="这是解析",
            category_id="cat-1",
            tag_ids=[]
        )
        
        result = question_service.create_question(question_data)
        
        assert result is not None
        assert result.id == "q-1"
        assert result.content == "测试题目内容"
        category_repo.get_by_id.assert_called_with("cat-1")
        question_repo.create.assert_called_once()
    
    def test_create_question_with_tags(self, question_service, mock_repos):
        """测试创建带标签的题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        # 准备数据
        category = Category(id="cat-1", name="测试分类", description="测试", parent_id=None)
        tag = Tag(id="tag-1", name="测试标签", color="#FF0000")
        
        category_repo.get_by_id.return_value = category
        tag_repo.get_by_id.return_value = tag
        
        created_question = Question(
            id="q-1",
            content="测试题目",
            options=[],
            answer="A",
            explanation="解析",
            category_id="cat-1"
        )
        question_repo.create.return_value = created_question
        question_repo.get_question_tags.return_value = [tag]
        question_repo.add_tags.return_value = True
        question_repo.get_by_id.return_value = created_question
        
        question_data = QuestionCreate(
            content="测试题目",
            options=[],
            answer="A",
            explanation="解析",
            category_id="cat-1",
            tag_ids=["tag-1"]
        )
        
        result = question_service.create_question(question_data)
        
        assert result is not None
        question_repo.add_tags.assert_called_with("q-1", ["tag-1"])
    
    def test_create_question_category_not_found(self, question_service, mock_repos):
        """测试创建题目时分类不存在"""
        question_repo, category_repo, tag_repo = mock_repos
        
        category_repo.get_by_id.return_value = None
        
        question_data = QuestionCreate(
            content="测试题目",
            options=[],
            answer="A",
            explanation="解析",
            category_id="nonexistent-cat"
        )
        
        with pytest.raises(ValueError, match="分类不存在"):
            question_service.create_question(question_data)
    
    def test_create_question_tag_not_found(self, question_service, mock_repos):
        """测试创建题目时标签不存在"""
        question_repo, category_repo, tag_repo = mock_repos
        
        category = Category(id="cat-1", name="测试分类", description="测试", parent_id=None)
        category_repo.get_by_id.return_value = category
        tag_repo.get_by_id.return_value = None
        
        question_data = QuestionCreate(
            content="测试题目",
            options=[],
            answer="A",
            explanation="解析",
            category_id="cat-1",
            tag_ids=["nonexistent-tag"]
        )
        
        with pytest.raises(ValueError, match="标签不存在"):
            question_service.create_question(question_data)


class TestQuestionServiceGet:
    """测试 QuestionService 获取题目方法"""
    
    def test_get_question_success(self, question_service, mock_repos):
        """测试成功获取题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        category = Category(id="cat-1", name="测试分类", description="测试", parent_id=None)
        question = Question(
            id="q-1",
            content="测试题目",
            options=[],
            answer="A",
            explanation="解析",
            category_id="cat-1"
        )
        
        question_repo.get_by_id.return_value = question
        category_repo.get_by_id.return_value = category
        
        result = question_service.get_question("q-1")
        
        assert result is not None
        assert result.category_name == "测试分类"
        question_repo.get_by_id.assert_called_with("q-1")
    
    def test_get_question_not_found(self, question_service, mock_repos):
        """测试获取不存在的题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        question_repo.get_by_id.return_value = None
        
        result = question_service.get_question("nonexistent-id")
        
        assert result is None
    
    def test_get_question_with_tags(self, question_service, mock_repos):
        """测试获取题目及标签"""
        question_repo, category_repo, tag_repo = mock_repos
        
        question = Question(
            id="q-1",
            content="测试题目",
            options=[],
            answer="A",
            explanation="解析",
            category_id="cat-1"
        )
        tag = Tag(id="tag-1", name="测试标签", color="#FF0000")
        
        question_repo.get_by_id.return_value = question
        question_repo.get_question_tags.return_value = [tag]
        
        result = question_service.get_question_with_tags("q-1")
        
        assert result is not None
        assert hasattr(result, 'tag_ids')
        assert "tag-1" in result.tag_ids
    
    def test_get_all_questions(self, question_service, mock_repos):
        """测试获取所有题目（分页）"""
        question_repo, category_repo, tag_repo = mock_repos
        
        questions = [
            Question(id="q-1", content="题目 1", options=[], answer="A", explanation="解析 1", category_id="cat-1"),
            Question(id="q-2", content="题目 2", options=[], answer="B", explanation="解析 2", category_id="cat-1")
        ]
        
        question_repo.get_all.return_value = {
            "data": questions,
            "total": 2,
            "page": 1,
            "limit": 20,
            "pages": 1
        }
        category_repo.get_by_id.return_value = Category(id="cat-1", name="测试分类", description="测试", parent_id=None)
        
        result = question_service.get_all_questions(page=1, limit=20)
        
        assert result["total"] == 2
        assert len(result["data"]) == 2
        assert result["data"][0].category_name == "测试分类"
    
    def test_get_all_questions_with_filters(self, question_service, mock_repos):
        """测试带筛选条件获取题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        question_repo.get_all.return_value = {
            "data": [],
            "total": 0,
            "page": 1,
            "limit": 20,
            "pages": 0
        }
        
        result = question_service.get_all_questions(
            category_id="cat-1",
            tag_id="tag-1",
            keyword="测试",
            page=1,
            limit=10
        )
        
        question_repo.get_all.assert_called_with(
            category_id="cat-1",
            tag_id="tag-1",
            keyword="测试",
            page=1,
            limit=10
        )


class TestQuestionServiceUpdate:
    """测试 QuestionService.update_question 方法"""
    
    def test_update_question_success(self, question_service, mock_repos):
        """测试成功更新题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        old_question = Question(
            id="q-1",
            content="原题目",
            options=[],
            answer="A",
            explanation="原解析",
            category_id="cat-1"
        )
        updated_question = Question(
            id="q-1",
            content="新题目",
            options=[],
            answer="A",
            explanation="新解析",
            category_id="cat-1"
        )
        
        question_repo.get_by_id.return_value = old_question
        question_repo.update.return_value = updated_question
        
        update_data = QuestionUpdate(content="新题目", explanation="新解析")
        result = question_service.update_question("q-1", update_data)
        
        assert result is not None
        assert result.content == "新题目"
        question_repo.update.assert_called_with("q-1", update_data)
    
    def test_update_question_not_found(self, question_service, mock_repos):
        """测试更新不存在的题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        question_repo.get_by_id.return_value = None
        question_repo.update.return_value = None
        
        update_data = QuestionUpdate(content="新题目")
        result = question_service.update_question("nonexistent-id", update_data)
        
        assert result is None


class TestQuestionServiceDelete:
    """测试 QuestionService.delete_question 方法"""
    
    def test_delete_question_success(self, question_service, mock_repos):
        """测试成功删除题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        question_repo.delete.return_value = True
        
        result = question_service.delete_question("q-1")
        
        assert result is True
        question_repo.delete.assert_called_with("q-1")
    
    def test_delete_question_not_found(self, question_service, mock_repos):
        """测试删除不存在的题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        question_repo.delete.return_value = False
        
        result = question_service.delete_question("nonexistent-id")
        
        assert result is False


class TestQuestionServiceTagManagement:
    """测试 QuestionService 标签管理方法"""
    
    def test_add_tag_to_question_success(self, question_service, mock_repos):
        """测试成功添加标签到题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        question = Question(id="q-1", content="题目", options=[], answer="A", explanation="解析", category_id="cat-1")
        tag = Tag(id="tag-1", name="标签", color="#FF0000")
        
        question_repo.get_by_id.return_value = question
        tag_repo.get_by_id.return_value = tag
        question_repo.add_tag.return_value = True
        
        result = question_service.add_tag_to_question("q-1", "tag-1")
        
        assert result is True
        question_repo.add_tag.assert_called_with("q-1", "tag-1")
    
    def test_add_tag_to_question_not_found(self, question_service, mock_repos):
        """测试添加标签时题目或标签不存在"""
        question_repo, category_repo, tag_repo = mock_repos
        
        question_repo.get_by_id.return_value = None
        tag_repo.get_by_id.return_value = None
        
        result = question_service.add_tag_to_question("q-1", "tag-1")
        
        assert result is False
    
    def test_remove_tag_from_question_success(self, question_service, mock_repos):
        """测试成功从题目移除标签"""
        question_repo, category_repo, tag_repo = mock_repos
        
        question_repo.remove_tag.return_value = True
        
        result = question_service.remove_tag_from_question("q-1", "tag-1")
        
        assert result is True
        question_repo.remove_tag.assert_called_with("q-1", "tag-1")
    
    def test_remove_tag_from_question_failure(self, question_service, mock_repos):
        """测试移除标签失败"""
        question_repo, category_repo, tag_repo = mock_repos
        
        question_repo.remove_tag.return_value = False
        
        result = question_service.remove_tag_from_question("q-1", "tag-1")
        
        assert result is False


class TestQuestionServiceSearch:
    """测试 QuestionService 搜索方法"""
    
    def test_get_questions_by_category(self, question_service, mock_repos):
        """测试按分类获取题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        questions = [
            Question(id="q-1", content="题目 1", options=[], answer="A", explanation="解析 1", category_id="cat-1")
        ]
        question_repo.get_by_category.return_value = questions
        
        result = question_service.get_questions_by_category("cat-1")
        
        assert isinstance(result, list)
        question_repo.get_by_category.assert_called_with("cat-1")
    
    def test_get_questions_by_tag(self, question_service, mock_repos):
        """测试按标签获取题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        questions = [
            Question(id="q-1", content="题目 1", options=[], answer="A", explanation="解析 1", category_id="cat-1")
        ]
        question_repo.get_by_tag.return_value = questions
        
        result = question_service.get_questions_by_tag("tag-1")
        
        assert isinstance(result, list)
        question_repo.get_by_tag.assert_called_with("tag-1")
    
    def test_search_questions(self, question_service, mock_repos):
        """测试搜索题目"""
        question_repo, category_repo, tag_repo = mock_repos
        
        questions = [
            Question(id="q-1", content="测试题目", options=[], answer="A", explanation="解析", category_id="cat-1")
        ]
        question_repo.search.return_value = questions
        
        result = question_service.search_questions("测试")
        
        assert isinstance(result, list)
        assert len(result) == 1
        question_repo.search.assert_called_with("测试")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
