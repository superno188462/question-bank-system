"""
分类管理API路由 - Web入口

提供分类的CRUD操作：
- 创建分类（支持层级）
- 获取分类列表
- 获取树形分类结构
- 获取单个分类
- 更新分类
- 删除分类
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.models import (
    Category, CategoryCreate, CategoryUpdate, 
    SuccessResponse, ErrorResponse, ErrorCodes
)
from core.services import CategoryService
from core.database.repositories import category_repo


# 树形节点模型
class CategoryTreeNode(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    children: List['CategoryTreeNode'] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# 创建路由
router = APIRouter(prefix="/categories", tags=["分类管理"])

# 创建服务实例
category_service = CategoryService(category_repo)


def build_category_tree(categories: List[Category], parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """构建分类树形结构"""
    tree = []
    for cat in categories:
        if cat.parent_id == parent_id:
            node = {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "parent_id": cat.parent_id,
                "created_at": cat.created_at.isoformat() if cat.created_at else None,
                "updated_at": cat.updated_at.isoformat() if cat.updated_at else None,
                "children": build_category_tree(categories, cat.id)
            }
            tree.append(node)
    return tree


def get_category_breadcrumb(categories: List[Category], category_id: str) -> List[Dict[str, str]]:
    """获取分类的面包屑路径"""
    breadcrumb = []
    current_id = category_id
    max_depth = 10  # 防止循环引用
    
    while current_id and max_depth > 0:
        cat = next((c for c in categories if c.id == current_id), None)
        if not cat:
            break
        breadcrumb.insert(0, {"id": cat.id, "name": cat.name})
        current_id = cat.parent_id
        max_depth -= 1
    
    return breadcrumb


def get_all_children_ids(categories: List[Category], parent_id: str) -> List[str]:
    """获取某个分类下的所有子分类ID（包括间接子分类）"""
    children_ids = [parent_id]
    direct_children = [c.id for c in categories if c.parent_id == parent_id]
    
    for child_id in direct_children:
        children_ids.extend(get_all_children_ids(categories, child_id))
    
    return children_ids


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate):
    """
    创建新分类（支持层级）
    
    - **name**: 分类名称（必填）
    - **description**: 分类描述（可选）
    - **parent_id**: 父分类ID（可选，为空则为根分类）
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
    获取所有分类列表（扁平结构）
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


@router.get("/tree", response_model=List[Dict[str, Any]])
async def get_category_tree():
    """
    获取分类树形结构
    
    返回嵌套的树形结构，包含所有层级关系
    """
    try:
        categories = category_service.get_all_categories()
        return build_category_tree(categories)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"获取分类树失败: {str(e)}"
            ).dict()
        )


@router.get("/{category_id}/breadcrumb", response_model=List[Dict[str, str]])
async def get_breadcrumb(category_id: str):
    """
    获取分类的面包屑路径
    
    - **category_id**: 分类ID
    
    返回从根分类到当前分类的路径
    """
    try:
        categories = category_service.get_all_categories()
        category = next((c for c in categories if c.id == category_id), None)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.NOT_FOUND,
                    message="分类不存在"
                ).dict()
            )
        return get_category_breadcrumb(categories, category_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"获取面包屑失败: {str(e)}"
            ).dict()
        )


@router.get("/{category_id}/children", response_model=List[str])
async def get_children_ids(category_id: str):
    """
    获取分类的所有子分类ID（包括自身）
    
    - **category_id**: 分类ID
    
    用于查询某个分类及其所有子分类下的题目
    """
    try:
        categories = category_service.get_all_categories()
        category = next((c for c in categories if c.id == category_id), None)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.NOT_FOUND,
                    message="分类不存在"
                ).dict()
            )
        return get_all_children_ids(categories, category_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"获取子分类失败: {str(e)}"
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
    - **parent_id**: 新的父分类ID（可选，用于移动分类）
    """
    try:
        # 检查是否会造成循环引用
        if update_data.parent_id and update_data.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="不能将分类设置为自己的父分类"
                ).dict()
            )
        
        category = category_service.update_category(category_id, update_data)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.NOT_FOUND,
                    message="分类不存在"
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


@router.delete("/{category_id}")
async def delete_category(category_id: str):
    """
    删除分类
    
    - **category_id**: 分类ID
    
    注意：如果分类下有子分类，需要先删除或移动子分类
    """
    try:
        # 检查是否有子分类
        categories = category_service.get_all_categories()
        has_children = any(c.parent_id == category_id for c in categories)
        if has_children:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.VALIDATION_ERROR,
                    message="该分类下还有子分类，请先删除子分类"
                ).dict()
            )
        
        success = category_service.delete_category(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=True,
                    code=ErrorCodes.NOT_FOUND,
                    message="分类不存在"
                ).dict()
            )
        return SuccessResponse(message="分类删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"删除分类失败: {str(e)}"
            ).dict()
        )
