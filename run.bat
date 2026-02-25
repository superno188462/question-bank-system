@echo off
REM Windows一键运行脚本
REM 题库系统Windows启动脚本

echo ========================================
echo  题库系统Windows一键启动脚本
echo ========================================
echo.

REM 检查Python环境
echo [INFO] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查uv
echo [INFO] 检查uv包管理器...
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] 未找到uv，将使用pip安装依赖
    set USE_UV=false
) else (
    echo [SUCCESS] 找到uv包管理器
    set USE_UV=true
)

REM 检查虚拟环境
echo [INFO] 检查虚拟环境...
if exist .venv\Scripts\python.exe (
    echo [SUCCESS] 找到虚拟环境: .venv
    set VENV_ACTIVE=true
    set PYTHON_CMD=.venv\Scripts\python
) else (
    echo [WARNING] 未找到虚拟环境
    set VENV_ACTIVE=false
    set PYTHON_CMD=python
)

REM 安装依赖
echo.
echo [INFO] 安装Python依赖...
if "%USE_UV%"=="true" (
    if "%VENV_ACTIVE%"=="false" (
        echo [INFO] 创建uv虚拟环境...
        uv venv
        if exist .venv\Scripts\python.exe (
            set VENV_ACTIVE=true
            set PYTHON_CMD=.venv\Scripts\python
        )
    )
    echo [INFO] 使用uv安装依赖...
    uv pip install -r config\requirements.txt
) else (
    echo [INFO] 使用pip安装依赖...
    %PYTHON_CMD% -m pip install --upgrade pip
    %PYTHON_CMD% -m pip install -r config\requirements.txt
)

REM 检查数据库
echo.
echo [INFO] 检查数据库...
if not exist data (
    mkdir data
    echo [INFO] 创建数据目录: data
)

if not exist data\question_bank.db (
    echo [INFO] 初始化数据库...
    %PYTHON_CMD% -c "
import sys
import os
sys.path.insert(0, os.getcwd())

from core.database.connection import db
from core.database.migrations import create_tables

# 确保数据目录存在
os.makedirs('data', exist_ok=True)

# 创建表
create_tables()
print('数据库初始化完成')
"
)

REM 启动服务
echo.
echo [INFO] 启动Web服务...
echo [INFO] 停止可能正在运行的服务...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo [INFO] 启动FastAPI服务...
start "Web服务" %PYTHON_CMD% web\main.py

echo [INFO] 等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查服务状态
echo.
echo [INFO] 检查服务状态...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Web服务启动成功！
    echo.
    echo ========================================
    echo  服务访问地址
    echo ========================================
    echo  管理界面: http://localhost:8000
    echo  API文档:  http://localhost:8000/docs
    echo.
    echo  按任意键打开浏览器...
    pause >nul
    start http://localhost:8000
) else (
    echo [ERROR] Web服务启动失败
    echo 请检查:
    echo  1. 端口8000是否被占用
    echo  2. 依赖是否正确安装
    echo  3. 查看日志: web.log
)

echo.
echo [INFO] 按任意键退出...
pause >nul