"""
题目解析生成器
使用 LLM 为题目生成详细解析
"""
import json
from typing import Dict, Any, Optional, List

from agent.config import AgentConfig
from agent.services.model_client import ModelClient


class ExplanationGenerator:
    """题目解析生成器"""
    
    GENERATION_PROMPT = """
你是一位专业的题目解析助手。请根据以下题目信息生成详细、清晰的解析。

【题目类型】{type}
【题干】{content}
{options_section}
【正确答案】{answer}

请生成解析，要求：
1. 解释为什么正确答案是对的
2. 分析常见错误选项为什么错（如果是选择题）
3. 如果涉及知识点，请说明相关概念
4. 如果包含代码，请分析代码逻辑和执行过程
5. 语言简洁清晰，适合学习者理解
6. 长度适中，不要过于冗长

直接返回解析内容，不需要额外说明。
"""
    
    def __init__(self, config: Optional[dict] = None):
        """
        初始化解析生成器
        
        Args:
            config: LLM 模型配置
        """
        llm_config = config or AgentConfig.get_llm_config()
        self.client = ModelClient(llm_config)
    
    def generate(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        为题目生成解析
        
        Args:
            question_data: 题目数据，包含 type, content, options, answer
        
        Returns:
            包含解析的结果
        """
        try:
            # 构造选项部分
            options_section = ""
            if question_data.get("options"):
                options_text = "\n".join(question_data["options"])
                options_section = f"【选项】\n{options_text}"
            
            # 构造 Prompt
            prompt = self.GENERATION_PROMPT.format(
                type=question_data.get("type", "unknown"),
                content=question_data.get("content", ""),
                options_section=options_section,
                answer=question_data.get("answer", "")
            )
            
            # 调用 LLM
            messages = [{"role": "user", "content": prompt}]
            explanation = self.client.chat(messages, temperature=0.7, max_tokens=1024)
            
            return {
                "success": True,
                "explanation": explanation.strip(),
                "question_id": question_data.get("id"),
                "generated_at": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "question_id": question_data.get("id")
            }
    
    def generate_batch(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量生成解析
        
        Args:
            questions: 题目列表
        
        Returns:
            解析结果列表
        """
        results = []
        for q in questions:
            result = self.generate(q)
            results.append(result)
        return results
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def close(self):
        """关闭客户端"""
        self.client.close()
