#!/bin/bash

# 题库系统快速启动脚本
# 在其他电脑上部署和使用的简化脚本
# 支持Linux、macOS、Windows MSYS2/Cygwin

set -e  # 遇到错误时退出

echo "=========================================="
echo "  题库系统快速部署脚本"
echo "=========================================="

# 检测操作系统环境
detect_environment() {
    print_info "检测运行环境..."
    
    # 检查是否是MSYS2/Cygwin
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        IS_MSYS=true
        print_info "检测到MSYS2/Cygwin环境"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        IS_MACOS=true
        print_info "检测到macOS环境"
    else
        IS_LINUX=true
        print_info "检测到Linux环境"
    fi
    
    # 检查是否在Windows上
    if [[ -f "/proc/version" ]] && grep -qi "microsoft" /proc/version; then
        IS_WSL=true
        print_info "检测到WSL环境"
    fi
}

# 颜色定义（MSYS2可能不支持，添加检查）
setup_colors() {
    # 检查终端是否支持颜色
    if [[ -t 1 ]] && [[ "$TERM" != "dumb" ]]; then
        RED='\033[0;31m'
        GREEN='\033[0;32m'
        YELLOW='\033[1;33m'
        NC='\033[0m' # No Color
        HAS_COLORS=true
    else
        HAS_COLORS=false
    fi
}

# 函数：打印带颜色的消息
print_info() {
    if [ "$HAS_COLORS" = true ]; then
        echo -e "${GREEN}[INFO]${NC} $1"
    else
        echo "[INFO] $1"
    fi
}

print_warning() {
    if [ "$HAS_COLORS" = true ]; then
        echo -e "${YELLOW}[WARNING]${NC} $1"
    else
        echo "[WARNING] $1"
    fi
}

print_error() {
    if [ "$HAS_COLORS" = true ]; then
        echo -e "${RED}[ERROR]${NC} $1"
    else
        echo "[ERROR] $1"
    fi
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."
    
    # 只使用python命令
    PYTHON_CMD="python"
    
    if ! command -v $PYTHON_CMD &> /dev/null; then
        print_error "未找到Python命令：python"
        echo "请确保python命令可用"
        echo "Windows用户: 安装Python时勾选'Add Python to PATH'"
        echo "或创建别名: alias python=python3"
        exit 1
    fi
    
    # 获取Python版本
    if $PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" &> /dev/null; then
        PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_info "找到Python $PYTHON_VERSION (命令: $PYTHON_CMD)"
    else
        print_error "无法获取Python版本，命令: $PYTHON_CMD"
        exit 1
    fi
    
    # 检查版本是否>=3.8
    MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
    MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
    
    if [ $MAJOR -lt 3 ] || [ $MAJOR -eq 3 -a $MINOR -lt 8 ]; then
        print_error "需要Python 3.8+，当前版本: $PYTHON_VERSION"
        exit 1
    fi
}

# 安装uv（推荐）
install_uv() {
    print_info "安装uv包管理器..."
    if command -v uv &> /dev/null; then
        print_info "uv已安装"
        return 0
    fi
    
    # 尝试安装uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    if [ $? -eq 0 ]; then
        print_info "uv安装成功"
        # 重新加载PATH
        if [ -f "$HOME/.cargo/bin/uv" ]; then
            export PATH="$HOME/.cargo/bin:$PATH"
        fi
        return 0
    else
        print_warning "uv安装失败，将使用传统pip"
        return 1
    fi
}

# 激活虚拟环境
activate_venv() {
    print_info "激活虚拟环境..."
    
    # 尝试不同的激活脚本位置
    if [ -f ".venv/bin/activate" ]; then
        # Linux/macOS
        source .venv/bin/activate
    elif [ -f ".venv/Scripts/activate" ]; then
        # Windows
        source .venv/Scripts/activate
    elif [ -f ".venv/Scripts/activate.bat" ] && [ "$IS_MSYS" = true ]; then
        # MSYS2 with .bat file
        print_info "在MSYS2中检测到.bat激活脚本，使用替代方法"
        # 在MSYS2中，我们直接设置PATH
        export PATH="$(pwd)/.venv/Scripts:$PATH"
    else
        print_error "找不到虚拟环境激活脚本"
        return 1
    fi
    
    # 验证激活
    if command -v python &> /dev/null && [[ $(python -c "import sys; print(sys.prefix)") == *".venv"* ]]; then
        print_info "虚拟环境激活成功"
        return 0
    else
        print_warning "虚拟环境可能未正确激活，尝试继续..."
        return 0
    fi
}

# 使用uv安装依赖
install_with_uv() {
    print_info "使用uv安装依赖..."
    
    # 创建虚拟环境
    uv venv
    
    # 激活虚拟环境
    activate_venv
    
    # 安装依赖
    uv pip install -e ".[dev]"
    
    if [ $? -eq 0 ]; then
        print_info "依赖安装成功"
        return 0
    else
        print_error "依赖安装失败"
        return 1
    fi
}

# 使用pip安装依赖
install_with_pip() {
    print_info "使用pip安装依赖..."
    
    # 创建虚拟环境
    $PYTHON_CMD -m venv .venv
    
    # 激活虚拟环境
    activate_venv
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖（使用国内镜像加速）
    print_info "安装依赖（使用清华镜像加速）..."
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    if [ $? -eq 0 ]; then
        print_info "主依赖安装成功"
    else
        print_warning "主依赖安装失败，尝试不使用镜像..."
        pip install -r requirements.txt
    fi
    
    # 安装开发依赖
    pip install -r requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    if [ $? -eq 0 ]; then
        print_info "依赖安装成功"
        return 0
    else
        print_warning "开发依赖安装失败，继续..."
        return 0
    fi
}

# 初始化数据库
initialize_database() {
    print_info "初始化数据库..."
    
    # 先运行配置脚本（不检查错误）
    if [ -f "setup_uv.py" ]; then
        print_info "运行配置脚本..."
        $PYTHON_CMD setup_uv.py 2>/dev/null || print_warning "配置脚本完成（可能有警告）"
    fi
    
    # 使用专门的数据库初始化脚本
    if [ -f "init_database.py" ]; then
        print_info "使用数据库初始化脚本..."
        echo "1" | $PYTHON_CMD init_database.py > /tmp/db_init.log 2>&1
        
        if grep -q "数据库初始化成功" /tmp/db_init.log || grep -q "数据库初始化完成" /tmp/db_init.log; then
            print_info "数据库初始化成功"
        else
            print_warning "数据库初始化可能有警告，继续..."
        fi
    else
        print_info "手动初始化数据库..."
        $PYTHON_CMD -c "
import sqlite3
import json
import uuid
from datetime import datetime

print('创建数据库...')
conn = sqlite3.connect('data/question_bank.db')
cursor = conn.cursor()

# 创建题目表
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
sample_questions = [
    (str(uuid.uuid4()), 'Python中如何定义函数？', 'short_answer', 'easy', 'python,function', 
     json.dumps({'category': 'programming', 'language': 'python'})),
    (str(uuid.uuid4()), '什么是MVC设计模式？', 'essay', 'medium', 'design_pattern,mvc',
     json.dumps({'category': 'software_design', 'framework': 'general'})),
]

for q in sample_questions:
    cursor.execute('''
    INSERT OR IGNORE INTO questions (id, content, question_type, difficulty, tags, metadata)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', q)

conn.commit()

# 检查数据
cursor.execute('SELECT COUNT(*) FROM questions')
count = cursor.fetchone()[0]
print(f'✅ 创建数据库成功，包含 {count} 个示例题目')

conn.close()
"
    fi
    
    # 检查数据库文件
    if [ -f "data/question_bank.db" ]; then
        print_info "数据库文件创建成功: data/question_bank.db"
        # 显示文件大小
        if command -v stat &> /dev/null; then
            FILESIZE=$(stat -c%s data/question_bank.db 2>/dev/null || stat -f%z data/question_bank.db 2>/dev/null || echo "unknown")
            print_info "文件大小: ${FILESIZE}字节"
        fi
        return 0
    else
        print_error "数据库文件创建失败"
        print_info "尝试创建空数据库..."
        $PYTHON_CMD -c "import sqlite3; conn = sqlite3.connect('data/question_bank.db'); conn.close(); print('创建空数据库文件')"
        
        if [ -f "data/question_bank.db" ]; then
            print_info "空数据库文件创建成功"
            return 0
        else
            return 1
        fi
    fi
}

# 启动开发服务器
start_development_server() {
    print_info "启动开发服务器..."
    
    # 给启动脚本添加执行权限
    if [ -f "start_development.sh" ]; then
        chmod +x start_development.sh
        ./start_development.sh &
    else
        # 手动启动
        uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000 --reload &
    fi
    
    SERVER_PID=$!
    print_info "服务器启动中 (PID: $SERVER_PID)..."
    
    # 等待服务器启动
    sleep 3
    
    # 测试服务器是否运行
    if curl -s http://localhost:8000/ > /dev/null; then
        print_info "服务器启动成功!"
        return 0
    else
        print_error "服务器启动失败"
        return 1
    fi
}

# 显示访问信息
show_access_info() {
    echo ""
    echo "=========================================="
    echo "       部署完成！访问信息如下"
    echo "=========================================="
    echo ""
    
    # 获取IP地址
    if command -v ip &> /dev/null; then
        IP_ADDR=$(ip addr show | grep -oP 'inet \K[\d.]+' | grep -v '127.0.0.1' | head -1)
    elif command -v ifconfig &> /dev/null; then
        IP_ADDR=$(ifconfig | grep -oP 'inet \K[\d.]+' | grep -v '127.0.0.1' | head -1)
    else
        IP_ADDR="<你的服务器IP>"
    fi
    
    echo "🌐 本地访问:"
    echo "   http://localhost:8000/"
    echo "   http://localhost:8000/docs (API文档)"
    echo ""
    
    echo "📱 局域网访问:"
    echo "   http://${IP_ADDR}:8000/"
    echo ""
    
    echo "🔧 管理命令:"
    echo "   停止服务器: kill $SERVER_PID"
    echo "   查看日志:   tail -f nohup.out"
    echo ""
    
    echo "📚 快速测试:"
    echo "   测试API:    curl http://localhost:8000/"
    echo "   测试搜索:   curl 'http://localhost:8000/api/questions/search?query=python'"
    echo ""
    
    echo "💡 提示:"
    echo "   1. 确保防火墙开放8000端口"
    echo "   2. 如需外网访问，需要配置公网IP或内网穿透"
    echo "   3. 详细文档请查看 README.md 和 DEPLOYMENT_GUIDE.md"
    echo ""
}

# 主函数
main() {
    echo ""
    
    # 初始化
    setup_colors
    detect_environment
    
    print_info "开始部署题库系统..."
    echo ""
    
    # 步骤1: 检查Python
    check_python
    
    # 步骤2: 安装uv或使用pip
    if install_uv; then
        if ! install_with_uv; then
            print_warning "uv安装失败，尝试使用pip..."
            install_with_pip
        fi
    else
        install_with_pip
    fi
    
    # 步骤3: 初始化数据库
    initialize_database
    
    # 步骤4: 启动服务器
    if start_development_server; then
        show_access_info
        
        # 保持脚本运行
        echo "按 Ctrl+C 停止服务器"
        wait $SERVER_PID
    else
        print_error "部署失败，请检查错误信息"
        exit 1
    fi
}

# 运行主函数
main "$@"