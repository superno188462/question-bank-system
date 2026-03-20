"""
题目管理 API 路由 - Web 入口

提供题目的 CRUD 操作：
- 创建题目
- 获取题目列表
- 获取单个题目
- 更新题目
- 删除题目
- 搜索题目
- 管理题目标签
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
import logging

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.models import (
    Question, QuestionCreate, QuestionUpdate, 
    SuccessResponse, ErrorResponse, ErrorCodes
)
from core.services import QuestionService
from core.database.repositories import question_repo, category_repo, tag_repo
from core.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException,
    BusinessException,
    QuestionBankException
)

logger = logging.getLogger(__name__)


# 题目列表响应模型
class QuestionListResponse(BaseModel):
    data: List[Question]
    total: int
    page: int
    limit: int
    pages: int


# 创建路由
router = APIRouter(prefix="/questions", tags=["题目管理"])

# 创建服务实例
question_service = QuestionService(question_repo, category_repo, tag_repo)


@router.post("/", response_model=Question, status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionCreate):
    """
    创建新题目（五个核心信息必填）
    
    - **content**: 题干内容（必填）
    - **options**: 选项列表，JSON 格式（填空题目为空列表）
    - **answer**: 正确答案（必填）
    - **explanation**: 题目解析（必填）
    - **category_id**: 分类 ID（必填）
    - **tag_ids**: 标签 ID 列表（可选）
    """
    try:
        logger.info(f"创建题目：category_id={question.category_id}, content={question.content[:50]}...")
        result = question_service.create_question(question)
        logger.info(f"题目创建成功：id={result.id}")
        return result
    except ResourceNotFoundException as e:
        logger.warning(f"资源未找到：{e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.NOT_FOUND,
                message=str(e)
            ).dict()
        )
    except ValidationException as e:
        logger.warning(f"验证失败：{e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.VALIDATION_ERROR,
                message=str(e)
            ).dict()
        )
    except BusinessException as e:
        logger.warning(f"业务错误：{e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.BUSINESS_ERROR,
                message=str(e)
            ).dict()
        )
    except DatabaseException as e:
        logger.error(f"数据库错误：{e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.DATABASE_ERROR,
                message="数据库操作失败"
            ).dict()
        )
    except Exception as e:
        logger.error(f"未预期错误：{e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"创建题目失败：{str(e)}"
            ).dict()
        )


@router.get("/", response_model=QuestionListResponse)
async def get_questions(
    category_id: Optional[str] = Query(None, description="按分类筛选"),
    tag_id: Optional[str] = Query(None, description="按标签筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取题目列表
    
    - **category_id**: 按分类筛选（可选）
    - **tag_id**: 按标签筛选（可选）
    - **page**: 页码，从 1 开始
    - **limit**: 每页数量，1-100
    """
    try:
        logger.info(f"获取题目列表：category_id={category_id}, tag_id={tag_id}, page={page}, limit={limit}")
        result = question_service.get_all_questions(
            category_id=category_id,
            tag_id=tag_id,
            page=page,
            limit=limit
        )
        logger.info(f"获取题目列表成功：total={result['total']}")
        return QuestionListResponse(**result)
    except Exception as e:
        logger.error(f"获取题目列表失败：{e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"获取题目列表失败：{str(e)}"
            ).dict()
        )


@router.get("/{question_id}", response_model=Question)
async def get_question(question_id: str):
    """
    获取单个题目详情
    
    - **question_id**: 题目 ID
    """
    try:
        logger.info(f"获取题目：id={question_id}")
        question = question_service.get_question(question_id)
        if not question:
            logger.warning(f"题目未找到：id={question_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.NOT_FOUND,
                    message="题目不存在"
                ).dict()
            )
        logger.info(f"获取题目成功：id={question_id}")
        return question
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取题目失败：{e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"获取题目失败：{str(e)}"
            ).dict()
        )


@router.put("/{question_id}", response_model=Question)
async def update_question(question_id: str, update_data: QuestionUpdate):
    """
    更新题目
    
    - **question_id**: 题目 ID
    - **update_data**: 更新的字段（部分更新）
    """
    try:
        logger.info(f"更新题目：id={question_id}")
        question = question_service.update_question(question_id, update_data)
        if not question:
            logger.warning(f"题目未找到：id={question_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.NOT_FOUND,
                    message="题目不存在"
                ).dict()
            )
        logger.info(f"题目更新成功：id={question_id}")
        return question
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新题目失败：{e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"更新题目失败：{str(e)}"
            ).dict()
        )


@router.delete("/{question_id}")
async def delete_question(question_id: str):
    """
    删除题目
    
    - **question_id**: 题目 ID
    """
    try:
        logger.info(f"删除题目：id={question_id}")
        success = question_service.delete_question(question_id)
        if not success:
            logger.warning(f"题目未找到：id={question_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.NOT_FOUND,
                    message="题目不存在"
                ).dict()
            )
        logger.info(f"题目删除成功：id={question_id}")
        return SuccessResponse(message="题目删除成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除题目失败：{e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"删除题目失败：{str(e)}"
            ).dict()
        )


@router.get("/search/keyword")
async def search_questions(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    搜索题目
    
    - **keyword**: 搜索关键词（至少 1 个字符）
    - **page**: 页码，从 1 开始
    - **limit**: 每页数量，1-100
    """
    try:
        logger.info(f"搜索题目：keyword={keyword}, page={page}, limit={limit}")
        result = question_service.get_all_questions(
            keyword=keyword,
            page=page,
            limit=limit
        )
        logger.info(f"搜索题目成功：total={result['total']}")
        return QuestionListResponse(**result)
    except Exception as e:
        logger.error(f"搜索题目失败：{e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"搜索题目失败：{str(e)}"
            ).dict()
        )


@router.post("/{question_id}/tags/{tag_id}")
async def add_tag_to_question(question_id: str, tag_id: str):
    """
    为题目添加标签
    
    - **question_id**: 题目 ID
    - **tag_id**: 标签 ID
    """
    try:
        logger.info(f"添加标签：question_id={question_id}, tag_id={tag_id}")
        success = question_service.add_tag_to_question(question_id, tag_id)
        if not success:
            logger.warning(f"添加标签失败：question_id={question_id}, tag_id={tag_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="添加标签失败，请检查题目和标签是否存在"
                ).dict()
            )
        logger.info(f"标签添加成功：question_id={question_id}, tag_id={tag_id}")
        return SuccessResponse(message="标签添加成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加标签失败：{e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"添加标签失败：{str(e)}"
            ).dict()
        )


@router.delete("/{question_id}/tags/{tag_id}")
async def remove_tag_from_question(question_id: str, tag_id: str):
    """
    从题目移除标签
    
    - **question_id**: 题目 ID
    - **tag_id**: 标签 ID
    """
    try:
        logger.info(f"移除标签：question_id={question_id}, tag_id={tag_id}")
        success = question_service.remove_tag_from_question(question_id, tag_id)
        if not success:
            logger.warning(f"移除标签失败：question_id={question_id}, tag_id={tag_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="移除标签失败"
                ).dict()
            )
        logger.info(f"标签移除成功：question_id={question_id}, tag_id={tag_id}")
        return SuccessResponse(message="标签移除成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"移除标签失败：{e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"移除标签失败：{str(e)}"
            ).dict()
        )
