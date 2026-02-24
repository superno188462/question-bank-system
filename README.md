# 题库系统 (Question Bank System)

## 🎯 一句话指南：根据你的身份选择入口

**如果你是：**
- 👨‍🏫 **老师/管理员** → 用 **[Web入口](#-web入口)**（完整管理功能）
- 👨‍🎓 **学生** → 用 **[微信小程序入口](#-微信小程序入口)**（手机刷题）
- 👨‍💻 **开发者/AI爱好者** → 用 **[MCP入口](#-mcp入口)**（AI集成）

**详细用户指南**：[USER_GUIDE.md](USER_GUIDE.md) - 根据身份选择入口的完整说明

---

一个功能完整的题库管理系统，提供**三个清晰的入口**：
1. **🌐 Web入口** - 完整的Web管理界面
2. **🤖 MCP入口** - 通过Model Context Protocol与AI助手交互
3. **📱 微信小程序入口** - 移动端微信小程序后端

## 🎯 清晰架构

### 三个入口，共享核心
```
┌─────────────────────────────────────────────────────────┐
│                   题库管理系统                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐    ┌─────────┐    ┌──────────────┐       │
│  │  Web    │    │   MCP   │    │  微信小程序  │       │
│  │ 入口    │    │  入口   │    │    入口      │       │
│  └────┬────┘    └────┬────┘    └──────┬───────┘       │
│       │              │                 │               │
│       └──────────────┼─────────────────┘               │
│                      │                                 │
│           ┌──────────▼──────────┐                     │
│           │   共享核心模块      │                     │
│           │  (业务逻辑+数据层)  │                     │
│           └─────────────────────┘                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📋 项目导航

### 架构说明
- **清晰架构**：[docs/architecture/CLEAR_ARCHITECTURE.md](docs/architecture/CLEAR_ARCHITECTURE.md) - 三个入口的详细说明
- **架构验证**：[docs/architecture/ARCHITECTURE_VALIDATION.md](docs/architecture/ARCHITECTURE_VALIDATION.md) - 架构验证报告

### 用户指南
- **用户选择指南**：[docs/guides/USER_GUIDE.md](docs/guides/USER_GUIDE.md) - 根据身份选择入口
- **入口选择流程图**：[docs/guides/ENTRY_CHOICE.md](docs/guides/ENTRY_CHOICE.md) - 可视化选择流程
- **快速选择备忘**：[docs/guides/QUICK_CHOICE.txt](docs/guides/QUICK_CHOICE.txt) - 快速参考

### 核心文档
- **项目规则**：[docs/PROJECT_RULES.md](docs/PROJECT_RULES.md) - 开发规范
- **API设计**：[docs/new_api_design.md](docs/new_api_design.md) - 三个入口的接口规范
- **部署指南**：[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - 多入口部署指南
- **数据库设计**：[docs/deployment/new_database_schema.sql](docs/deployment/new_database_schema.sql)
- **微信小程序指南**：[docs/deployment/WECHAT_MINIPROGRAM_GUIDE.md](docs/deployment/WECHAT_MINIPROGRAM_GUIDE.md)
- **UV使用指南**：[docs/deployment/UV_USAGE.md](docs/deployment/UV_USAGE.md)
- **质量保证**：[scripts/pre_commit_test.sh](scripts/pre_commit_test.sh) - 预提交测试

## 🚀 快速开始：根据你的身份

### 👨‍🏫 **我是老师/管理员**（需要管理题目）
```bash
# 1. 克隆项目
git clone https://github.com/superno188462/question-bank-system.git
cd question-bank-system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动Web管理后台
python start.py web

# 4. 打开浏览器访问
#   管理界面: http://localhost:8000
#   API文档: http://localhost:8000/docs
```

### 👨‍🎓 **我是学生**（需要手机刷题）
```bash
# 1-2步同上...

# 3. 启动微信小程序后端
python start.py wechat

# 4. 在微信开发者工具中配置
#   服务器地址: http://localhost:8002
```

### 👨‍💻 **我是开发者/AI爱好者**
```bash
# 1-2步同上...

# 3. 启动MCP服务器
python start.py mcp

# 4. 在AI工具中连接
#   MCP地址: http://localhost:8001
```

### 🚀 **启动方式**

#### 最简单的一键启动（推荐）
打开**三个终端**，分别运行：

**终端1 - Web入口**（管理员用）：
```bash
python start.py web
# 访问: http://localhost:8000
# 文档: http://localhost:8000/docs
```

**终端2 - MCP入口**（开发者用）：
```bash
python start.py mcp
# 访问: http://localhost:8001
```

**终端3 - 微信入口**（学生用）：
```bash
python start.py wechat  
# 访问: http://localhost:8002
```

#### 使用脚本启动
```bash
# 尝试一键启动（可能需要调整）
./scripts/start_all.sh

# 停止所有服务
./scripts/stop_all.sh

# 快速启动指南
./scripts/quick_start.sh
```

#### 分别启动特定服务
```bash
# 显示所有启动选项
python start.py all

# 或直接启动特定服务
python start.py web    # Web入口
python start.py mcp    # MCP入口  
python start.py wechat # 微信入口
```

#### 🔧 **通用命令**
```bash
# 初始化数据库（所有入口共享）
python start.py init

# 运行测试
python start.py test

# 查看系统状态
python start.py status
```

## 🌐 Web入口（老师/管理员用）

**用途**: 完整的题目管理后台
**用户**: 教师、管理员
**特点**: 
- 📝 可视化添加/编辑题目
- 🏷️ 分类和标签管理  
- 🔍 高级搜索功能
- 📊 批量操作支持

**目录**:
```
web/
├── main.py          # 服务器启动
├── api/             # 管理API（增删改查）
└── static/          # 网页界面
```

## 📱 微信小程序入口（学生用）

**用途**: 手机刷题学习
**用户**: 学生
**特点**:
- 📱 微信小程序集成
- 🎯 练习模式（隐藏答案）
- 📊 答题记录
- 🔐 微信登录

**目录**:
```
wechat/
├── server.py        # 小程序后端
├── api/             # 学生专用API
└── utils/           # 微信工具
```

## 🤖 MCP入口（开发者/AI用）

**用途**: 通过AI助手管理题目
**用户**: 开发者、AI爱好者
**特点**:
- 💬 自然语言交互
- 🤖 集成Claude/ChatGPT等
- ⚡ 高效批量操作
- 🔧 开发者友好

**目录**:
```
mcp_server/
└── server.py        # MCP协议服务器
```

## ⚙️ 共享核心（所有入口都用）

**用途**: 所有入口共享的业务逻辑
**特点**: 避免代码重复，统一数据

**目录**:
```
core/                # 共享核心
├── models.py        # 数据结构
├── services.py      # 业务逻辑
└── database/        # 数据库
```

## 📁 项目结构

```
question-bank-system/
├── core/           # 核心共享模块（业务逻辑+数据层）
├── web/           # 🌐 Web入口（FastAPI + 前端）
├── mcp_server/           # 🤖 MCP入口（Model Context Protocol）
├── wechat/        # 📱 微信小程序入口（移动端API）
├── shared/        # 共享工具和配置
├── scripts/       # 部署和工具脚本
├── docs/          # 项目文档
├── deployments/   # 部署配置
└── archive/       # 旧文件归档
```

## 🔧 开发指南

### 添加新功能
1. **修改核心逻辑** → 编辑 `core/` 中的文件
2. **添加Web API** → 编辑 `web/api/` 中的文件
3. **添加MCP工具** → 编辑 `mcp_server/tools/` 中的文件
4. **添加微信API** → 编辑 `wechat/api/` 中的文件

### 数据流示例
```
微信小程序请求 → wechat/api/ → core/services.py → core/database/
      ↑                              ↑                    ↑
Web API请求 → web/api/ → 共享同一业务逻辑 → 共享同一数据库
      ↑                              ↑                    ↑
MCP工具调用 → mcp_server/tools/ → core/services.py → core/database/
```

## 📊 入口对比

| 特性 | Web入口 | MCP入口 | 微信小程序入口 |
|------|---------|---------|---------------|
| **目标用户** | 管理员/教师 | AI助手/开发者 | 学生 |
| **使用场景** | 桌面管理 | AI辅助管理 | 移动学习 |
| **交互方式** | Web界面 | 自然语言 | 微信小程序 |
| **技术栈** | FastAPI + HTML | MCP协议 | 微信SDK |
| **端口** | 8000 | 8001 | 8002 |

## 🤝 贡献

欢迎贡献代码！请先阅读：
- [docs/PROJECT_RULES.md](docs/PROJECT_RULES.md) - 开发规范
- [scripts/pre_commit_test.sh](scripts/pre_commit_test.sh) - 提交前测试

## 📞 支持

如有问题，请查看文档或提交Issue。

## 🎯 功能特性

### 核心功能
- **自定义分类**：用户创建和管理分类
- **标签系统**：灵活的标签管理
- **完整题目**：题干、选项、答案、解析
- **多种题型**：选择题和填空题
- **智能搜索**：按分类、标签、关键词搜索

### 管理功能
- **增删改查**：完整的题目管理
- **批量操作**：支持批量处理
- **数据导出**：多种格式导出
- **系统统计**：题目数量统计

### 技术特性
- **RESTful API**：多客户端支持
- **响应式前端**：桌面和移动端
- **易于部署**：一键部署脚本
- **代码规范**：清晰的架构和注释

## 🏗️ 系统架构

### 目录结构
```
question-bank-system/
├── ARCHITECTURE.md          # 架构总览
├── README.md               # 本文件
├── PROJECT_RULES.md        # 项目规则
├── new_api_design.md       # API设计
├── new_database_schema.sql # 数据库结构
├── init_new_database.py    # 数据库初始化
│
├── src/                    # 源代码
│   ├── core/              # 核心逻辑
│   ├── api/               # API接口
│   ├── database/          # 数据访问
│   └── utils/             # 工具函数
│
├── static/                # 前端文件
│   ├── index.html        # 完整前端
│   └── style.css         # 样式表
│
├── tests/                 # 测试代码
├── docs/                  # 文档
├── scripts/               # 部署脚本
└── requirements.txt       # 依赖列表
```

### 技术栈
- **后端**：FastAPI + SQLite + Python 3.8+
- **前端**：原生HTML/CSS/JavaScript
- **部署**：uv优先，支持多平台
- **测试**：预提交测试框架

## 🚀 部署选项

### 1. UV优先部署（推荐）
```bash
./UV_SETUP.sh
```
- 使用uv管理依赖，避免全局污染
- 极速安装，更好的依赖解决
- 自动创建虚拟环境

### 2. 简单部署
```bash
./SIMPLE_SETUP.sh
```
- 兼容性更好，支持没有uv的环境
- 自动检测Python版本
- 提供uv安装建议

### 3. MSYS2专用
```bash
./SETUP_MSYS2.sh
```
- 针对Windows MSYS2环境优化
- 处理路径和命令别名
- 详细的错误提示

### 4. Windows批处理
```bash
QUICK_START_WINDOWS.bat
```
- 原生Windows支持
- 双击运行，无需命令行
- 自动环境检测

## 🔧 开发指南

### 代码规范
1. **文件大小**：单个文件不超过1000行
2. **注释要求**：详细注释，特别是公开接口
3. **类型提示**：使用Python类型提示
4. **测试覆盖**：提交前必须通过测试

### 开发流程
```bash
# 1. 运行预提交测试
./pre_commit_test.sh

# 2. 如果测试通过，提交代码
git add .
git commit -m "描述变更"
git push origin master

# 3. 验证提交
./post_commit_check.sh
```

### 测试框架
- **预提交测试**：`pre_commit_test.sh` - 7项全面测试
- **前端验证**：`verify_frontend.sh` - 前端文件检查
- **数据库测试**：`test_database.py` - 数据库功能测试
- **服务器测试**：`test_server.py` - 服务器启动测试

## 📚 API文档

### 主要接口
- **分类管理**：`GET/POST/PUT/DELETE /api/categories`
- **标签管理**：`GET/POST/DELETE /api/tags`
- **题目管理**：`GET/POST/PUT/DELETE /api/questions`
- **题目标签**：`GET/POST/DELETE /api/questions/{id}/tags`

### 在线文档
启动服务器后访问：
- **交互式文档**：http://localhost:8000/docs
- **ReDoc文档**：http://localhost:8000/redoc
- **API测试**：直接在文档中测试接口

## 🐛 问题解决

### 常见问题
1. **Python命令问题**：脚本优先使用`python`，其次`python3`
2. **数据库错误**：运行`python fix_database.py`修复
3. **依赖安装**：建议安装uv获得更好体验
4. **端口占用**：确保8000端口可用

### 调试工具
```bash
# 检查服务器状态
curl http://localhost:8000/

# 测试数据库
python test_database.py

# 验证前端
./verify_frontend.sh
```

## 🤝 贡献指南

### 贡献流程
1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 运行预提交测试
5. 提交Pull Request

### 代码审查标准
- 功能正确性
- 测试覆盖率
- 代码规范性
- 文档完整性

## 📄 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。

## 📞 支持

- **问题反馈**：GitHub Issues
- **功能建议**：GitHub Discussions
- **紧急问题**：查看[常见问题](#常见问题)部分

---
*最后更新：2026-02-24*
*版本：2.0*