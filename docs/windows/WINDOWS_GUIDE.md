# Windows用户指南

## 问题描述
在Windows环境下运行 `.\run.sh web --system` 时出现错误：
```
ModuleNotFoundError: No module named 'fastapi'
```

## 问题原因
1. **脚本兼容性**：`run.sh` 是Linux/macOS脚本，在Windows上无法直接运行
2. **依赖未安装**：Python依赖没有正确安装到系统或虚拟环境
3. **环境差异**：Windows和Linux的环境变量、路径格式不同

## 解决方案

### 方案1：使用Windows专用脚本（推荐）

#### 1.1 PowerShell脚本（功能最全）
```powershell
# 首次运行前，设置执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 一键启动所有服务
.\run.ps1 start

# 只启动Web服务
.\run.ps1 web

# 查看服务状态
.\run.ps1 status

# 停止所有服务
.\run.ps1 stop

# 安装依赖和初始化
.\run.ps1 setup
```

#### 1.2 批处理脚本（最简单）
```batch
# 双击运行或命令行执行
run.bat
```

### 方案2：手动安装和启动

#### 2.1 安装Python 3.8+
1. 访问 https://www.python.org/downloads/
2. 下载Python 3.8+安装程序
3. **重要**：安装时勾选 **"Add Python to PATH"**
4. 完成安装

#### 2.2 安装依赖
```cmd
# 打开命令提示符或PowerShell
cd D:\zkjiao\github\question-bank-system-master

# 安装依赖（使用系统Python）
python -m pip install -r config\requirements.txt

# 或使用虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate
pip install -r config\requirements.txt
```

#### 2.3 启动服务
```cmd
# 使用系统Python
python web\main.py

# 或使用虚拟环境
.venv\Scripts\python web\main.py
```

### 方案3：使用uv包管理器（最快）

#### 3.1 安装uv
```cmd
# 安装uv
pip install uv

# 验证安装
uv --version
```

#### 3.2 使用uv安装依赖
```cmd
# 创建虚拟环境并安装依赖
uv venv
uv pip install -r config\requirements.txt

# 启动服务
uv run python web\main.py
```

## 详细步骤

### 步骤1：环境准备
1. **安装Python 3.8+**：确保勾选"Add Python to PATH"
2. **验证安装**：
   ```cmd
   python --version
   pip --version
   ```

### 步骤2：获取项目代码
```cmd
# 方法1：Git克隆
git clone https://github.com/superno188462/question-bank-system.git
cd question-bank-system

# 方法2：下载ZIP
# 1. 访问 https://github.com/superno188462/question-bank-system
# 2. 点击"Code" → "Download ZIP"
# 3. 解压到目录，如 D:\question-bank-system
```

### 步骤3：安装依赖
```cmd
# 进入项目目录
cd D:\question-bank-system

# 安装依赖（选择一种方式）

# 方式A：使用系统Python（最简单）
python -m pip install -r config\requirements.txt

# 方式B：使用虚拟环境（推荐，避免污染系统）
python -m venv .venv
.venv\Scripts\activate
pip install -r config\requirements.txt

# 方式C：使用uv（最快）
uv venv
uv pip install -r config\requirements.txt
```

### 步骤4：初始化数据库
```cmd
# 创建数据目录
mkdir data

# 初始化数据库
python -c "
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
```

### 步骤5：启动服务
```cmd
# 启动Web服务
python web\main.py

# 或使用虚拟环境
.venv\Scripts\python web\main.py

# 或使用uv
uv run python web\main.py
```

### 步骤6：访问服务
1. **Web管理界面**：http://localhost:8000
2. **API文档**：http://localhost:8000/docs
3. **微信API**：http://localhost:8001
4. **MCP接口**：http://localhost:8002

## 常见问题解决

### 问题1：ModuleNotFoundError
```
ModuleNotFoundError: No module named 'fastapi'
```
**解决方案**：
```cmd
# 确保依赖已安装
python -m pip install -r config\requirements.txt

# 或重新安装
pip uninstall -r config\requirements.txt -y
pip install -r config\requirements.txt
```

### 问题2：权限不足
```
PermissionError: [Errno 13] Permission denied
```
**解决方案**：
```powershell
# 方法1：以管理员身份运行PowerShell
# 右键点击PowerShell → "以管理员身份运行"

# 方法2：使用虚拟环境
python -m venv .venv
.venv\Scripts\activate
pip install -r config\requirements.txt

# 方法3：使用--user参数
pip install --user -r config\requirements.txt
```

### 问题3：端口被占用
```
Address already in use
```
**解决方案**：
```cmd
# 查看占用端口的进程
netstat -ano | findstr :8000

# 停止进程（替换<PID>为实际进程ID）
taskkill /PID <PID> /F

# 或修改端口
# 编辑 web/main.py，修改端口号
```

### 问题4：脚本无法运行
```
.\run.ps1 : 无法加载文件...，因为在此系统上禁止运行脚本
```
**解决方案**：
```powershell
# 设置执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 验证设置
Get-ExecutionPolicy
```

### 问题5：路径问题
```
FileNotFoundError: [Errno 2] No such file or directory
```
**解决方案**：
```cmd
# 确保在正确目录
cd /d D:\zkjiao\github\question-bank-system-master

# 检查文件是否存在
dir config\requirements.txt
dir web\main.py
```

## 脚本说明

### run.ps1 (PowerShell脚本)
- **功能**：完整的Windows启动脚本
- **特点**：颜色输出、错误处理、多命令支持
- **用法**：`.\run.ps1 [start|web|status|stop|setup|help]`

### run.bat (批处理脚本)
- **功能**：简单的Windows启动脚本
- **特点**：双击运行、自动安装依赖
- **用法**：双击`run.bat`或命令行执行

### run.sh (Linux/macOS脚本)
- **注意**：在Windows上无法直接运行
- **替代**：使用`run.ps1`或`run.bat`

## 最佳实践

### 开发环境设置
1. **使用虚拟环境**：避免污染系统Python
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **使用uv管理依赖**：安装速度快，依赖解析准确
   ```cmd
   pip install uv
   uv venv
   uv pip install -r config\requirements.txt
   ```

3. **使用IDE**：推荐VS Code或PyCharm
   - 配置Python解释器为虚拟环境
   - 安装Python扩展

### 生产环境部署
1. **使用Docker**：跨平台一致性
   ```dockerfile
   FROM python:3.10-slim
   COPY . /app
   WORKDIR /app
   RUN pip install -r config/requirements.txt
   CMD ["python", "web/main.py"]
   ```

2. **使用系统服务**：Windows服务或计划任务
3. **使用反向代理**：Nginx或IIS

## 联系支持

如果遇到问题：
1. **查看日志**：检查`web.log`、`wechat.log`、`mcp.log`
2. **验证环境**：运行`python -c "import fastapi; print('OK')"`
3. **检查网络**：确保能访问 http://localhost:8000/health
4. **提交Issue**：https://github.com/superno188462/question-bank-system/issues

## 更新日志

### 2026-02-25
- 添加Windows专用脚本：`run.ps1`和`run.bat`
- 创建Windows用户指南
- 修复依赖安装问题
- 改进错误提示

---
*文档版本: 1.0*
*最后更新: 2026-02-25*