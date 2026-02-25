"""
微信小程序入口服务器
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 添加项目根目录到Python路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import config


def create_wechat_app() -> FastAPI:
    """
    创建微信小程序应用
    """
    app = FastAPI(
        title="题库管理系统 - 微信小程序入口",
        description="为微信小程序优化的API接口",
        version="1.0",
        docs_url="/docs",
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 根路径
    @app.get("/")
    async def root():
        return {
            "service": "题库管理系统 - 微信小程序入口",
            "status": "运行中",
            "docs": "/docs",
        }
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "wechat"}
    
    # 获取题目列表
    @app.get("/api/questions")
    async def get_questions():
        """获取题目列表"""
        return {
            "success": True,
            "data": [],
            "message": "微信小程序API待实现"
        }
    
    return app


# 创建应用实例
app = create_wechat_app()

if __name__ == "__main__":
    # 直接运行时的启动代码
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.WECHAT_PORT,
        log_level="info"
    )