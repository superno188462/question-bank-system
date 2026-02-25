#!/bin/bash
# 项目快速启动脚本 - 使用项目自带的启动机制

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_PATH="/home/zkjiao/usr/github/question-bank-system"

# 函数：打印带颜色的消息
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 函数：检查项目是否存在
check_project() {
    if [[ ! -d "$PROJECT_PATH" ]]; then
        print_error "项目目录不存在: $PROJECT_PATH"
        echo "请先克隆项目:"
        echo "  git clone git@github.com:superno188462/question-bank-system.git $PROJECT_PATH"
        exit 1
    fi
    
    cd "$PROJECT_PATH" || {
        print_error "无法进入项目目录"
        exit 1
    }
    
    print_success "项目目录: $PROJECT_PATH"
}

# 函数：使用项目自带的启动脚本
use_project_launcher() {
    print_info "使用项目自带的启动脚本..."
    
    cd "$PROJECT_PATH" || exit 1
    
    # 检查项目启动脚本
    if [[ -f "start.py" ]]; then
        print_info "找到项目启动脚本: start.py"
        echo ""
        print_info "启动命令: python start.py"
        echo ""
        
        # 显示启动选项
        python start.py --help 2>/dev/null || {
            print_info "直接启动项目..."
            python start.py
        }
    elif [[ -f "launch_all.py" ]]; then
        print_info "找到项目启动脚本: launch_all.py"
        echo ""
        print_info "启动命令: python launch_all.py"
        echo ""
        python launch_all.py
    else
        print_error "未找到项目启动脚本"
        echo "可用的启动方式:"
        echo "  1. python web/main.py     # 启动Web服务"
        echo "  2. python wechat/main.py  # 启动微信API"
        echo "  3. python mcp_server/main.py # 启动MCP服务"
        exit 1
    fi
}

# 函数：一键启动所有服务
start_all_services() {
    print_info "🚀 一键启动所有服务..."
    
    check_project
    
    # 检查Python
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        print_error "未找到Python命令"
        exit 1
    fi
    
    # 检查依赖
    print_info "检查Python依赖..."
    if [[ ! -d "venv" ]] && [[ ! -d ".venv" ]]; then
        print_warning "未找到虚拟环境，尝试安装依赖..."
        
        if [[ -f "config/requirements.txt" ]]; then
            if command -v uv &> /dev/null; then
                print_info "使用uv安装依赖..."
                uv pip install -r config/requirements.txt
            else
                print_info "使用pip安装依赖..."
                $PYTHON_CMD -m pip install --upgrade pip
                $PYTHON_CMD -m pip install -r config/requirements.txt
            fi
        fi
    fi
    
    # 检查数据库
    print_info "检查数据库..."
    if [[ ! -f "data/question_bank.db" ]]; then
        print_info "初始化数据库..."
        mkdir -p data
        $PYTHON_CMD -c "
from core.database.connection import get_db
from core.database.migrations import init_database
import asyncio

async def init():
    db = await get_db()
    await init_database(db)
    print('数据库初始化完成')

asyncio.run(init())
" 2>/dev/null || print_warning "数据库初始化可能失败，但将继续启动"
    fi
    
    # 启动服务
    print_info "启动服务..."
    
    # 停止可能已经在运行的服务
    pkill -f "web/main.py" 2>/dev/null || true
    pkill -f "wechat/main.py" 2>/dev/null || true
    pkill -f "mcp_server/main.py" 2>/dev/null || true
    sleep 1
    
    # 启动Web服务（后台）
    print_info "启动Web服务..."
    $PYTHON_CMD web/main.py > web.log 2>&1 &
    WEB_PID=$!
    echo $WEB_PID > .web_pid
    
    # 启动微信API服务（后台）
    print_info "启动微信API服务..."
    $PYTHON_CMD wechat/main.py > wechat.log 2>&1 &
    WECHAT_PID=$!
    echo $WECHAT_PID > .wechat_pid
    
    # 启动MCP服务（后台）
    print_info "启动MCP服务..."
    $PYTHON_CMD mcp_server/main.py > mcp.log 2>&1 &
    MCP_PID=$!
    echo $MCP_PID > .mcp_pid
    
    # 等待服务启动
    print_info "等待服务启动..."
    sleep 5
    
    # 显示状态
    show_status
}

# 函数：显示服务状态
show_status() {
    print_info "📊 服务状态"
    echo ""
    
    # 检查Web服务
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "  🌐 Web服务:    运行中 ✅"
        echo "      管理界面: http://localhost:8000"
        echo "      API文档:  http://localhost:8000/docs"
    else
        echo "  🌐 Web服务:    未运行 ❌"
    fi
    
    # 检查微信API服务
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "  📱 微信API:    运行中 ✅"
        echo "      接口地址: http://localhost:8001"
        echo "      API文档:  http://localhost:8001/docs"
    else
        echo "  📱 微信API:    未运行 ❌"
    fi
    
    # 检查MCP服务
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        echo "  🤖 MCP服务:    运行中 ✅"
        echo "      接口地址: http://localhost:8002"
        echo "      文档:     http://localhost:8002/docs"
    else
        echo "  🤖 MCP服务:    未运行 ❌"
    fi
    
    echo ""
    print_info "📋 日志文件"
    echo "  Web服务日志:    $PROJECT_PATH/web.log"
    echo "  微信API日志:    $PROJECT_PATH/wechat.log"
    echo "  MCP服务日志:    $PROJECT_PATH/mcp.log"
    
    echo ""
    print_info "🛑 停止服务命令"
    echo "  $0 stop    # 停止所有服务"
}

# 函数：停止服务
stop_services() {
    print_info "停止服务..."
    
    cd "$PROJECT_PATH" 2>/dev/null || {
        print_error "无法进入项目目录"
        exit 1
    }
    
    # 停止Web服务
    if [[ -f ".web_pid" ]]; then
        WEB_PID=$(cat .web_pid)
        if kill -0 "$WEB_PID" 2>/dev/null; then
            kill "$WEB_PID" 2>/dev/null || true
            print_info "已停止Web服务 (PID: $WEB_PID)"
        fi
        rm -f .web_pid
    fi
    
    # 停止微信API服务
    if [[ -f ".wechat_pid" ]]; then
        WECHAT_PID=$(cat .wechat_pid)
        if kill -0 "$WECHAT_PID" 2>/dev/null; then
            kill "$WECHAT_PID" 2>/dev/null || true
            print_info "已停止微信API服务 (PID: $WECHAT_PID)"
        fi
        rm -f .wechat_pid
    fi
    
    # 停止MCP服务
    if [[ -f ".mcp_pid" ]]; then
        MCP_PID=$(cat .mcp_pid)
        if kill -0 "$MCP_PID" 2>/dev/null; then
            kill "$MCP_PID" 2>/dev/null || true
            print_info "已停止MCP服务 (PID: $MCP_PID)"
        fi
        rm -f .mcp_pid
    fi
    
    # 清理进程
    pkill -f "web/main.py" 2>/dev/null || true
    pkill -f "wechat/main.py" 2>/dev/null || true
    pkill -f "mcp_server/main.py" 2>/dev/null || true
    
    print_success "所有服务已停止"
}

# 函数：显示帮助
show_help() {
    echo "项目快速启动脚本"
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start        一键启动所有服务"
    echo "  status       显示服务状态"
    echo "  stop         停止所有服务"
    echo "  restart      重启所有服务"
    echo "  logs         查看服务日志"
    echo "  project      使用项目自带的启动脚本"
    echo "  help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start     # 一键启动所有服务"
    echo "  $0 status    # 查看服务状态"
    echo "  $0 stop      # 停止所有服务"
    echo "  $0 project   # 使用项目自带的启动方式"
    echo ""
    echo "项目路径: $PROJECT_PATH"
    echo "GitHub仓库: https://github.com/superno188462/question-bank-system"
}

# 函数：查看日志
show_logs() {
    print_info "查看服务日志..."
    
    cd "$PROJECT_PATH" 2>/dev/null || {
        print_error "无法进入项目目录"
        exit 1
    }
    
    echo ""
    echo "选择要查看的日志:"
    echo "  1. Web服务日志"
    echo "  2. 微信API日志"
    echo "  3. MCP服务日志"
    echo "  4. 所有日志"
    echo "  0. 返回"
    echo ""
    
    read -p "请选择 (0-4): " choice
    
    case $choice in
        1)
            if [[ -f "web.log" ]]; then
                tail -50 web.log
            else
                print_warning "Web服务日志不存在"
            fi
            ;;
        2)
            if [[ -f "wechat.log" ]]; then
                tail -50 wechat.log
            else
                print_warning "微信API日志不存在"
            fi
            ;;
        3)
            if [[ -f "mcp.log" ]]; then
                tail -50 mcp.log
            else
                print_warning "MCP服务日志不存在"
            fi
            ;;
        4)
            echo "=== Web服务日志 ==="
            tail -20 web.log 2>/dev/null || echo "无日志"
            echo ""
            echo "=== 微信API日志 ==="
            tail -20 wechat.log 2>/dev/null || echo "无日志"
            echo ""
            echo "=== MCP服务日志 ==="
            tail -20 mcp.log 2>/dev/null || echo "无日志"
            ;;
        *)
            echo "返回"
            ;;
    esac
}

# 主程序
main() {
    print_info "🚀 项目快速启动脚本"
    echo "项目: 题库管理系统"
    echo "路径: $PROJECT_PATH"
    echo ""
    
    case "${1:-help}" in
        "start")
            start_all_services
            ;;
        "status")
            check_project
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_all_services
            ;;
        "logs")
            show_logs
            ;;
        "project")
            check_project
            use_project_launcher
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
}

# 运行主程序
main "$@"