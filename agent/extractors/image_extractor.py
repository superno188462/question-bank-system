"""
图片题目提取器
使用多模态模型从图片中提取题目
"""
import json
import re
import ssl
from typing import List, Dict, Any, Optional
from pathlib import Path

from agent.config import AgentConfig
from agent.services.model_client import ModelClient


class ImageExtractor:
    """图片题目提取器"""
    
    # 提取题目的 Prompt 模板
    EXTRACTION_PROMPT = """
请仔细分析这张图片，提取其中所有的题目。

要求：
1. 识别图片中的所有题目（可能有 1 到多道）
2. 准确识别题型（选择题、填空题、判断题、简答题等）
3. 完整提取题干内容，如果包含代码请用 ``` 语言 ``` 包裹
4. 准确提取选项（如果有）
5. 提取正确答案
6. 如果有解析，也一并提取

请严格按照以下 JSON 格式返回，不要添加任何额外说明：

{
    "questions": [
        {
            "type": "single_choice|multiple_choice|fill_blank|judgment|short_answer",
            "content": "完整的题干内容，代码用 ``` 包裹",
            "options": ["A. 选项内容", "B. 选项内容"],
            "answer": "正确答案（选择题为字母，填空题为答案内容）",
            "explanation": "解析内容，没有则为空字符串"
        }
    ],
    "total_count": 题目总数，
    "confidence": 0.0-1.0 之间的置信度
}

题型说明：
- single_choice: 单选题
- multiple_choice: 多选题
- fill_blank: 填空题
- judgment: 判断题
- short_answer: 简答题

如果图片中没有题目或无法识别，返回：
{"questions": [], "total_count": 0, "confidence": 0.0, "error": "无法识别题目"}
"""
    
    def __init__(self, config: Optional[dict] = None):
        """
        初始化图片提取器
        
        Args:
            config: 视觉模型配置
        """
        vision_config = config or AgentConfig.get_vision_config()
        self.client = ModelClient(vision_config)
        self.max_questions = AgentConfig.MAX_QUESTIONS_PER_IMAGE
    
    def extract(self, image_path: str) -> Dict[str, Any]:
        """
        从图片中提取题目
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            提取结果，包含 questions 列表和元信息
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"图片文件不存在：{image_path}")
        
        # 编码图片为 base64
        image_data = self.client._encode_image(str(image_path))
        
        # 构造多模态消息
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_data}},
                    {"type": "text", "text": self.EXTRACTION_PROMPT}
                ]
            }
        ]
        
        try:
            # 调用视觉模型
            response = self.client.chat_with_images(messages, temperature=0.3)
            
            # 解析 JSON 响应
            result = self._parse_response(response)
            
            # 添加元信息
            result["source_type"] = "image"
            result["source_file"] = image_path.name
            result["extracted_at"] = self._get_timestamp()
            
            # 限制题目数量
            if len(result.get("questions", [])) > self.max_questions:
                result["questions"] = result["questions"][:self.max_questions]
                result["total_count"] = len(result["questions"])
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                "questions": [],
                "total_count": 0,
                "confidence": 0.0,
                "error": f"JSON 解析失败：{str(e)}",
                "raw_response": response[:500] if 'response' in dir() else ""
            }
        except ssl.SSLCertVerificationError as e:
            return {
                "questions": [],
                "total_count": 0,
                "confidence": 0.0,
                "error": "SSL 证书验证失败",
                "error_detail": "API 服务器的 SSL 证书不受信任。请联系管理员检查 VERIFY_SSL 配置或安装正确的 CA 证书。",
                "solution": "设置环境变量 VERIFY_SSL=false 可临时禁用 SSL 验证（仅开发环境）"
            }
        except Exception as e:
            error_msg = str(e)
            # 提取友好的错误信息
            if "CERTIFICATE_VERIFY_FAILED" in error_msg or "ssl" in error_msg.lower():
                error_detail = "SSL 证书验证失败，可能是自签名证书或证书链不完整"
                solution = "设置环境变量 VERIFY_SSL=false 可临时禁用 SSL 验证（仅开发环境）"
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                error_detail = "网络连接失败，请检查网络或 API 服务是否可用"
                solution = "检查网络连接，确认 API 服务正常运行"
            elif "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower() or "401" in error_msg:
                error_detail = "API Key 无效或已过期"
                solution = "在设置页面检查并更新 API Key 配置"
            elif "model" in error_msg.lower() or "not found" in error_msg.lower():
                error_detail = "指定的模型不可用"
                solution = "在设置页面检查模型配置是否正确"
            else:
                error_detail = error_msg
                solution = "请查看日志获取详细信息，或联系技术支持"
            
            return {
                "questions": [],
                "total_count": 0,
                "confidence": 0.0,
                "error": self._get_friendly_error_name(e),
                "error_detail": error_detail,
                "solution": solution
            }
    
    def extract_batch(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        批量从多张图片中提取题目
        
        Args:
            image_paths: 图片文件路径列表
        
        Returns:
            合并的提取结果
        """
        all_questions = []
        total_confidence = 0
        error_count = 0
        
        for image_path in image_paths:
            try:
                result = self.extract(image_path)
                if result.get("questions"):
                    all_questions.extend(result["questions"])
                    total_confidence += result.get("confidence", 0) * len(result["questions"])
                if result.get("error"):
                    error_count += 1
            except Exception as e:
                error_count += 1
                continue
        
        return {
            "questions": all_questions,
            "total_count": len(all_questions),
            "source_type": "image_batch",
            "source_files": [Path(p).name for p in image_paths],
            "average_confidence": total_confidence / len(all_questions) if all_questions else 0,
            "error_count": error_count,
            "extracted_at": self._get_timestamp()
        }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析模型响应，提取 JSON"""
        # 尝试直接解析
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        # 尝试提取 JSON 代码块
        json_pattern = r'```(?:json)?\s*({.*?})\s*```'
        match = re.search(json_pattern, response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试提取第一个 { 到最后一个 }
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(response[start:end])
            except json.JSONDecodeError:
                pass
        
        # 解析失败
        return {
            "questions": [],
            "total_count": 0,
            "confidence": 0.0,
            "error": "无法解析响应为 JSON"
        }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_friendly_error_name(self, exception: Exception) -> str:
        """获取友好的错误名称"""
        error_msg = str(exception).lower()
        if "certificate" in error_msg or "ssl" in error_msg:
            return "证书验证失败"
        elif "connection" in error_msg or "timeout" in error_msg:
            return "网络连接失败"
        elif "api_key" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
            return "认证失败"
        elif "model" in error_msg or "not found" in error_msg:
            return "模型不可用"
        else:
            return "提取失败"
    
    def close(self):
        """关闭客户端"""
        self.client.close()
