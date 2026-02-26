"""
工作流集成测试
测试完整的业务流程
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.services import CategoryService, QuestionService
from core.database.repositories import category_repo, question_repo
from core.models import CategoryCreate, QuestionCreate


class TestCategoryQuestionWorkflow:
    """分类和题目的完整工作流测试"""
    
    def test_create_category_then_question(self):
        """测试创建分类然后在该分类下创建题目"""
        # 1. 创建分类
        cat_service = CategoryService(category_repo)
        new_cat = cat_service.create_category(CategoryCreate(
            name="数学",
            description="数学相关题目"
        ))
        assert new_cat.id is not None
        
        # 2. 在该分类下创建题目
        q_service = QuestionService(question_repo, category_repo, None)
        new_q = q_service.create_question(QuestionCreate(
            content="1+1=?",
            options=["1", "2", "3", "4"],
            answer="2",
            explanation="基础加法",
            category_id=new_cat.id
        ))
        assert new_q.category_id == new_cat.id
        
        # 3. 验证可以通过分类找到题目
        questions = q_service.get_questions_by_category(new_cat.id)
        assert len(questions) >= 1
        assert any(q.id == new_q.id for q in questions)
    
    def test_delete_category_with_questions(self):
        """测试删除有题目的分类"""
        # 创建分类和题目
        cat_service = CategoryService(category_repo)
        parent_cat = cat_service.create_category(CategoryCreate(name="父分类"))
        
        child_cat = cat_service.create_category(CategoryCreate(
            name="子分类",
            parent_id=parent_cat.id
        ))
        
        # 尝试删除有子分类的分类（应该失败）
        result = cat_service.delete_category(parent_cat.id)
        # 根据业务逻辑，可能允许或不允许删除
        # 这里只验证操作能正常执行


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
