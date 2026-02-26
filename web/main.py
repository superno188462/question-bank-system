"""
Web入口主文件
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.api import categories, tags, questions
from web.config import settings

# 获取web目录路径
WEB_DIR = os.path.dirname(os.path.abspath(__file__))


def create_web_app() -> FastAPI:
    """
    创建Web应用实例
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="题库管理系统 - Web管理界面",
        version="2.0",
        docs_url=settings.DOCS_URL,
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 挂载静态文件
    app.mount("/static", StaticFiles(directory=os.path.join(WEB_DIR, "static")), name="static")
    
    # 配置模板
    templates = Jinja2Templates(directory=os.path.join(WEB_DIR, "templates"))
    
    # 注册API路由
    app.include_router(categories.router, prefix="/api", tags=["分类管理"])
    app.include_router(tags.router, prefix="/api", tags=["标签管理"])
    app.include_router(questions.router, prefix="/api", tags=["题目管理"])
    
    # 主页 - 返回管理界面
    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
    
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
    
    uvicorn.run(
        "web.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )