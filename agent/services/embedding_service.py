"""
Embedding 服务
支持在线 API 和 Ollama 本地模型（OpenAI 兼容格式）
"""
import numpy as np
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Embedding 服务
    支持 OpenAI 兼容 API（包括 Ollama）
    """
    
    def __init__(self, config: Dict):
        """
        初始化 Embedding 服务
        
        Args:
            config: 配置字典，包含：
                - model_name: 模型名称
                - api_key: API Key
                - base_url: API 基础 URL
        """
        self.model_name = config.get('model_name', 'text-embedding-v3')
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', '')
        
        # 初始化 OpenAI 客户端（兼容 Ollama）
        from openai import OpenAI
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        logger.info(f"Embedding 服务初始化：model={self.model_name}, base_url={self.base_url}")
    
    def embed(self, text: str) -> np.ndarray:
        """
        将文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            numpy 数组表示的向量
        """
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            embedding = np.array(response.data[0].embedding)
            logger.debug(f"Embedding 计算成功：dimension={len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Embedding 计算失败：{e}")
            raise
    
    def embed_batch(self, texts: list[str], batch_size: int = 32) -> list[np.ndarray]:
        """
        批量计算 Embedding
        
        Args:
            texts: 文本列表
            batch_size: 批次大小
            
        Returns:
            向量列表
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=batch
                )
                for data in response.data:
                    embeddings.append(np.array(data.embedding))
            except Exception as e:
                logger.error(f"批量 Embedding 失败：{e}")
                raise
        
        return embeddings


# 缓存实例（避免重复创建）
_embedding_service: Optional[EmbeddingService] = None
_last_config_hash: str = ""


def get_embedding_service(config: Dict) -> EmbeddingService:
    """
    获取 Embedding 服务单例
    
    Args:
        config: 配置字典
        
    Returns:
        EmbeddingService 实例
    """
    global _embedding_service, _last_config_hash
    
    # 配置哈希检测（配置变化时重新创建）
    import hashlib
    config_hash = hashlib.md5(str(sorted(config.items())).encode()).hexdigest()
    
    if _embedding_service is None or config_hash != _last_config_hash:
        _embedding_service = EmbeddingService(config)
        _last_config_hash = config_hash
        logger.info("创建新的 Embedding 服务实例")
    
    return _embedding_service
