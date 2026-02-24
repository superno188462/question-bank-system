#!/bin/bash

# MSYS2专用修复脚本
# 解决数据库列缺失和导入错误问题

echo "=========================================="
echo "  MSYS2环境问题修复脚本"
echo "=========================================="
echo ""

# 检查Python
if command -v python &> /dev/null; then
    PYTHON=python
else
    echo "错误：需要Python（命令：python）"
    echo "请确保python命令可用"
    exit 1
fi

echo "使用Python: $($PYTHON --version 2>&1)"
echo ""

# 1. 修复数据库表结构
echo "[1/3] 修复数据库表结构..."
$PYTHON -c "
import sqlite3
import os

db_file = 'data/question_bank.db'
print(f'处理数据库: {db_file}')

if not os.path.exists(db_file):
    print('创建新数据库...')
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 创建完整表结构
    cursor.execute('''
    CREATE TABLE questions (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        question_type TEXT NOT NULL,
        difficulty TEXT,
        tags TEXT,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 插入示例数据
    import uuid
    samples = [
        (str(uuid.uuid4()), 'Python中如何定义函数？', 'short_answer', 'easy', 'python,function', '{}'),
        (str(uuid.uuid4()), '什么是面向对象编程？', 'essay', 'medium', 'oop,programming', '{}'),
    ]
    
    cursor.executemany('''
    INSERT INTO questions (id, content, question_type, difficulty, tags, metadata)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', samples)
    
    conn.commit()
    print(f'创建新数据库，包含 {len(samples)} 个题目')
    
else:
    print('修复现有数据库...')
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute(\"PRAGMA table_info(questions)\")
    columns = [col[1] for col in cursor.fetchall()]
    print(f'当前列: {columns}')
    
    # 添加缺失的列
    required_columns = ['difficulty', 'tags', 'metadata', 'created_at', 'updated_at']
    for col in required_columns:
        if col not in columns:
            print(f'添加列: {col}')
            if col in ['created_at', 'updated_at']:
                cursor.execute(f\"ALTER TABLE questions ADD COLUMN {col} TIMESTAMP DEFAULT CURRENT_TIMESTAMP\")
            else:
                cursor.execute(f\"ALTER TABLE questions ADD COLUMN {col} TEXT\")
    
    conn.commit()
    print('表结构修复完成')

conn.close()
print('✅ 数据库修复完成')
"

# 2. 创建简化版的web_interface（避免导入错误）
echo ""
echo "[2/3] 创建简化版Web接口..."
cat > simple_web_interface.py << 'PYTHON'
"""
简化版Web接口
避免复杂的导入错误
"""

from fastapi import FastAPI
import sqlite3
import json

app = FastAPI(title="题库系统简化版", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "题库系统简化版",
        "status": "running",
        "version": "1.0.0",
        "database": "data/question_bank.db"
    }

@app.get("/questions")
async def get_questions(limit: int = 10):
    """获取题目列表"""
    try:
        conn = sqlite3.connect("data/question_bank.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, content, question_type, difficulty FROM questions LIMIT {limit}")
        questions = []
        for row in cursor.fetchall():
            questions.append({
                "id": row[0],
                "content": row[1],
                "type": row[2],
                "difficulty": row[3]
            })
        conn.close()
        return {"questions": questions, "count": len(questions)}
    except Exception as e:
        return {"error": str(e), "questions": []}

@app.post("/questions")
async def add_question(content: str, question_type: str = "short_answer", difficulty: str = "medium"):
    """添加题目"""
    try:
        import uuid
        conn = sqlite3.connect("data/question_bank.db")
        cursor = conn.cursor()
        
        question_id = str(uuid.uuid4())
        cursor.execute('''
        INSERT INTO questions (id, content, question_type, difficulty)
        VALUES (?, ?, ?, ?)
        ''', (question_id, content, question_type, difficulty))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "id": question_id, "message": "题目添加成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/health")
async def health():
    """健康检查"""
    try:
        conn = sqlite3.connect("data/question_bank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]
        conn.close()
        return {"status": "healthy", "question_count": count}
    except:
        return {"status": "unhealthy", "error": "数据库连接失败"}

if __name__ == "__main__":
    import uvicorn
    print("启动简化版服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYTHON

echo "✅ 简化版Web接口创建完成"

# 3. 启动服务器选项
echo ""
echo "[3/3] 启动选项..."
echo ""
echo "选择启动方式:"
echo "1. 启动简化版服务器（推荐，避免导入错误）"
echo "2. 尝试启动原版服务器"
echo "3. 仅测试数据库"
echo "4. 退出"
echo ""

read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "启动简化版服务器..."
        $PYTHON simple_web_interface.py
        ;;
    2)
        echo "尝试启动原版服务器..."
        $PYTHON -m uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000 --reload
        ;;
    3)
        echo "测试数据库..."
        $PYTHON -c "
import sqlite3
conn = sqlite3.connect('data/question_bank.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM questions')
count = cursor.fetchone()[0]
print(f'数据库中有 {count} 个题目')
cursor.execute('PRAGMA table_info(questions)')
print('表结构:')
for col in cursor.fetchall():
    print(f'  {col[1]} ({col[2]})')
conn.close()
"
        ;;
    4)
        echo "退出"
        ;;
    *)
        echo "无效选择"
        ;;
esac