#!/bin/bash
# 题库系统测试运行脚本
# 支持单独运行Web、后端(Core)、集成等测试

set -e

# ============================================
# 颜色定义
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# ============================================
# Python环境设置
# ============================================
setup_python() {
    if command -v uv &> /dev/null && [[ -d ".venv" ]]; then
        PYTHON_CMD="uv run python"
    elif [[ -f ".venv/bin/python" ]]; then
        PYTHON_CMD=".venv/bin/python"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
}

# ============================================
# 测试运行函数
# ============================================
run_core_tests() {
    print_info "运行 Core (后端) 测试..."
    if [[ -d "core/tests" ]]; then
        $PYTHON_CMD -m pytest core/tests/ -v --tb=short
        print_success "Core 测试通过"
    else
        print_warning "未找到 core/tests 目录"
    fi
}

run_web_tests() {
    print_info "运行 Web 测试..."
    if [[ -d "web/tests" ]]; then
        $PYTHON_CMD -m pytest web/tests/ -v --tb=short
        print_success "Web 测试通过"
    else
        print_warning "未找到 web/tests 目录"
    fi
}

run_integration_tests() {
    print_info "运行集成测试..."
    if [[ -d "tests" ]]; then
        $PYTHON_CMD -m pytest tests/ -v --tb=short
        print_success "集成测试通过"
    else
        print_warning "未找到 tests 目录"
    fi
}

run_all_tests() {
    print_info "运行所有测试..."
    $PYTHON_CMD -m pytest core/tests/ web/tests/ tests/ -v --tb=short
    print_success "所有测试通过"
}

# ============================================
# 帮助信息
# ============================================
show_help() {
    echo "题库系统测试运行脚本"
    echo ""
    echo "用法: ./run_tests.sh [命令]"
    echo ""
    echo "命令:"
    echo "  core          运行后端(Core)模块测试"
    echo "  web           运行Web模块测试"
    echo "  integration   运行集成测试"
    echo "  all           运行所有测试(默认)"
    echo "  help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./run_tests.sh core         # 只测试后端"
    echo "  ./run_tests.sh web          # 只测试Web"
    echo "  ./run_tests.sh all          # 测试全部"
    echo "  ./run_tests.sh              # 默认测试全部"
}

# ============================================
# 主程序
# ============================================
main() {
    print_info "🧪 题库系统测试运行器"
    echo ""
    
    setup_python
    
    COMMAND="${1:-all}"
    
    case "$COMMAND" in
        "core")
            run_core_tests
            ;;
        "web")
            run_web_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "all")
            run_all_tests
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知命令: $COMMAND"
            echo ""
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    print_success "测试完成！"
}

main "$@"
