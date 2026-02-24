#!/bin/bash

# MSYS2专用部署脚本
# 在Windows MSYS2 bash中运行

echo "=========================================="
echo "  题库系统MSYS2部署脚本"
echo "=========================================="
echo ""

# 检查是否在MSYS2中
if [[ "$OSTYPE" != "msys" ]] && [[ "$OSTYPE" != "cygwin" ]]; then
    echo "错误：这不是MSYS2环境"
    echo "请在MSYS2终端中运行此脚本"
    exit 1
fi

echo "[1/6] 检查Python..."
if ! command -v python &> /dev/null; then
    echo "错误：未找到Python命令：python"
    echo "请安装Python for Windows: https://www.python.org/downloads/"
    echo "安装时请勾选 'Add Python to PATH'"
    echo "或在MSYS2中创建别名: alias python=python3"
    exit 1
fi

PYTHON_CMD="python"
echo "找到Python: $($PYTHON_CMD --version)"

echo ""
echo "[2/6] 创建虚拟环境..."
$PYTHON_CMD -m venv .venv

echo ""
echo "[3/6] 激活虚拟环境..."
# MSYS2特殊处理
if [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
elif [ -f ".venv/Scripts/activate.bat" ]; then
    # 对于.bat文件，我们直接设置PATH
    export PATH="$(pwd)/.venv/Scripts:$PATH"
    echo "已设置PATH: .venv/Scripts"
else
    echo "警告：找不到激活脚本，尝试继续..."
fi

echo ""
echo "[4/6] 安装依赖..."
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if [ $? -ne 0 ]; then
    echo "警告：使用镜像安装失败，尝试直接安装..."
    pip install -r requirements.txt
fi

echo ""
echo "[5/6] 初始化数据库..."
# 先运行配置脚本（可能失败但继续）
python setup_uv.py 2>/dev/null || echo "配置脚本完成"

# 使用专门的数据库初始化脚本
if [ -f "init_database.py" ]; then
    echo "使用 init_database.py 初始化数据库..."
    python init_database.py <<< "1"  # 自动选择选项1
else
    echo "创建数据库初始化脚本..."
    python -c "
import sqlite3
conn = sqlite3.connect('data/question_bank.db')
cursor = conn.cursor()

# 创建基本表
cursor.execute('''
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    question_type TEXT NOT NULL,
    difficulty TEXT,
    tags TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 插入示例数据
cursor.execute(\"\"\"
INSERT OR IGNORE INTO questions (id, content, question_type, difficulty, tags)
VALUES ('sample1', 'Python中如何定义函数？', 'short_answer', 'easy', 'python,function')
\"\"\")

conn.commit()
conn.close()
print('✅ 数据库初始化完成')
"
fi

# 检查数据库文件
if [ -f "data/question_bank.db" ]; then
    echo "✅ 数据库文件创建成功: data/question_bank.db"
    # 显示文件大小
    if command -v stat &> /dev/null; then
        echo "   文件大小: $(stat -c%s data/question_bank.db) 字节"
    fi
else
    echo "❌ 数据库文件创建失败"
    echo "尝试手动创建..."
    python -c "import sqlite3; conn = sqlite3.connect('data/question_bank.db'); conn.close(); print('创建空数据库文件')"
fi

echo ""
echo "[6/6] 启动服务器..."
echo ""
echo "=========================================="
echo "  部署完成！启动服务器..."
echo "=========================================="
echo ""
echo "访问地址: http://localhost:8000/"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
python -m uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000 --reload