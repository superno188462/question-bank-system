@echo off
chcp 65001 > nul
echo ==========================================
echo   题库系统快速部署脚本 (Windows版本)
echo ==========================================
echo.

echo [INFO] 开始部署题库系统...
echo.

REM 步骤1: 检查Python
echo [INFO] 检查Python版本...
where python >nul 2>nul
if %errorlevel% equ 0 (
    python --version
    echo [INFO] Python已安装
) else (
    where python3 >nul 2>nul
    if %errorlevel% equ 0 (
        python3 --version
        echo [INFO] Python3已安装
    ) else (
        echo [ERROR] 未找到Python，请先安装Python 3.8+
        echo 下载地址: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

REM 步骤2: 检查Git
echo.
echo [INFO] 检查Git...
where git >nul 2>nul
if %errorlevel% equ 0 (
    git --version
    echo [INFO] Git已安装
) else (
    echo [WARNING] Git未安装，将无法更新代码
    echo 下载地址: https://git-scm.com/download/win
)

REM 步骤3: 创建虚拟环境
echo.
echo [INFO] 创建虚拟环境...
if exist .venv (
    echo [INFO] 虚拟环境已存在
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo [INFO] 虚拟环境创建成功
)

REM 步骤4: 激活虚拟环境
echo.
echo [INFO] 激活虚拟环境...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] 激活虚拟环境失败
    pause
    exit /b 1
)
echo [INFO] 虚拟环境已激活

REM 步骤5: 安装依赖
echo.
echo [INFO] 安装依赖...
pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [ERROR] 升级pip失败
    pause
    exit /b 1
)

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] 安装依赖失败
    echo 尝试使用国内镜像: pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    pause
    exit /b 1
)

pip install -r requirements-dev.txt
if %errorlevel% neq 0 (
    echo [WARNING] 安装开发依赖失败，继续...
)

echo [INFO] 依赖安装成功

REM 步骤6: 初始化数据库
echo.
echo [INFO] 初始化数据库...
python setup_uv.py
if %errorlevel% neq 0 (
    echo [WARNING] 初始化脚本失败，尝试手动初始化...
    python -c "from src.core.question_bank_system import QuestionBankSystem; system = QuestionBankSystem(); system.initialize(); print('数据库初始化完成')"
)

if exist data/question_bank.db (
    echo [INFO] 数据库文件创建成功: data/question_bank.db
) else (
    echo [ERROR] 数据库文件创建失败
    pause
    exit /b 1
)

REM 步骤7: 启动服务器
echo.
echo [INFO] 启动开发服务器...
echo [INFO] 服务器将在后台启动，按Ctrl+C停止

REM 检查是否有启动脚本
if exist start_development.bat (
    echo [INFO] 使用启动脚本...
    start_development.bat
) else if exist start_development.sh (
    echo [INFO] 使用Shell启动脚本...
    bash start_development.sh
) else (
    echo [INFO] 手动启动服务器...
    uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000 --reload
)

echo.
echo ==========================================
echo       部署完成！访问信息如下
echo ==========================================
echo.
echo 🌐 本地访问:
echo    http://localhost:8000/
echo    http://localhost:8000/docs (API文档)
echo.
echo 📱 局域网访问:
echo    1. 按 Win+R 输入 cmd 打开命令提示符
echo    2. 输入 ipconfig 查看IPv4地址
echo    3. 在其他设备访问: http://<你的IP>:8000/
echo.
echo 🔧 管理命令:
echo    停止服务器: 按 Ctrl+C
echo    重新启动: 再次运行此脚本
echo.
echo 📚 快速测试:
echo    测试API:    curl http://localhost:8000/
echo    或直接在浏览器打开上面地址
echo.
echo 💡 提示:
echo    1. 确保Windows防火墙允许8000端口
echo    2. 如需外网访问，需要配置公网IP或内网穿透
echo    3. 详细文档请查看 README.md 和 DEPLOYMENT_GUIDE.md
echo.
echo 按任意键退出...
pause >nul