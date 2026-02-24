#!/bin/bash
# 快速启动所有服务 - 简化版

set -e

echo "🚀 题库系统 - 快速启动所有服务"
echo "======================================"

# 检查Python和依赖
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到python3"
    exit 1
fi

# 检查是否在项目根目录
if [ ! -f "start.py" ]; then
    echo "❌ 请在项目根目录运行"
    exit 1
fi

# 初始化数据库
echo "🔧 初始化数据库..."
python3 start.py init

echo ""
echo "📡 启动三个服务..."
echo ""

# 方法1：使用tmux启动三个窗口（如果可用）
if command -v tmux &> /dev/null; then
    echo "🎭 使用tmux启动三个服务窗口..."
    tmux new-session -d -s question-bank "python3 start.py web"
    tmux split-window -h "python3 start.py mcp"
    tmux split-window -v "python3 start.py wechat"
    tmux select-pane -t 0
    tmux attach-session -t question-bank
    exit 0
fi

# 方法2：使用screen启动三个窗口（如果可用）
if command -v screen &> /dev/null; then
    echo "🖥️  使用screen启动三个服务窗口..."
    screen -dmS question-bank-web python3 start.py web
    screen -dmS question-bank-mcp python3 start.py mcp
    screen -dmS question-bank-wechat python3 start.py wechat
    echo "✅ 服务已在后台启动"
    echo "📋 查看服务: screen -ls"
    echo "🔍 连接Web服务: screen -r question-bank-web"
    echo "🔍 连接MCP服务: screen -r question-bank-mcp"
    echo "🔍 连接微信服务: screen -r question-bank-wechat"
    exit 0
fi

# 方法3：直接在前台启动（最简单）
echo "📱 直接启动服务（需要三个终端）..."
echo ""
echo "请打开三个终端，分别运行:"
echo ""
echo "终端1 - Web服务:"
echo "  cd $(pwd)"
echo "  python3 start.py web"
echo ""
echo "终端2 - MCP服务:"
echo "  cd $(pwd)"
echo "  python3 start.py mcp"
echo ""
echo "终端3 - 微信服务:"
echo "  cd $(pwd)"
echo "  python3 start.py wechat"
echo ""
echo "📊 服务地址:"
echo "  🌐 Web: http://localhost:8000"
echo "  🤖 MCP: http://localhost:8001"
echo "  📱 微信: http://localhost:8002"
echo ""
echo "🛑 停止服务: 在每个终端按 Ctrl+C"