"""
自定义异常类
用于统一异常处理和错误分类
"""


class QuestionBankException(Exception):
    """题库系统基础异常类"""
    
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ResourceNotFoundException(QuestionBankException):
    """资源未找到异常 (404)"""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} 不存在：{resource_id}"
        super().__init__(message, code="NOT_FOUND")


class ValidationException(QuestionBankException):
    """验证异常 (400)"""
    
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")


class DatabaseException(QuestionBankException):
    """数据库操作异常 (500)"""
    
    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(message, code="DATABASE_ERROR")


class BusinessException(QuestionBankException):
    """业务逻辑异常 (400)"""
    
    def __init__(self, message: str):
        super().__init__(message, code="BUSINESS_ERROR")


class DuplicateException(QuestionBankException):
    """重复数据异常 (409)"""
    
    def __init__(self, resource_type: str, field: str, value: str):
        message = f"{resource_type} 已存在：{field}={value}"
        super().__init__(message, code="DUPLICATE_ERROR")


class UnauthorizedException(QuestionBankException):
    """未授权异常 (401)"""
    
    def __init__(self, message: str = "未授权访问"):
        super().__init__(message, code="UNAUTHORIZED")


class ForbiddenException(QuestionBankException):
    """禁止访问异常 (403)"""
    
    def __init__(self, message: str = "禁止访问"):
        super().__init__(message, code="FORBIDDEN")


class AIServiceException(QuestionBankException):
    """AI 服务异常 (503)"""
    
    def __init__(self, message: str, service: str = None):
        if service:
            message = f"AI 服务 ({service}) 不可用：{message}"
        super().__init__(message, code="AI_SERVICE_ERROR")


class FileUploadException(QuestionBankException):
    """文件上传异常 (400)"""
    
    def __init__(self, message: str, filename: str = None):
        if filename:
            message = f"文件上传失败 ({filename}): {message}"
        super().__init__(message, code="FILE_UPLOAD_ERROR")
