"""
标签管理服务

提供标签的 CRUD 操作
"""

from typing import List, Optional
import logging

from core.models import Tag, TagCreate
from core.database.repositories import TagRepository

logger = logging.getLogger(__name__)


class TagService:
    """标签管理服务"""
    
    def __init__(self, repo: TagRepository):
        self.repo = repo
    
    def create_tag(self, tag_data: TagCreate) -> Tag:
        """
        创建标签
        
        Args:
            tag_data: 标签创建数据
            
        Returns:
            创建的标签对象
        """
        logger.info(f"创建标签：name={tag_data.name}, color={tag_data.color}")
        tag = self.repo.create(tag_data)
        logger.info(f"标签创建成功：id={tag.id}")
        return tag
    
    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """
        获取单个标签
        
        Args:
            tag_id: 标签 ID
            
        Returns:
            标签对象，不存在则返回 None
        """
        logger.debug(f"获取标签：id={tag_id}")
        return self.repo.get_by_id(tag_id)
    
    def get_all_tags(self) -> List[Tag]:
        """
        获取所有标签
        
        Returns:
            标签列表
        """
        logger.debug("获取所有标签")
        return self.repo.get_all()
    
    def delete_tag(self, tag_id: str) -> bool:
        """
        删除标签（同时删除关联的题目标签）
        
        Args:
            tag_id: 标签 ID
            
        Returns:
            是否删除成功
        """
        logger.info(f"删除标签：id={tag_id}")
        success = self.repo.delete(tag_id)
        if success:
            logger.info(f"标签删除成功：id={tag_id}")
        else:
            logger.warning(f"标签删除失败：id={tag_id}")
        return success
    
    def search_tags(self, keyword: str) -> List[Tag]:
        """
        搜索标签
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的标签列表
        """
        logger.debug(f"搜索标签：keyword={keyword}")
        return self.repo.search(keyword)
