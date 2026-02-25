"""
共享配置管理
所有入口（Web、MCP、微信小程序）共享的配置
"""

import os


class SharedConfig:
    """共享配置类"""
    
    # 数据库配置（所有入口共享）
    DATABASE_URL: str = "sqlite:///./data/question_bank.db"
    
    # 应用通用配置
    APP_NAME: str = "题库管理系统"
    DEBUG: bool = True
    
    # 各入口端口配置
    WEB_PORT: int = 8000
    MCP_PORT: int = 8001
    WECHAT_PORT: int = 8002
    
    def __init__(self):
        """初始化配置，从环境变量加载"""
        # 从环境变量加载配置
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        
        # 数据库配置
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            self.DATABASE_URL = db_url
        
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
        """
        if self.DATABASE_URL.startswith("sqlite:///"):
            # 提取SQLite文件路径
            db_path = self.DATABASE_URL.replace("sqlite:///", "")
            return db_path
        return "data/question_bank.db"


# 创建全局配置实例
config = SharedConfig()