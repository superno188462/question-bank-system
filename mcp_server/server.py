"""
MCP入口服务器

通过Model Context Protocol提供AI助手访问题库系统的能力
"""

import asyncio
from typing import Any
import mcp
from mcp.server import Server
from mcp.server.models import InitializationOptions
from fastapi import FastAPI
import uvicorn

from shared.config import config
from core.services import CategoryService, TagService, QuestionService
from core.database.repositories import category_repo, tag_repo, question_repo


class QuestionBankMCPServer:
    """题库系统MCP服务器"""
    
    def __init__(self):
        # 创建服务实例
        self.category_service = CategoryService(category_repo)
        self.tag_service = TagService(tag_repo)
        self.question_service = QuestionService(question_repo, category_repo, tag_repo)
        
        # 创建MCP服务器
        self.server = Server("question-bank-system")
    
    async def initialize(self):
        """初始化MCP服务器"""
        # 注册工具
        await self.server.tool.list_tools()
        
        # 添加搜索题目工具
        @self.server.tool()
        async def search_questions(keyword: str) -> str:
            """搜索题目
            
            Args:
                keyword: 搜索关键词
                
            Returns:
                str: 搜索结果
            """
            questions = self.question_service.search_questions(keyword)
            if not questions:
                return f"没有找到包含 '{keyword}' 的题目"
            
            result = f"找到 {len(questions)} 个相关题目:\n\n"
            for q in questions:
                result += f"题目ID: {q.id}\n"
                result += f"内容: {q.content[:100]}...\n"
                result += f"分类: {q.category_name}\n"
                result += f"难度: {q.difficulty}\n"
                result += "-" * 50 + "\n"
            
            return result
        
        # 添加获取分类工具
        @self.server.tool()
        async def get_categories() -> str:
            """获取所有题目分类
            
            Returns:
                str: 分类列表
            """
            categories = self.category_service.get_all_categories()
            if not categories:
                return "暂无分类"
            
            result = f"共有 {len(categories)} 个分类:\n\n"
            for cat in categories:
                result += f"分类ID: {cat.id}\n"
                result += f"名称: {cat.name}\n"
                result += f"描述: {cat.description}\n"
                result += "-" * 50 + "\n"
            
            return result
        
        # 添加添加题目工具
        @self.server.tool()
        async def add_question(
            content: str,
            answer: str,
            category_id: str = None,
            difficulty: str = "medium"
        ) -> str:
            """添加新题目
            
            Args:
                content: 题目内容
                answer: 正确答案
                category_id: 分类ID（可选）
                difficulty: 难度（easy/medium/hard）
                
            Returns:
                str: 添加结果
            """
            try:
                question_data = {
                    "content": content,
                    "answer": answer,
                    "difficulty": difficulty,
                    "category_id": category_id
                }
                
                result = self.question_service.create_question(question_data)
                return f"✅ 题目添加成功！\n题目ID: {result['id']}"
            except Exception as e:
                return f"❌ 添加失败: {str(e)}"


# 创建FastAPI应用
app = FastAPI(
    title="题库系统 - MCP入口",
    description="通过MCP协议提供AI助手访问题库系统的能力",
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 创建MCP服务器实例
mcp_server = QuestionBankMCPServer()

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化MCP服务器"""
    await mcp_server.initialize()

@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "question-bank-mcp",
        "version": "2.0",
        "description": "题库系统MCP入口",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "mcp"}

@app.get("/shutdown")
async def shutdown():
    """关闭服务器（开发用）"""
    import os
    import signal
    os.kill(os.getpid(), signal.SIGINT)
    return {"message": "正在关闭服务器..."}


if __name__ == "__main__":
    # 直接运行时的启动代码
    uvicorn.run(
        app,
        host=config.MCP_HOST,
        port=config.MCP_PORT,
        log_level="info"
    )