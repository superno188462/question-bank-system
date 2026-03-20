"""
分类管理服务

提供分类的 CRUD 操作和层级管理
"""

from typing import List, Optional
import logging

from core.models import Category, CategoryCreate, CategoryUpdate
from core.database.repositories import CategoryRepository

logger = logging.getLogger(__name__)


class CategoryService:
    """分类管理服务"""
    
    def __init__(self, repo: CategoryRepository):
        self.repo = repo
    
    def create_category(self, category_data: CategoryCreate) -> Category:
        """
        创建分类
        
        Args:
            category_data: 分类创建数据
            
        Returns:
            创建的分类对象
        """
        logger.info(f"创建分类：name={category_data.name}, parent_id={category_data.parent_id}")
        category = self.repo.create(category_data)
        logger.info(f"分类创建成功：id={category.id}")
        return category
    
    def get_category(self, category_id: str) -> Optional[Category]:
        """
        获取单个分类
        
        Args:
            category_id: 分类 ID
            
        Returns:
            分类对象，不存在则返回 None
        """
        logger.debug(f"获取分类：id={category_id}")
        return self.repo.get_by_id(category_id)
    
    def get_all_categories(self) -> List[Category]:
        """
        获取所有分类
        
        Returns:
            分类列表
        """
        logger.debug("获取所有分类")
        return self.repo.get_all()
    
    def update_category(self, category_id: str, update_data: CategoryUpdate) -> Optional[Category]:
        """
        更新分类
        
        Args:
            category_id: 分类 ID
            update_data: 更新数据
            
        Returns:
            更新后的分类对象，不存在则返回 None
        """
        logger.info(f"更新分类：id={category_id}")
        category = self.repo.update(category_id, update_data)
        if category:
            logger.info(f"分类更新成功：id={category_id}")
        else:
            logger.warning(f"分类未找到：id={category_id}")
        return category
    
    def delete_category(self, category_id: str) -> bool:
        """
        删除分类
        
        Args:
            category_id: 分类 ID
            
        Returns:
            是否删除成功
        """
        logger.info(f"删除分类：id={category_id}")
        success = self.repo.delete(category_id)
        if success:
            logger.info(f"分类删除成功：id={category_id}")
        else:
            logger.warning(f"分类删除失败：id={category_id}")
        return success
    
    def search_categories(self, keyword: str) -> List[Category]:
        """
        搜索分类
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的分类列表
        """
        logger.debug(f"搜索分类：keyword={keyword}")
        return self.repo.search(keyword)
