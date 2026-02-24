"""
标签管理API路由 - Web入口

提供标签的CRUD操作：
- 创建标签
- 获取标签列表
- 获取单个标签
- 更新标签
- 删除标签
- 搜索标签
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query, status

from core.models import Tag, TagCreate, SuccessResponse, ErrorResponse, ErrorCodes
from core.services import TagService
from core.database.repositories import tag_repo


# 创建路由
router = APIRouter(prefix="/tags", tags=["标签管理"])

# 创建服务实例
tag_service = TagService(tag_repo)


@router.post("/", response_model=Tag, status_code=status.HTTP_201_CREATED)
async def create_tag(tag: TagCreate):
    """
    创建新标签
    
    - **name**: 标签名称（必填）
    - **color**: 标签颜色，十六进制格式如#FF0000（必填）
    """
    try:
        return tag_service.create_tag(tag)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.VALIDATION_ERROR,
                message=f"创建标签失败: {str(e)}"
            ).dict()
        )


@router.get("/", response_model=List[Tag])
async def get_tags():
    """
    获取所有标签列表
    
    返回所有标签，按创建时间倒序排列
    """
    try:
        return tag_service.get_all_tags()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"获取标签列表失败: {str(e)}"
            ).dict()
        )


@router.get("/{tag_id}", response_model=Tag)
async def get_tag(tag_id: str):
    """
    根据ID获取标签详情
    
    - **tag_id**: 标签ID
    """
    tag = tag_service.get_tag(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.NOT_FOUND,
                message=f"标签不存在: {tag_id}"
            ).dict()
        )
    return tag


@router.delete("/{tag_id}", response_model=SuccessResponse)
async def delete_tag(tag_id: str):
    """
    删除标签
    
    - **tag_id**: 标签ID
    
    注意：删除标签会同时删除题目标签关联
    """
    success = tag_service.delete_tag(tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.NOT_FOUND,
                message=f"标签不存在: {tag_id}"
            ).dict()
        )
    
    return SuccessResponse(
        success=True,
        message=f"标签已删除: {tag_id}"
    )


@router.get("/search/", response_model=List[Tag])
async def search_tags(keyword: str = Query(..., description="搜索关键词")):
    """
    搜索标签
    
    - **keyword**: 搜索关键词，匹配标签名称
    """
    try:
        return tag_service.search_tags(keyword)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=True,
                code=ErrorCodes.INTERNAL_ERROR,
                message=f"搜索标签失败: {str(e)}"
            ).dict()
        )