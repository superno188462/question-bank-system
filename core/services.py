"""
业务服务层

包含所有核心业务逻辑，如：
1. 分类管理服务
2. 标签管理服务
3. 题目管理服务
4. 搜索服务
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from core.models import (
    Category, CategoryCreate, CategoryUpdate,
    Tag, TagCreate,
    Question, QuestionCreate, QuestionUpdate, QuestionWithTags
)
from core.database.repositories import (
    CategoryRepository, TagRepository, QuestionRepository
)


class CategoryService:
    """分类管理服务"""
    
    def __init__(self, repo: CategoryRepository):
        self.repo = repo
    
    def create_category(self, category_data: CategoryCreate) -> Category:
        """创建分类"""
        return self.repo.create(category_data)
    
    def get_category(self, category_id: str) -> Optional[Category]:
        """获取单个分类"""
        return self.repo.get_by_id(category_id)
    
    def get_all_categories(self) -> List[Category]:
        """获取所有分类"""
        return self.repo.get_all()
    
    def update_category(self, category_id: str, update_data: CategoryUpdate) -> Optional[Category]:
        """更新分类"""
        return self.repo.update(category_id, update_data)
    
    def delete_category(self, category_id: str) -> bool:
        """删除分类"""
        return self.repo.delete(category_id)
    
    def search_categories(self, keyword: str) -> List[Category]:
        """搜索分类"""
        return self.repo.search(keyword)


class TagService:
    """标签管理服务"""
    
    def __init__(self, repo: TagRepository):
        self.repo = repo
    
    def create_tag(self, tag_data: TagCreate) -> Tag:
        """创建标签"""
        return self.repo.create(tag_data)
    
    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """获取单个标签"""
        return self.repo.get_by_id(tag_id)
    
    def get_all_tags(self) -> List[Tag]:
        """获取所有标签"""
        return self.repo.get_all()
    
    def delete_tag(self, tag_id: str) -> bool:
        """删除标签"""
        return self.repo.delete(tag_id)
    
    def search_tags(self, keyword: str) -> List[Tag]:
        """搜索标签"""
        return self.repo.search(keyword)


class QuestionService:
    """题目管理服务"""
    
    def __init__(self, question_repo: QuestionRepository, 
                 category_repo: CategoryRepository,
                 tag_repo: TagRepository):
        self.question_repo = question_repo
        self.category_repo = category_repo
        self.tag_repo = tag_repo
    
    def create_question(self, question_data: QuestionCreate) -> Question:
        """创建题目"""
        # 验证分类是否存在
        if question_data.category_id:
            category = self.category_repo.get_by_id(question_data.category_id)
            if not category:
                raise ValueError(f"分类不存在: {question_data.category_id}")
        
        # 验证标签是否存在
        if question_data.tag_ids:
            for tag_id in question_data.tag_ids:
                tag = self.tag_repo.get_by_id(tag_id)
                if not tag:
                    raise ValueError(f"标签不存在: {tag_id}")
        
        # 创建题目
        question = self.question_repo.create(question_data)
        
        # 关联标签
        if question_data.tag_ids:
            self.question_repo.add_tags(question.id, question_data.tag_ids)
        
        # 获取完整的题目信息（包含标签）
        return self.get_question_with_tags(question.id)
    
    def get_question(self, question_id: str) -> Optional[Question]:
        """获取单个题目"""
        return self.question_repo.get_by_id(question_id)
    
    def get_question_with_tags(self, question_id: str) -> Optional[QuestionWithTags]:
        """获取题目及其标签"""
        question = self.question_repo.get_by_id(question_id)
        if not question:
            return None
        
        # 获取题目标签
        tags = self.question_repo.get_question_tags(question_id)
        question.tags = tags
        
        # 转换为包含标签ID的模型
        tag_ids = [tag.id for tag in tags]
        return QuestionWithTags(
            **question.dict(),
            tag_ids=tag_ids
        )
    
    def get_all_questions(self, 
                         category_id: Optional[str] = None,
                         tag_id: Optional[str] = None,
                         keyword: Optional[str] = None,
                         page: int = 1,
                         limit: int = 20) -> Dict[str, Any]:
        """获取所有题目（支持筛选和分页）"""
        return self.question_repo.get_all(
            category_id=category_id,
            tag_id=tag_id,
            keyword=keyword,
            page=page,
            limit=limit
        )
    
    def update_question(self, question_id: str, update_data: QuestionUpdate) -> Optional[Question]:
        """更新题目"""
        return self.question_repo.update(question_id, update_data)
    
    def delete_question(self, question_id: str) -> bool:
        """删除题目"""
        return self.question_repo.delete(question_id)
    
    def add_tag_to_question(self, question_id: str, tag_id: str) -> bool:
        """为题目添加标签"""
        # 验证题目和标签是否存在
        question = self.question_repo.get_by_id(question_id)
        tag = self.tag_repo.get_by_id(tag_id)
        
        if not question or not tag:
            return False
        
        return self.question_repo.add_tag(question_id, tag_id)
    
    def remove_tag_from_question(self, question_id: str, tag_id: str) -> bool:
        """从题目移除标签"""
        return self.question_repo.remove_tag(question_id, tag_id)
    
    def get_questions_by_category(self, category_id: str) -> List[Question]:
        """获取指定分类下的题目"""
        return self.question_repo.get_by_category(category_id)
    
    def get_questions_by_tag(self, tag_id: str) -> List[Question]:
        """获取指定标签下的题目"""
        return self.question_repo.get_by_tag(tag_id)
    
    def search_questions(self, keyword: str) -> List[Question]:
        """搜索题目"""
        return self.question_repo.search(keyword)


class SearchService:
    """搜索服务"""
    
    def __init__(self, question_service: QuestionService,
                 category_service: CategoryService,
                 tag_service: TagService):
        self.question_service = question_service
        self.category_service = category_service
        self.tag_service = tag_service
    
    def global_search(self, keyword: str) -> Dict[str, Any]:
        """全局搜索（题目、分类、标签）"""
        questions = self.question_service.search_questions(keyword)
        categories = self.category_service.search_categories(keyword)
        tags = self.tag_service.search_tags(keyword)
        
        return {
            "questions": questions,
            "categories": categories,
            "tags": tags,
            "total": len(questions) + len(categories) + len(tags)
        }