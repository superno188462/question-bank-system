# 题库系统Windows PowerShell启动脚本
# 用法: .\run.ps1 [命令]

param(
    [string]$Command = "start",
    [switch]$System
)

# 颜色定义
$ErrorColor = "Red"
$SuccessColor = "Green"
$WarningColor = "Yellow"
$InfoColor = "Cyan"

# 函数：打印带颜色的消息
function Write-Info($message) { Write-Host "[INFO] $message" -ForegroundColor $InfoColor }
function Write-Success($message) { Write-Host "[SUCCESS] $message" -ForegroundColor $SuccessColor }
function Write-Warning($message) { Write-Host "[WARNING] $message" -ForegroundColor $WarningColor }
function Write-Error($message) { Write-Host "[ERROR] $message" -ForegroundColor $ErrorColor }

# 显示标题
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  题库系统Windows启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 函数：检查Python环境
function Check-Python {
    Write-Info "检查Python环境..."
    
    # 检查Python
    $pythonCmd = $null
    $pythonVersion = $null
    
    # 尝试python命令
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = "python"
        }
    } catch {}
    
    # 尝试python3命令
    if (-not $pythonCmd) {
        try {
            $pythonVersion = python3 --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $pythonCmd = "python3"
            }
        } catch {}
    }
    
    if ($pythonCmd) {
        Write-Success "找到Python: $pythonCmd ($pythonVersion)"
        return $pythonCmd
    } else {
        Write-Error "未找到Python，请先安装Python 3.8+"
        Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
}

# 函数：检查uv
function Check-UV {
    Write-Info "检查uv包管理器..."
    
    try {
        $uvVersion = uv --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "找到uv包管理器: $uvVersion"
            return $true
        }
    } catch {}
    
    Write-Warning "未找到uv，将使用pip安装依赖"
    return $false
}

# 函数：检查虚拟环境
function Check-Venv {
    Write-Info "检查虚拟环境..."
    
    $venvPath = ".venv"
    $pythonPath = "$venvPath\Scripts\python.exe"
    
    if (Test-Path $pythonPath) {
        Write-Success "找到虚拟环境: $venvPath"
        return @{
            Active = $true
            PythonCmd = $pythonPath
            Path = $venvPath
        }
    } else {
        Write-Warning "未找到虚拟环境"
        return @{
            Active = $false
            PythonCmd = $script:PythonCmd
            Path = $null
        }
    }
}

# 函数：安装依赖
function Install-Dependencies {
    param(
        [string]$PythonCmd,
        [bool]$UvAvailable,
        [hashtable]$VenvInfo,
        [bool]$UseSystem
    )
    
    Write-Info "安装Python依赖..."
    
    # 检查requirements.txt
    $requirementsPath = "config\requirements.txt"
    if (-not (Test-Path $requirementsPath)) {
        Write-Error "未找到依赖文件: $requirementsPath"
        exit 1
    }
    
    if ($UvAvailable) {
        if (-not $VenvInfo.Active -and -not $UseSystem) {
            Write-Info "创建uv虚拟环境..."
            uv venv
            if (Test-Path ".venv\Scripts\python.exe") {
                $VenvInfo.Active = $true
                $VenvInfo.PythonCmd = ".venv\Scripts\python.exe"
                Write-Success "uv虚拟环境创建成功"
            }
        }
        
        if ($UseSystem) {
            Write-Warning "使用--system参数，将安装到系统Python"
            Write-Warning "注意：可能需要管理员权限"
            uv pip install --system -r $requirementsPath
        } else {
            uv pip install -r $requirementsPath
        }
    } else {
        Write-Info "使用pip安装依赖..."
        & $PythonCmd -m pip install --upgrade pip
        & $PythonCmd -m pip install -r $requirementsPath
    }
    
    Write-Success "依赖安装完成"
    return $VenvInfo
}

# 函数：初始化数据库
function Init-Database {
    param([string]$PythonCmd)
    
    Write-Info "初始化数据库..."
    
    # 创建数据目录
    if (-not (Test-Path "data")) {
        New-Item -ItemType Directory -Path "data" -Force | Out-Null
        Write-Info "创建数据目录: data"
    }
    
    # 检查数据库文件
    $dbPath = "data\question_bank.db"
    if (Test-Path $dbPath) {
        Write-Info "数据库文件已存在: $dbPath"
        $choice = Read-Host "是否重新初始化数据库？（将清空现有数据）(y/N)"
        if ($choice -eq "y" -or $choice -eq "Y") {
            Remove-Item $dbPath -Force
            Write-Info "已删除旧数据库"
        } else {
            Write-Info "使用现有数据库"
            return
        }
    }
    
    # 初始化数据库
    Write-Info "创建数据库表结构..."
    $pythonCode = @"
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
"@
    
    & $PythonCmd -c $pythonCode
    Write-Success "数据库初始化完成"
}

# 函数：启动Web服务
function Start-WebService {
    param([string]$PythonCmd)
    
    Write-Info "启动Web服务..."
    
    # 检查端口是否被占用
    $port = 8000
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($process) {
        Write-Warning "端口$port已被占用，尝试停止现有服务..."
        $process | ForEach-Object {
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 1
    }
    
    # 启动服务
    Write-Info "启动FastAPI服务..."
    $webProcess = Start-Process -FilePath $PythonCmd -ArgumentList "web\main.py" -PassThru -WindowStyle Hidden
    
    # 保存进程ID
    $webProcess.Id | Out-File -FilePath ".web_pid" -Encoding ASCII
    
    # 等待服务启动
    Start-Sleep -Seconds 3
    
    # 检查服务是否启动成功
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Success "Web服务启动成功"
            Write-Host "  🌐 管理界面: http://localhost:8000" -ForegroundColor Green
            Write-Host "  📚 API文档:  http://localhost:8000/docs" -ForegroundColor Green
            Write-Host "  🔧 PID: $($webProcess.Id)" -ForegroundColor Green
            return $true
        }
    } catch {}
    
    Write-Error "Web服务启动失败"
    return $false
}

# 函数：显示服务状态
function Show-Status {
    Write-Info "📊 服务状态"
    Write-Host ""
    
    $webStatus = "❌"
    $wechatStatus = "❌"
    $mcpStatus = "❌"
    
    # 检查Web服务
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $webStatus = "✅"
            Write-Host "  🌐 Web服务:    运行中 $webStatus" -ForegroundColor Green
            Write-Host "      管理界面: http://localhost:8000" -ForegroundColor Gray
            Write-Host "      API文档:  http://localhost:8000/docs" -ForegroundColor Gray
        } else {
            Write-Host "  🌐 Web服务:    未运行 $webStatus" -ForegroundColor Red
        }
    } catch {
        Write-Host "  🌐 Web服务:    未运行 $webStatus" -ForegroundColor Red
    }
    
    # 检查微信API服务
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $wechatStatus = "✅"
            Write-Host "  📱 微信API:    运行中 $wechatStatus" -ForegroundColor Green
            Write-Host "      接口地址: http://localhost:8001" -ForegroundColor Gray
            Write-Host "      API文档:  http://localhost:8001/docs" -ForegroundColor Gray
        } else {
            Write-Host "  📱 微信API:    未运行 $wechatStatus" -ForegroundColor Red
        }
    } catch {
        Write-Host "  📱 微信API:    未运行 $wechatStatus" -ForegroundColor Red
    }
    
    # 检查MCP服务
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8002/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $mcpStatus = "✅"
            Write-Host "  🤖 MCP服务:    运行中 $mcpStatus" -ForegroundColor Green
            Write-Host "      接口地址: http://localhost:8002" -ForegroundColor Gray
            Write-Host "      文档:     http://localhost:8002/docs" -ForegroundColor Gray
        } else {
            Write-Host "  🤖 MCP服务:    未运行 $mcpStatus" -ForegroundColor Red
        }
    } catch {
        Write-Host "  🤖 MCP服务:    未运行 $mcpStatus" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Info "📋 快速访问"
    Write-Host "  管理界面: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  API文档:  http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "  微信API:  http://localhost:8001" -ForegroundColor Cyan
    Write-Host "  MCP接口:  http://localhost:8002" -ForegroundColor Cyan
}

# 函数：停止服务
function Stop-Services {
    Write-Info "停止所有服务..."
    
    # 停止Web服务
    if (Test-Path ".web_pid") {
        $pid = Get-Content ".web_pid"
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Info "已停止Web服务 (PID: $pid)"
        } catch {}
        Remove-Item ".web_pid" -Force -ErrorAction SilentlyContinue
    }
    
    # 停止所有Python进程
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -like "*question-bank-system*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Success "所有服务已停止"
}

# 函数：显示帮助
function Show-Help {
    Write-Host "Windows一键运行脚本" -ForegroundColor Cyan
    Write-Host "用法: .\run.ps1 [命令] [选项]" -ForegroundColor White
    Write-Host ""
    Write-Host "命令:" -ForegroundColor Yellow
    Write-Host "  start        启动所有服务" -ForegroundColor White
    Write-Host "  web          只启动Web服务" -ForegroundColor White
    Write-Host "  status       显示服务状态" -ForegroundColor White
    Write-Host "  stop         停止所有服务" -ForegroundColor White
    Write-Host "  setup        安装依赖和初始化" -ForegroundColor White
    Write-Host "  help         显示此帮助信息" -ForegroundColor White
    Write-Host ""
    Write-Host "选项:" -ForegroundColor Yellow
    Write-Host "  -System      使用系统Python安装依赖" -ForegroundColor White
    Write-Host ""
    Write-Host "示例:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 start            # 一键启动所有服务" -ForegroundColor White
    Write-Host "  .\run.ps1 web              # 只启动Web服务" -ForegroundColor White
    Write-Host "  .\run.ps1 status           # 查看服务状态" -ForegroundColor White
    Write-Host "  .\run.ps1 stop             # 停止所有服务" -ForegroundColor White
    Write-Host "  .\run.ps1 setup -System    # 安装依赖到系统Python" -ForegroundColor White
    Write-Host ""
    Write-Host "跨平台支持:" -ForegroundColor Yellow
    Write-Host "  - Windows:     使用此脚本 (scripts/windows/run.ps1)" -ForegroundColor White
    Write-Host "  - Linux/macOS: 使用根目录的 run.sh" -ForegroundColor White
    Write-Host "  - 通用入口:    使用根目录的 ./run 脚本（自动检测）" -ForegroundColor White
    Write-Host ""
    Write-Host "环境要求:" -ForegroundColor Yellow
    Write-Host "  - Python 3.8+" -ForegroundColor White
    Write-Host "  - 推荐使用uv包管理器 (https://astral.sh/uv)" -ForegroundColor White
    Write-Host "  - PowerShell 5.1+" -ForegroundColor White
}

# 主程序
try {
    # 检查Python
    $script:PythonCmd = Check-Python
    
    # 检查uv
    $uvAvailable = Check-UV
    
    # 检查虚拟环境
    $venvInfo = Check-Venv
    
    # 根据命令执行操作
    switch ($Command.ToLower()) {
        "start" {
            # 安装依赖
            $venvInfo = Install-Dependencies -PythonCmd $script:PythonCmd -UvAvailable $uvAvailable -VenvInfo $venvInfo -UseSystem $System
            
            # 初始化数据库
            Init-Database -PythonCmd $venvInfo.PythonCmd
            
            # 启动Web服务
            $success = Start-WebService -PythonCmd $venvInfo.PythonCmd
            if ($success) {
                Show-Status
            }
        }
        
        "web" {
            # 安装依赖
            $venvInfo = Install-Dependencies -PythonCmd $script:PythonCmd -UvAvailable $uvAvailable -VenvInfo $venvInfo -UseSystem $System
            
            # 启动Web服务
            $success = Start-WebService -PythonCmd $venvInfo.PythonCmd
        }
        
        "status" {
            Show-Status
        }
        
        "stop" {
            Stop-Services
        }
        
        "setup" {
            # 安装依赖
            $venvInfo = Install-Dependencies -PythonCmd $script:PythonCmd -UvAvailable $uvAvailable -VenvInfo $venvInfo -UseSystem $System
            
            # 初始化数据库
            Init-Database -PythonCmd $venvInfo.PythonCmd
            
            Write-Success "项目设置完成"
        }
        
        "help" {
            Show-Help
        }
        
        default {
            Write-Error "未知命令: $Command"
            Write-Host ""
            Show-Help
            exit 1
        }
    }
    
    Write-Host ""
    Write-Success "操作完成！"
    
} catch {
    Write-Error "执行过程中出现错误: $_"
    exit 1
}