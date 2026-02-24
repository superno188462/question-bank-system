"""
微信小程序入口服务器

为微信小程序提供优化的API接口
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from shared.config import config
from core.services import QuestionService
from core.database.repositories import question_repo, category_repo, tag_repo
from wechat.utils.wechat_auth import WeChatAuth


def create_wechat_app() -> FastAPI:
    """
    创建微信小程序应用
    
    返回:
        FastAPI: 配置好的微信小程序应用
    """
    app = FastAPI(
        title="题库管理系统 - 微信小程序入口",
        description="为微信小程序优化的API接口",
        version="1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # 配置CORS（允许微信小程序域名）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://servicewechat.com",  # 微信小程序域名
            "http://localhost:3000",      # 开发环境
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 创建服务实例
    question_service = QuestionService(question_repo, category_repo, tag_repo)
    
    # 微信认证依赖
    async def verify_wechat_token(
        authorization: Optional[str] = Header(None),
        x_wx_code: Optional[str] = Header(None)
    ):
        """
        验证微信用户身份
        
        在实际应用中，这里应该实现微信登录验证
        目前简化处理，只检查是否有认证头
        """
        if not config.WECHAT_APP_ID or not config.WECHAT_APP_SECRET:
            # 开发模式，跳过认证
            return {"user_id": "dev_user", "is_authenticated": True}
        
        if not authorization and not x_wx_code:
            raise HTTPException(
                status_code=401,
                detail="需要微信认证"
            )
        
        # 这里应该调用微信API验证code或token
        # 简化处理，返回模拟用户
        return {"user_id": "wechat_user_001", "is_authenticated": True}
    
    # 根路径
    @app.get("/")
    async def root():
        return {
            "service": "题库管理系统 - 微信小程序入口",
            "status": "运行中",
            "docs": "/docs",
            "app_id": config.WECHAT_APP_ID or "未设置"
        }
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "wechat"}
    
    # 微信登录接口
    @app.post("/api/wechat/login")
    async def wechat_login(code: str):
        """
        微信小程序登录
        
        - **code**: 微信登录code
        """
        if not config.WECHAT_APP_ID or not config.WECHAT_APP_SECRET:
            # 开发模式，返回模拟数据
            return {
                "success": True,
                "user_id": "dev_user_001",
                "session_key": "dev_session_key",
                "token": "dev_token_123456"
            }
        
        # 实际应该调用微信API
        # auth = WeChatAuth(config.WECHAT_APP_ID, config.WECHAT_APP_SECRET)
        # user_info = auth.login(code)
        
        # 简化处理
        return {
            "success": True,
            "user_id": f"wechat_user_{code[:8]}",
            "session_key": "simulated_session_key",
            "token": f"token_{code}"
        }
    
    # 获取题目列表（小程序优化版）
    @app.get("/api/questions")
    async def get_questions(
        category_id: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        user: dict = Depends(verify_wechat_token)
    ):
        """
        获取题目列表（小程序优化）
        
        - **category_id**: 分类ID（可选）
        - **page**: 页码（从1开始）
        - **limit**: 每页数量（1-20）
        """
        try:
            questions = question_service.get_questions(
                category_id=category_id,
                page=page,
                limit=min(limit, 20)  # 小程序限制每页数量
            )
            
            # 简化返回数据，适合移动端
            simplified_questions = []
            for q in questions:
                simplified = {
                    "id": q["id"],
                    "content": q["content"],
                    "options": q.get("options", []),
                    "has_explanation": bool(q.get("explanation")),
                    "category": q.get("category_name"),
                    "tags": [tag["name"] for tag in q.get("tags", [])],
                    "created_at": q["created_at"]
                }
                simplified_questions.append(simplified)
            
            return {
                "success": True,
                "data": simplified_questions,
                "page": page,
                "limit": limit,
                "total": len(simplified_questions)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "error": str(e)}
            )
    
    # 搜索题目（小程序优化版）
    @app.get("/api/questions/search")
    async def search_questions(
        keyword: str,
        page: int = 1,
        limit: int = 10,
        user: dict = Depends(verify_wechat_token)
    ):
        """
        搜索题目
        
        - **keyword**: 搜索关键词
        - **page**: 页码
        - **limit**: 每页数量
        """
        try:
            questions = question_service.search_questions(keyword, page, limit)
            
            simplified_questions = []
            for q in questions:
                simplified = {
                    "id": q["id"],
                    "content": q["content"][:100] + "..." if len(q["content"]) > 100 else q["content"],
                    "has_explanation": bool(q.get("explanation")),
                    "category": q.get("category_name"),
                    "match_score": len(keyword) / len(q["content"]) if keyword else 0
                }
                simplified_questions.append(simplified)
            
            return {
                "success": True,
                "data": simplified_questions,
                "keyword": keyword,
                "page": page,
                "total": len(simplified_questions)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "error": str(e)}
            )
    
    # 获取题目详情（不含答案，用于练习）
    @app.get("/api/questions/{question_id}/practice")
    async def get_question_for_practice(
        question_id: str,
        user: dict = Depends(verify_wechat_token)
    ):
        """
        获取题目详情（练习模式，不含答案）
        
        - **question_id**: 题目ID
        """
        question = question_service.get_question(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="题目不存在")
        
        # 练习模式，隐藏答案
        practice_question = {
            "id": question["id"],
            "content": question["content"],
            "options": question.get("options", []),
            "explanation": None,  # 练习时不显示解析
            "category": question.get("category_name"),
            "tags": [tag["name"] for tag in question.get("tags", [])],
            "has_answer": bool(question.get("answer")),
            "is_multiple_choice": len(question.get("options", [])) > 0
        }
        
        return {"success": True, "data": practice_question}
    
    # 提交答案
    @app.post("/api/questions/{question_id}/submit")
    async def submit_answer(
        question_id: str,
        answer: str,
        user: dict = Depends(verify_wechat_token)
    ):
        """
        提交题目答案
        
        - **question_id**: 题目ID
        - **answer**: 用户答案
        """
        question = question_service.get_question(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="题目不存在")
        
        correct_answer = question.get("answer", "")
        is_correct = answer.strip() == correct_answer.strip()
        
        result = {
            "success": True,
            "is_correct": is_correct,
            "correct_answer": correct_answer if not is_correct else None,
            "explanation": question.get("explanation", "") if is_correct else None,
            "user_answer": answer
        }
        
        # 这里可以记录用户的答题历史
        # user_id = user["user_id"]
        # record_answer(user_id, question_id, answer, is_correct)
        
        return result
    
    return app


# 创建应用实例
app = create_wechat_app()


if __name__ == "__main__":
    import uvicorn
    
    print(f"📱 启动微信小程序服务器...")
    print(f"📡 地址: http://{config.WECHAT_HOST}:{config.WECHAT_PORT}")
    print(f"📚 API文档: http://{config.WECHAT_HOST}:{config.WECHAT_PORT}/docs")
    
    if not config.WECHAT_APP_ID or not config.WECHAT_APP_SECRET:
        print("⚠️  微信小程序配置未设置，运行在开发模式")
        print("   设置环境变量: WECHAT_APP_ID, WECHAT_APP_SECRET")
    
    uvicorn.run(
        "wechat.server:app",
        host=config.WECHAT_HOST,
        port=config.WECHAT_PORT,
        reload=config.DEBUG,
        log_level="info"
    )