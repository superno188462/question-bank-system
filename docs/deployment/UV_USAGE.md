# UV 使用指南

## 快速开始

```bash
# 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
uv pip install -e ".[dev]"
```

## 常用命令

```bash
# 添加依赖
uv add package-name
uv add --dev package-name

# 运行脚本
uv run python script.py

# 代码质量
uv run black src/
uv run ruff check src/

# 启动服务
uv run uvicorn app.main:app --reload
```

## 更多信息

查看项目 README.md 获取完整使用说明。
