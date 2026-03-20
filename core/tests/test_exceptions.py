"""
异常类测试
测试 core.exceptions 模块中的所有自定义异常
"""
import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.exceptions import (
    QuestionBankException,
    ResourceNotFoundException,
    ValidationException,
    DatabaseException,
    BusinessException,
    DuplicateException,
    UnauthorizedException,
    ForbiddenException,
    AIServiceException,
    FileUploadException
)


class TestQuestionBankException:
    """基础异常类测试"""
    
    def test_init_with_message(self):
        """测试使用消息初始化"""
        exc = QuestionBankException("测试错误")
        
        assert exc.message == "测试错误"
        assert exc.code == "INTERNAL_ERROR"
        assert str(exc) == "测试错误"
    
    def test_init_with_message_and_code(self):
        """测试使用消息和错误码初始化"""
        exc = QuestionBankException("自定义错误", "CUSTOM_CODE")
        
        assert exc.message == "自定义错误"
        assert exc.code == "CUSTOM_CODE"
    
    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(QuestionBankException) as exc_info:
            raise QuestionBankException("抛出测试")
        
        assert exc_info.value.message == "抛出测试"
        assert exc_info.value.code == "INTERNAL_ERROR"
    
    def test_inherits_from_exception(self):
        """测试继承自 Exception"""
        exc = QuestionBankException("测试")
        
        assert isinstance(exc, Exception)


class TestResourceNotFoundException:
    """资源未找到异常测试"""
    
    def test_init(self):
        """测试初始化"""
        exc = ResourceNotFoundException("题目", "123")
        
        assert exc.message == "题目 不存在：123"
        assert exc.code == "NOT_FOUND"
    
    def test_with_category(self):
        """测试分类资源"""
        exc = ResourceNotFoundException("分类", "cat_456")
        
        assert exc.message == "分类 不存在：cat_456"
        assert exc.code == "NOT_FOUND"
    
    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(ResourceNotFoundException) as exc_info:
            raise ResourceNotFoundException("用户", "user_789")
        
        assert exc_info.value.code == "NOT_FOUND"
    
    def test_inherits_from_question_bank_exception(self):
        """测试继承自 QuestionBankException"""
        exc = ResourceNotFoundException("资源", "id")
        
        assert isinstance(exc, QuestionBankException)
        assert isinstance(exc, Exception)


class TestValidationException:
    """验证异常测试"""
    
    def test_init(self):
        """测试初始化"""
        exc = ValidationException("字段验证失败")
        
        assert exc.message == "字段验证失败"
        assert exc.code == "VALIDATION_ERROR"
    
    def test_with_different_messages(self):
        """测试不同消息"""
        exc1 = ValidationException("必填字段不能为空")
        exc2 = ValidationException("邮箱格式不正确")
        
        assert exc1.message == "必填字段不能为空"
        assert exc2.message == "邮箱格式不正确"
        assert exc1.code == exc2.code == "VALIDATION_ERROR"
    
    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(ValidationException):
            raise ValidationException("验证失败")
    
    def test_inherits_from_question_bank_exception(self):
        """测试继承关系"""
        exc = ValidationException("测试")
        
        assert isinstance(exc, QuestionBankException)


class TestDatabaseException:
    """数据库异常测试"""
    
    def test_init_without_original_error(self):
        """测试不带原始错误初始化"""
        exc = DatabaseException("数据库连接失败")
        
        assert exc.message == "数据库连接失败"
        assert exc.code == "DATABASE_ERROR"
        assert exc.original_error is None
    
    def test_init_with_original_error(self):
        """测试带原始错误初始化"""
        original = Exception("SQLite error")
        exc = DatabaseException("查询失败", original)
        
        assert exc.message == "查询失败"
        assert exc.code == "DATABASE_ERROR"
        assert exc.original_error is original
    
    def test_with_sqlite_error(self):
        """测试 SQLite 错误"""
        import sqlite3
        original = sqlite3.OperationalError("table not found")
        exc = DatabaseException("SQL 执行失败", original)
        
        assert exc.original_error is original
        assert isinstance(exc.original_error, sqlite3.OperationalError)
    
    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(DatabaseException):
            raise DatabaseException("数据库错误")
    
    def test_inherits_from_question_bank_exception(self):
        """测试继承关系"""
        exc = DatabaseException("测试")
        
        assert isinstance(exc, QuestionBankException)


class TestBusinessException:
    """业务异常测试"""
    
    def test_init(self):
        """测试初始化"""
        exc = BusinessException("业务规则违反")
        
        assert exc.message == "业务规则违反"
        assert exc.code == "BUSINESS_ERROR"
    
    def test_with_inventory_error(self):
        """测试库存业务错误"""
        exc = BusinessException("库存不足")
        
        assert exc.message == "库存不足"
        assert exc.code == "BUSINESS_ERROR"
    
    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(BusinessException):
            raise BusinessException("业务错误")
    
    def test_inherits_from_question_bank_exception(self):
        """测试继承关系"""
        exc = BusinessException("测试")
        
        assert isinstance(exc, QuestionBankException)


class TestDuplicateException:
    """重复数据异常测试"""
    
    def test_init(self):
        """测试初始化"""
        exc = DuplicateException("题目", "content", "测试题目内容")
        
        assert exc.message == "题目 已存在：content=测试题目内容"
        assert exc.code == "DUPLICATE_ERROR"
    
    def test_with_category(self):
        """测试分类重复"""
        exc = DuplicateException("分类", "name", "Python")
        
        assert exc.message == "分类 已存在：name=Python"
        assert exc.code == "DUPLICATE_ERROR"
    
    def test_with_user(self):
        """测试用户重复"""
        exc = DuplicateException("用户", "email", "test@example.com")
        
        assert exc.message == "用户 已存在：email=test@example.com"
    
    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(DuplicateException):
            raise DuplicateException("资源", "field", "value")
    
    def test_inherits_from_question_bank_exception(self):
        """测试继承关系"""
        exc = DuplicateException("类型", "字段", "值")
        
        assert isinstance(exc, QuestionBankException)


class TestUnauthorizedException:
    """未授权异常测试"""
    
    def test_init_default_message(self):
        """测试默认消息初始化"""
        exc = UnauthorizedException()
        
        assert exc.message == "未授权访问"
        assert exc.code == "UNAUTHORIZED"
    
    def test_init_custom_message(self):
        """测试自定义消息初始化"""
        exc = UnauthorizedException("Token 已过期")
        
        assert exc.message == "Token 已过期"
        assert exc.code == "UNAUTHORIZED"
    
    def test_with_token_error(self):
        """测试 Token 错误"""
        exc = UnauthorizedException("无效的 Token")
        
        assert exc.message == "无效的 Token"
    
    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(UnauthorizedException):
            raise UnauthorizedException()
    
    def test_inherits_from_question_bank_exception(self):
        """测试继承关系"""
        exc = UnauthorizedException()
        
        assert isinstance(exc, QuestionBankException)


class TestForbiddenException:
    """禁止访问异常测试"""
    
    def test_init_default_message(self):
        """测试默认消息初始化"""
        exc = ForbiddenException()
        
        assert exc.message == "禁止访问"
        assert exc.code == "FORBIDDEN"
    
    def test_init_custom_message(self):
        """测试自定义消息初始化"""
        exc = ForbiddenException("没有权限访问此资源")
        
        assert exc.message == "没有权限访问此资源"
        assert exc.code == "FORBIDDEN"
    
    def test_with_permission_error(self):
        """测试权限错误"""
        exc = ForbiddenException("需要管理员权限")
        
        assert exc.message == "需要管理员权限"
    
    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(ForbiddenException):
            raise ForbiddenException()
    
    def test_inherits_from_question_bank_exception(self):
        """测试继承关系"""
        exc = ForbiddenException()
        
        assert isinstance(exc, QuestionBankException)


class TestAIServiceException:
    """AI 服务异常测试"""
    
    def test_init_without_service(self):
        """测试不带服务名初始化"""
        exc = AIServiceException("服务不可用")
        
        assert exc.message == "服务不可用"
        assert exc.code == "AI_SERVICE_ERROR"
    
    def test_init_with_service(self):
        """测试带服务名初始化"""
        exc = AIServiceException("连接超时", "LLM")
        
        assert exc.message == "AI 服务 (LLM) 不可用：连接超时"
        assert exc.code == "AI_SERVICE_ERROR"
    
    def test_with_embedding_service(self):
        """测试 Embedding 服务错误"""
        exc = AIServiceException("模型加载失败", "Embedding")
        
        assert exc.message == "AI 服务 (Embedding) 不可用：模型加载失败"
    
    def test_with_vision_service(self):
        """测试视觉服务错误"""
        exc = AIServiceException("API 限流", "Vision")
        
        assert exc.message == "AI 服务 (Vision) 不可用：API 限流"
    
    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(AIServiceException):
            raise AIServiceException("AI 错误")
    
    def test_inherits_from_question_bank_exception(self):
        """测试继承关系"""
        exc = AIServiceException("测试")
        
        assert isinstance(exc, QuestionBankException)


class TestFileUploadException:
    """文件上传异常测试"""
    
    def test_init_without_filename(self):
        """测试不带文件名初始化"""
        exc = FileUploadException("文件大小超限")
        
        assert exc.message == "文件大小超限"
        assert exc.code == "FILE_UPLOAD_ERROR"
    
    def test_init_with_filename(self):
        """测试带文件名初始化"""
        exc = FileUploadException("格式不支持", "test.pdf")
        
        assert exc.message == "文件上传失败 (test.pdf): 格式不支持"
        assert exc.code == "FILE_UPLOAD_ERROR"
    
    def test_with_image_file(self):
        """测试图片文件错误"""
        exc = FileUploadException("图片损坏", "photo.jpg")
        
        assert exc.message == "文件上传失败 (photo.jpg): 图片损坏"
    
    def test_with_document_file(self):
        """测试文档文件错误"""
        exc = FileUploadException("无法解析文档", "report.docx")
        
        assert exc.message == "文件上传失败 (report.docx): 无法解析文档"
    
    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(FileUploadException):
            raise FileUploadException("上传失败")
    
    def test_inherits_from_question_bank_exception(self):
        """测试继承关系"""
        exc = FileUploadException("测试")
        
        assert isinstance(exc, QuestionBankException)


class TestExceptionHierarchy:
    """异常层次结构测试"""
    
    def test_all_exceptions_inherit_from_question_bank_exception(self):
        """测试所有异常都继承自 QuestionBankException"""
        exceptions = [
            ResourceNotFoundException("type", "id"),
            ValidationException("msg"),
            DatabaseException("msg"),
            BusinessException("msg"),
            DuplicateException("type", "field", "value"),
            UnauthorizedException(),
            ForbiddenException(),
            AIServiceException("msg"),
            FileUploadException("msg")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, QuestionBankException)
    
    def test_all_exceptions_inherit_from_exception(self):
        """测试所有异常都继承自 Exception"""
        exceptions = [
            ResourceNotFoundException("type", "id"),
            ValidationException("msg"),
            DatabaseException("msg"),
            BusinessException("msg"),
            DuplicateException("type", "field", "value"),
            UnauthorizedException(),
            ForbiddenException(),
            AIServiceException("msg"),
            FileUploadException("msg")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, Exception)
    
    def test_catch_with_base_exception(self):
        """测试可以用基础异常捕获所有子类"""
        exceptions_to_test = [
            ResourceNotFoundException("type", "id"),
            ValidationException("msg"),
            DatabaseException("msg"),
        ]
        
        for exc_to_raise in exceptions_to_test:
            with pytest.raises(QuestionBankException):
                raise exc_to_raise
    
    def test_exception_codes_are_unique(self):
        """测试错误码区分不同类型的异常"""
        exc1 = ResourceNotFoundException("type", "id")
        exc2 = ValidationException("msg")
        exc3 = DatabaseException("msg")
        exc4 = BusinessException("msg")
        exc5 = DuplicateException("type", "field", "value")
        
        codes = [exc1.code, exc2.code, exc3.code, exc4.code, exc5.code]
        
        # 验证错误码都不同
        assert len(set(codes)) == len(codes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
