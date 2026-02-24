"""
数据库模型定义
定义分类、标签、题目等数据模型
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, validator
import uuid


class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, max_length=500, description="分类描述")


class CategoryCreate(CategoryBase):
    """创建分类请求模型"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, max_length=500, description="分类描述")


class Category(CategoryBase):
    """分类完整模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="分类ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        from_attributes = True


class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    color: str = Field(default="#667eea", description="标签颜色")


class TagCreate(TagBase):
    """创建标签请求模型"""
    pass


class Tag(TagBase):
    """标签完整模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="标签ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    """题目基础模型"""
    content: str = Field(..., min_length=1, description="题干内容")
    options: Optional[List[str]] = Field(None, description="选项列表（填空题为空）")
    answer: str = Field(..., min_length=1, description="正确答案")
    explanation: Optional[str] = Field(None, description="题目解析")
    category_id: Optional[str] = Field(None, description="分类ID")


class QuestionCreate(QuestionBase):
    """创建题目请求模型"""
    tag_ids: Optional[List[str]] = Field(default=[], description="标签ID列表")
    
    @validator('options')
    def validate_options(cls, v):
        """验证选项格式"""
        if v is not None:
            # 确保选项是字符串列表
            if not all(isinstance(item, str) for item in v):
                raise ValueError("选项必须是字符串列表")
            # 选项不能为空字符串
            if any(not item.strip() for item in v):
                raise ValueError("选项不能为空字符串")
        return v
    
    @validator('answer')
    def validate_answer(cls, v, values):
        """验证答案格式"""
        options = values.get('options')
        if options is not None and len(options) > 0:
            # 如果是选择题，答案必须在选项中
            if v not in options:
                raise ValueError(f"答案必须在选项中: {options}")
        return v


class QuestionUpdate(BaseModel):
    """更新题目请求模型"""
    content: Optional[str] = Field(None, min_length=1, description="题干内容")
    options: Optional[List[str]] = Field(None, description="选项列表")
    answer: Optional[str] = Field(None, min_length=1, description="正确答案")
    explanation: Optional[str] = Field(None, description="题目解析")
    category_id: Optional[str] = Field(None, description="分类ID")


class Question(QuestionBase):
    """题目完整模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="题目ID")
    tags: List[Tag] = Field(default=[], description="标签列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        from_attributes = True


class QuestionWithTags(Question):
    """包含标签信息的题目模型"""
    tag_ids: List[str] = Field(default=[], description="标签ID列表")


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    data: List[Any] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: bool = Field(True, description="是否错误")
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误信息")
    details: Optional[dict] = Field(None, description="详细错误信息")


class SuccessResponse(BaseModel):
    """成功响应模型"""
    success: bool = Field(True, description="是否成功")
    data: Optional[Any] = Field(None, description="返回数据")
    message: Optional[str] = Field(None, description="成功信息")


# 预定义的错误代码
class ErrorCodes:
    """错误代码常量"""
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    DUPLICATE_ERROR = "DUPLICATE_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_ERROR = "INTERNAL_ERROR"