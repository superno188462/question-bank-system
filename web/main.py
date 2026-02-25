"""
Web入口主文件

启动FastAPI服务器，提供Web管理界面和RESTful API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# 添加项目根目录到Python路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.api import categories, tags, questions
from web.config import settings


def create_web_app() -> FastAPI:
    """
    创建Web应用实例
    
    返回:
        FastAPI: 配置好的Web应用实例
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="题库管理系统 - Web管理界面",
        version="2.0",
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册API路由
    app.include_router(categories.router, prefix="/api", tags=["分类管理"])
    app.include_router(tags.router, prefix="/api", tags=["标签管理"])
    app.include_router(questions.router, prefix="/api", tags=["题目管理"])
    
    # 挂载静态文件
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # 根路径重定向到前端
    @app.get("/")
    async def root():
        return {
            "message": "题库管理系统 Web入口",
            "docs": settings.DOCS_URL,
            "frontend": "/static/index.html",
            "api_base": "/api"
        }
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "web"}
    
    return app


# 创建Web应用实例
app = create_web_app()

if __name__ == "__main__":
    import uvicorn
    
    print(f"🚀 启动Web服务器...")
    print(f"📡 地址: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API文档: http://{settings.HOST}:{settings.PORT}{settings.DOCS_URL}")
    print(f"🌐 前端界面: http://{settings.HOST}:{settings.PORT}/static/index.html")
    
    uvicorn.run(
        "web.main:app",  # 改为导入字符串形式
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )