# 使用官方 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV WORKERS=4
ENV RELOAD=false

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv（极速 Python 包管理器）
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# 复制项目文件
COPY pyproject.toml requirements.txt requirements-dev.txt ./
COPY src/ ./src/

# 创建必要目录
RUN mkdir -p uploads logs

# 使用 uv 安装依赖
RUN uv venv
RUN uv pip install --system -r requirements.txt

# 复制启动脚本
COPY start_production.sh ./
RUN chmod +x start_production.sh

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["./start_production.sh"]