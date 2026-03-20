@echo off
chcp 65001 >nul
echo ==========================================
echo 🚀 题库系统 Web 服务启动脚本 (Windows)
echo ==========================================
echo.

REM 检查Python环境
echo ℹ️ 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python已安装

REM 检查虚拟环境
if not exist ".venv\Scripts\activate.bat" (
    echo ℹ️ 创建虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 错误: 创建虚拟环境失败
        pause
        exit /b 1
    )
)
echo ✅ 虚拟环境就绪

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 安装依赖
echo ℹ️ 安装依赖...
pip install -q fastapi uvicorn pydantic jinja2
if errorlevel 1 (
    echo ❌ 错误: 安装依赖失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

REM 启动Web服务
echo.
echo ==========================================
echo 🚀 启动Web服务器...
echo 📡 地址: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
echo ==========================================
echo.
echo 按 Ctrl+C 停止服务
echo.

python web\main.py

pause
