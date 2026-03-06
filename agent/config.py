"""
Agent 配置模块
支持多种模型提供商（OpenAI 兼容 API）
"""
import os
from dotenv import load_dotenv

load_dotenv()


class AgentConfig:
    """Agent 配置类"""
    
    # 模型配置（支持 OpenAI 兼容 API）
    LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "qwen-plus")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # Embedding 模型配置
    EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "text-embedding-v3")
    EMBED_API_KEY = os.getenv("EMBED_API_KEY", "")
    EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # 多模态模型配置（用于图片提取）
    VISION_MODEL_ID = os.getenv("VISION_MODEL_ID", "qwen-vl-max")
    VISION_API_KEY = os.getenv("VISION_API_KEY", "")
    VISION_BASE_URL = os.getenv("VISION_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # 代理配置（可选）
    HTTP_PROXY = os.getenv("HTTP_PROXY", "")
    
    # 提取配置
    MAX_QUESTIONS_PER_IMAGE = 10  # 单张图片最多提取的题目数
    MAX_QUESTIONS_PER_DOCUMENT = 50  # 单个文档最多提取的题目数
    CONFIDENCE_THRESHOLD = 0.6  # 置信度阈值，低于此值需要人工重点检查
    
    # 文件上传配置
    MAX_FILE_SIZE_MB = 50  # 最大文件大小（MB）
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "txt", "md"}
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        if not cls.LLM_API_KEY:
            raise ValueError("LLM_API_KEY 未配置")
        if not cls.VISION_API_KEY:
            raise ValueError("VISION_API_KEY 未配置")
        return True
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """获取 LLM 配置"""
        return {
            "model": cls.LLM_MODEL_ID,
            "api_key": cls.LLM_API_KEY,
            "base_url": cls.LLM_BASE_URL,
        }
    
    @classmethod
    def get_vision_config(cls) -> dict:
        """获取视觉模型配置"""
        return {
            "model": cls.VISION_MODEL_ID,
            "api_key": cls.VISION_API_KEY,
            "base_url": cls.VISION_BASE_URL,
        }
    
    @classmethod
    def get_embed_config(cls) -> dict:
        """获取 Embedding 模型配置"""
        return {
            "model": cls.EMBED_MODEL_NAME,
            "api_key": cls.EMBED_API_KEY,
            "base_url": cls.EMBED_BASE_URL,
        }
