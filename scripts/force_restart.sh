#!/bin/bash
# 强制完全重启脚本 - 清除所有缓存

echo "🧹 强制完全重启..."

# 1. 停止所有Python进程
echo "1. 停止所有Python进程..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    taskkill //F //IM python.exe 2>/dev/null || true
    taskkill //F //IM pythonw.exe 2>/dev/null || true
else
    # Linux/Mac
    pkill -9 -f "python.*main.py" 2>/dev/null || true
    pkill -9 -f "uvicorn" 2>/dev/null || true
fi

sleep 2

# 2. 清除Python缓存
echo "2. 清除Python缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# 3. 删除pid文件
echo "3. 清理pid文件..."
rm -f .web_pid .wechat_pid .mcp_pid

# 4. 验证端口释放
echo "4. 检查端口状态..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    netstat -ano | grep ":8000" || echo "✅ 端口8000已释放"
else
    lsof -ti:8000 || echo "✅ 端口8000已释放"
fi

echo ""
echo "✅ 清理完成！"
echo ""
echo "现在可以重新启动服务:"
echo "  ./run.sh web"
