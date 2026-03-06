"""
文档题目提取器
支持 PDF、Word、TXT、Markdown 等格式
"""
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from agent.config import AgentConfig
from agent.services.model_client import ModelClient


class DocumentExtractor:
    """文档题目提取器"""
    
    EXTRACTION_PROMPT = """
请分析这个文档内容，提取其中所有的题目。

要求：
1. 识别文档中的所有题目（可能有 1 到多道）
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

如果文档中没有题目或无法识别，返回：
{"questions": [], "total_count": 0, "confidence": 0.0, "error": "无法识别题目"}
"""
    
    def __init__(self, config: Optional[dict] = None):
        """
        初始化文档提取器
        
        Args:
            config: LLM 模型配置
        """
        llm_config = config or AgentConfig.get_llm_config()
        self.client = ModelClient(llm_config)
        self.max_questions = AgentConfig.MAX_QUESTIONS_PER_DOCUMENT
    
    def extract(self, document_path: str) -> Dict[str, Any]:
        """
        从文档中提取题目
        
        Args:
            document_path: 文档文件路径
        
        Returns:
            提取结果
        """
        document_path = Path(document_path)
        
        if not document_path.exists():
            raise FileNotFoundError(f"文档文件不存在：{document_path}")
        
        # 读取文档内容
        content = self._read_document(document_path)
        
        if not content.strip():
            return {
                "questions": [],
                "total_count": 0,
                "confidence": 0.0,
                "error": "文档内容为空"
            }
        
        # 构造消息
        messages = [
            {
                "role": "user",
                "content": f"{self.EXTRACTION_PROMPT}\n\n文档内容：\n{content}"
            }
        ]
        
        try:
            # 调用 LLM
            response = self.client.chat(messages, temperature=0.3, max_tokens=4096)
            
            # 解析响应
            result = self._parse_response(response)
            
            # 添加元信息
            result["source_type"] = "document"
            result["source_file"] = document_path.name
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
                "error": f"JSON 解析失败：{str(e)}"
            }
        except Exception as e:
            return {
                "questions": [],
                "total_count": 0,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _read_document(self, path: Path) -> str:
        """读取文档内容"""
        suffix = path.suffix.lower()
        
        if suffix in {".txt", ".md", ".markdown"}:
            return self._read_text(path)
        elif suffix == ".pdf":
            return self._read_pdf(path)
        elif suffix in {".doc", ".docx"}:
            return self._read_word(path)
        else:
            # 默认按文本读取
            return self._read_text(path)
    
    def _read_text(self, path: Path) -> str:
        """读取纯文本文件"""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    
    def _read_pdf(self, path: Path) -> str:
        """读取 PDF 文件"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            # 如果没有安装 PyMuPDF，尝试用 pdfplumber
            try:
                import pdfplumber
                
                text = ""
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                return text
            except ImportError:
                return "[PDF 读取需要安装 PyMuPDF 或 pdfplumber]"
        except Exception as e:
            return f"[PDF 读取失败：{str(e)}]"
    
    def _read_word(self, path: Path) -> str:
        """读取 Word 文件"""
        try:
            from docx import Document
            
            doc = Document(path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except ImportError:
            return "[Word 读取需要安装 python-docx]"
        except Exception as e:
            return f"[Word 读取失败：{str(e)}]"
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析模型响应"""
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
        
        # 尝试提取 JSON
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(response[start:end])
            except json.JSONDecodeError:
                pass
        
        return {
            "questions": [],
            "total_count": 0,
            "confidence": 0.0,
            "error": "无法解析响应为 JSON"
        }
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def close(self):
        """关闭客户端"""
        self.client.close()
