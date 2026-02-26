#!/bin/bash
# 题库系统测试运行脚本
# 支持运行：全部测试、Web测试、Core测试、集成测试

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
print_error() { echo -e "${RED}[FAIL]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# 检测平台
detect_platform() {
    case "$(uname -s)" in
        Linux*)     echo "Linux";;
        Darwin*)    echo "Mac";;
        CYGWIN*|MINGW*|MSYS*) echo "Windows";;
        *)          echo "Unknown";;
    esac
}

PLATFORM=$(detect_platform)

# 设置Python命令
setup_python() {
    if [[ "$PLATFORM" == "Windows" ]]; then
        if [[ -f ".venv/Scripts/python.exe" ]]; then
            PYTHON_CMD=".venv/Scripts/python"
        elif command -v python &> /dev/null; then
            PYTHON_CMD="python"
        else
            PYTHON_CMD="python3"
        fi
    else
        if command -v uv &> /dev/null && [[ -d ".venv" ]]; then
            PYTHON_CMD="uv run python"
        elif [[ -f ".venv/bin/python" ]]; then
            PYTHON_CMD=".venv/bin/python"
        elif command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
        else
            PYTHON_CMD="python"
        fi
    fi
}

# 运行测试的通用函数
run_test_module() {
    local module=$1
    local name=$2
    
    print_info "运行 $name 测试..."
    
    if $PYTHON_CMD -m pytest "$module" -v --tb=short 2>&1; then
        print_success "$name 测试通过"
        return 0
    else
        print_error "$name 测试失败"
        return 1
    fi
}

# 显示帮助
show_help() {
    echo "题库系统测试运行脚本"
    echo ""
    echo "用法: ./run_tests.sh [选项]"
    echo ""
    echo "选项:"
    echo "  all         运行所有测试 (默认)"
    echo "  core        只运行Core模块测试"
    echo "  web         只运行Web模块测试"
    echo "  integration 只运行集成测试"
    echo "  e2e         只运行端到端测试"
    echo "  ci          CI模式(无交互，生成报告)"
    echo "  help        显示此帮助"
    echo ""
    echo "示例:"
    echo "  ./run_tests.sh           # 运行所有测试"
    echo "  ./run_tests.sh core      # 只测试Core模块"
    echo "  ./run_tests.sh web       # 只测试Web模块"
    echo "  ./run_tests.sh ci        # CI模式"
}

# 主函数
main() {
    setup_python
    
    local TEST_TYPE="${1:-all}"
    local EXIT_CODE=0
    
    print_info "🧪 题库系统测试套件"
    print_info "平台: $PLATFORM"
    print_info "Python: $PYTHON_CMD"
    echo ""
    
    # 安装测试依赖
    print_info "安装测试依赖..."
    $PYTHON_CMD -m pip install -q pytest pytest-asyncio httpx 2>/dev/null || true
    
    case "$TEST_TYPE" in
        "core")
            print_info "========== Core模块测试 =========="
            run_test_module "core/tests" "Core" || EXIT_CODE=1
            ;;
        "web")
            print_info "========== Web模块测试 =========="
            run_test_module "web/tests" "Web" || EXIT_CODE=1
            ;;
        "integration")
            print_info "========== 集成测试 =========="
            run_test_module "tests/integration" "集成" || EXIT_CODE=1
            ;;
        "e2e")
            print_info "========== 端到端测试 =========="
            run_test_module "tests/e2e" "E2E" || EXIT_CODE=1
            ;;
        "ci")
            print_info "========== CI模式 - 全部测试 =========="
            $PYTHON_CMD -m pytest \
                core/tests \
                web/tests \
                tests/integration \
                -v \
                --tb=short \
                --junitxml=test-results.xml \
                --cov=core \
                --cov=web \
                --cov-report=xml \
                --cov-report=html \
                2>&1 || EXIT_CODE=1
            ;;
        "all"|"")
            print_info "========== 运行全部测试 =========="
            echo ""
            
            # Core测试
            run_test_module "core/tests" "Core" || EXIT_CODE=1
            echo ""
            
            # Web测试
            run_test_module "web/tests" "Web" || EXIT_CODE=1
            echo ""
            
            # 集成测试（如果有）
            if [[ -d "tests/integration" ]] && [[ $(find tests/integration -name "test_*.py" | wc -l) -gt 0 ]]; then
                run_test_module "tests/integration" "集成" || EXIT_CODE=1
            else
                print_warning "跳过集成测试(未找到测试文件)"
            fi
            ;;
        "help"|"-h"|"--help")
            show_help
            exit 0
            ;;
        *)
            print_error "未知选项: $TEST_TYPE"
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    if [[ $EXIT_CODE -eq 0 ]]; then
        print_success "🎉 所有测试通过!"
    else
        print_error "❌ 部分测试失败"
    fi
    
    exit $EXIT_CODE
}

main "$@"
