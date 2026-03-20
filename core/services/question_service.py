"""
题目管理服务

提供题目的 CRUD 操作、标签管理和向量索引
"""

from typing import List, Optional, Dict, Any
import logging

from core.models import (
    Category, CategoryCreate, CategoryUpdate,
    Tag, TagCreate,
    Question, QuestionCreate, QuestionUpdate, QuestionWithTags
)
from core.database.repositories import (
    CategoryRepository, TagRepository, QuestionRepository
)
from core.database.connection import db

logger = logging.getLogger(__name__)


class QuestionService:
    """题目管理服务"""
    
    def __init__(self, question_repo: QuestionRepository, 
                 category_repo: CategoryRepository,
                 tag_repo: TagRepository):
        self.question_repo = question_repo
        self.category_repo = category_repo
        self.tag_repo = tag_repo
        self._embedding_service = None
        self._vector_index = None
        self._model_version = None
    
    def _init_embedding(self):
        """延迟初始化 Embedding 服务"""
        if self._embedding_service is None:
            try:
                from agent.config import AgentConfig
                from agent.services.embedding_service import get_embedding_service
                from core.services.vector_index import get_vector_index
                
                config = AgentConfig._load_config()
                embedding_config = config.get('embedding', {})
                
                if embedding_config:
                    self._embedding_service = get_embedding_service(embedding_config)
                    self._model_version = self._embedding_service.get_model_version()
                    self._vector_index = get_vector_index(db)
                    logger.info(f"Embedding 服务已初始化：{self._model_version}")
                else:
                    logger.warning("未配置 Embedding 服务，跳过向量化")
            except Exception as e:
                logger.warning(f"初始化 Embedding 服务失败：{e}，跳过向量化")
    
    def _try_embed_question(self, question_id: str, content: str, options: str = None):
        """
        尝试为题目生成向量（智能检测，仅必要时生成）
        
        Args:
            question_id: 题目 ID
            content: 题目内容
            options: 选项列表（JSON 字符串）
        """
        try:
            self._init_embedding()
            
            if not self._embedding_service or not self._vector_index:
                return
            
            # 检查是否需要重新向量化
            options_json = str(options) if options else None
            needs_update, reason = self._vector_index.needs_reembedding(
                question_id, content, options_json, self._model_version
            )
            
            if needs_update:
                logger.debug(f"题目 {question_id} 需要重新向量化：{reason}")
                embedding = self._embedding_service.embed(content)
                self._vector_index.update_embedding(
                    question_id, embedding, self._model_version, content, options_json
                )
            else:
                logger.debug(f"题目 {question_id} 无需重新向量化：{reason}")
                
        except Exception as e:
            logger.error(f"题目向量化失败 {question_id}: {e}")
            # 向量化失败不影响题目创建/更新
    
    def create_question(self, question_data: QuestionCreate) -> Question:
        """
        创建题目
        
        Args:
            question_data: 题目创建数据
            
        Returns:
            创建的题目对象（包含标签）
            
        Raises:
            ValueError: 分类或标签不存在
        """
        logger.info(f"创建题目：category_id={question_data.category_id}, content={question_data.content[:50]}...")
        
        # 验证分类是否存在
        if question_data.category_id:
            category = self.category_repo.get_by_id(question_data.category_id)
            if not category:
                logger.warning(f"分类不存在：{question_data.category_id}")
                raise ValueError(f"分类不存在：{question_data.category_id}")
        
        # 验证标签是否存在
        if question_data.tag_ids:
            for tag_id in question_data.tag_ids:
                tag = self.tag_repo.get_by_id(tag_id)
                if not tag:
                    logger.warning(f"标签不存在：{tag_id}")
                    raise ValueError(f"标签不存在：{tag_id}")
        
        # 创建题目
        question = self.question_repo.create(question_data)
        logger.info(f"题目创建成功：id={question.id}")
        
        # 关联标签
        if question_data.tag_ids:
            self.question_repo.add_tags(question.id, question_data.tag_ids)
            logger.debug(f"关联标签：question_id={question.id}, tag_ids={question_data.tag_ids}")
        
        # 生成向量（智能检测）
        self._try_embed_question(question.id, question_data.content, question_data.options)
        
        # 获取完整的题目信息（包含标签）
        return self.get_question_with_tags(question.id)
    
    def get_question(self, question_id: str) -> Optional[Question]:
        """
        获取单个题目（包含分类名称）
        
        Args:
            question_id: 题目 ID
            
        Returns:
            题目对象，不存在则返回 None
        """
        logger.debug(f"获取题目：id={question_id}")
        question = self.question_repo.get_by_id(question_id)
        if question and question.category_id:
            category = self.category_repo.get_by_id(question.category_id)
            if category:
                question.category_name = category.name
        return question
    
    def get_question_with_tags(self, question_id: str) -> Optional[QuestionWithTags]:
        """
        获取题目及其标签
        
        Args:
            question_id: 题目 ID
            
        Returns:
            题目对象（包含标签 ID），不存在则返回 None
        """
        logger.debug(f"获取题目及标签：id={question_id}")
        question = self.question_repo.get_by_id(question_id)
        if not question:
            return None
        
        # 获取题目标签
        tags = self.question_repo.get_question_tags(question_id)
        question.tags = tags
        
        # 转换为包含标签 ID 的模型
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
        """
        获取所有题目（支持筛选和分页，包含分类名称）
        
        Args:
            category_id: 分类 ID（可选）
            tag_id: 标签 ID（可选）
            keyword: 搜索关键词（可选）
            page: 页码
            limit: 每页数量
            
        Returns:
            分页响应字典 {data, total, page, limit, pages}
        """
        logger.debug(f"获取题目列表：category_id={category_id}, tag_id={tag_id}, keyword={keyword}, page={page}, limit={limit}")
        result = self.question_repo.get_all(
            category_id=category_id,
            tag_id=tag_id,
            keyword=keyword,
            page=page,
            limit=limit
        )
        
        # 为每个题目添加分类名称
        if result.get('data'):
            for question in result['data']:
                if question.category_id:
                    category = self.category_repo.get_by_id(question.category_id)
                    if category:
                        question.category_name = category.name
        
        return result
    
    def update_question(self, question_id: str, update_data: QuestionUpdate) -> Optional[Question]:
        """
        更新题目
        
        Args:
            question_id: 题目 ID
            update_data: 更新数据
            
        Returns:
            更新后的题目对象，不存在则返回 None
        """
        logger.info(f"更新题目：id={question_id}")
        
        # 获取原题目（用于向量化检测）
        old_question = self.get_question(question_id)
        
        # 更新题目
        question = self.question_repo.update(question_id, update_data)
        
        if question:
            logger.info(f"题目更新成功：id={question_id}")
            
            # 如果内容变更，重新生成向量
            if update_data.content or update_data.options:
                content = update_data.content or (old_question.content if old_question else '')
                options = update_data.options or (old_question.options if old_question else [])
                self._try_embed_question(question_id, content, options)
        else:
            logger.warning(f"题目未找到：id={question_id}")
        
        return question
    
    def delete_question(self, question_id: str) -> bool:
        """
        删除题目
        
        Args:
            question_id: 题目 ID
            
        Returns:
            是否删除成功
        """
        logger.info(f"删除题目：id={question_id}")
        success = self.question_repo.delete(question_id)
        if success:
            logger.info(f"题目删除成功：id={question_id}")
        else:
            logger.warning(f"题目删除失败：id={question_id}")
        return success
    
    def add_tag_to_question(self, question_id: str, tag_id: str) -> bool:
        """
        为题目添加标签
        
        Args:
            question_id: 题目 ID
            tag_id: 标签 ID
            
        Returns:
            是否添加成功
        """
        logger.info(f"添加标签到题目：question_id={question_id}, tag_id={tag_id}")
        
        # 验证题目和标签是否存在
        question = self.question_repo.get_by_id(question_id)
        tag = self.tag_repo.get_by_id(tag_id)
        
        if not question or not tag:
            logger.warning(f"题目或标签不存在：question_id={question_id}, tag_id={tag_id}")
            return False
        
        success = self.question_repo.add_tag(question_id, tag_id)
        if success:
            logger.info(f"标签添加成功：question_id={question_id}, tag_id={tag_id}")
        return success
    
    def remove_tag_from_question(self, question_id: str, tag_id: str) -> bool:
        """
        从题目移除标签
        
        Args:
            question_id: 题目 ID
            tag_id: 标签 ID
            
        Returns:
            是否移除成功
        """
        logger.info(f"从题目移除标签：question_id={question_id}, tag_id={tag_id}")
        success = self.question_repo.remove_tag(question_id, tag_id)
        if success:
            logger.info(f"标签移除成功：question_id={question_id}, tag_id={tag_id}")
        else:
            logger.warning(f"标签移除失败：question_id={question_id}, tag_id={tag_id}")
        return success
    
    def get_questions_by_category(self, category_id: str) -> List[Question]:
        """
        获取指定分类下的题目
        
        Args:
            category_id: 分类 ID
            
        Returns:
            题目列表
        """
        logger.debug(f"获取分类下题目：category_id={category_id}")
        return self.question_repo.get_by_category(category_id)
    
    def get_questions_by_tag(self, tag_id: str) -> List[Question]:
        """
        获取指定标签下的题目
        
        Args:
            tag_id: 标签 ID
            
        Returns:
            题目列表
        """
        logger.debug(f"获取标签下题目：tag_id={tag_id}")
        return self.question_repo.get_by_tag(tag_id)
    
    def search_questions(self, keyword: str) -> List[Question]:
        """
        搜索题目
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的题目列表
        """
        logger.debug(f"搜索题目：keyword={keyword}")
        return self.question_repo.search(keyword)
