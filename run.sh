#!/bin/bash
# 题库系统一键运行脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 函数：检查并设置Python命令
setup_python_command() {
    print_info "检查Python环境..."
    
    # 优先使用uv
    if command -v uv &> /dev/null; then
        print_success "找到uv包管理器"
        
        # 检查uv虚拟环境是否存在
        if [[ -d ".venv" ]]; then
            print_success "找到uv虚拟环境: .venv"
            PYTHON_CMD="uv run python"
        else
            print_warning "未找到uv虚拟环境，将自动创建并安装依赖..."
            uv venv
            if [[ -d ".venv" ]]; then
                print_success "uv虚拟环境创建成功: .venv"
                PYTHON_CMD="uv run python"
                
                # 安装依赖
                print_info "安装依赖..."
                uv pip install -r config/requirements.txt
            else
                print_error "uv虚拟环境创建失败"
                print_info "尝试使用--system参数安装到系统..."
                PYTHON_CMD="uv run --system python"
            fi
        fi
    elif [[ -f ".venv/bin/python" ]]; then
        print_success "找到虚拟环境: .venv/bin/python"
        PYTHON_CMD=".venv/bin/python"
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
    fi
    
    export PYTHON_CMD
}

# 函数：安装依赖
install_dependencies() {
    print_info "检查依赖..."
    
    if [[ -d ".venv" ]]; then
        if command -v uv &> /dev/null; then
            uv pip install -r config/requirements.txt
        elif [[ -f ".venv/bin/pip" ]]; then
            .venv/bin/pip install -r config/requirements.txt
        fi
    else
        $PYTHON_CMD -m pip install -r config/requirements.txt
    fi
    
    print_success "依赖检查完成"
}

# 函数：启动Web服务
start_web() {
    print_info "启动Web服务..."
    
    # 检查端口是否被占用
    if lsof -ti:8000 &> /dev/null; then
        print_warning "端口8000已被占用，尝试停止现有服务..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    # 启动服务
    $PYTHON_CMD web/main.py &
    WEB_PID=$!
    echo $WEB_PID > .web_pid
    
    # 等待启动
    sleep 3
    
    # 检查是否启动成功
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Web服务启动成功"
        echo "  🌐 管理界面: http://localhost:8000"
        echo "  📚 API文档: http://localhost:8000/docs"
    else
        print_error "Web服务启动失败"
        return 1
    fi
}

# 函数：启动微信API服务
start_wechat() {
    print_info "启动微信API服务..."
    
    # 检查端口是否被占用
    if lsof -ti:8001 &> /dev/null; then
        print_warning "端口8001已被占用，尝试停止现有服务..."
        lsof -ti:8001 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    # 启动服务
    $PYTHON_CMD wechat/server.py &
    WECHAT_PID=$!
    echo $WECHAT_PID > .wechat_pid
    
    # 等待启动
    sleep 2
    
    # 检查是否启动成功
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "微信API服务启动成功"
        echo "  📱 微信API: http://localhost:8001"
    else
        print_error "微信API服务启动失败"
        return 1
    fi
}

# 函数：启动MCP服务
start_mcp() {
    print_info "启动MCP服务..."
    
    # 检查端口是否被占用
    if lsof -ti:8002 &> /dev/null; then
        print_warning "端口8002已被占用，尝试停止现有服务..."
        lsof -ti:8002 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    # 启动服务
    $PYTHON_CMD mcp_server/server.py &
    MCP_PID=$!
    echo $MCP_PID > .mcp_pid
    
    # 等待启动
    sleep 2
    
    # 检查是否启动成功
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        print_success "MCP服务启动成功"
        echo "  🤖 MCP接口: http://localhost:8002"
    else
        print_error "MCP服务启动失败"
        return 1
    fi
}

# 函数：显示服务状态
show_status() {
    print_info "📊 服务状态"
    echo ""
    
    # 检查Web服务
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "  🌐 Web服务:    运行中 ✅"
        echo "      管理界面: http://localhost:8000"
    else
        echo "  🌐 Web服务:    未运行 ❌"
    fi
    
    # 检查微信API服务
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "  📱 微信API:    运行中 ✅"
        echo "      接口地址: http://localhost:8001"
    else
        echo "  📱 微信API:    未运行 ❌"
    fi
    
    # 检查MCP服务
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        echo "  🤖 MCP服务:    运行中 ✅"
        echo "      接口地址: http://localhost:8002"
    else
        echo "  🤖 MCP服务:    未运行 ❌"
    fi
}

# 函数：停止所有服务
stop_services() {
    print_info "停止所有服务..."
    
    # 停止Web服务
    if [[ -f ".web_pid" ]]; then
        local pid=$(cat .web_pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            print_info "已停止Web服务 (PID: $pid)"
        fi
        rm -f .web_pid
    fi
    
    # 停止微信API服务
    if [[ -f ".wechat_pid" ]]; then
        local pid=$(cat .wechat_pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            print_info "已停止微信API服务 (PID: $pid)"
        fi
        rm -f .wechat_pid
    fi
    
    # 停止MCP服务
    if [[ -f ".mcp_pid" ]]; then
        local pid=$(cat .mcp_pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            print_info "已停止MCP服务 (PID: $pid)"
        fi
        rm -f .mcp_pid
    fi
    
    print_success "所有服务已停止"
}

# 函数：显示帮助
show_help() {
    echo "题库系统一键运行脚本"
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start        启动所有服务"
    echo "  web          只启动Web服务"
    echo "  wechat       只启动微信API服务"
    echo "  mcp          只启动MCP服务"
    echo "  status       显示服务状态"
    echo "  stop         停止所有服务"
    echo "  restart      重启所有服务"
    echo "  setup        安装依赖和初始化"
    echo "  help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 web        # 启动Web服务"
    echo "  $0 start      # 启动所有服务"
    echo "  $0 status     # 查看服务状态"
    echo "  $0 stop       # 停止所有服务"
    echo ""
    echo "访问地址:"
    echo "  Web管理界面: http://localhost:8000"
    echo "  微信API:     http://localhost:8001"
    echo "  MCP接口:     http://localhost:8002"
}

# 函数：安装依赖和初始化
setup_project() {
    print_info "项目设置..."
    
    # 检查uv
    if ! command -v uv &> /dev/null; then
        print_warning "未找到uv，建议安装以获得更好体验"
        print_info "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    fi
    
    # 创建虚拟环境（如果使用uv）
    if command -v uv &> /dev/null && [[ ! -d ".venv" ]]; then
        print_info "创建uv虚拟环境..."
        uv venv
    fi
    
    # 安装依赖
    install_dependencies
    
    # 初始化数据库
    print_info "初始化数据库..."
    mkdir -p data
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
    
    print_success "项目设置完成"
}

# 主程序
main() {
    print_info "🚀 题库系统一键运行脚本"
    echo ""
    
    # 解析参数
    COMMAND="help"
    
    # 解析参数
    for arg in "$@"; do
        case "$arg" in
            start|web|wechat|mcp|status|stop|restart|setup|help)
                COMMAND="$arg"
                ;;
            *)
                # 忽略其他参数
                ;;
        esac
    done
    
    # 设置Python命令
    setup_python_command
    
    case "$COMMAND" in
        "start")
            install_dependencies
            start_web
            start_wechat
            start_mcp
            show_status
            ;;
        "web")
            install_dependencies
            start_web
            ;;
        "wechat")
            install_dependencies
            start_wechat
            ;;
        "mcp")
            install_dependencies
            start_mcp
            ;;
        "status")
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            install_dependencies
            start_web
            start_wechat
            start_mcp
            show_status
            ;;
        "setup")
            setup_project
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
    
    echo ""
    print_success "操作完成！"
}

# 运行主程序
main "$@"