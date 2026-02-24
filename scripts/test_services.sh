#!/bin/bash
# 测试所有服务是否正常工作

set -e

echo "🔍 题库系统服务测试"
echo "======================================"

# 检查是否在项目根目录
if [ ! -f "start.py" ]; then
    echo "❌ 请在项目根目录运行"
    exit 1
fi

echo ""
echo "1. 检查项目状态..."
python3 start.py status

echo ""
echo "2. 测试数据库连接..."
if python3 -c "
from core.database.connection import db
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM questions')
count = cursor.fetchone()[0]
print(f'✅ 数据库连接正常，题目数量: {count}')
"; then
    echo "✅ 数据库测试通过"
else
    echo "❌ 数据库测试失败"
    exit 1
fi

echo ""
echo "3. 测试Web应用创建..."
if python3 -c "
from web.main import create_web_app
app = create_web_app()
print('✅ Web应用创建成功')
"; then
    echo "✅ Web应用测试通过"
else
    echo "❌ Web应用测试失败"
    exit 1
fi

echo ""
echo "4. 测试MCP应用创建..."
if python3 -c "
from mcp_server.server import app
print('✅ MCP应用导入成功')
"; then
    echo "✅ MCP应用测试通过"
else
    echo "❌ MCP应用测试失败"
    exit 1
fi

echo ""
echo "5. 测试微信应用创建..."
if python3 -c "
from wechat.server import create_wechat_app
app = create_wechat_app()
print('✅ 微信应用创建成功')
"; then
    echo "✅ 微信应用测试通过"
else
    echo "❌ 微信应用测试失败"
    exit 1
fi

echo ""
echo "6. 测试核心服务..."
if python3 -c "
from core.services import QuestionService, CategoryService, TagService
print('✅ 核心服务导入成功')
"; then
    echo "✅ 核心服务测试通过"
else
    echo "❌ 核心服务测试失败"
    exit 1
fi

echo ""
echo "======================================"
echo "🎉 所有服务测试通过！"
echo ""
echo "📡 服务地址："
echo "   🌐 Web: http://localhost:8000"
echo "   🤖 MCP: http://localhost:8001"
echo "   📱 微信: http://localhost:8002"
echo ""
echo "🚀 启动服务："
echo "   方案A: 分别启动三个终端"
echo "   方案B: ./scripts/start_all.sh"
echo "   方案C: ./scripts/quick_start.sh"