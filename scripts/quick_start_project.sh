#!/bin/bash
# 题库系统快速启动脚本（uv版本）
# 使用uv虚拟环境运行Python项目

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径 - 使用脚本所在目录的父目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="$(dirname "$SCRIPT_DIR")"

# 函数：打印带颜色的消息
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 函数：检查并设置Python命令（使用uv优先）
setup_python_command() {
    print_info "检查Python环境..."
    
    # 优先使用uv
    if command -v uv &> /dev/null; then
        print_success "找到uv包管理器"
        PYTHON_CMD="uv run python"
        UV_AVAILABLE=true
    elif [[ -f ".venv/bin/python" ]]; then
        print_success "找到虚拟环境: .venv/bin/python"
        PYTHON_CMD=".venv/bin/python"
        UV_AVAILABLE=false
    elif [[ -f "venv/bin/python" ]]; then
        print_success "找到虚拟环境: venv/bin/python"
        PYTHON_CMD="venv/bin/python"
        UV_AVAILABLE=false
    else
        print_warning "未找到uv或虚拟环境，将使用系统Python"
        
        # 检查系统Python
        if command -v python &> /dev/null; then
            PYTHON_CMD="python"
        elif command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
        else
            print_error "未找到Python命令，请先安装Python 3.8+"
            exit 1
        fi
        
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
        print_warning "使用系统Python: $PYTHON_CMD ($PYTHON_VERSION)"
        print_warning "建议安装uv或创建虚拟环境：uv venv 或 python -m venv .venv"
        UV_AVAILABLE=false
    fi
    
    export PYTHON_CMD
    export UV_AVAILABLE
}

# 函数：安装依赖
install_dependencies() {
    print_info "安装Python依赖..."
    
    cd "$PROJECT_PATH" || {
        print_error "无法进入项目目录: $PROJECT_PATH"
        exit 1
    }
    
    # 检查requirements.txt是否存在
    if [[ ! -f "config/requirements.txt" ]]; then
        print_error "未找到依赖文件: config/requirements.txt"
        exit 1
    fi
    
    if [[ "$UV_AVAILABLE" == true ]]; then
        print_info "使用uv安装依赖（极速）..."
        
        # 检查虚拟环境是否存在
        if [[ -d ".venv" ]]; then
            print_info "在现有虚拟环境中安装依赖..."
            uv pip install -r config/requirements.txt
        else
            print_warning "虚拟环境不存在，创建并安装依赖..."
            uv venv
            if [[ -d ".venv" ]]; then
                print_success "虚拟环境创建成功"
                print_info "安装依赖到新虚拟环境..."
                uv pip install -r config/requirements.txt
            else
                print_error "虚拟环境创建失败"
                print_info "尝试使用--system参数：uv pip install --system -r config/requirements.txt"
                print_info "或手动创建：uv venv"
                return 1
            fi
        fi
    elif [[ -f ".venv/bin/pip" ]]; then
        print_info "使用虚拟环境pip安装依赖..."
        .venv/bin/pip install -r config/requirements.txt
    elif [[ -f "venv/bin/pip" ]]; then
        print_info "使用虚拟环境pip安装依赖..."
        venv/bin/pip install -r config/requirements.txt
    else
        print_warning "使用系统pip安装依赖（可能污染全局环境）..."
        $PYTHON_CMD -m pip install --upgrade pip
        $PYTHON_CMD -m pip install -r config/requirements.txt
    fi
    
    print_success "依赖安装完成"
}

# 函数：初始化数据库
init_database() {
    print_info "初始化数据库..."
    
    cd "$PROJECT_PATH" || exit 1
    
    # 检查数据库文件
    if [[ -f "data/question_bank.db" ]]; then
        print_info "数据库文件已存在: data/question_bank.db"
        
        read -p "是否重新初始化数据库？（将清空现有数据）(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f data/question_bank.db
            print_info "已删除旧数据库"
        else
            print_info "使用现有数据库"
            return 0
        fi
    fi
    
    # 创建数据库目录
    mkdir -p data
    
    # 初始化数据库
    print_info "创建数据库表结构..."
    $PYTHON_CMD -c "
import sys
import os
sys.path.insert(0, os.getcwd())

from core.database.connection import db
from core.database.migrations import create_tables

# 确保数据目录存在
os.makedirs('data', exist_ok=True)

# 创建表
create_tables()
print('数据库初始化完成')
"
    
    print_success "数据库初始化完成"
}

# 函数：启动Web服务
start_web_service() {
    print_info "启动Web服务..."
    
    cd "$PROJECT_PATH" || exit 1
    
    # 检查Web服务是否已在运行
    if lsof -ti:8000 &> /dev/null; then
        print_warning "端口8000已被占用，尝试停止现有服务..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    # 启动Web服务（后台运行）
    print_info "启动FastAPI服务..."
    $PYTHON_CMD web/main.py &
    WEB_PID=$!
    
    # 等待服务启动
    sleep 3
    
    # 检查服务是否启动成功
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Web服务启动成功"
        echo "  🌐 管理界面: http://localhost:8000"
        echo "  📚 API文档: http://localhost:8000/docs"
        echo "  🔧 PID: $WEB_PID"
    else
        print_error "Web服务启动失败"
        return 1
    fi
}

# 函数：启动微信API服务
start_wechat_service() {
    print_info "启动微信API服务..."
    
    cd "$PROJECT_PATH" || exit 1
    
    # 检查微信服务是否已在运行
    if lsof -ti:8001 &> /dev/null; then
        print_warning "端口8001已被占用，尝试停止现有服务..."
        lsof -ti:8001 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    # 启动微信API服务（后台运行）
    print_info "启动微信小程序API服务..."
    $PYTHON_CMD wechat/server.py &
    WECHAT_PID=$!
    
    # 等待服务启动
    sleep 3
    
    # 检查服务是否启动成功
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "微信API服务启动成功"
        echo "  📱 微信API: http://localhost:8001"
        echo "  📚 API文档: http://localhost:8001/docs"
        echo "  🔧 PID: $WECHAT_PID"
    else
        print_error "微信API服务启动失败"
        return 1
    fi
}

# 函数：启动MCP服务
start_mcp_service() {
    print_info "启动MCP服务..."
    
    cd "$PROJECT_PATH" || exit 1
    
    # 检查MCP服务是否已在运行
    if lsof -ti:8002 &> /dev/null; then
        print_warning "端口8002已被占用，尝试停止现有服务..."
        lsof -ti:8002 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    # 启动MCP服务（后台运行）
    print_info "启动MCP协议服务..."
    $PYTHON_CMD mcp_server/server.py &
    MCP_PID=$!
    
    # 等待服务启动
    sleep 3
    
    # 检查服务是否启动成功
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        print_success "MCP服务启动成功"
        echo "  🤖 MCP接口: http://localhost:8002"
        echo "  📚 文档: http://localhost:8002/docs"
        echo "  🔧 PID: $MCP_PID"
    else
        print_error "MCP服务启动失败"
        return 1
    fi
}

# 函数：显示服务状态
show_services_status() {
    print_info "📊 服务状态"
    echo ""
    
    # Web服务
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "  🌐 Web服务: 运行中 ✅ (http://localhost:8000)"
    else
        echo "  🌐 Web服务: 未运行 ❌"
    fi
    
    # 微信API服务
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "  📱 微信API: 运行中 ✅ (http://localhost:8001)"
    else
        echo "  📱 微信API: 未运行 ❌"
    fi
    
    # MCP服务
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        echo "  🤖 MCP服务: 运行中 ✅ (http://localhost:8002)"
    else
        echo "  🤖 MCP服务: 未运行 ❌"
    fi
    
    echo ""
    print_info "📋 快速访问"
    echo "  管理界面: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
    echo "  微信API: http://localhost:8001"
    echo "  MCP接口: http://localhost:8002"
}

# 函数：停止所有服务
stop_services() {
    print_info "停止所有服务..."
    
    # 停止Web服务
    if lsof -ti:8000 &> /dev/null; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        print_info "已停止Web服务"
    fi
    
    # 停止微信API服务
    if lsof -ti:8001 &> /dev/null; then
        lsof -ti:8001 | xargs kill -9 2>/dev/null || true
        print_info "已停止微信API服务"
    fi
    
    # 停止MCP服务
    if lsof -ti:8002 &> /dev/null; then
        lsof -ti:8002 | xargs kill -9 2>/dev/null || true
        print_info "已停止MCP服务"
    fi
    
    print_success "所有服务已停止"
}

# 函数：显示帮助
show_help() {
    echo "题库系统快速启动脚本（uv版本）"
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  setup        安装依赖和初始化环境"
    echo "  start        启动所有服务"
    echo "  web          只启动Web服务"
    echo "  wechat       只启动微信API服务"
    echo "  mcp          只启动MCP服务"
    echo "  status       显示服务状态"
    echo "  stop         停止所有服务"
    echo "  restart      重启所有服务"
    echo "  full         完整流程（安装+启动）"
    echo "  help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 full      # 一键安装并启动所有服务"
    echo "  $0 setup     # 只安装依赖"
    echo "  $0 start     # 只启动服务（假设依赖已安装）"
    echo "  $0 status    # 查看服务状态"
    echo ""
    echo "环境要求:"
    echo "  - 优先使用uv包管理器 (https://astral.sh/uv)"
    echo "  - 或已创建虚拟环境 (.venv 或 venv)"
    echo "  - 或系统Python 3.8+"
    echo ""
    echo "项目路径: $PROJECT_PATH"
}

# 主程序
main() {
    print_info "📦 题库系统快速启动脚本（uv版本）"
    echo "使用uv虚拟环境运行Python项目"
    echo "项目路径: $PROJECT_PATH"
    echo ""
    
    # 设置Python命令
    setup_python_command
    
    case "${1:-help}" in
        "setup")
            install_dependencies
            init_database
            ;;
        "start")
            install_dependencies
            start_web_service
            start_wechat_service
            start_mcp_service
            show_services_status
            ;;
        "web")
            install_dependencies
            start_web_service
            ;;
        "wechat")
            install_dependencies
            start_wechat_service
            ;;
        "mcp")
            install_dependencies
            start_mcp_service
            ;;
        "status")
            show_services_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            install_dependencies
            start_web_service
            start_wechat_service
            start_mcp_service
            show_services_status
            ;;
        "full")
            install_dependencies
            init_database
            start_web_service
            start_wechat_service
            start_mcp_service
            show_services_status
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
    
    print_success "操作完成！"
}

# 运行主程序
main "$@"