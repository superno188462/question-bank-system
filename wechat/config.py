"""
微信小程序入口配置
"""

from shared.config import config as shared_config


class WeChatConfig:
    """微信小程序入口配置类"""
    
    def __init__(self):
        # 继承共享配置
        self.shared = shared_config
        
        # 微信特定配置
        self.HOST = "0.0.0.0"
        self.PORT = shared_config.WECHAT_PORT
    
    @property
    def DATABASE_URL(self):
        return self.shared.DATABASE_URL
    
    @property
    def DEBUG(self):
        return self.shared.DEBUG
    
    @property
    def APP_NAME(self):
        return self.shared.APP_NAME + " (微信小程序)"


# 创建微信配置实例
settings = WeChatConfig()