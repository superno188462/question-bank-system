#!/bin/bash
# 题库系统一键运行脚本 (支持 Linux/macOS/Windows MSYS2)

set -e

# ============================================
# 平台检测
# ============================================
detect_platform() {
    case "$(uname -s)" in
        Linux*)     PLATFORM=Linux;;
        Darwin*)    PLATFORM=Mac;;
        CYGWIN*)    PLATFORM=Windows;;
        MINGW*)     PLATFORM=Windows;;
        MSYS*)      PLATFORM=Windows;;
        *)          PLATFORM="UNKNOWN:$(uname -s)";;
    esac
    echo "$PLATFORM"
}

PLATFORM=$(detect_platform)

# ============================================
# 颜色定义 (Windows MSYS2需要特殊处理)
# ============================================
if [[ "$PLATFORM" == "Windows" ]]; then
    # Windows MSYS2/MINGW 简化颜色输出
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
else
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
fi

# 函数：打印带颜色的消息
print_info() { 
    if [[ "$PLATFORM" == "Windows" ]]; then
        echo "[INFO] $1"
    else
        echo -e "${BLUE}ℹ️  $1${NC}"
    fi
}

print_success() { 
    if [[ "$PLATFORM" == "Windows" ]]; then
        echo "[OK] $1"
    else
        echo -e "${GREEN}✅ $1${NC}"
    fi
}

print_warning() { 
    if [[ "$PLATFORM" == "Windows" ]]; then
        echo "[WARN] $1"
    else
        echo -e "${YELLOW}⚠️  $1${NC}"
    fi
}

print_error() { 
    if [[ "$PLATFORM" == "Windows" ]]; then
        echo "[ERROR] $1"
    else
        echo -e "${RED}❌ $1${NC}"
    fi
}

# ============================================
# Python环境设置
# ============================================
setup_python_command() {
    print_info "检查Python环境..."
    
    # Windows平台优先使用python命令
    if [[ "$PLATFORM" == "Windows" ]]; then
        if command -v python &> /dev/null; then
            PYTHON_CMD="python"
            PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
            print_success "找到Python: $PYTHON_VERSION"
        elif command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
            PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
            print_success "找到Python3: $PYTHON_VERSION"
        else
            print_error "未找到Python，请先安装Python 3.8+"
            exit 1
        fi
        
        # Windows下检查/创建虚拟环境
        if [[ ! -d ".venv" ]]; then
            print_info "创建虚拟环境..."
            $PYTHON_CMD -m venv .venv --system-site-packages
            print_success "虚拟环境创建成功"
        fi
        
        # 确保pip已安装
        if [[ -f ".venv/Scripts/python.exe" ]]; then
            PYTHON_CMD=".venv/Scripts/python"
            if ! $PYTHON_CMD -m pip --version &> /dev/null; then
                print_info "安装pip到虚拟环境..."
                curl -s https://bootstrap.pypa.io/get-pip.py | $PYTHON_CMD
            fi
            print_success "使用虚拟环境Python"
        fi
        
    # Linux/Mac平台优先使用uv
    elif command -v uv &> /dev/null; then
        print_success "找到uv包管理器"
        
        if [[ -d ".venv" ]]; then
            print_success "找到uv虚拟环境: .venv"
            PYTHON_CMD="uv run python"
        else
            print_warning "未找到uv虚拟环境，将自动创建..."
            uv venv
            if [[ -d ".venv" ]]; then
                print_success "uv虚拟环境创建成功"
                PYTHON_CMD="uv run python"
                
                print_info "安装依赖..."
                uv pip install -r config/requirements.txt
            else
                print_error "uv虚拟环境创建失败"
                PYTHON_CMD="uv run --system python"
            fi
        fi
    elif [[ -f ".venv/bin/python" ]]; then
        print_success "找到虚拟环境: .venv/bin/python"
        PYTHON_CMD=".venv/bin/python"
    else
        print_warning "未找到uv或虚拟环境，将使用系统Python"
        
        if command -v python &> /dev/null; then
            PYTHON_CMD="python"
        elif command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
        else
            print_error "未找到Python命令，请先安装Python 3.8+"
            exit 1
        fi
        
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
        print_warning "使用系统Python: $PYTHON_VERSION"
    fi
    
    export PYTHON_CMD
}

# ============================================
# 依赖安装
# ============================================
install_dependencies() {
    print_info "检查依赖..."
    
    if [[ "$PLATFORM" == "Windows" ]]; then
        # Windows直接使用pip
        $PYTHON_CMD -m pip install -q fastapi uvicorn pydantic jinja2
    elif [[ -d ".venv" ]]; then
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

# ============================================
# 端口检查和进程管理
# ============================================
check_port() {
    local port=$1
    if [[ "$PLATFORM" == "Windows" ]]; then
        netstat -ano | grep ":$port " > /dev/null 2>&1
    else
        lsof -ti:$port &> /dev/null
    fi
}

kill_port() {
    local port=$1
    if [[ "$PLATFORM" == "Windows" ]]; then
        local pid=$(netstat -ano | grep ":$port " | awk '{print $5}' | head -1)
        if [[ -n "$pid" ]]; then
            taskkill //F //PID "$pid" 2>/dev/null || true
        fi
    else
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
}

# ============================================
# 服务启动
# ============================================
start_web() {
    print_info "启动Web服务..."
    
    # 强制清理端口 - 确保端口完全释放
    if check_port 8000; then
        print_warning "端口8000已被占用，正在强制清理..."
        
        # Windows平台使用PowerShell强制终止
        if [[ "$PLATFORM" == "Windows" ]]; then
            # 方法1：使用PowerShell的Get-NetTCPConnection
            powershell -Command "
                try {
                    \$connections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction Stop
                    foreach (\$conn in \$connections) {
                        Write-Host '终止PID:' \$conn.OwningProcess
                        Stop-Process -Id \$conn.OwningProcess -Force -ErrorAction SilentlyContinue
                    }
                } catch { }
            " 2>/dev/null || true
            
            # 方法2：使用taskkill终止所有Python进程
            taskkill //F //IM python.exe 2>/dev/null || true
            taskkill //F //IM pythonw.exe 2>/dev/null || true
        else
            # Linux/Mac
            lsof -ti:8000 | xargs kill -9 2>/dev/null || true
            pkill -9 -f "python.*main.py" 2>/dev/null || true
        fi
        
        # 等待端口释放
        local wait_count=0
        while check_port 8000 && [[ $wait_count -lt 10 ]]; do
            sleep 1
            ((wait_count++))
            print_info "等待端口释放... ($wait_count/10)"
        done
        
        if check_port 8000; then
            print_error "端口8000仍被占用，请手动检查: netstat -ano | findstr ':8000'"
            exit 1
        else
            print_success "端口8000已释放"
        fi
    fi
    
    # 后台启动（Windows和Linux方式不同）
    if [[ "$PLATFORM" == "Windows" ]]; then
        # Windows下直接前台启动（MSYS2不支持真正的后台）
        print_info "启动Web服务器..."
        print_info "地址: http://localhost:8000"
        print_info "API文档: http://localhost:8000/docs"
        print_info "按 Ctrl+C 停止服务"
        echo ""
        $PYTHON_CMD web/main.py
    else
        # Linux/Mac下后台启动
        $PYTHON_CMD web/main.py &
        WEB_PID=$!
        echo $WEB_PID > .web_pid
        
        sleep 3
        
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Web服务启动成功"
            echo "  🌐 管理界面: http://localhost:8000"
            echo "  📚 API文档: http://localhost:8000/docs"
        else
            print_error "Web服务启动失败"
            return 1
        fi
    fi
}

start_wechat() {
    print_info "启动微信API服务..."
    
    if check_port 8001; then
        print_warning "端口8001已被占用，尝试停止现有服务..."
        kill_port 8001
        sleep 1
    fi
    
    if [[ "$PLATFORM" == "Windows" ]]; then
        print_info "Windows环境下请单独运行: $PYTHON_CMD wechat/server.py"
    else
        $PYTHON_CMD wechat/server.py &
        WECHAT_PID=$!
        echo $WECHAT_PID > .wechat_pid
        
        sleep 2
        
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            print_success "微信API服务启动成功"
            echo "  📱 微信API: http://localhost:8001"
        else
            print_error "微信API服务启动失败"
            return 1
        fi
    fi
}

start_mcp() {
    print_info "启动MCP服务..."
    
    if check_port 8002; then
        print_warning "端口8002已被占用，尝试停止现有服务..."
        kill_port 8002
        sleep 1
    fi
    
    if [[ "$PLATFORM" == "Windows" ]]; then
        print_info "Windows环境下请单独运行: $PYTHON_CMD mcp_server/server.py"
    else
        $PYTHON_CMD mcp_server/server.py &
        MCP_PID=$!
        echo $MCP_PID > .mcp_pid
        
        sleep 2
        
        if curl -s http://localhost:8002/health > /dev/null 2>&1; then
            print_success "MCP服务启动成功"
            echo "  🤖 MCP接口: http://localhost:8002"
        else
            print_error "MCP服务启动失败"
            return 1
        fi
    fi
}

# ============================================
# 状态显示
# ============================================
show_status() {
    print_info "📊 服务状态"
    echo ""
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "  🌐 Web服务:    运行中 ✅"
        echo "      管理界面: http://localhost:8000"
    else
        echo "  🌐 Web服务:    未运行 ❌"
    fi
    
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "  📱 微信API:    运行中 ✅"
        echo "      接口地址: http://localhost:8001"
    else
        echo "  📱 微信API:    未运行 ❌"
    fi
    
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        echo "  🤖 MCP服务:    运行中 ✅"
        echo "      接口地址: http://localhost:8002"
    else
        echo "  🤖 MCP服务:    未运行 ❌"
    fi
}

# ============================================
# 停止服务
# ============================================
stop_services() {
    print_info "停止所有服务..."
    
    kill_port 8000
    kill_port 8001
    kill_port 8002
    
    rm -f .web_pid .wechat_pid .mcp_pid
    
    print_success "所有服务已停止"
}

# ============================================
# 帮助信息
# ============================================
show_help() {
    echo "题库系统一键运行脚本 (支持 Linux/macOS/Windows MSYS2)"
    echo "当前平台: $PLATFORM"
    echo ""
    echo "用法: ./run.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start        启动所有服务 (仅Linux/Mac)"
    echo "  web          启动Web服务"
    echo "  wechat       启动微信API服务 (仅Linux/Mac)"
    echo "  mcp          启动MCP服务 (仅Linux/Mac)"
    echo "  status       显示服务状态"
    echo "  stop         停止所有服务"
    echo "  restart      重启所有服务"
    echo "  setup        安装依赖和初始化"
    echo "  help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./run.sh web        # 启动Web服务"
    echo "  ./run.sh status     # 查看服务状态"
    echo "  ./run.sh stop       # 停止所有服务"
    echo ""
    echo "访问地址:"
    echo "  Web管理界面: http://localhost:8000"
    echo "  微信API:     http://localhost:8001"
    echo "  MCP接口:     http://localhost:8002"
    echo ""
    echo "注意: Windows环境下建议只运行 './run.sh web'"
}

# ============================================
# 项目设置
# ============================================
setup_project() {
    print_info "项目设置..."
    print_info "当前平台: $PLATFORM"
    
    # 创建数据目录
    mkdir -p data
    
    # 安装依赖
    install_dependencies
    
    # 初始化数据库
    print_info "初始化数据库..."
    $PYTHON_CMD -c "
import sys
import os
sys.path.insert(0, os.getcwd())

from core.database.migrations import create_tables
create_tables()
print('数据库初始化完成')
"
    
    print_success "项目设置完成"
}

# ============================================
# 主程序
# ============================================
main() {
    print_info "🚀 题库系统一键运行脚本"
    print_info "平台: $PLATFORM"
    echo ""
    
    COMMAND="help"
    
    for arg in "$@"; do
        case "$arg" in
            start|web|wechat|mcp|status|stop|restart|setup|help)
                COMMAND="$arg"
                ;;
        esac
    done
    
    setup_python_command
    
    case "$COMMAND" in
        "start")
            if [[ "$PLATFORM" == "Windows" ]]; then
                print_warning "Windows环境下 'start' 命令只启动Web服务"
                install_dependencies
                start_web
            else
                install_dependencies
                start_web
                start_wechat
                start_mcp
                show_status
            fi
            ;;
        "web")
            install_dependencies
            start_web
            ;;
        "wechat")
            if [[ "$PLATFORM" == "Windows" ]]; then
                print_error "Windows环境下请直接运行: $PYTHON_CMD wechat/server.py"
            else
                install_dependencies
                start_wechat
            fi
            ;;
        "mcp")
            if [[ "$PLATFORM" == "Windows" ]]; then
                print_error "Windows环境下请直接运行: $PYTHON_CMD mcp_server/server.py"
            else
                install_dependencies
                start_mcp
            fi
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
            if [[ "$PLATFORM" != "Windows" ]]; then
                start_wechat
                start_mcp
            fi
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
    
    if [[ "$PLATFORM" != "Windows" ]] || [[ "$COMMAND" != "web" ]]; then
        echo ""
        print_success "操作完成！"
    fi
}

main "$@"
