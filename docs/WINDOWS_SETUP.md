# Windows 快速配置指南

> 适用于 Windows 用户的快速配置说明

---

## 一、解决 SSL 证书验证失败问题

### 问题现象
使用 AI 提取题目时提示：
```
❌ 证书验证失败
API 服务器的 SSL 证书不受信任
```

### 解决方案

#### 方式 1：创建 .env 文件（推荐）

1. **打开项目目录**
   ```
   D:\zkjiao\github\question-bank-system
   ```

2. **复制配置文件**
   - 找到 `.env.example` 文件
   - 复制并重命名为 `.env`
   
   或使用命令行：
   ```cmd
   cd D:\zkjiao\github\question-bank-system
   copy .env.example .env
   ```

3. **编辑 .env 文件**
   - 用记事本或 VS Code 打开 `.env`
   - 找到 `VERIFY_SSL=false`（应该已经是 false）
   - 保存文件

4. **重启服务**
   - 关闭当前运行的服务（Ctrl+C 或关闭命令行窗口）
   - 重新启动：
     ```cmd
     cd D:\zkjiao\github\question-bank-system
     python -m web.main
     ```
   - 或使用批处理文件：
     ```cmd
     run_web.bat
     ```

5. **验证**
   - 打开浏览器访问：http://localhost:8000
   - 尝试 AI 提取题目
   - 应该不再出现 SSL 错误

---

#### 方式 2：命令行临时设置

**CMD 命令行**：
```cmd
cd D:\zkjiao\github\question-bank-system
set VERIFY_SSL=false
python -m web.main
```

**PowerShell**：
```powershell
cd D:\zkjiao\github\question-bank-system
$env:VERIFY_SSL="false"
python -m web.main
```

**注意**：此方式仅在当前命令行窗口有效，关闭窗口后失效。

---

## 二、安装依赖

如果提示缺少 `python-dotenv` 模块：

```cmd
cd D:\zkjiao\github\question-bank-system
pip install python-dotenv
```

或使用项目虚拟环境：
```cmd
cd D:\zkjiao\github\question-bank-system
.venv\Scripts\pip install python-dotenv
```

---

## 三、验证配置是否生效

### 方法 1：查看启动日志

启动服务后，应该看到：
```
✅ 已加载环境变量：D:\zkjiao\github\question-bank-system\.env
```

### 方法 2：检查健康状态

浏览器访问：http://localhost:8000/health

应返回：
```json
{"status":"healthy","service":"web"}
```

### 方法 3：测试 AI 提取

1. 访问 http://localhost:8000
2. 点击"🤖 AI 提取"
3. 上传题目图片
4. 如果不再提示 SSL 错误，说明配置成功

---

## 四、常见问题

### Q1: .env 文件不生效？

**检查项**：
- 文件名是否正确（是 `.env` 不是 `.env.txt`）
- 文件是否在正确的目录（项目根目录）
- 是否重启了服务（修改 .env 后需要重启）

**查看文件扩展名**：
- 打开文件夹选项
- 取消勾选"隐藏已知文件类型的扩展名"
- 确认文件名是 `.env` 而不是 `.env.txt`

### Q2: 仍然提示 SSL 错误？

**可能原因**：
1. .env 文件未正确加载
2. 服务未重启
3. 有多个 Python 环境冲突

**解决步骤**：
```cmd
REM 1. 停止所有 Python 进程
taskkill /F /IM python.exe

REM 2. 确认 .env 文件存在
dir .env

REM 3. 重新启动服务
python -m web.main
```

### Q3: 如何确认 VERIFY_SSL 的值？

在启动日志中查找：
```
✅ 已加载环境变量：...
```

或添加测试代码（临时）：
```python
import os
print(f"VERIFY_SSL = {os.getenv('VERIFY_SSL')}")
```

---

## 五、其他配置

编辑 `.env` 文件可以配置：

```ini
# SSL 验证
VERIFY_SSL=false

# 数据库路径
DATABASE_URL=sqlite:///./data/question_bank.db

# AI 模型配置（可选，建议在网页设置中配置）
# LLM_API_KEY=your_api_key
# LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/tmp/question-bank.log
```

---

## 六、获取帮助

如果问题仍未解决：

1. **查看日志文件**
   ```cmd
   type \tmp\question-bank.log
   ```

2. **检查 Python 版本**
   ```cmd
   python --version
   ```
   应该是 Python 3.11+

3. **提交 Issue**
   https://github.com/superno188462/question-bank-system/issues

---

## 附录：完整配置流程

```cmd
REM 1. 进入项目目录
cd D:\zkjiao\github\question-bank-system

REM 2. 复制配置文件
copy .env.example .env

REM 3. 编辑 .env 文件（用记事本）
notepad .env

REM 4. 确认 VERIFY_SSL=false
REM 保存并关闭

REM 5. 安装依赖（如果需要）
pip install python-dotenv

REM 6. 启动服务
python -m web.main

REM 7. 验证
REM 浏览器访问：http://localhost:8000
```

---

**最后更新**: 2026-03-10
