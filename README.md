# 题库系统 (Question Bank System)

一个简洁的题库管理系统，提供三个入口：
1. **🌐 Web入口** - 完整的Web管理界面
2. **🤖 MCP入口** - 通过Model Context Protocol与AI助手交互
3. **📱 微信小程序入口** - 移动端微信小程序后端

## 🚀 快速开始

### 一键启动
```bash
# 克隆项目
git clone https://github.com/superno188462/question-bank-system.git
cd question-bank-system

# 启动Web服务（推荐使用uv）
./run.sh web

# 或启动所有服务
./run.sh start
```

### 访问地址
- **Web管理界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **微信API**: http://localhost:8001
- **MCP接口**: http://localhost:8002

## 📁 项目结构

```
question-bank-system/
├── config/              # 配置文件
├── core/               # 核心业务逻辑
├── data/               # 数据文件
├── mcp_server/         # MCP服务入口
├── web/                # Web服务入口
├── wechat/             # 微信小程序入口
├── shared/             # 共享模块
├── run.sh              # 一键运行脚本
├── start.py            # Python启动入口
└── README.md           # 项目说明
```

## 🔧 使用方法

### 启动单个服务
```bash
./run.sh web           # 启动Web服务
./run.sh wechat        # 启动微信API服务
./run.sh mcp           # 启动MCP服务
```

### 其他命令
```bash
./run.sh start         # 启动所有服务
./run.sh status        # 查看服务状态
./run.sh stop          # 停止所有服务
./run.sh setup         # 安装依赖和初始化
```

## 📋 功能特性

### Web入口
- 题目管理（增删改查）
- 分类和标签管理
- 搜索和筛选功能
- 完整的API文档

### MCP入口
- 通过MCP协议与AI助手交互
- 支持题目查询和搜索
- 提供智能推荐功能

### 微信小程序入口
- 移动端题目浏览
- 答题功能
- 学习进度跟踪

## 🧪 验证脚本

项目包含完整的验证脚本，确保修改后仍然正常工作：

### 快速验证
```bash
bash test/quick_validate.sh
```

### 完整验证
```bash
python3 test/validate_project.py
```

### 预提交验证
```bash
bash test/pre_commit_validate.sh
```

### Git自动验证
每次提交前会自动运行验证，确保代码质量。

## 🛠️ 技术栈

- **后端**: Python + FastAPI
- **数据库**: SQLite
- **包管理**: uv（推荐）或 pip
- **部署**: 一键脚本，支持多平台
- **验证**: 完整的自动化验证脚本

## 📄 许可证

MIT License