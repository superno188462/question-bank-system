"""
OCR + 文本模型题目提取器
当视觉模型不可用时，使用 OCR 识别文字后通过文本 LLM 进行题目结构化提取
"""
import json
import re
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from agent.config import AgentConfig
from agent.services.ocr_service import OcrService
from agent.services.model_client import ModelClient

logger = logging.getLogger(__name__)


class OcrQuestionExtractor:
    """
    OCR + 文本模型题目提取器
    
    工作流程：
    1. 使用 OCR 引擎识别图片中的文字
    2. 使用文本 LLM 对识别的文字进行结构化提取
    3. 返回标准化的题目 JSON 格式
    """
    
    # 题目提取 Prompt 模板
    EXTRACTION_PROMPT = """
请分析以下从图片中识别的文本内容，提取其中所有的题目。

要求：
1. 识别文本中的所有题目（可能有 1 到多道）
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

注意：
- 如果识别的文本中没有题目或无法理解，返回：{"questions": [], "total_count": 0, "confidence": 0.0}
- 确保 JSON 格式正确，可以被直接解析
- 置信度基于你对提取结果的把握程度（0.0-1.0）

识别的文本内容：
{text}
"""
    
    def __init__(self, ocr_config: Optional[dict] = None, llm_config: Optional[dict] = None):
        """
        初始化 OCR 题目提取器
        
        Args:
            ocr_config: OCR 服务配置
            llm_config: 文本 LLM 配置
        """
        # 初始化 OCR 服务
        self.ocr_config = ocr_config or AgentConfig.get_ocr_config()
        self.ocr_service = OcrService(self.ocr_config)
        
        # 初始化 LLM 客户端（使用文本模型）
        self.llm_config = llm_config or AgentConfig.get_llm_config()
        self.llm_client = ModelClient(self.llm_config)
        
        # 配置参数
        self.max_questions = AgentConfig.MAX_QUESTIONS_PER_IMAGE
        self.confidence_threshold = AgentConfig.CONFIDENCE_THRESHOLD
    
    def extract(self, image_path: str) -> Dict[str, Any]:
        """
        从图片中提取题目（OCR + LLM 方案）
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            提取结果，包含 questions 列表和元信息
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"图片文件不存在：{image_path}")
        
        try:
            # 步骤 1: OCR 识别
            ocr_result = self.ocr_service.recognize_with_confidence(str(image_path))
            text = ocr_result.get("text", "")
            ocr_confidence = ocr_result.get("confidence", 0.0)
            
            # 检查 OCR 结果
            if not text.strip():
                logger.warning(f"OCR 识别结果为空：{image_path}")
                return {
                    "questions": [],
                    "total_count": 0,
                    "confidence": 0.0,
                    "error": "OCR 识别结果为空",
                    "extraction_method": "ocr+llm",
                    "ocr_engine": self.ocr_service.current_engine
                }
            
            # 步骤 2: 使用 LLM 提取题目
            messages = [{
                "role": "user",
                "content": self.EXTRACTION_PROMPT.format(text=text)
            }]
            
            response = self.llm_client.chat(messages, temperature=0.3)
            result = self._parse_response(response)
            
            # 合并 OCR 置信度和 LLM 置信度
            llm_confidence = result.get("confidence", 0.0)
            combined_confidence = (ocr_confidence + llm_confidence) / 2
            
            # 添加元信息
            result["confidence"] = combined_confidence
            result["extraction_method"] = "ocr+llm"
            result["ocr_engine"] = self.ocr_service.current_engine
            result["ocr_confidence"] = ocr_confidence
            result["source_type"] = "image"
            result["source_file"] = image_path.name
            result["extracted_at"] = self._get_timestamp()
            
            # 限制题目数量
            if len(result.get("questions", [])) > self.max_questions:
                result["questions"] = result["questions"][:self.max_questions]
                result["total_count"] = len(result["questions"])
            
            # 记录日志
            logger.info(
                f"OCR+LLM 提取完成：method=ocr+llm, "
                f"engine={self.ocr_service.current_engine}, "
                f"questions={result.get('total_count', 0)}, "
                f"confidence={combined_confidence:.2f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"OCR+LLM 提取失败：{e}")
            return {
                "questions": [],
                "total_count": 0,
                "confidence": 0.0,
                "error": f"OCR+LLM 提取失败：{str(e)}",
                "extraction_method": "ocr+llm",
                "ocr_engine": self.ocr_service.current_engine
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
        ocr_engine_used = None
        
        for image_path in image_paths:
            try:
                result = self.extract(image_path)
                if result.get("questions"):
                    all_questions.extend(result["questions"])
                    total_confidence += result.get("confidence", 0) * len(result["questions"])
                if result.get("error"):
                    error_count += 1
                if result.get("ocr_engine"):
                    ocr_engine_used = result["ocr_engine"]
            except Exception as e:
                logger.error(f"批量提取中图片失败 {image_path}: {e}")
                error_count += 1
                continue
        
        return {
            "questions": all_questions,
            "total_count": len(all_questions),
            "source_type": "image_batch",
            "source_files": [Path(p).name for p in image_paths],
            "average_confidence": total_confidence / len(all_questions) if all_questions else 0,
            "error_count": error_count,
            "extraction_method": "ocr+llm",
            "ocr_engine": ocr_engine_used,
            "extracted_at": self._get_timestamp()
        }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析 LLM 响应，提取 JSON"""
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
        logger.warning(f"无法解析 LLM 响应为 JSON: {response[:200]}...")
        return {
            "questions": [],
            "total_count": 0,
            "confidence": 0.0,
            "error": "无法解析 LLM 响应为 JSON"
        }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def close(self):
        """关闭服务"""
        self.ocr_service.close()
        self.llm_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
