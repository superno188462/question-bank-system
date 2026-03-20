"""
业务服务层 - 组合服务

包含依赖其他服务的组合服务：
1. SearchService - 全局搜索服务
"""

from typing import Dict, Any
import logging

from core.services.category_service import CategoryService
from core.services.tag_service import TagService
from core.services.question_service import QuestionService

logger = logging.getLogger(__name__)


class SearchService:
    """搜索服务"""
    
    def __init__(self, question_service: QuestionService,
                 category_service: CategoryService,
                 tag_service: TagService):
        self.question_service = question_service
        self.category_service = category_service
        self.tag_service = tag_service
    
    def global_search(self, keyword: str) -> Dict[str, Any]:
        """
        全局搜索（题目、分类、标签）
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            搜索结果字典 {questions, categories, tags, total}
        """
        logger.info(f"全局搜索：keyword={keyword}")
        questions = self.question_service.search_questions(keyword)
        categories = self.category_service.search_categories(keyword)
        tags = self.tag_service.search_tags(keyword)
        
        result = {
            "questions": questions,
            "categories": categories,
            "tags": tags,
            "total": len(questions) + len(categories) + len(tags)
        }
        
        logger.info(f"全局搜索结果：total={result['total']}")
        return result
