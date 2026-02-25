"""
MCP入口服务器
"""

from fastapi import FastAPI
import uvicorn

# 添加项目根目录到Python路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import config


# 创建FastAPI应用
app = FastAPI(
    title="题库系统 - MCP入口",
    description="通过MCP协议提供AI助手访问题库系统的能力",
    version="2.0",
    docs_url="/docs",
)

@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "question-bank-mcp",
        "version": "2.0",
        "description": "题库系统MCP入口",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "mcp"}


if __name__ == "__main__":
    # 直接运行时的启动代码
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.MCP_PORT,
        log_level="info"
    )