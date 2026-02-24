#!/bin/bash

# 前端验证脚本
# 验证Web前端文件是否有效

echo "=========================================="
echo "  前端文件验证"
echo "=========================================="
echo ""

# 检查文件是否存在
echo "[1/4] 检查前端文件..."
FILES=("static/index.html" "simple_frontend.html")
missing_files=()

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ 找到: $file"
        # 检查文件大小
        size=$(wc -c < "$file")
        echo "   大小: $((size/1024)) KB"
        
        # 检查基本HTML结构
        if grep -q "<!DOCTYPE html>" "$file" && grep -q "<html" "$file" && grep -q "</html>" "$file"; then
            echo "   HTML结构: 有效"
        else
            echo "   ⚠️  HTML结构可能不完整"
        fi
    else
        echo "❌ 缺失: $file"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "错误: 缺失 ${#missing_files[@]} 个前端文件"
    exit 1
fi

# 检查HTML语法
echo ""
echo "[2/4] 检查HTML语法..."
if command -v tidy &> /dev/null; then
    echo "使用tidy检查HTML语法..."
    tidy -q -errors static/index.html 2>&1 | head -20
else
    echo "跳过HTML语法检查 (tidy未安装)"
fi

# 检查JavaScript功能
echo ""
echo "[3/4] 检查JavaScript功能..."
for file in "${FILES[@]}"; do
    echo "检查 $file 的JavaScript..."
    
    # 检查是否有基本的JS函数
    if grep -q "function.*addQuestion\|async.*addQuestion" "$file"; then
        echo "  ✅ 找到添加题目函数"
    else
        echo "  ⚠️  未找到添加题目函数"
    fi
    
    if grep -q "function.*searchQuestions\|async.*searchQuestions" "$file"; then
        echo "  ✅ 找到搜索函数"
    else
        echo "  ⚠️  未找到搜索函数"
    fi
    
    if grep -q "fetch.*localhost:8000" "$file"; then
        echo "  ✅ 找到API调用"
    else
        echo "  ⚠️  未找到API调用"
    fi
done

# 测试API连接
echo ""
echo "[4/4] 测试API连接..."
echo "检查服务器是否运行..."

# 尝试连接本地服务器
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ 服务器正在运行 (localhost:8000)"
    
    # 测试API端点
    echo "测试API端点..."
    if curl -s http://localhost:8000/questions/?limit=1 | grep -q "questions"; then
        echo "✅ /questions/ API 工作正常"
    else
        echo "⚠️  /questions/ API 可能有问题"
    fi
    
else
    echo "⚠️  服务器未运行在 localhost:8000"
    echo "   请先启动服务器: python -m uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000"
fi

echo ""
echo "=========================================="
echo "  验证结果"
echo "=========================================="
echo ""
echo "前端文件验证完成。"
echo ""
echo "使用说明:"
echo "1. 完整版前端: http://localhost:8000/static/index.html"
echo "2. 简化版前端: 直接打开 simple_frontend.html"
echo "3. API文档: http://localhost:8000/docs"
echo ""
echo "如果服务器未运行，请先启动:"
echo "  python -m uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000"