#!/bin/bash
# 一键启动所有前端服务

set -e  # 遇到错误退出

echo "🚀 题库系统 - 一键启动所有前端服务"
echo "======================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到python3，请先安装Python"
    exit 1
fi

# 检查依赖
if [ ! -f "config/requirements.txt" ]; then
    echo "❌ 未找到config/requirements.txt，请确保在项目根目录"
    exit 1
fi

# 检查数据库
if [ ! -f "data/question_bank.db" ]; then
    echo "⚠️  数据库文件不存在，正在初始化..."
    python3 start.py init
fi

echo ""
echo "📡 启动三个服务进程..."
echo "   🌐 Web入口: http://localhost:8000"
echo "   🤖 MCP入口: http://localhost:8001"
echo "   📱 微信入口: http://localhost:8002"
echo ""

# 创建日志目录
mkdir -p logs

# 启动Web服务（后台运行，使用nohup防止终端关闭影响）
echo "🌐 启动Web服务..."
nohup python3 start.py web > logs/web.log 2>&1 &
WEB_PID=$!
echo "   PID: $WEB_PID, 日志: logs/web.log"
sleep 5  # 给Web服务更多时间启动

# 检查Web服务是否启动成功
if ! kill -0 $WEB_PID 2>/dev/null; then
    echo "❌ Web服务启动失败，检查日志: logs/web.log"
    tail -20 logs/web.log
    exit 1
fi

# 启动MCP服务（后台运行）
echo "🤖 启动MCP服务..."
nohup python3 start.py mcp > logs/mcp.log 2>&1 &
MCP_PID=$!
echo "   PID: $MCP_PID, 日志: logs/mcp.log"
sleep 3

# 启动微信服务（后台运行）
echo "📱 启动微信服务..."
nohup python3 start.py wechat > logs/wechat.log 2>&1 &
WECHAT_PID=$!
echo "   PID: $WECHAT_PID, 日志: logs/wechat.log"
sleep 3

echo ""
echo "✅ 所有服务已启动！"
echo ""
echo "📊 服务状态:"
echo "   🌐 Web入口: http://localhost:8000"
echo "      文档: http://localhost:8000/docs"
echo "      前端: http://localhost:8000/static/index.html"
echo "   🤖 MCP入口: http://localhost:8001"
echo "      通过MCP客户端连接"
echo "   📱 微信入口: http://localhost:8002"
echo "      微信小程序API"
echo ""
echo "📝 查看日志:"
echo "   tail -f logs/web.log     # Web服务日志"
echo "   tail -f logs/mcp.log     # MCP服务日志"
echo "   tail -f logs/wechat.log  # 微信服务日志"
echo ""
echo "🛑 停止服务:"
echo "   1. 运行: ./scripts/stop_all.sh"
echo "   2. 或手动: kill $WEB_PID $MCP_PID $WECHAT_PID"
echo "   3. 或运行: pkill -f 'python.*start.py'"
echo ""
echo "🔍 检查服务状态:"
echo "   python3 start.py status"
echo ""

# 保存PID到文件
echo "$WEB_PID $MCP_PID $WECHAT_PID" > .service_pids
echo "服务PID已保存到 .service_pids"

# 等待用户中断
echo "按 Ctrl+C 停止所有服务并退出"
echo ""

trap 'echo ""; echo "🛑 正在停止所有服务..."; kill $WEB_PID $MCP_PID $WECHAT_PID 2>/dev/null; wait $WEB_PID $MCP_PID $WECHAT_PID 2>/dev/null; echo "✅ 所有服务已停止"; rm -f .service_pids; exit 0' INT

# 等待
while true; do
    sleep 1
done