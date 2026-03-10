"""
通用模型客户端
支持 OpenAI 兼容 API（千问、DeepSeek、GPT 等）
"""
import os
import base64
import mimetypes
from typing import Union, List, Optional
import httpx
from httpx import HTTPTransport

from agent.config import AgentConfig


class ModelClient:
    """通用模型客户端 - 支持 OpenAI 兼容 API"""
    
    def __init__(self, config: Optional[dict] = None):
        """
        初始化模型客户端
        
        Args:
            config: 模型配置，包含 model, api_key, base_url
        """
        self.config = config or AgentConfig.get_llm_config()
        self.model = self.config.get("model", "qwen-plus")
        self.api_key = self.config.get("api_key", "")
        self.base_url = self.config.get("base_url", "")
        
        # 配置 HTTP 客户端（支持代理和 SSL 验证）
        proxy = AgentConfig.HTTP_PROXY
        # SSL 验证配置（可通过环境变量控制）
        # VERIFY_SSL=false 禁用 SSL 验证（解决自签名证书问题）
        verify_ssl = os.getenv("VERIFY_SSL", "true").lower() == "true"
        
        if proxy:
            transport = HTTPTransport(proxy=proxy, verify=verify_ssl)
            self.http_client = httpx.Client(timeout=60.0, transport=transport, verify=verify_ssl)
        else:
            self.http_client = httpx.Client(timeout=60.0, verify=verify_ssl)
    
    def _encode_image(self, image_path: str) -> str:
        """将本地图片编码为 base64"""
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg"
        
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        
        return f"data:{mime_type};base64,{b64}"
    
    def chat(self, messages: List[dict], **kwargs) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user|assistant", "content": "..."}]
            **kwargs: 其他参数（temperature, max_tokens 等）
        
        Returns:
            AI 回复的文本内容
        """
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }
        
        response = self.http_client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def chat_with_images(self, messages: List[dict], **kwargs) -> str:
        """
        发送带图片的聊天请求（多模态）
        
        Args:
            messages: 消息列表，content 可以是文本或图片
                     格式：[{"role": "user", "content": [
                         {"type": "text", "text": "..."},
                         {"type": "image_url", "image_url": {"url": "..."}}
                     ]}]
            **kwargs: 其他参数
        
        Returns:
            AI 回复的文本内容
        """
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }
        
        response = self.http_client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def close(self):
        """关闭 HTTP 客户端"""
        self.http_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
