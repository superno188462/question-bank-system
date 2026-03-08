"""
Agent 配置模块
支持热更新（每次读取最新配置文件）
配置文件：config/agent.json
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class AgentConfig:
    """Agent 配置类（支持热更新）"""
    
    # 配置文件路径
    CONFIG_FILE = Path(__file__).parent.parent / "config" / "agent.json"
    
    # 缓存配置（用于性能优化，但提供刷新机制）
    _config_cache: Optional[Dict[str, Any]] = None
    _cache_mtime: float = 0
    
    @classmethod
    def _load_config(cls, force_refresh: bool = False) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            force_refresh: 是否强制刷新（忽略缓存）
        
        Returns:
            配置字典
        """
        import time
        
        # 检查是否需要刷新缓存
        if not force_refresh and cls._config_cache is not None:
            try:
                current_mtime = cls.CONFIG_FILE.stat().st_mtime
                if current_mtime == cls._cache_mtime:
                    return cls._config_cache
            except FileNotFoundError:
                pass
        
        # 加载配置文件
        config = {}
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                cls._config_cache = config
                cls._cache_mtime = cls.CONFIG_FILE.stat().st_mtime
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  读取配置文件失败：{e}，使用默认配置")
                config = cls._get_default_config()
                cls._config_cache = config
        else:
            # 配置文件不存在，使用默认配置
            config = cls._get_default_config()
            cls._config_cache = config
        
        return config
    
    @classmethod
    def _get_default_config(cls) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "llm": {
                "model_id": "qwen-plus",
                "api_key": "",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
            },
            "vision": {
                "model_id": "qwen-vl-max",
                "api_key": "",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
            },
            "embedding": {
                "model_name": "text-embedding-v3",
                "api_key": "",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
            },
            "settings": {
                "max_questions_per_image": 10,
                "max_questions_per_document": 50,
                "confidence_threshold": 0.6,
                "max_file_size_mb": 50
            },
            "allowed_extensions": {
                "images": ["png", "jpg", "jpeg", "gif", "webp"],
                "documents": ["pdf", "doc", "docx", "txt", "md"]
            }
        }
    
    @classmethod
    def refresh(cls):
        """强制刷新配置缓存"""
        cls._config_cache = None
        cls._cache_mtime = 0
        cls._load_config(force_refresh=True)
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 配置字典
        
        Returns:
            是否保存成功
        """
        try:
            # 确保 config 目录存在
            cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 刷新缓存
            cls.refresh()
            return True
        except IOError as e:
            print(f"❌ 保存配置文件失败：{e}")
            return False
    
    # ========== LLM 配置 ==========
    
    @classmethod
    @property
    def LLM_MODEL_ID(cls) -> str:
        """LLM 模型 ID"""
        config = cls._load_config()
        return config.get("llm", {}).get("model_id", "qwen-plus")
    
    @classmethod
    @property
    def LLM_API_KEY(cls) -> str:
        """LLM API Key"""
        config = cls._load_config()
        return config.get("llm", {}).get("api_key", "")
    
    @classmethod
    @property
    def LLM_BASE_URL(cls) -> str:
        """LLM API Base URL"""
        config = cls._load_config()
        return config.get("llm", {}).get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # ========== Vision 配置 ==========
    
    @classmethod
    @property
    def VISION_MODEL_ID(cls) -> str:
        """视觉模型 ID"""
        config = cls._load_config()
        return config.get("vision", {}).get("model_id", "qwen-vl-max")
    
    @classmethod
    @property
    def VISION_API_KEY(cls) -> str:
        """视觉模型 API Key"""
        config = cls._load_config()
        return config.get("vision", {}).get("api_key", "")
    
    @classmethod
    @property
    def VISION_BASE_URL(cls) -> str:
        """视觉模型 API Base URL"""
        config = cls._load_config()
        return config.get("vision", {}).get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # ========== Embedding 配置 ==========
    
    @classmethod
    @property
    def EMBED_MODEL_NAME(cls) -> str:
        """Embedding 模型名称"""
        config = cls._load_config()
        return config.get("embedding", {}).get("model_name", "text-embedding-v3")
    
    @classmethod
    @property
    def EMBED_API_KEY(cls) -> str:
        """Embedding API Key"""
        config = cls._load_config()
        return config.get("embedding", {}).get("api_key", "")
    
    @classmethod
    @property
    def EMBED_BASE_URL(cls) -> str:
        """Embedding API Base URL"""
        config = cls._load_config()
        return config.get("embedding", {}).get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # ========== 设置 ==========
    
    @classmethod
    @property
    def MAX_QUESTIONS_PER_IMAGE(cls) -> int:
        """单张图片最多提取的题目数"""
        config = cls._load_config()
        return config.get("settings", {}).get("max_questions_per_image", 10)
    
    @classmethod
    @property
    def MAX_QUESTIONS_PER_DOCUMENT(cls) -> int:
        """单个文档最多提取的题目数"""
        config = cls._load_config()
        return config.get("settings", {}).get("max_questions_per_document", 50)
    
    @classmethod
    @property
    def CONFIDENCE_THRESHOLD(cls) -> float:
        """置信度阈值"""
        config = cls._load_config()
        return config.get("settings", {}).get("confidence_threshold", 0.6)
    
    @classmethod
    @property
    def HTTP_PROXY(cls) -> Optional[str]:
        """HTTP 代理（可选）"""
        config = cls._load_config()
        return config.get("settings", {}).get("http_proxy", None)
    
    @classmethod
    @property
    def MAX_FILE_SIZE_MB(cls) -> int:
        """最大文件大小（MB）"""
        config = cls._load_config()
        return config.get("settings", {}).get("max_file_size_mb", 50)
    
    # ========== 文件扩展名 ==========
    
    @classmethod
    @property
    def ALLOWED_IMAGE_EXTENSIONS(cls) -> set:
        """允许的图片扩展名"""
        config = cls._load_config()
        extensions = config.get("allowed_extensions", {}).get("images", [])
        return set(extensions)
    
    @classmethod
    @property
    def ALLOWED_DOCUMENT_EXTENSIONS(cls) -> set:
        """允许的文档扩展名"""
        config = cls._load_config()
        extensions = config.get("allowed_extensions", {}).get("documents", [])
        return set(extensions)
    
    # ========== 配置验证 ==========
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        if not cls.LLM_API_KEY:
            raise ValueError("LLM_API_KEY 未配置，请在 Web 设置中配置 API Key")
        if not cls.VISION_API_KEY:
            raise ValueError("VISION_API_KEY 未配置，请在 Web 设置中配置 API Key")
        return True
    
    @classmethod
    def is_configured(cls) -> bool:
        """检查是否已配置"""
        return bool(cls.LLM_API_KEY and cls.VISION_API_KEY)
    
    # ========== 配置导出 ==========
    
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
    
    @classmethod
    def get_full_config(cls) -> Dict[str, Any]:
        """获取完整配置（用于 API 返回）"""
        config = cls._load_config(force_refresh=True)
        # 隐藏敏感的 API Key（部分掩码）
        safe_config = json.loads(json.dumps(config))
        for key in ["llm", "vision", "embedding"]:
            if key in safe_config and "api_key" in safe_config[key]:
                api_key = safe_config[key]["api_key"]
                if api_key:
                    safe_config[key]["api_key"] = api_key[:10] + "..." + api_key[-5:] if len(api_key) > 15 else "***"
        return safe_config
