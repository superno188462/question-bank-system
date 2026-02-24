#!/bin/bash
# 开发环境启动脚本
# 支持热重载和调试

set -e

# 颜色定义
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  题库系统 - 开发环境启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3${NC}"
    exit 1
fi

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo -e "${GREEN}[1/5] 激活虚拟环境...${NC}"
    source .venv/bin/activate
fi

# 检查依赖
echo -e "${YELLOW}[2/5] 检查依赖...${NC}"
if ! python3 -c "import fastapi" &> /dev/null; then
    echo -e "${YELLOW}安装依赖...${NC}"
    pip install fastapi uvicorn pydantic
fi

# 显示配置
echo -e "${YELLOW}[3/5] 加载配置...${NC}"
export HOST=0.0.0.0
export PORT=${PORT:-8000}
export RELOAD=true
export LOG_LEVEL=debug

echo "主机: $HOST (外网可访问)"
echo "端口: $PORT"
echo "热重载: 启用"
echo "日志级别: $LOG_LEVEL"

# 检查端口占用
echo -e "${YELLOW}[4/5] 检查端口 $PORT...${NC}"
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}端口 $PORT 已被占用，尝试端口 $((PORT+1))...${NC}"
    PORT=$((PORT+1))
    export PORT=$PORT
fi

# 创建必要目录
echo -e "${YELLOW}[5/5] 创建目录...${NC}"
mkdir -p uploads
mkdir -p logs

# 启动服务
echo -e "${GREEN}✅ 服务启动成功！${NC}"
echo ""
echo -e "${BLUE}访问地址:${NC}"
echo -e "本地访问: ${GREEN}http://localhost:$PORT${NC}"
echo -e "网络访问: ${GREEN}http://$(hostname -I | awk '{print $1}'):$PORT${NC}"
echo -e "API文档: ${GREEN}http://localhost:$PORT/docs${NC}"
echo -e "ReDoc文档: ${GREEN}http://localhost:$PORT/redoc${NC}"
echo ""
echo -e "${YELLOW}📝 开发功能:${NC}"
echo "- 热重载: 代码修改后自动重启"
echo "- 详细日志: 显示请求和错误信息"
echo "- CORS 启用: 支持前端开发"
echo ""
echo -e "${YELLOW}🛑 按 Ctrl+C 停止服务${NC}"
echo ""

# 启动 uvicorn
exec uvicorn src.interfaces.web_interface:app \
    --host $HOST \
    --port $PORT \
    --reload \
    --log-level $LOG_LEVEL \
    --reload-dir src \
    --reload-include "*.py"