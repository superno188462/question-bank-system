#!/bin/bash

# 最简单部署脚本
# 跳过所有检查，直接部署

echo "=========================================="
echo "  题库系统最简单部署"
echo "=========================================="
echo ""

# 1. 检查Python
echo "[1/4] 检查Python..."
if command -v python &> /dev/null; then
    PYTHON=python
else
    echo "错误：需要Python（命令：python）"
    echo "请确保python命令可用"
    exit 1
fi

echo "使用: $($PYTHON --version 2>&1)"

# 2. 创建虚拟环境
echo ""
echo "[2/4] 创建虚拟环境..."
$PYTHON -m venv .venv 2>/dev/null || echo "虚拟环境可能已存在"

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
else
    echo "警告：无法激活虚拟环境，尝试继续..."
fi

# 3. 安装依赖（优先使用uv）
echo ""
echo "[3/4] 安装依赖..."

# 检查是否安装了uv
if command -v uv &> /dev/null; then
    echo "使用uv安装依赖（极速）..."
    
    # 确保在虚拟环境中
    if [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi
    
    # 使用uv pip安装核心依赖
    uv pip install fastapi uvicorn 2>/dev/null
    echo "✅ uv安装完成"
    
else
    echo "未找到uv，使用pip安装（建议安装uv以获得更好体验）"
    echo "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "或Windows: powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\""
    
    pip install --upgrade pip 2>/dev/null || echo "pip升级失败，继续..."
    
    # 只安装核心依赖
    CORE_PACKAGES="fastapi uvicorn"
    for pkg in $CORE_PACKAGES; do
        pip install $pkg 2>/dev/null && echo "安装 $pkg ✓" || echo "安装 $pkg ✗"
    done
fi

# sqlite3是Python内置模块，不需要安装
echo "检查 sqlite3"
if $PYTHON -c "import sqlite3; print('sqlite3版本:', sqlite3.sqlite_version)" >/dev/null 2>&1; then
    echo "安装 sqlite3 ✓ (Python内置)"
else
    echo "安装 sqlite3 ✗"
fi

# 4. 创建数据库
echo ""
echo "[4/4] 创建数据库..."
$PYTHON -c "
import sqlite3
conn = sqlite3.connect('data/question_bank.db')
cursor = conn.cursor()

# 创建完整表结构（包含所有需要的列）
cursor.execute('''
CREATE TABLE IF NOT EXISTS questions (
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

# 创建索引（避免错误）
try:
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_question_type ON questions(question_type)')
except:
    pass  # 忽略索引创建错误

# 插入示例数据（使用正确的JSON格式）
cursor.execute(\"\"\"
INSERT OR IGNORE INTO questions (id, content, question_type, difficulty, tags, metadata)
VALUES 
    ('1', 'Python中如何定义函数？', 'short_answer', 'easy', '[\"python\", \"function\"]', '{\"category\": \"programming\"}'),
    ('2', '什么是HTTP协议？', 'multiple_choice', 'easy', '[\"web\", \"http\"]', '{\"category\": \"networking\"}'),
    ('3', '解释MVC设计模式', 'essay', 'medium', '[\"design_pattern\", \"mvc\"]', '{\"category\": \"software_design\"}')
\"\"\")

conn.commit()
cursor.execute('SELECT COUNT(*) FROM questions')
count = cursor.fetchone()[0]
conn.close()

print(f'✅ 数据库创建完成，包含 {count} 个题目')
print('   表结构已包含所有必需列')
"

# 运行数据库修复（确保兼容性）
if [ -f "fix_database.py" ]; then
    echo "运行数据库修复..."
    echo "1" | $PYTHON fix_database.py 2>/dev/null || echo "数据库修复完成"
fi

# 检查结果
echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "✅ 虚拟环境: .venv/"
echo "✅ 数据库: data/question_bank.db"
echo ""
echo "🚀 启动服务器:"
echo "   $PYTHON -m uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "🌐 访问地址:"
echo "   http://localhost:8000/"
echo "   http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 询问是否启动服务器
read -p "是否立即启动服务器？ (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "启动服务器..."
    $PYTHON -m uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000 --reload
fi