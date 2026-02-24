"""
共享配置管理

所有入口（Web、MCP、微信小程序）共享的配置
"""

import os
from typing import Optional


class SharedConfig:
    """共享配置类"""
    
    # ========== 数据库配置（所有入口共享） ==========
    DATABASE_URL: str = "sqlite:///./data/question_bank.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # ========== 应用通用配置 ==========
    APP_NAME: str = "题库管理系统"
    DEBUG: bool = True
    
    # ========== 安全配置 ==========
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ========== 文件上传配置 ==========
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # ========== 各入口特定配置 ==========
    
    # Web入口配置
    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 8000
    
    # MCP入口配置
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8001
    
    # 微信小程序入口配置
    WECHAT_HOST: str = "0.0.0.0"
    WECHAT_PORT: int = 8002
    WECHAT_APP_ID: Optional[str] = None  # 从环境变量获取
    WECHAT_APP_SECRET: Optional[str] = None  # 从环境变量获取
    
    def __init__(self):
        """初始化配置，从环境变量加载"""
        # 从环境变量加载配置
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        
        # 数据库配置
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            self.DATABASE_URL = db_url
        
        # 微信小程序配置
        self.WECHAT_APP_ID = os.getenv("WECHAT_APP_ID")
        self.WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET")
        
        # 端口配置
        web_port = os.getenv("WEB_PORT")
        if web_port:
            self.WEB_PORT = int(web_port)
        
        mcp_port = os.getenv("MCP_PORT")
        if mcp_port:
            self.MCP_PORT = int(mcp_port)
        
        wechat_port = os.getenv("WECHAT_PORT")
        if wechat_port:
            self.WECHAT_PORT = int(wechat_port)
    
    def get_database_path(self) -> str:
        """
        获取数据库文件路径
        
        返回:
            str: 数据库文件路径
        """
        if self.DATABASE_URL.startswith("sqlite:///"):
            # 提取SQLite文件路径
            db_path = self.DATABASE_URL.replace("sqlite:///", "")
            return os.path.join(os.path.dirname(__file__), "..", db_path)
        return "data/question_bank.db"
    
    def ensure_directories(self) -> None:
        """
        确保必要的目录存在
        """
        # 确保上传目录存在
        upload_dir = os.path.join(os.path.dirname(__file__), "..", self.UPLOAD_DIR)
        os.makedirs(upload_dir, exist_ok=True)
        
        # 确保静态文件目录存在
        static_dir = os.path.join(os.path.dirname(__file__), "..", "web", "static")
        os.makedirs(static_dir, exist_ok=True)


# 创建全局配置实例
config = SharedConfig()