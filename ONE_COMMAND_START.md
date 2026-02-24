# 一键启动所有前端服务指南

## 🎯 目标
**一个命令启动所有三个前端服务**：Web、MCP、微信小程序

## 📋 当前状态

### 已实现的方案

#### 方案1：分别启动（最可靠）
```bash
# 打开三个终端，分别运行：

# 终端1 - Web服务
python start.py web

# 终端2 - MCP服务  
python start.py mcp

# 终端3 - 微信服务
python start.py wechat
```

#### 方案2：使用启动脚本
```bash
# 尝试一键启动
./scripts/start_all.sh

# 停止所有服务
./scripts/stop_all.sh
```

#### 方案3：快速启动指南
```bash
# 显示启动指南
./scripts/quick_start.sh
```

## 🔧 技术挑战

### 为什么不能真正"一键启动"？
1. **进程管理复杂**：三个服务需要独立运行
2. **日志输出冲突**：多个服务输出到同一个终端会混乱
3. **错误处理困难**：一个服务崩溃不应影响其他服务
4. **用户交互问题**：如何优雅地停止所有服务

### 已尝试的解决方案
1. **多进程启动**：Python multiprocessing（有导入问题）
2. **子进程启动**：subprocess.Popen（需要处理输出）
3. **后台进程**：nohup + &（难以管理）
4. **终端多路复用**：tmux/screen（需要用户安装）

## 🚀 推荐方案

### 对于开发者（推荐）
```bash
# 使用tmux（如果已安装）
tmux new-session -d -s question-bank "python start.py web"
tmux split-window -h "python start.py mcp"  
tmux split-window -v "python start.py wechat"
tmux attach-session -t question-bank
```

### 对于普通用户
```bash
# 分别打开三个终端，最简单可靠
```

### 对于生产环境
```bash
# 使用systemd服务
sudo systemctl start question-bank-web
sudo systemctl start question-bank-mcp  
sudo systemctl start question-bank-wechat
```

## 📁 文件说明

### 启动相关文件
```
scripts/
├── start_all.sh      # 一键启动脚本（尝试版）
├── stop_all.sh       # 停止所有服务脚本
└── quick_start.sh    # 快速启动指南

launch_all.py         # Python版一键启动
```

### 核心启动文件
```
start.py              # 统一启动脚本
web/main.py           # Web服务入口
mcp_server/server.py         # MCP服务入口  
wechat/server.py      # 微信服务入口
```

## 🛠️ 故障排除

### 常见问题

#### 问题1：服务启动后立即退出
```bash
# 检查日志
tail -f logs/web.log
tail -f logs/mcp.log  
tail -f logs/wechat.log

# 检查导入错误
python3 -c "from web.main import create_web_app; app = create_web_app()"
```

#### 问题2：端口被占用
```bash
# 检查端口占用
sudo lsof -i :8000
sudo lsof -i :8001
sudo lsof -i :8002

# 停止占用进程
sudo kill -9 <PID>
```

#### 问题3：数据库错误
```bash
# 重置数据库
rm -f data/question_bank.db
python start.py init
```

## 🔄 未来改进计划

### 短期改进
1. 完善`start_all.sh`脚本，确保可靠启动
2. 添加服务健康检查
3. 改进日志管理

### 长期改进  
1. 使用Docker Compose一键启动
2. 实现真正的进程管理
3. 添加Web管理界面控制服务

## 📞 支持

### 获取帮助
1. 查看详细文档：`docs/`目录
2. 运行状态检查：`python start.py status`
3. 查看服务日志：`logs/`目录

### 报告问题
1. 描述具体问题
2. 提供错误日志
3. 说明操作系统和环境

---
*最后更新：2026-02-24*
*状态：支持分别启动，一键启动在完善中*