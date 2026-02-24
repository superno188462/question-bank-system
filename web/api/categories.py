"""
分类管理API路由 - Web入口

提供分类的CRUD操作：
- 创建分类
- 获取分类列表
- 获取单个分类
- 更新分类
- 删除分类
- 搜索分类
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query, status

from core.models import (
    Category, CategoryCreate, CategoryUpdate, 
    SuccessResponse, ErrorResponse, ErrorCodes
)
from core.services import CategoryService
from core.database.repositories import category_repo


# 创建路由
router = APIRouter(prefix="/categories", tags=["分类管理"])

# 创建服务实例
category_service = CategoryService(category_repo)


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate):
    """
    创建新分类
    
    - **name**: 分类名称（必填）
    - **description**: 分类描述（可选）
    """
    try:
        return category_service.create_category(category)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"创建分类失败: {str(e)}"
            ).dict()
        )


@router.get("/", response_model=List[Category])
async def get_categories():
    """
    获取所有分类列表
    
    返回所有分类，按创建时间倒序排列
    """
    try:
        return category_service.get_all_categories()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"获取分类列表失败: {str(e)}"
            ).dict()
        )


@router.get("/{category_id}", response_model=Category)
async def get_category(category_id: str):
    """
    根据ID获取分类详情
    
    - **category_id**: 分类ID
    """
    category = category_service.get_category(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.NOT_FOUND,
                message=f"分类不存在: {category_id}"
            ).dict()
        )
    return category


@router.put("/{category_id}", response_model=Category)
async def update_category(category_id: str, update_data: CategoryUpdate):
    """
    更新分类信息
    
    - **category_id**: 分类ID
    - **name**: 新的分类名称（可选）
    - **description**: 新的分类描述（可选）
    """
    try:
        category = category_service.update_category(category_id, update_data)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.NOT_FOUND,
                    message=f"分类不存在: {category_id}"
                ).dict()
            )
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"更新分类失败: {str(e)}"
            ).dict()
        )


@router.delete("/{category_id}", response_model=SuccessResponse)
async def delete_category(category_id: str):
    """
    删除分类
    
    - **category_id**: 分类ID
    
    注意：删除分类不会删除该分类下的题目，只会将题目的分类ID设为NULL
    """
    success = category_service.delete_category(category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.NOT_FOUND,
                message=f"分类不存在: {category_id}"
            ).dict()
        )
    
    return SuccessResponse(
        success=True,
        message=f"分类已删除: {category_id}"
    )


@router.get("/search/", response_model=List[Category])
async def search_categories(keyword: str = Query(..., description="搜索关键词")):
    """
    搜索分类
    
    - **keyword**: 搜索关键词，匹配分类名称或描述
    """
    try:
        return category_service.search_categories(keyword)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"搜索分类失败: {str(e)}"
            ).dict()
        )