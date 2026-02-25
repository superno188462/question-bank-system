#!/bin/bash
# 项目验证和提交脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径 - 使用相对路径或当前目录
# 禁止硬编码绝对路径，使用脚本所在目录或当前工作目录
if [[ -n "$PROJECT_ROOT" ]]; then
    PROJECT_PATH="$PROJECT_ROOT"
elif [[ -n "$PWD" ]]; then
    PROJECT_PATH="$PWD"
else
    PROJECT_PATH="."
fi

# 函数：打印带颜色的消息
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 函数：检查项目状态
check_project_status() {
    print_info "检查项目状态..."
    
    cd "$PROJECT_PATH" || {
        print_error "无法进入项目目录"
        return 1
    }
    
    # 检查Git状态
    if ! git status &> /dev/null; then
        print_error "不是Git仓库"
        return 1
    fi
    
    print_success "Git仓库状态正常"
    
    # 检查是否有未提交的更改
    if [[ -n $(git status --porcelain) ]]; then
        print_warning "有未提交的更改"
        git status --short
        return 2
    else
        print_success "工作树干净"
        return 0
    fi
}

# 函数：验证项目结构
validate_project_structure() {
    print_info "验证项目结构..."
    
    cd "$PROJECT_PATH" || return 1
    
    local errors=0
    local warnings=0
    
    # 1. 检查根目录文件数量
    local root_files=$(ls -la | grep -E "^-" | wc -l)
    if [[ $root_files -gt 5 ]]; then
        print_warning "根目录文件数量: $root_files (建议 ≤ 5)"
        warnings=$((warnings + 1))
    else
        print_success "根目录文件数量: $root_files"
    fi
    
    # 2. 检查必需文件
    local required_files=(
        "README.md"
        ".gitignore"
        "config/pyproject.toml"
        "config/requirements.txt"
        "core/models.py"
        "web/main.py"
        "wechat/server.py"
        "mcp_server/server.py"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            print_success "文件存在: $file"
        else
            print_error "文件缺失: $file"
            errors=$((errors + 1))
        fi
    done
    
    # 3. 检查目录结构
    local required_dirs=(
        "config"
        "data"
        "core"
        "web"
        "wechat"
        "mcp_server"
        "shared"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            print_success "目录存在: $dir/"
        else
            print_error "目录缺失: $dir/"
            errors=$((errors + 1))
        fi
    done
    
    # 4. 检查配置文件
    if [[ -f "config/pyproject.toml" ]]; then
        print_success "项目配置: config/pyproject.toml"
    else
        print_error "缺失项目配置"
        errors=$((errors + 1))
    fi
    
    # 5. 检查.gitignore
    if grep -q "data/" .gitignore 2>/dev/null; then
        print_success ".gitignore包含数据目录排除"
    else
        print_warning ".gitignore可能未排除数据目录"
        warnings=$((warnings + 1))
    fi
    
    # 总结
    echo ""
    print_info "验证结果:"
    if [[ $errors -eq 0 ]]; then
        print_success "✅ 结构验证通过 (错误: $errors, 警告: $warnings)"
        return 0
    else
        print_error "❌ 结构验证失败 (错误: $errors, 警告: $warnings)"
        return 1
    fi
}

# 函数：验证基本功能
validate_basic_functionality() {
    print_info "验证基本功能..."
    
    cd "$PROJECT_PATH" || return 1
    
    local errors=0
    
    # 1. 检查Python版本
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python版本: $python_version"
    else
        print_error "未找到Python3"
        errors=$((errors + 1))
    fi
    
    # 2. 检查数据库连接
    print_info "测试数据库连接..."
    python3 -c "
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from core.database.connection import db
    from core.database.migrations import create_tables
    
    # 确保数据目录存在
    os.makedirs('data', exist_ok=True)
    
    # 测试连接
    conn = db.get_connection()
    print('✅ 数据库连接成功')
    
    # 测试创建表
    create_tables()
    print('✅ 数据库表创建成功')
    
    conn.close()
    
except Exception as e:
    print(f'❌ 数据库测试失败: {e}')
    sys.exit(1)
" 2>&1
    
    if [[ $? -eq 0 ]]; then
        print_success "数据库测试通过"
    else
        print_error "数据库测试失败"
        errors=$((errors + 1))
    fi
    
    # 3. 检查启动脚本
    if [[ -f "start.py" ]] && [[ -x "start.py" ]]; then
        print_success "启动脚本: start.py (可执行)"
    elif [[ -f "start.py" ]]; then
        print_success "启动脚本: start.py"
    else
        print_warning "未找到启动脚本"
    fi
    
    # 总结
    echo ""
    if [[ $errors -eq 0 ]]; then
        print_success "✅ 基本功能验证通过"
        return 0
    else
        print_error "❌ 基本功能验证失败 (错误: $errors)"
        return 1
    fi
}

# 函数：提交到Git
commit_to_git() {
    print_info "提交到Git..."
    
    cd "$PROJECT_PATH" || return 1
    
    local commit_message="${1:-项目验证和优化}"
    
    # 检查是否有更改
    if [[ -z $(git status --porcelain) ]]; then
        print_info "没有更改需要提交"
        return 0
    fi
    
    # 添加所有更改
    print_info "添加更改..."
    git add .
    
    # 提交
    print_info "提交更改: $commit_message"
    git commit -m "$commit_message"
    
    if [[ $? -eq 0 ]]; then
        print_success "提交成功"
    else
        print_error "提交失败"
        return 1
    fi
    
    # 推送到远程
    print_info "推送到GitHub..."
    git push origin master
    
    if [[ $? -eq 0 ]]; then
        print_success "推送成功"
        return 0
    else
        print_error "推送失败"
        return 1
    fi
}

# 函数：显示验证报告
show_validation_report() {
    print_info "📋 验证报告"
    echo ""
    
    cd "$PROJECT_PATH" || return 1
    
    echo "项目信息:"
    echo "  路径: $PROJECT_PATH"
    echo "  分支: $(git branch --show-current 2>/dev/null || echo '未知')"
    echo "  远程: $(git remote get-url origin 2>/dev/null || echo '未设置')"
    echo ""
    
    echo "文件结构:"
    echo "  根目录文件: $(ls -la | grep -E "^-" | wc -l) 个"
    echo "  配置文件: config/pyproject.toml $(if [[ -f "config/pyproject.toml" ]]; then echo '✅'; else echo '❌'; fi)"
    echo "  依赖文件: config/requirements.txt $(if [[ -f "config/requirements.txt" ]]; then echo '✅'; else echo '❌'; fi)"
    echo ""
    
    echo "核心组件:"
    echo "  Web服务: web/main.py $(if [[ -f "web/main.py" ]]; then echo '✅'; else echo '❌'; fi)"
    echo "  微信API: wechat/server.py $(if [[ -f "wechat/server.py" ]]; then echo '✅'; else echo '❌'; fi)"
    echo "  MCP服务: mcp_server/server.py $(if [[ -f "mcp_server/server.py" ]]; then echo '✅'; else echo '❌'; fi)"
    echo ""
    
    echo "数据管理:"
    echo "  数据库连接: core/database/connection.py $(if [[ -f "core/database/connection.py" ]]; then echo '✅'; else echo '❌'; fi)"
    echo "  数据目录: data/ $(if [[ -d "data" ]]; then echo '✅'; else echo '❌'; fi)"
    echo ""
    
    echo "文档:"
    echo "  README.md: $(if [[ -f "README.md" ]]; then echo '✅'; else echo '❌'; fi)"
    echo "  项目总结: PROJECT_SUMMARY.md $(if [[ -f "PROJECT_SUMMARY.md" ]]; then echo '✅'; else echo '❌'; fi)"
    echo "  启动指南: ONE_COMMAND_START.md $(if [[ -f "ONE_COMMAND_START.md" ]]; then echo '✅'; else echo '❌'; fi)"
}

# 函数：显示帮助
show_help() {
    echo "项目验证和提交脚本"
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  status       检查项目状态"
    echo "  validate     验证项目结构"
    echo "  test         测试基本功能"
    echo "  commit       提交更改到Git"
    echo "  full         完整验证和提交"
    echo "  report       显示验证报告"
    echo "  help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 full      # 完整验证并提交"
    echo "  $0 status    # 检查状态"
    echo "  $0 validate  # 验证结构"
    echo "  $0 report    # 显示报告"
    echo ""
    echo "项目路径: $PROJECT_PATH"
}

# 主程序
main() {
    print_info "🔍 项目验证和提交脚本"
    echo "项目: 题库管理系统"
    echo "路径: $PROJECT_PATH"
    echo ""
    
    case "${1:-help}" in
        "status")
            check_project_status
            ;;
        "validate")
            validate_project_structure
            ;;
        "test")
            validate_basic_functionality
            ;;
        "commit")
            commit_to_git "${2:-项目验证和优化}"
            ;;
        "full")
            check_project_status
            if [[ $? -eq 0 ]] || [[ $? -eq 2 ]]; then
                validate_project_structure
                if [[ $? -eq 0 ]]; then
                    validate_basic_functionality
                    if [[ $? -eq 0 ]]; then
                        commit_to_git "项目验证通过，结构优化"
                    fi
                fi
            fi
            ;;
        "report")
            show_validation_report
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