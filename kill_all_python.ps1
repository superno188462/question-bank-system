# PowerShell脚本：强制停止所有Python进程
Write-Host "🛑 停止所有Python进程..." -ForegroundColor Yellow

# 获取所有Python进程
$pythonProcesses = Get-Process | Where-Object { $_.ProcessName -like "*python*" }

if ($pythonProcesses) {
    Write-Host "发现以下Python进程:" -ForegroundColor Cyan
    $pythonProcesses | Select-Object ProcessName, Id, Path | Format-Table
    
    Write-Host "正在终止..." -ForegroundColor Red
    $pythonProcesses | Stop-Process -Force
    
    Write-Host "✅ 所有Python进程已停止" -ForegroundColor Green
} else {
    Write-Host "✅ 没有发现Python进程" -ForegroundColor Green
}

# 检查端口
Write-Host ""
Write-Host "检查端口8000..." -ForegroundColor Cyan
$portCheck = netstat -ano | findstr ":8000"
if ($portCheck) {
    Write-Host "❌ 端口8000仍被占用:" -ForegroundColor Red
    Write-Host $portCheck
    
    # 强制释放端口
    $portCheck | ForEach-Object {
        $parts = $_ -split '\s+'
        $pid = $parts[$parts.Length - 1]
        if ($pid -match '^\d+$') {
            Write-Host "终止PID: $pid" -ForegroundColor Yellow
            taskkill /F /PID $pid 2>$null
        }
    }
} else {
    Write-Host "✅ 端口8000已释放" -ForegroundColor Green
}

Write-Host ""
Write-Host "完成！可以重新启动服务了" -ForegroundColor Green
pause
