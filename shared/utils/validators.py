"""
数据验证工具

包含各种数据验证函数：
1. 分类验证
2. 标签验证
3. 题目验证
4. 通用验证
"""

import re
from typing import List, Optional, Any
from datetime import datetime


def validate_category_name(name: str) -> tuple[bool, str]:
    """
    验证分类名称
    
    参数:
        name: 分类名称
        
    返回:
        (是否有效, 错误信息)
    """
    if not name or not name.strip():
        return False, "分类名称不能为空"
    
    if len(name.strip()) > 100:
        return False, "分类名称不能超过100个字符"
    
    # 检查是否包含非法字符
    if re.search(r'[<>"\'&]', name):
        return False, "分类名称包含非法字符"
    
    return True, ""


def validate_category_description(description: Optional[str]) -> tuple[bool, str]:
    """
    验证分类描述
    
    参数:
        description: 分类描述
        
    返回:
        (是否有效, 错误信息)
    """
    if description is None:
        return True, ""
    
    if len(description) > 500:
        return False, "分类描述不能超过500个字符"
    
    return True, ""


def validate_tag_name(name: str) -> tuple[bool, str]:
    """
    验证标签名称
    
    参数:
        name: 标签名称
        
    返回:
        (是否有效, 错误信息)
    """
    if not name or not name.strip():
        return False, "标签名称不能为空"
    
    if len(name.strip()) > 50:
        return False, "标签名称不能超过50个字符"
    
    # 检查是否包含非法字符
    if re.search(r'[<>"\'&]', name):
        return False, "标签名称包含非法字符"
    
    return True, ""


def validate_tag_color(color: str) -> tuple[bool, str]:
    """
    验证标签颜色
    
    参数:
        color: 颜色代码（如#FFFFFF）
        
    返回:
        (是否有效, 错误信息)
    """
    if not color:
        return False, "颜色不能为空"
    
    # 检查是否为有效的十六进制颜色代码
    if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
        return False, "颜色格式无效，应为#FFFFFF格式"
    
    return True, ""


def validate_question_content(content: str) -> tuple[bool, str]:
    """
    验证题目内容
    
    参数:
        content: 题干内容
        
    返回:
        (是否有效, 错误信息)
    """
    if not content or not content.strip():
        return False, "题干内容不能为空"
    
    if len(content.strip()) < 5:
        return False, "题干内容太短，至少5个字符"
    
    if len(content) > 5000:
        return False, "题干内容不能超过5000个字符"
    
    return True, ""


def validate_question_options(options: Optional[List[str]]) -> tuple[bool, str]:
    """
    验证题目选项
    
    参数:
        options: 选项列表
        
    返回:
        (是否有效, 错误信息)
    """
    if options is None:
        return True, ""
    
    if not isinstance(options, list):
        return False, "选项必须是列表"
    
    if len(options) == 0:
        return True, ""  # 填空题目允许空选项
    
    # 检查每个选项
    for i, option in enumerate(options):
        if not isinstance(option, str):
            return False, f"第{i+1}个选项必须是字符串"
        
        if not option.strip():
            return False, f"第{i+1}个选项不能为空"
        
        if len(option) > 1000:
            return False, f"第{i+1}个选项不能超过1000个字符"
    
    # 检查选项是否重复
    unique_options = set(options)
    if len(unique_options) != len(options):
        return False, "选项不能重复"
    
    return True, ""


def validate_question_answer(answer: str, options: Optional[List[str]] = None) -> tuple[bool, str]:
    """
    验证题目答案
    
    参数:
        answer: 答案
        options: 选项列表（可选）
        
    返回:
        (是否有效, 错误信息)
    """
    if not answer or not answer.strip():
        return False, "答案不能为空"
    
    if len(answer) > 1000:
        return False, "答案不能超过1000个字符"
    
    # 如果是选择题，答案必须在选项中
    if options and len(options) > 0:
        if answer not in options:
            return False, "答案必须在选项中"
    
    return True, ""


def validate_question_explanation(explanation: Optional[str]) -> tuple[bool, str]:
    """
    验证题目解析
    
    参数:
        explanation: 题目解析
        
    返回:
        (是否有效, 错误信息)
    """
    if explanation is None:
        return True, ""
    
    if len(explanation) > 5000:
        return False, "题目解析不能超过5000个字符"
    
    return True, ""


def validate_uuid(uuid_str: str) -> tuple[bool, str]:
    """
    验证UUID格式
    
    参数:
        uuid_str: UUID字符串
        
    返回:
        (是否有效, 错误信息)
    """
    if not uuid_str:
        return False, "ID不能为空"
    
    # 简单的UUID格式验证
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, uuid_str, re.IGNORECASE):
        return False, "ID格式无效"
    
    return True, ""


def validate_pagination_params(page: int, limit: int) -> tuple[bool, str]:
    """
    验证分页参数
    
    参数:
        page: 页码
        limit: 每页数量
        
    返回:
        (是否有效, 错误信息)
    """
    if page < 1:
        return False, "页码必须大于等于1"
    
    if limit < 1:
        return False, "每页数量必须大于等于1"
    
    if limit > 100:
        return False, "每页数量不能超过100"
    
    return True, ""


def validate_search_keyword(keyword: str) -> tuple[bool, str]:
    """
    验证搜索关键词
    
    参数:
        keyword: 搜索关键词
        
    返回:
        (是否有效, 错误信息)
    """
    if not keyword or not keyword.strip():
        return False, "搜索关键词不能为空"
    
    if len(keyword.strip()) > 100:
        return False, "搜索关键词不能超过100个字符"
    
    # 检查是否包含危险字符
    dangerous_patterns = [
        r'--',  # SQL注释
        r';',   # SQL语句分隔符
        r'/\*', # SQL注释开始
        r'\*/', # SQL注释结束
        r'union.*select',  # SQL注入
        r'insert.*into',   # SQL注入
        r'delete.*from',   # SQL注入
        r'drop.*table',    # SQL注入
        r'update.*set',    # SQL注入
    ]
    
    keyword_lower = keyword.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, keyword_lower, re.IGNORECASE):
            return False, "搜索关键词包含危险字符"
    
    return True, ""


def sanitize_input(text: str) -> str:
    """
    清理输入文本，防止XSS攻击
    
    参数:
        text: 输入文本
        
    返回:
        清理后的文本
    """
    if not text:
        return ""
    
    # 替换危险字符
    replacements = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        '&': '&amp;',
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text


def format_datetime(dt: datetime) -> str:
    """
    格式化日期时间
    
    参数:
        dt: 日期时间对象
        
    返回:
        格式化后的字符串
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """
    解析日期时间字符串
    
    参数:
        dt_str: 日期时间字符串
        
    返回:
        日期时间对象或None
    """
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except:
        return None