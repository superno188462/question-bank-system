#!/bin/bash
# 停止所有前端服务

echo "🛑 题库系统 - 停止所有前端服务"
echo "======================================"

# 方法1: 使用保存的PID文件
if [ -f ".service_pids" ]; then
    echo "📋 从 .service_pids 读取服务PID..."
    read WEB_PID MCP_PID WECHAT_PID < .service_pids
    
    echo "正在停止服务..."
    
    # 停止Web服务
    if kill -0 $WEB_PID 2>/dev/null; then
        echo "🌐 停止Web服务 (PID: $WEB_PID)..."
        kill $WEB_PID
        sleep 1
    fi
    
    # 停止MCP服务
    if kill -0 $MCP_PID 2>/dev/null; then
        echo "🤖 停止MCP服务 (PID: $MCP_PID)..."
        kill $MCP_PID
        sleep 1
    fi
    
    # 停止微信服务
    if kill -0 $WECHAT_PID 2>/dev/null; then
        echo "📱 停止微信服务 (PID: $WECHAT_PID)..."
        kill $WECHAT_PID
        sleep 1
    fi
    
    # 删除PID文件
    rm -f .service_pids
    echo "✅ 通过PID文件停止完成"
    
else
    # 方法2: 通过进程名查找
    echo "🔍 通过进程名查找服务..."
    
    # 查找并停止Web服务
    WEB_PIDS=$(pgrep -f "python.*start.py web" 2>/dev/null || true)
    if [ -n "$WEB_PIDS" ]; then
        echo "🌐 停止Web服务 (PIDs: $WEB_PIDS)..."
        kill $WEB_PIDS 2>/dev/null || true
    fi
    
    # 查找并停止MCP服务
    MCP_PIDS=$(pgrep -f "python.*start.py mcp" 2>/dev/null || true)
    if [ -n "$MCP_PIDS" ]; then
        echo "🤖 停止MCP服务 (PIDs: $MCP_PIDS)..."
        kill $MCP_PIDS 2>/dev/null || true
    fi
    
    # 查找并停止微信服务
    WECHAT_PIDS=$(pgrep -f "python.*start.py wechat" 2>/dev/null || true)
    if [ -n "$WECHAT_PIDS" ]; then
        echo "📱 停止微信服务 (PIDs: $WECHAT_PIDS)..."
        kill $WECHAT_PIDS 2>/dev/null || true
    fi
    
    # 方法3: 强制停止所有相关进程
    echo "🧹 清理残留进程..."
    pkill -f "python.*start.py" 2>/dev/null || true
    
    echo "✅ 通过进程名停止完成"
fi

# 等待进程结束
sleep 2

# 检查是否还有相关进程
REMAINING=$(pgrep -f "python.*start.py" 2>/dev/null || true)
if [ -n "$REMAINING" ]; then
    echo "⚠️  仍有进程运行，强制停止..."
    pkill -9 -f "python.*start.py" 2>/dev/null || true
    sleep 1
fi

echo ""
echo "📊 最终状态检查:"
if pgrep -f "python.*start.py" >/dev/null; then
    echo "❌ 仍有服务在运行"
    pgrep -f "python.*start.py"
else
    echo "✅ 所有服务已停止"
fi

echo ""
echo "🧹 清理临时文件..."
rm -f .service_pids 2>/dev/null || true

echo "✅ 停止脚本执行完成"