"""
智能问答 API 模块

提供智能问答和预备题目管理功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import os
import json

router = APIRouter(prefix="/qa", tags=["智能问答"])

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data")
PENDING_FILE = os.path.join(DATA_DIR, "pending_questions.json")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)


# ============ 数据模型 ============

class QuestionAsk(BaseModel):
    question: str


class PendingQuestion(BaseModel):
    id: str
    content: str
    answer: str
    source: str = "智能问答"
    created_at: str


# ============ 数据存取 ============

def load_pending_questions() -> List[dict]:
    """加载预备题目"""
    if not os.path.exists(PENDING_FILE):
        return []
    
    try:
        with open(PENDING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


def save_pending_questions(questions: List[dict]):
    """保存预备题目"""
    with open(PENDING_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)


def add_pending_question(content: str, answer: str) -> PendingQuestion:
    """添加预备题目"""
    question = {
        "id": str(uuid.uuid4()),
        "content": content,
        "answer": answer,
        "source": "智能问答",
        "created_at": datetime.now().isoformat()
    }
    
    questions = load_pending_questions()
    questions.append(question)
    save_pending_questions(questions)
    
    return PendingQuestion(**question)


# ============ API 端点 ============

@router.post("/ask")
async def ask_question(data: QuestionAsk):
    """
    智能问答
    
    接收用户问题，从题库中匹配相关题目并返回答案
    """
    question_text = data.question
    
    # TODO: 实现真正的 AI 问答逻辑
    # 目前返回一个简单的响应
    
    # 尝试从题库中搜索相关题目
    try:
        from core.database import get_db
        from core.models import Question
        from sqlalchemy import text
        
        db = next(get_db())
        
        # 简单关键词匹配
        result = db.execute(
            text("SELECT * FROM questions WHERE content LIKE :query LIMIT 3"),
            {"query": f"%{question_text}%"}
        )
        questions = [dict(row._mapping) for row in result.fetchall()]
        
        if questions:
            # 找到相关题目
            answer = f"我找到了 {len(questions)} 道相关题目：\n\n"
            for i, q in enumerate(questions, 1):
                answer += f"{i}. {q['content']}\n"
                answer += f"   答案：{q['answer']}\n\n"
            
            return {
                "answer": answer,
                "related_questions": questions,
                "pending_question": None
            }
        else:
            # 没有找到，创建预备题目
            pending = add_pending_question(
                content=question_text,
                answer="待添加解析"
            )
            
            return {
                "answer": f"抱歉，题库中暂无相关题目。已将该问题记录为预备题目，等待管理员审核入库。",
                "related_questions": [],
                "pending_question": {
                    "id": pending.id,
                    "content": pending.content
                }
            }
            
    except Exception as e:
        # 数据库错误时返回通用响应
        return {
            "answer": f"收到您的问题：{question_text}\n\n目前题库系统正在学习中，暂时无法提供详细解答。",
            "related_questions": [],
            "pending_question": None
        }


@router.get("/pending")
async def get_pending_questions():
    """
    获取所有预备题目
    """
    questions = load_pending_questions()
    return questions


@router.get("/pending/{question_id}")
async def get_pending_question(question_id: str):
    """
    获取单个预备题目详情
    """
    questions = load_pending_questions()
    
    for q in questions:
        if q["id"] == question_id:
            return q
    
    raise HTTPException(status_code=404, detail="预备题目不存在")


@router.post("/pending/{question_id}/approve")
async def approve_pending_question(question_id: str):
    """
    批准预备题目入库
    
    将预备题目转换为正式题目
    """
    questions = load_pending_questions()
    
    # 找到预备题目
    pending_question = None
    for i, q in enumerate(questions):
        if q["id"] == question_id:
            pending_question = q
            break
    
    if not pending_question:
        raise HTTPException(status_code=404, detail="预备题目不存在")
    
    # 转换为正式题目
    try:
        from core.database import get_db
        from core.models import Question
        from sqlalchemy import text
        
        db = next(get_db())
        
        # 获取或创建默认分类
        result = db.execute(text("SELECT id FROM categories LIMIT 1"))
        row = result.fetchone()
        category_id = row[0] if row else None
        
        if not category_id:
            # 创建默认分类
            from datetime import datetime
            default_cat_id = str(uuid.uuid4())
            db.execute(
                text("""
                    INSERT INTO categories (id, name, description, created_at, updated_at)
                    VALUES (:id, :name, :description, :created_at, :updated_at)
                """),
                {
                    "id": default_cat_id,
                    "name": "未分类",
                    "description": "默认分类",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            )
            db.commit()
            category_id = default_cat_id
        
        # 创建正式题目
        question_id_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        db.execute(
            text("""
                INSERT INTO questions (id, content, options, answer, explanation, category_id, created_at, updated_at)
                VALUES (:id, :content, :options, :answer, :explanation, :category_id, :created_at, :updated_at)
            """),
            {
                "id": question_id_uuid,
                "content": pending_question["content"],
                "options": "[]",
                "answer": pending_question["answer"],
                "explanation": "待补充解析",
                "category_id": category_id,
                "created_at": now,
                "updated_at": now
            }
        )
        db.commit()
        
        # 从预备题目中删除
        questions = [q for q in questions if q["id"] != question_id]
        save_pending_questions(questions)
        
        return {"status": "success", "message": "题目已入库"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"入库失败：{str(e)}")


@router.delete("/pending/{question_id}")
async def delete_pending_question(question_id: str):
    """
    删除预备题目
    """
    questions = load_pending_questions()
    questions = [q for q in questions if q["id"] != question_id]
    save_pending_questions(questions)
    
    return {"status": "success", "message": "已删除"}
