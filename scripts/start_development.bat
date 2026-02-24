@echo off
chcp 65001 > nul
echo ==========================================
echo   题库系统开发服务器启动脚本
echo ==========================================
echo.

echo [INFO] 检查虚拟环境...
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] 虚拟环境不存在，请先运行 QUICK_START_WINDOWS.bat
    pause
    exit /b 1
)

echo [INFO] 激活虚拟环境...
call .venv\Scripts\activate.bat

echo [INFO] 检查依赖...
python -c "import fastapi, uvicorn, sqlite3" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] 依赖未安装，请先运行 QUICK_START_WINDOWS.bat
    pause
    exit /b 1
)

echo [INFO] 检查数据库...
if not exist "data/question_bank.db" (
    echo [WARNING] 数据库文件不存在，尝试初始化...
    python setup_uv.py
    if %errorlevel% neq 0 (
        python -c "from src.core.question_bank_system import QuestionBankSystem; system = QuestionBankSystem(); system.initialize()"
    )
)

echo [INFO] 启动服务器...
echo [INFO] 访问地址: http://localhost:8000/
echo [INFO] API文档: http://localhost:8000/docs
echo [INFO] 按 Ctrl+C 停止服务器
echo.

uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000 --reload

echo.
echo [INFO] 服务器已停止
pause