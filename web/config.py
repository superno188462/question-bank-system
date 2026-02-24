"""
Web入口配置

继承共享配置，添加Web特定配置
"""

from shared.config import config as shared_config


class WebConfig:
    """Web入口配置类"""
    
    def __init__(self):
        # 继承共享配置
        self.shared = shared_config
        
        # Web特定配置
        self.HOST = shared_config.WEB_HOST
        self.PORT = shared_config.WEB_PORT
        
        # CORS配置
        self.CORS_ORIGINS = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]
        
        # 静态文件配置
        self.STATIC_DIR = "web/static"
        
        # API文档配置
        self.DOCS_URL = "/docs"
        self.REDOC_URL = "/redoc"
    
    @property
    def DATABASE_URL(self):
        return self.shared.DATABASE_URL
    
    @property
    def DEBUG(self):
        return self.shared.DEBUG
    
    @property
    def APP_NAME(self):
        return self.shared.APP_NAME + " (Web)"
    
    def get_database_path(self):
        return self.shared.get_database_path()
    
    def ensure_directories(self):
        return self.shared.ensure_directories()


# 创建Web配置实例
settings = WebConfig()