#!/bin/bash
# 快速验证脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 快速验证题库系统"
echo "项目目录: $PROJECT_ROOT"
echo ""

# 1. 检查项目结构
print_info "1. 检查项目结构..."
required_dirs=("config" "core" "data" "mcp_server" "web" "wechat" "shared" "test")
required_files=("README.md" "run.sh" "start.py" "config/requirements.txt" "web/main.py")

all_good=true

for dir in "${required_dirs[@]}"; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        echo "  ✅ 目录存在: $dir"
    else
        echo "  ❌ 目录不存在: $dir"
        all_good=false
    fi
done

for file in "${required_files[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "  ✅ 文件存在: $file"
    else
        echo "  ❌ 文件不存在: $file"
        all_good=false
    fi
done

if [ "$all_good" = true ]; then
    print_success "项目结构检查通过"
else
    print_error "项目结构检查失败"
    exit 1
fi

echo ""

# 2. 检查Python导入
print_info "2. 检查Python导入..."
cd "$PROJECT_ROOT"

# 检查Python命令
if command -v python3 > /dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python > /dev/null 2>&1; then
    PYTHON_CMD="python"
else
    print_error "Python命令未找到"
    exit 1
fi

if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
try:
    from shared.config import config
    from core.database.migrations import create_tables
    from web.main import app
    from mcp_server.server import app as mcp_app
    from wechat.server import app as wechat_app
    print('  ✅ Python导入成功')
except Exception as e:
    print(f'  ❌ Python导入失败: {e}')
    sys.exit(1)
"; then
    print_success "Python导入检查通过"
else
    print_error "Python导入检查失败"
    exit 1
fi

echo ""

# 3. 检查运行脚本
print_info "3. 检查运行脚本..."
if [ -x "$PROJECT_ROOT/run.sh" ]; then
    echo "  ✅ run.sh可执行"
    
    # 测试帮助命令
    if timeout 5 "$PROJECT_ROOT/run.sh" help > /dev/null 2>&1; then
        echo "  ✅ run.sh help命令正常"
        print_success "运行脚本检查通过"
    else
        echo "  ❌ run.sh help命令失败"
        print_error "运行脚本检查失败"
        exit 1
    fi
else
    echo "  ❌ run.sh不可执行"
    print_error "运行脚本检查失败"
    exit 1
fi

echo ""

# 4. 检查数据库
print_info "4. 检查数据库..."
cd "$PROJECT_ROOT"

# 确保数据目录存在
mkdir -p data

if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
try:
    from core.database.migrations import create_tables
    create_tables()
    print('  ✅ 数据库表创建成功')
except Exception as e:
    print(f'  ❌ 数据库创建失败: {e}')
    sys.exit(1)
"; then
    if [ -f "data/question_bank.db" ]; then
        echo "  ✅ 数据库文件存在"
        print_success "数据库检查通过"
    else
        echo "  ❌ 数据库文件不存在"
        print_error "数据库检查失败"
        exit 1
    fi
else
    print_error "数据库检查失败"
    exit 1
fi

echo ""

# 5. 快速Web服务测试
print_info "5. 快速Web服务测试..."

# 先停止可能存在的服务
print_info "  停止现有服务..."
"$PROJECT_ROOT/run.sh" stop > /dev/null 2>&1 || true
sleep 2

# 启动Web服务（后台运行）
print_info "  启动Web服务..."
"$PROJECT_ROOT/run.sh" web > /tmp/web_test.log 2>&1 &
WEB_PID=$!

# 等待服务启动
sleep 5

# 检查服务是否运行
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✅ Web服务运行正常"
    
    # 测试根路径
    if curl -s http://localhost:8000/ | grep -q "题库管理系统"; then
        echo "  ✅ Web服务根路径正常"
        print_success "Web服务测试通过"
    else
        echo "  ❌ Web服务根路径异常"
        print_error "Web服务测试失败"
        kill $WEB_PID 2>/dev/null || true
        exit 1
    fi
    
    # 停止服务
    kill $WEB_PID 2>/dev/null || true
    sleep 2
else
    echo "  ❌ Web服务启动失败"
    print_error "Web服务测试失败"
    kill $WEB_PID 2>/dev/null || true
    cat /tmp/web_test.log
    exit 1
fi

echo ""
print_success "🎉 所有快速验证通过！"
echo ""
echo "📋 验证项目:"
echo "  ✅ 项目结构"
echo "  ✅ Python导入"
echo "  ✅ 运行脚本"
echo "  ✅ 数据库"
echo "  ✅ Web服务"
echo ""
echo "🔧 详细验证请运行: python test/validate_project.py"