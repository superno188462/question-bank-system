"""
数据库模型定义
定义分类、标签、题目等数据模型
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, validator
import uuid
import re


class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, max_length=500, description="分类描述")
    parent_id: Optional[str] = Field(None, description="父分类 ID，为空则为根分类")


class CategoryCreate(CategoryBase):
    """创建分类请求模型"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, max_length=500, description="分类描述")
    parent_id: Optional[str] = Field(None, description="父分类 ID，用于移动分类")


class Category(CategoryBase):
    """分类完整模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="分类 ID")
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
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="标签 ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    """题目基础模型 - 包含五个核心信息"""
    content: str = Field(..., min_length=1, max_length=10000, description="题干内容（必填）")
    options: Optional[List[str]] = Field(default=[], description="选项列表（填空题为空列表）")
    answer: str = Field(..., min_length=1, max_length=1000, description="正确答案（必填）")
    explanation: str = Field(default="", max_length=5000, description="题目解析（可选）")
    category_id: str = Field(..., min_length=1, max_length=100, description="分类 ID（必填）")


class QuestionCreate(QuestionBase):
    """创建题目请求模型"""
    tag_ids: Optional[List[str]] = Field(default=[], description="标签 ID 列表")
    category_id: Optional[str] = Field(None, description="分类 ID（可选）")
    
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
            # 如果是选择题，答案可以是选项索引（A/B/C/D）或选项内容
            # 允许 A/B/C/D 格式（转换为对应选项）
            if re.match(r'^[A-D]$', v.upper()):
                # 答案是 A/B/C/D 格式，验证索引是否在范围内
                index = ord(v.upper()) - ord('A')
                if index >= len(options):
                    raise ValueError(f"答案索引 {v} 超出选项范围 (0-{len(options)-1})")
                return v.upper()  # 保持大写格式
            # 否则答案必须是选项内容
            if v not in options:
                raise ValueError(f"答案必须在选项中：{options}")
        return v


class QuestionUpdate(BaseModel):
    """更新题目请求模型"""
    content: Optional[str] = Field(None, min_length=1, max_length=10000, description="题干内容")
    options: Optional[List[str]] = Field(None, description="选项列表")
    answer: Optional[str] = Field(None, min_length=1, max_length=1000, description="正确答案")
    explanation: Optional[str] = Field(None, max_length=5000, description="题目解析")
    category_id: Optional[str] = Field(None, max_length=100, description="分类 ID")
    tag_ids: Optional[List[str]] = Field(default=[], description="标签 ID 列表")


class Question(QuestionBase):
    """题目完整模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="题目 ID")
    category_name: Optional[str] = Field(None, description="分类名称")
    tags: List[Tag] = Field(default=[], description="标签列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        from_attributes = True


class QuestionWithTags(Question):
    """包含标签信息的题目模型"""
    tag_ids: List[str] = Field(default=[], description="标签 ID 列表")


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


# ========== AI Agent 相关模型 ==========

class StagingQuestionBase(BaseModel):
    """预备题目基础模型"""
    source_type: str = Field(..., description="来源类型：image|document|chat")
    source_file: Optional[str] = Field(None, max_length=255, description="原始文件名")
    content: str = Field(..., min_length=1, max_length=10000, description="题干内容")
    type: str = Field(..., description="题型：single_choice|multiple_choice|fill_blank|judgment|short_answer")
    options: Optional[List[str]] = Field(default=[], description="选项列表")
    answer: str = Field(..., min_length=1, max_length=1000, description="正确答案")
    explanation: str = Field(default="", max_length=5000, description="解析")
    category_id: Optional[str] = Field(None, max_length=100, description="分类 ID")
    tags: Optional[List[str]] = Field(default=[], description="标签列表")
    confidence: float = Field(default=1.0, ge=0, le=1, description="AI 置信度")


class StagingQuestionCreate(StagingQuestionBase):
    """创建预备题目请求模型"""
    pass


class StagingQuestionUpdate(BaseModel):
    """更新预备题目请求模型"""
    content: Optional[str] = Field(None, min_length=1, max_length=10000, description="题干内容")
    type: Optional[str] = Field(None, description="题型")
    options: Optional[List[str]] = Field(None, description="选项列表")
    answer: Optional[str] = Field(None, min_length=1, max_length=1000, description="正确答案")
    explanation: Optional[str] = Field(None, max_length=5000, description="解析")
    category_id: Optional[str] = Field(None, max_length=100, description="分类 ID")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    status: Optional[str] = Field(None, description="状态：pending|approved|rejected")


class StagingQuestion(StagingQuestionBase):
    """预备题目完整模型"""
    id: int = Field(..., description="题目 ID")
    status: str = Field(default="pending", description="状态：pending|approved|rejected")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    reviewed_at: Optional[datetime] = Field(None, description="审核时间")
    reviewed_by: Optional[str] = Field(None, description="审核人")
    
    class Config:
        from_attributes = True


class BatchExtractRequest(BaseModel):
    """批量提取请求模型"""
    file_paths: List[str] = Field(..., max_items=50, description="文件路径列表（最多 50 个）")
    source_type: str = Field(..., description="来源类型：image|document")


class ExtractResponse(BaseModel):
    """提取响应模型"""
    success: bool = Field(..., description="是否成功")
    questions: List[StagingQuestion] = Field(default=[], description="提取的题目列表")
    total_count: int = Field(..., description="题目总数")
    source_type: str = Field(..., description="来源类型")
    source_files: List[str] = Field(default=[], description="源文件列表")
    confidence: float = Field(default=0, description="平均置信度")
    error: Optional[str] = Field(None, description="错误信息")


class ExplanationGenerateRequest(BaseModel):
    """解析生成请求模型"""
    question_id: Optional[str] = Field(None, max_length=100, description="题目 ID（从题库读取）")
    content: Optional[str] = Field(None, max_length=10000, description="题干内容（直接传入）")
    options: Optional[List[str]] = Field(None, description="选项列表")
    answer: Optional[str] = Field(None, max_length=1000, description="正确答案")
    type: Optional[str] = Field(None, description="题型")


class ExplanationGenerateResponse(BaseModel):
    """解析生成响应模型"""
    success: bool = Field(..., description="是否成功")
    explanation: Optional[str] = Field(None, description="生成的解析")
    error: Optional[str] = Field(None, description="错误信息")


class QAAskRequest(BaseModel):
    """智能问答请求模型"""
    question: str = Field(..., min_length=1, max_length=2000, description="用户问题")
    category_id: Optional[str] = Field(None, max_length=100, description="限定分类")
    top_k: int = Field(default=5, ge=1, le=100, description="返回相关题目数量")


class QAAskResponse(BaseModel):
    """智能问答响应模型"""
    answer: str = Field(..., description="AI 回答")
    related_questions: List[dict] = Field(default=[], description="相关题目")
    suggested_question: Optional[dict] = Field(None, description="建议的新题目")


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
