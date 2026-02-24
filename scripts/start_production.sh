#!/bin/bash
# 生产环境启动脚本
# 支持外网访问

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  题库系统 - 生产环境启动脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3${NC}"
    exit 1
fi

# 检查依赖
echo -e "${YELLOW}[1/5] 检查依赖...${NC}"
if ! python3 -c "import fastapi" &> /dev/null; then
    echo -e "${RED}错误: 缺少 FastAPI 依赖${NC}"
    echo "请运行: pip install fastapi uvicorn pydantic"
    exit 1
fi

# 显示配置
echo -e "${YELLOW}[2/5] 加载配置...${NC}"
python3 production_config.py

# 检查端口占用
PORT=${PORT:-8000}
echo -e "${YELLOW}[3/5] 检查端口 $PORT...${NC}"
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}错误: 端口 $PORT 已被占用${NC}"
    echo "请修改 PORT 环境变量或停止占用端口的进程"
    exit 1
fi

# 创建必要目录
echo -e "${YELLOW}[4/5] 创建目录...${NC}"
mkdir -p uploads
mkdir -p logs

# 启动服务
echo -e "${YELLOW}[5/5] 启动服务...${NC}"
echo -e "${GREEN}服务将在以下地址启动:${NC}"
echo -e "本地访问: ${GREEN}http://localhost:$PORT${NC}"
echo -e "网络访问: ${GREEN}http://$(hostname -I | awk '{print $1}'):$PORT${NC}"
echo -e "外网访问: ${GREEN}http://<你的公网IP>:$PORT${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

# 设置环境变量并启动
export HOST=0.0.0.0
export PORT=$PORT
export WORKERS=4
export RELOAD=false
export LOG_LEVEL=info

# 启动 uvicorn
exec uvicorn src.interfaces.web_interface:app \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    --log-level $LOG_LEVEL \
    --access-log