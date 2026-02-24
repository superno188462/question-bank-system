#!/bin/bash

# 提交后检查脚本
# 验证提交后的项目状态

echo "=========================================="
echo "  提交后项目状态检查"
echo "=========================================="
echo ""

# 检查当前提交
echo "📊 检查Git状态..."
git log --oneline -1
echo ""

# 检查文件变更
echo "📁 本次提交的文件变更:"
git diff --name-only HEAD~1 HEAD
echo ""

# 运行快速测试
echo "🧪 运行快速功能测试..."
echo ""

# 确定Python命令
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "⚠️  使用python3命令（建议: alias python=python3）"
else
    echo "❌ 未找到python或python3命令"
    exit 1
fi

# 1. 检查Python导入
echo "[1/4] 检查Python导入..."
$PYTHON_CMD -c "
try:
    import sqlite3
    print('✅ sqlite3 导入成功')
    
    # 尝试导入项目模块
    try:
        from src.core.question_bank_system import QuestionBankSystem
        print('✅ 项目核心模块导入成功')
    except ImportError as e:
        print(f'⚠️  项目模块导入警告: {e}')
    
    exit(0)
except Exception as e:
    print(f'❌ 导入失败: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Python导入检查通过"
else
    echo "❌ Python导入检查失败"
fi
echo ""

# 2. 检查数据库
echo "[2/4] 检查数据库..."
if [ -f "data/question_bank.db" ]; then
    echo "✅ 数据库文件存在"
    
    # 检查数据库是否可读
    python -c "
import sqlite3
try:
    conn = sqlite3.connect('data/question_bank.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
    tables = cursor.fetchall()
    print(f'✅ 数据库可访问，包含 {len(tables)} 个表')
    for table in tables:
        print(f'   - {table[0]}')
    conn.close()
except Exception as e:
    print(f'❌ 数据库访问错误: {e}')
    "
else
    echo "⚠️  数据库文件不存在（如果是新项目可能正常）"
fi
echo ""

# 3. 检查部署脚本
echo "[3/4] 检查部署脚本..."
if [ -f "SIMPLE_SETUP.sh" ]; then
    # 检查脚本语法
    if bash -n SIMPLE_SETUP.sh; then
        echo "✅ 部署脚本语法正确"
        
        # 检查脚本是否包含关键部分
        if grep -q "检查Python" SIMPLE_SETUP.sh && \
           grep -q "创建数据库" SIMPLE_SETUP.sh && \
           grep -q "启动服务器" SIMPLE_SETUP.sh; then
            echo "✅ 部署脚本功能完整"
        else
            echo "⚠️  部署脚本可能缺少关键功能"
        fi
    else
        echo "❌ 部署脚本语法错误"
    fi
else
    echo "⚠️  缺少部署脚本"
fi
echo ""

# 4. 检查文档
echo "[4/4] 检查文档..."
if [ -f "README.md" ]; then
    README_SIZE=$(wc -l < README.md)
    if [ $README_SIZE -gt 20 ]; then
        echo "✅ README文档完整 ($README_SIZE 行)"
        
        # 检查是否有使用说明
        if grep -q -i "使用\|usage\|quick start" README.md; then
            echo "✅ README包含使用说明"
        else
            echo "⚠️  README可能缺少使用说明"
        fi
    else
        echo "⚠️  README可能过短"
    fi
else
    echo "❌ 缺少README.md文件"
fi

echo ""
echo "=========================================="
echo "  检查完成"
echo "=========================================="
echo ""
echo "建议："
echo "1. 如果发现警告，考虑在下次提交中修复"
echo "2. 运行完整测试: ./pre_commit_test.sh"
echo "3. 测试部署: ./SIMPLE_SETUP.sh"
echo "4. 验证功能: python test_server.py"
echo ""
echo "保持代码质量，快乐编程！🚀"