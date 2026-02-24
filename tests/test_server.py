#!/usr/bin/env python3
"""
测试服务器 - 验证FastAPI是否能正常工作
"""

from fastapi import FastAPI
import uvicorn

# 创建最简单的应用
app = FastAPI(title="测试服务器", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "题库系统测试服务器", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/test/db")
async def test_db():
    try:
        import sqlite3
        conn = sqlite3.connect("data/question_bank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]
        conn.close()
        return {"database": "connected", "question_count": count}
    except Exception as e:
        return {"database": "error", "error": str(e)}

if __name__ == "__main__":
    print("启动测试服务器...")
    print("访问地址: http://localhost:8000/")
    print("健康检查: http://localhost:8000/health")
    print("数据库测试: http://localhost:8000/test/db")
    print("按 Ctrl+C 停止")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")