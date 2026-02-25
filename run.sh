#!/bin/bash
# 根目录一键运行脚本
# 使用uv虚拟环境运行Python项目

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
            UV_AVAILABLE=true
        else
            print_warning "未找到uv虚拟环境，将自动创建..."
            uv venv
            if [[ -d ".venv" ]]; then
                print_success "uv虚拟环境创建成功: .venv"
                PYTHON_CMD="uv run python"
                UV_AVAILABLE=true
            else
                print_error "uv虚拟环境创建失败"
                print_info "尝试使用--system参数安装到系统..."
                PYTHON_CMD="uv run --system python"
                UV_AVAILABLE=true
            fi
        fi
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

# 函数：安装依赖（如果需要）
install_dependencies() {
    print_info "检查依赖..."
    
    if [[ "$UV_AVAILABLE" == true ]]; then
        print_info "使用uv安装/更新依赖..."
        
        # 检查是否使用--system参数
        if [[ "$USE_SYSTEM" == "true" ]]; then
            print_warning "使用--system参数，将安装到系统Python"
            print_warning "注意：可能需要sudo权限"
            
            # 尝试安装，如果失败给出提示
            if uv pip install --system -r config/requirements.txt 2>/dev/null; then
                print_success "依赖安装成功（系统Python）"
            else
                print_error "系统Python安装失败，可能需要sudo权限"
                print_info "请尝试：sudo uv pip install --system -r config/requirements.txt"
                print_info "或使用虚拟环境（推荐）：删除--system参数"
                return 1
            fi
        else
            # 检查虚拟环境是否存在
            if [[ -d ".venv" ]]; then
                uv pip install -r config/requirements.txt
            else
                print_warning "虚拟环境不存在，尝试创建..."
                uv venv
                if [[ -d ".venv" ]]; then
                    uv pip install -r config/requirements.txt
                else
                    print_error "虚拟环境创建失败，使用--system参数"
                    uv pip install --system -r config/requirements.txt
                fi
            fi
        fi
    elif [[ -f ".venv/bin/pip" ]]; then
        print_info "使用虚拟环境pip安装依赖..."
        .venv/bin/pip install -r config/requirements.txt
    elif [[ -f "venv/bin/pip" ]]; then
        print_info "使用虚拟环境pip安装依赖..."
        venv/bin/pip install -r config/requirements.txt
    else
        print_warning "未找到虚拟环境，将使用系统pip安装依赖（可能污染全局环境）"
        $PYTHON_CMD -m pip install --upgrade pip
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
        echo "  🔧 PID: $WEB_PID"
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
    sleep 3
    
    # 检查是否启动成功
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
    sleep 3
    
    # 检查是否启动成功
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
show_status() {
    print_info "📊 服务状态"
    echo ""
    
    local web_status="❌"
    local wechat_status="❌"
    local mcp_status="❌"
    
    # 检查Web服务
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        web_status="✅"
        echo "  🌐 Web服务:    运行中 $web_status"
        echo "      管理界面: http://localhost:8000"
        echo "      API文档:  http://localhost:8000/docs"
    else
        echo "  🌐 Web服务:    未运行 $web_status"
    fi
    
    # 检查微信API服务
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        wechat_status="✅"
        echo "  📱 微信API:    运行中 $wechat_status"
        echo "      接口地址: http://localhost:8001"
        echo "      API文档:  http://localhost:8001/docs"
    else
        echo "  📱 微信API:    未运行 $wechat_status"
    fi
    
    # 检查MCP服务
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        mcp_status="✅"
        echo "  🤖 MCP服务:    运行中 $mcp_status"
        echo "      接口地址: http://localhost:8002"
        echo "      文档:     http://localhost:8002/docs"
    else
        echo "  🤖 MCP服务:    未运行 $mcp_status"
    fi
    
    echo ""
    print_info "📋 快速访问"
    echo "  管理界面: http://localhost:8000"
    echo "  API文档:  http://localhost:8000/docs"
    echo "  微信API:  http://localhost:8001"
    echo "  MCP接口:  http://localhost:8002"
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
    
    # 清理可能遗留的进程
    pkill -f "web/main.py" 2>/dev/null || true
    pkill -f "wechat/server.py" 2>/dev/null || true
    pkill -f "mcp_server/server.py" 2>/dev/null || true
    
    print_success "所有服务已停止"
}

# 函数：显示帮助
show_help() {
    echo "Linux/macOS一键运行脚本"
    echo "用法: $0 [命令] [选项]"
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
    echo "选项:"
    echo "  --system     使用系统Python安装依赖（不创建虚拟环境）"
    echo ""
    echo "示例:"
    echo "  $0 start              # 一键启动所有服务（使用虚拟环境）"
    echo "  $0 web --system       # 启动Web服务（使用系统Python）"
    echo "  $0 status             # 查看服务状态"
    echo "  $0 stop               # 停止所有服务"
    echo "  $0 setup --system     # 安装依赖到系统Python"
    echo ""
    echo "跨平台支持:"
    echo "  - Linux/macOS: 使用此脚本 (run.sh)"
    echo "  - Windows:     使用 scripts/windows/run.ps1"
    echo "  - 通用入口:    使用根目录的 ./run 脚本（自动检测）"
    echo ""
    echo "环境要求:"
    echo "  - Python 3.8+"
    echo "  - 推荐使用uv包管理器 (https://astral.sh/uv)"
    echo "  - 默认创建.venv虚拟环境，使用--system跳过"
    echo ""
    echo "访问地址:"
    echo "  Web管理界面: http://localhost:8000"
    echo "  API文档:     http://localhost:8000/docs"
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
        read -p "是否现在安装uv？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
            if command -v uv &> /dev/null; then
                print_success "uv安装成功"
            else
                print_error "uv安装失败"
            fi
        fi
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
    echo "使用uv虚拟环境运行Python项目"
    echo ""
    
    # 解析参数
    USE_SYSTEM="false"
    COMMAND="help"
    
    # 解析参数
    for arg in "$@"; do
        case "$arg" in
            --system)
                USE_SYSTEM="true"
                ;;
            start|web|wechat|mcp|status|stop|restart|setup|help)
                COMMAND="$arg"
                ;;
            *)
                # 忽略其他参数
                ;;
        esac
    done
    
    export USE_SYSTEM
    
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