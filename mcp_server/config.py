"""
MCP入口配置
"""

from shared.config import config as shared_config


class MCPConfig:
    """MCP入口配置类"""
    
    def __init__(self):
        # 继承共享配置
        self.shared = shared_config
        
        # MCP特定配置
        self.HOST = "0.0.0.0"
        self.PORT = shared_config.MCP_PORT
    
    @property
    def DATABASE_URL(self):
        return self.shared.DATABASE_URL
    
    @property
    def DEBUG(self):
        return self.shared.DEBUG
    
    @property
    def APP_NAME(self):
        return self.shared.APP_NAME + " (MCP)"


# 创建MCP配置实例
settings = MCPConfig()