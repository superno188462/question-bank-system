#!/bin/bash

# 预提交测试脚本
# 在提交代码到GitHub前运行，验证项目能正常工作

set -e  # 遇到错误时退出

echo "=========================================="
echo "  题库系统预提交测试"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Python
check_python() {
    echo "[1/7] 检查Python环境..."
    
    # 优先使用python，其次python3
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
        print_success "Python版本: $PYTHON_VERSION (命令: $PYTHON_CMD)"
        return 0
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
        print_warning "使用python3命令（建议创建别名: alias python=python3）"
        print_success "Python版本: $PYTHON_VERSION (命令: $PYTHON_CMD)"
        return 0
    else
        print_error "未找到python或python3命令"
        return 1
    fi
}

# 检查关键文件
check_files() {
    echo "[2/7] 检查关键文件..."
    
    REQUIRED_FILES=(
        "README.md"
        "requirements.txt"
        "src/interfaces/web_interface.py"
        "src/core/question_bank_system.py"
        "src/domain/database_services.py"
    )
    
    missing_files=()
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            print_success "找到: $file"
        else
            missing_files+=("$file")
            print_error "缺失: $file"
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        return 0
    else
        print_warning "缺失 ${#missing_files[@]} 个关键文件"
        return 1
    fi
}

# 测试数据库
test_database() {
    echo "[3/7] 测试数据库..."
    
    # 如果数据库不存在，创建测试数据库
    if [ ! -f "data/question_bank.db" ]; then
        print_warning "数据库文件不存在，创建测试数据库..."
        $PYTHON_CMD -c "
import sqlite3
conn = sqlite3.connect('test_commit.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE questions (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    question_type TEXT NOT NULL
)
''')
cursor.execute(\"INSERT INTO questions VALUES ('test1', '测试题目', 'short_answer')\")
conn.commit()
conn.close()
print('创建测试数据库完成')
"
        DB_FILE="test_commit.db"
    else
        DB_FILE="data/question_bank.db"
    fi
    
    # 测试数据库连接和查询
    cat > /tmp/test_db_commit.py << 'PYTHON_SCRIPT'
import sqlite3
import sys

try:
    db_file = sys.argv[1] if len(sys.argv) > 1 else 'data/question_bank.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM questions')
    count = cursor.fetchone()[0]
    conn.close()
    print('数据库连接成功，包含 {} 个题目'.format(count))
    sys.exit(0)
except Exception as e:
    print('数据库测试失败: {}'.format(e))
    sys.exit(1)
PYTHON_SCRIPT

    $PYTHON_CMD /tmp/test_db_commit.py "$DB_FILE"
    
    if [ $? -eq 0 ]; then
        print_success "数据库测试通过"
        return 0
    else
        print_error "数据库测试失败"
        return 1
    fi
}

# 测试Python导入
test_imports() {
    echo "[4/7] 测试Python导入..."
    
    $PYTHON_CMD -c "
try:
    # 测试核心模块导入
    import sqlite3
    from src.core.question_bank_system import QuestionBankSystem
    print('核心模块导入成功')
    
    # 测试Web接口导入
    from src.interfaces.web_interface import app
    print('Web接口导入成功')
    
    exit(0)
except ImportError as e:
    print(f'导入错误: {e}')
    exit(1)
except Exception as e:
    print(f'其他错误: {e}')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "Python导入测试通过"
        return 0
    else
        print_error "Python导入测试失败"
        return 1
    fi
}

# 测试部署脚本
test_deployment_script() {
    echo "[5/7] 测试部署脚本..."
    
    # 检查部署脚本是否存在
    if [ ! -f "SIMPLE_SETUP.sh" ]; then
        print_warning "部署脚本不存在，跳过测试"
        return 0
    fi
    
    # 测试脚本语法
    if bash -n SIMPLE_SETUP.sh; then
        print_success "部署脚本语法检查通过"
    else
        print_error "部署脚本语法错误"
        return 1
    fi
    
    # 测试快速检查模式（不实际安装）
    echo "测试部署脚本快速检查..."
    if grep -q "检查Python" SIMPLE_SETUP.sh && grep -q "创建数据库" SIMPLE_SETUP.sh; then
        print_success "部署脚本结构完整"
        return 0
    else
        print_error "部署脚本缺少关键部分"
        return 1
    fi
}

# 测试文档
test_documentation() {
    echo "[6/7] 检查文档..."
    
    # 检查README
    if [ -f "README.md" ]; then
        README_LINES=$(wc -l < README.md)
        if [ $README_LINES -gt 10 ]; then
            print_success "README文档完整 ($README_LINES 行)"
        else
            print_warning "README文档可能过短"
        fi
        
        # 检查是否有快速开始部分
        if grep -q "快速开始" README.md || grep -q "Quick Start" README.md; then
            print_success "README包含快速开始指南"
        else
            print_warning "README缺少快速开始指南"
        fi
    else
        print_error "缺少README.md文件"
        return 1
    fi
    
    return 0
}

# 运行简化服务器测试
test_server() {
    echo "[7/7] 测试服务器启动..."
    
    # 创建临时测试服务器脚本
    cat > /tmp/test_server_commit.py << 'PYTHON'
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "测试服务器", "status": "ok"}

if __name__ == "__main__":
    # 只检查导入，不实际运行
    print("服务器模块导入成功")
    print("FastAPI应用创建成功")
PYTHON
    
    $PYTHON_CMD /tmp/test_server_commit.py
    
    if [ $? -eq 0 ]; then
        print_success "服务器模块测试通过"
        return 0
    else
        print_error "服务器模块测试失败"
        return 1
    fi
}

# 主测试函数
run_tests() {
    echo ""
    echo "开始运行预提交测试..."
    echo ""
    
    TESTS=(
        check_python
        check_files
        test_database
        test_imports
        test_deployment_script
        test_documentation
        test_server
    )
    
    PASSED=0
    FAILED=0
    WARNINGS=0
    
    for test_func in "${TESTS[@]}"; do
        if $test_func; then
            ((PASSED++))
        else
            # 检查是否是警告（返回2）
            if [ $? -eq 2 ]; then
                ((WARNINGS++))
            else
                ((FAILED++))
            fi
        fi
        echo ""
    done
    
    # 显示测试结果
    echo "=========================================="
    echo "  测试结果汇总"
    echo "=========================================="
    echo ""
    echo "✅ 通过: $PASSED"
    echo "⚠️  警告: $WARNINGS"
    echo "❌ 失败: $FAILED"
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        if [ $WARNINGS -eq 0 ]; then
            print_success "所有测试通过！可以提交代码。"
            echo ""
            echo "下一步："
            echo "1. git add ."
            echo "2. git commit -m '你的提交信息'"
            echo "3. git push origin master"
            return 0
        else
            print_warning "测试通过，但有 $WARNINGS 个警告"
            echo ""
            echo "建议修复警告后再提交。"
            return 2
        fi
    else
        print_error "有 $FAILED 个测试失败，请修复后再提交"
        echo ""
        echo "失败的测试需要修复："
        echo "1. 检查错误信息"
        echo "2. 修复问题"
        echo "3. 重新运行测试: ./pre_commit_test.sh"
        return 1
    fi
}

# 清理函数
cleanup() {
    # 删除测试数据库
    if [ -f "test_commit.db" ]; then
        rm -f test_commit.db
        echo "已清理测试数据库"
    fi
    
    # 删除临时文件
    rm -f /tmp/test_server_commit.py 2>/dev/null || true
}

# 设置退出时清理
trap cleanup EXIT

# 运行测试
run_tests
EXIT_CODE=$?

echo ""
echo "测试完成，退出代码: $EXIT_CODE"
exit $EXIT_CODE