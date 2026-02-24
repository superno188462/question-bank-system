#!/bin/bash

# UV优先部署脚本
# 使用uv pip管理依赖，避免污染全局Python环境

set -e

echo "=========================================="
echo "  题库系统UV优先部署"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. 检查uv是否安装
echo "[1/5] 检查uv..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>/dev/null || echo "未知版本")
    print_success "找到uv: $UV_VERSION"
else
    print_error "未找到uv，请先安装uv"
    echo ""
    echo "安装方法:"
    echo "1. Linux/macOS: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "2. Windows PowerShell: irm https://astral.sh/uv/install.ps1 | iex"
    echo "3. 或从 https://github.com/astral-sh/uv 下载"
    echo ""
    echo "uv优势:"
    echo "  - 比pip快10-100倍"
    echo "  - 更好的依赖冲突解决"
    echo "  - 内置虚拟环境管理"
    echo "  - 跨平台一致体验"
    exit 1
fi

# 2. 检查Python
echo "[2/5] 检查Python..."
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    print_warning "使用python3命令（建议创建别名: alias python=python3）"
else
    print_error "未找到Python"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
print_success "Python版本: $PYTHON_VERSION"

# 3. 创建虚拟环境（使用uv）
echo "[3/5] 创建虚拟环境..."
if [ ! -d ".venv" ]; then
    uv venv .venv
    print_success "创建虚拟环境: .venv/"
else
    print_warning "虚拟环境已存在: .venv/"
fi

# 激活虚拟环境
if [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
    print_success "激活虚拟环境 (Windows)"
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    print_success "激活虚拟环境 (Linux/macOS)"
else
    print_error "无法激活虚拟环境"
    exit 1
fi

# 4. 安装依赖（使用uv pip）
echo "[4/5] 安装依赖..."
if [ -f "requirements.txt" ]; then
    print_info "从requirements.txt安装..."
    uv pip install -r requirements.txt
else
    print_info "安装核心依赖..."
    uv pip install fastapi uvicorn
fi

if [ $? -eq 0 ]; then
    print_success "依赖安装完成"
else
    print_error "依赖安装失败"
    exit 1
fi

# 5. 创建数据库
echo "[5/5] 创建数据库..."
$PYTHON_CMD -c "
import sqlite3
import json

conn = sqlite3.connect('data/question_bank.db')
cursor = conn.cursor()

# 创建完整表结构
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

# 创建索引
try:
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_difficulty ON questions(difficulty)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_question_type ON questions(question_type)')
except:
    pass

# 插入示例数据（使用正确JSON格式）
import uuid
samples = [
    (str(uuid.uuid4()), 'Python中如何定义函数？', 'short_answer', 'easy', '[\"python\", \"function\"]', '{\"category\": \"programming\"}'),
    (str(uuid.uuid4()), '什么是HTTP协议？', 'multiple_choice', 'easy', '[\"web\", \"http\"]', '{\"category\": \"networking\"}'),
    (str(uuid.uuid4()), '解释MVC设计模式', 'essay', 'medium', '[\"design_pattern\", \"mvc\"]', '{\"category\": \"software_design\"}')
]

cursor.executemany('''
INSERT OR IGNORE INTO questions (id, content, question_type, difficulty, tags, metadata)
VALUES (?, ?, ?, ?, ?, ?)
''', samples)

conn.commit()
cursor.execute('SELECT COUNT(*) FROM questions')
count = cursor.fetchone()[0]
conn.close()

print(f'数据库创建完成，包含 {count} 个题目')
print('所有数据使用标准JSON格式')
"

if [ $? -eq 0 ]; then
    print_success "数据库创建完成"
else
    print_error "数据库创建失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "✅ 虚拟环境: .venv/ (使用uv管理)"
echo "✅ 数据库: data/question_bank.db"
echo "✅ 依赖: 使用uv pip安装，避免全局污染"
echo ""
echo "🚀 启动服务器:"
echo "  python -m uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "🌐 访问地址:"
echo "  http://localhost:8000/"
echo "  http://localhost:8000/docs (API文档)"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""
echo "是否立即启动服务器？ (y/N): "
read -n 1 choice
echo ""

if [[ $choice == "y" || $choice == "Y" ]]; then
    echo "启动服务器..."
    $PYTHON_CMD -m uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000 --reload
else
    echo "手动启动命令:"
    echo "  python -m uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000 --reload"
fi