# 题库系统部署指南 - 多入口部署

本指南详细说明如何部署和使用题库系统的三个入口。

## 🎯 部署选项

根据你的需求选择部署方式：

### 1. 🌐 **只部署Web入口**（管理员/教师用）
- 只需要题目管理功能
- 在电脑上使用
- 最简单的部署方式

### 2. 📱 **只部署微信入口**（学生用）
- 只需要手机刷题功能
- 配合微信小程序使用
- 移动端优化

### 3. 🤖 **只部署MCP入口**（开发者用）
- 只需要AI集成功能
- 通过AI工具管理题目
- 技术爱好者使用

### 4. 🚀 **部署所有入口**（完整系统）
- 需要所有功能
- 支持多用户类型
- 完整的题库系统

## 📋 前置要求

### 1. 系统要求
- **操作系统**: Ubuntu 20.04+/CentOS 7+/macOS 10.15+/Windows 10+
- **Python**: 3.8 或更高版本
- **内存**: 至少 2GB RAM
- **磁盘空间**: 至少 500MB 可用空间

### 2. 网络要求
- 可以访问互联网（下载依赖）
- 如果需要外网访问，需要有公网IP或内网穿透

## 🚀 快速部署步骤

### 步骤1：克隆项目
```bash
# 克隆项目到本地
git clone https://github.com/superno188462/question-bank-system.git
cd question-bank-system
```

### 步骤2：安装依赖
```bash
# 安装Python依赖
pip install -r requirements.txt

# 或使用uv（推荐，更快）
pip install uv
uv pip install -r requirements.txt
```

### 步骤3：选择并启动入口

#### 选项A：启动Web入口（管理员用）
```bash
# 初始化数据库
python start.py init

# 启动Web管理后台
python start.py web

# 访问地址：
# 🌐 管理界面: http://localhost:8000
# 📚 API文档: http://localhost:8000/docs
```

#### 选项B：启动微信入口（学生用）
```bash
# 初始化数据库
python start.py init

# 启动微信小程序后端
python start.py wechat

# 访问地址：http://localhost:8002
# 需要在微信开发者工具中配置服务器地址
```

#### 选项C：启动MCP入口（开发者用）
```bash
# 初始化数据库
python start.py init

# 启动MCP服务器
python start.py mcp

# 访问地址：http://localhost:8001
# 在AI工具中配置MCP服务器地址
```

#### 选项D：启动所有入口（开发模式）
```bash
# 初始化数据库
python start.py init

# 需要三个终端分别启动：
# 终端1 - Web入口
python start.py web

# 终端2 - 微信入口
python start.py wechat

# 终端3 - MCP入口
python start.py mcp
```

## 🔧 详细配置

### 1. 数据库配置
```python
# 数据库文件位置
data/question_bank.db  # SQLite数据库文件

# 初始化数据库
python start.py init

# 重置数据库（谨慎使用）
rm -f data/question_bank.db
python start.py init
```

### 2. 端口配置
```python
# 修改 shared/config.py 调整端口
WEB_PORT = 8000      # Web入口端口
WECHAT_PORT = 8002   # 微信入口端口
MCP_PORT = 8001      # MCP入口端口
```

### 3. 微信小程序配置
```bash
# 设置微信小程序环境变量
export WECHAT_APP_ID=your_app_id
export WECHAT_APP_SECRET=your_app_secret

# 或编辑 shared/config.py
WECHAT_APP_ID = "your_app_id"
WECHAT_APP_SECRET = "your_app_secret"
```

## 🐳 Docker部署

### 1. 构建Docker镜像
```bash
# 构建镜像
docker build -t question-bank-system -f deployments/Dockerfile .

# 或使用docker-compose
docker-compose -f deployments/docker-compose.yml up -d
```

### 2. Docker运行
```bash
# 运行Web入口
docker run -p 8000:8000 question-bank-system python start.py web

# 运行微信入口
docker run -p 8002:8002 question-bank-system python start.py wechat

# 运行MCP入口
docker run -p 8001:8001 question-bank-system python start.py mcp
```

## 🌐 生产环境部署

### 1. Nginx反向代理
```nginx
# 配置示例（deployments/nginx.conf）
server {
    listen 80;
    server_name your-domain.com;
    
    # Web入口
    location /web/ {
        proxy_pass http://localhost:8000/;
    }
    
    # 微信入口
    location /wechat/ {
        proxy_pass http://localhost:8002/;
    }
    
    # MCP入口
    location /mcp/ {
        proxy_pass http://localhost:8001/;
    }
}
```

### 2. 系统服务（Systemd）
```ini
# /etc/systemd/system/question-bank-web.service
[Unit]
Description=Question Bank System Web Entry
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/question-bank-system
ExecStart=/usr/bin/python3 start.py web
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📊 监控和维护

### 1. 系统状态检查
```bash
# 检查系统状态
python start.py status

# 输出示例：
# 📊 系统状态检查...
# ✅ 数据库文件: data/question_bank.db (48.0 KB)
# ✅ 核心模块: core/
# ✅ Web入口: web/
# ✅ MCP入口: mcp/
# ✅ 微信入口: wechat/
```

### 2. 运行测试
```bash
# 运行所有测试
python start.py test

# 或运行特定测试
python -m pytest tests/
```

### 3. 日志查看
```bash
# 查看启动日志
python start.py web 2>&1 | tee web.log

# 查看错误日志
tail -f web.log | grep -i error
```

## 🔒 安全建议

### 1. 防火墙配置
```bash
# 只开放必要的端口
sudo ufw allow 8000/tcp  # Web入口
sudo ufw allow 8002/tcp  # 微信入口（如果需要外网访问）
sudo ufw allow 8001/tcp  # MCP入口（如果需要外网访问）
```

### 2. 数据库备份
```bash
# 定期备份数据库
cp data/question_bank.db data/question_bank.db.backup.$(date +%Y%m%d)

# 恢复数据库
cp data/question_bank.db.backup.20260224 data/question_bank.db
```

### 3. 更新维护
```bash
# 更新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启服务
pkill -f "python start.py"
python start.py web  # 重新启动
```

## 🆘 故障排除

### 常见问题1：端口被占用
```bash
# 检查端口占用
sudo lsof -i :8000

# 杀死占用进程
sudo kill -9 <PID>
```

### 常见问题2：依赖安装失败
```bash
# 使用uv安装（更快更稳定）
pip install uv
uv pip install -r requirements.txt
```

### 常见问题3：数据库错误
```bash
# 重置数据库
rm -f data/question_bank.db
python start.py init
```

### 常见问题4：微信配置错误
```bash
# 检查环境变量
echo $WECHAT_APP_ID
echo $WECHAT_APP_SECRET

# 或直接修改配置文件
vim shared/config.py
```

## 📞 支持

### 获取帮助
1. 查看详细文档：`docs/` 目录
2. 查看用户指南：`docs/guides/USER_GUIDE.md`
3. 查看架构说明：`docs/architecture/CLEAR_ARCHITECTURE.md`

### 报告问题
1. 检查日志文件
2. 运行状态检查：`python start.py status`
3. 提交GitHub Issue

---
*最后更新：2026-02-24*
*版本：3.0（多入口部署指南）*