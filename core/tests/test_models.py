"""
测试数据模型
"""
import pytest
from datetime import datetime
from core.models import (
    Category, CategoryCreate,
    Question, QuestionCreate,
    Tag, TagCreate
)


class TestCategoryModel:
    """测试分类模型"""
    
    def test_category_create(self):
        """测试创建分类"""
        cat = CategoryCreate(
            name="数学",
            description="数学相关题目",
            parent_id=None
        )
        assert cat.name == "数学"
        assert cat.description == "数学相关题目"
        assert cat.parent_id is None
    
    def test_category_full_model(self):
        """测试完整分类模型"""
        cat = Category(
            id="test-id-123",
            name="物理",
            description="物理题目",
            parent_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert cat.id == "test-id-123"
        assert cat.name == "物理"


class TestQuestionModel:
    """测试题目模型"""
    
    def test_question_create_minimal(self):
        """测试最小化创建题目"""
        q = QuestionCreate(
            content="1+1=?",
            options=["1", "2", "3", "4"],
            answer="2",
            explanation="基本加法",
            category_id="cat-123"
        )
        assert q.content == "1+1=?"
        assert q.answer == "2"
        assert len(q.options) == 4
    
    def test_question_create_fill_blank(self):
        """测试填空题创建（无选项）"""
        q = QuestionCreate(
            content="中国的首都是______。",
            options=[],  # 填空题无选项
            answer="北京",
            explanation="常识题",
            category_id="cat-123"
        )
        assert q.options == []
        assert q.answer == "北京"
    
    def test_question_validation_required_fields(self):
        """测试必填字段验证"""
        with pytest.raises(Exception):
            # 缺少content应该报错
            QuestionCreate(
                options=["A", "B"],
                answer="A",
                explanation="测试",
                category_id="cat-123"
            )


class TestTagModel:
    """测试标签模型"""
    
    def test_tag_create(self):
        """测试创建标签"""
        tag = TagCreate(
            name="重要",
            color="#ff0000"
        )
        assert tag.name == "重要"
        assert tag.color == "#ff0000"
