"""
题目管理API路由 - Web入口

提供题目的CRUD操作：
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

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.models import (
    Question, QuestionCreate, QuestionUpdate, 
    SuccessResponse, ErrorResponse, ErrorCodes
)
from core.services import QuestionService
from core.database.repositories import question_repo, category_repo, tag_repo


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
    - **options**: 选项列表，JSON格式（填空题目为空列表）
    - **answer**: 正确答案（必填）
    - **explanation**: 题目解析（必填）
    - **category_id**: 分类ID（必填）
    - **tag_ids**: 标签ID列表（可选）
    """
    try:
        return question_service.create_question(question)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"创建题目失败: {str(e)}"
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
    - **page**: 页码，从1开始
    - **limit**: 每页数量，1-100
    """
    try:
        result = question_service.get_all_questions(
            category_id=category_id,
            tag_id=tag_id,
            page=page,
            limit=limit
        )
        return QuestionListResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"获取题目列表失败: {str(e)}"
            ).dict()
        )


@router.get("/{question_id}", response_model=Question)
async def get_question(question_id: str):
    """
    获取单个题目详情
    
    - **question_id**: 题目ID
    """
    try:
        question = question_service.get_question(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.NOT_FOUND,
                    message="题目不存在"
                ).dict()
            )
        return question
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"获取题目失败: {str(e)}"
            ).dict()
        )


@router.put("/{question_id}", response_model=Question)
async def update_question(question_id: str, update_data: QuestionUpdate):
    """
    更新题目
    
    - **question_id**: 题目ID
    - **update_data**: 更新的字段（部分更新）
    """
    try:
        question = question_service.update_question(question_id, update_data)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.NOT_FOUND,
                    message="题目不存在"
                ).dict()
            )
        return question
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"更新题目失败: {str(e)}"
            ).dict()
        )


@router.delete("/{question_id}")
async def delete_question(question_id: str):
    """
    删除题目
    
    - **question_id**: 题目ID
    """
    try:
        success = question_service.delete_question(question_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.NOT_FOUND,
                    message="题目不存在"
                ).dict()
            )
        return SuccessResponse(message="题目删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"删除题目失败: {str(e)}"
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
    
    - **keyword**: 搜索关键词（至少1个字符）
    - **page**: 页码，从1开始
    - **limit**: 每页数量，1-100
    """
    try:
        result = question_service.get_all_questions(
            keyword=keyword,
            page=page,
            limit=limit
        )
        return QuestionListResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"搜索题目失败: {str(e)}"
            ).dict()
        )


@router.post("/{question_id}/tags/{tag_id}")
async def add_tag_to_question(question_id: str, tag_id: str):
    """
    为题目添加标签
    
    - **question_id**: 题目ID
    - **tag_id**: 标签ID
    """
    try:
        success = question_service.add_tag_to_question(question_id, tag_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="添加标签失败，请检查题目和标签是否存在"
                ).dict()
            )
        return SuccessResponse(message="标签添加成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"添加标签失败: {str(e)}"
            ).dict()
        )


@router.delete("/{question_id}/tags/{tag_id}")
async def remove_tag_from_question(question_id: str, tag_id: str):
    """
    从题目移除标签
    
    - **question_id**: 题目ID
    - **tag_id**: 标签ID
    """
    try:
        success = question_service.remove_tag_from_question(question_id, tag_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="移除标签失败"
                ).dict()
            )
        return SuccessResponse(message="标签移除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"移除标签失败: {str(e)}"
            ).dict()
        )
