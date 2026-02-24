# 题库系统 - 清晰架构说明

## 🎯 系统概览

题库系统提供**三个不同的入口**，共享相同的核心业务逻辑和数据层：

1. **🌐 Web入口** - 通过浏览器访问的完整Web应用
2. **🤖 MCP入口** - 通过Model Context Protocol与AI助手交互
3. **📱 微信小程序入口** - 移动端微信小程序

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
│           │    API网关层        │                     │
│           │  (统一请求处理)     │                     │
│           └──────────┬──────────┘                     │
│                      │                                 │
│           ┌──────────▼──────────┐                     │
│           │   核心业务层        │                     │
│           │  (共享业务逻辑)     │                     │
│           └──────────┬──────────┘                     │
│                      │                                 │
│           ┌──────────▼──────────┐                     │
│           │   数据访问层        │                     │
│           │  (统一数据存储)     │                     │
│           └─────────────────────┘                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📁 重新设计的项目结构

基于三个入口的清晰架构，我重新设计了项目结构：

```
question-bank-system/
├── 📄 README.md                    # 项目总览
├── 📄 CLEAR_ARCHITECTURE.md       # 本文件 - 清晰架构
├── 📄 start.py                    # 统一启动脚本
├── 📄 requirements.txt            # Python依赖
│
├── 📁 core/                       # 核心共享模块
│   ├── models.py                 # 数据模型（Pydantic）
│   ├── services.py               # 业务逻辑服务
│   └── database/                 # 数据访问层
│       ├── connection.py         # 数据库连接
│       ├── repositories.py       # 数据仓库
│       └── migrations.py         # 数据库迁移
│
├── 📁 web/                        # 🌐 Web入口
│   ├── main.py                   # FastAPI应用入口
│   ├── config.py                 # Web配置
│   ├── api/                      # RESTful API
│   │   ├── categories.py         # 分类API
│   │   ├── tags.py               # 标签API
│   │   └── questions.py          # 题目API
│   └── static/                   # 静态文件
│       └── index.html            # Web前端
│
├── 📁 mcp/                        # 🤖 MCP入口
│   ├── server.py                 # MCP服务器入口
│   ├── config.py                 # MCP配置
│   ├── tools/                    # MCP工具定义
│   │   ├── categories.py         # 分类工具
│   │   ├── tags.py               # 标签工具
│   │   └── questions.py          # 题目工具
│   └── handlers/                 # 请求处理器
│       └── question_handler.py   # 题目处理逻辑
│
├── 📁 wechat/                     # 📱 微信小程序入口
│   ├── server.py                 # 微信小程序服务器
│   ├── config.py                 # 微信配置
│   ├── api/                      # 小程序专用API
│   │   ├── auth.py               # 微信认证
│   │   ├── questions.py          # 题目API（小程序优化）
│   │   └── user.py               # 用户相关API
│   └── utils/                    # 微信工具
│       └── wechat_auth.py        # 微信认证工具
│
├── 📁 shared/                     # 共享工具和配置
│   ├── config.py                 # 共享配置
│   ├── utils/                    # 共享工具
│   │   ├── validators.py         # 数据验证
│   │   └── helpers.py            # 辅助函数
│   └── middleware/               # 共享中间件
│       └── auth.py               # 认证中间件
│
├── 📁 scripts/                    # 部署和工具脚本
├── 📁 docs/                       # 项目文档
├── 📁 deployments/                # 部署配置
└── 📁 archive/                    # 旧文件归档
```

## 🔄 三个入口的详细说明

### 1. 🌐 **Web入口** (`web/`)
**用途**: 完整的Web管理界面，适合管理员和教师使用
**技术栈**: FastAPI + HTML/CSS/JS
**特点**:
- 完整的RESTful API
- 丰富的管理功能
- 响应式Web界面
- 适合桌面和移动浏览器

**启动方式**:
```bash
# 启动Web服务器
python web/main.py
# 或使用统一脚本
python start.py web
```

### 2. 🤖 **MCP入口** (`mcp/`)
**用途**: 通过Model Context Protocol与AI助手（如Claude、ChatGPT）交互
**技术栈**: MCP协议 + FastAPI
**特点**:
- 标准化的AI工具接口
- 自然语言交互
- 适合AI辅助的题目管理
- 可集成到各种AI开发环境

**启动方式**:
```bash
# 启动MCP服务器
python mcp/server.py
# 或使用统一脚本
python start.py mcp
```

### 3. 📱 **微信小程序入口** (`wechat/`)
**用途**: 微信小程序的后端服务，适合学生移动端使用
**技术栈**: FastAPI + 微信小程序SDK
**特点**:
- 微信用户认证
- 移动端优化的API
- 小程序专用功能
- 适合学生随时随地学习

**启动方式**:
```bash
# 启动微信小程序服务器
python wechat/server.py
# 或使用统一脚本
python start.py wechat
```

## 🎯 共享核心模块

### **core/models.py** - 数据模型
```python
# 所有入口共享相同的数据模型
class Question(BaseModel):
    id: str
    content: str
    options: List[str] = []
    answer: str
    # ... 其他字段
```

### **core/services.py** - 业务逻辑
```python
# 所有入口共享相同的业务逻辑
class QuestionService:
    def add_question(self, question_data: QuestionCreate) -> Question:
        # 业务逻辑实现
        pass
    
    def search_questions(self, keyword: str) -> List[Question]:
        # 搜索逻辑
        pass
```

### **core/database/** - 数据访问
```python
# 所有入口共享相同的数据访问层
class QuestionRepository:
    def save(self, question: Question) -> Question:
        # 数据库操作
        pass
    
    def find_by_id(self, question_id: str) -> Optional[Question]:
        # 查询操作
        pass
```

## 🚀 统一启动和管理

### **start.py** - 智能启动脚本
```bash
# 启动Web入口
python start.py web

# 启动MCP入口
python start.py mcp

# 启动微信小程序入口
python start.py wechat

# 启动所有入口（开发模式）
python start.py all

# 初始化数据库
python start.py init

# 运行测试
python start.py test
```

### **共享配置管理**
```python
# shared/config.py - 统一配置
class Config:
    # 数据库配置（所有入口共享）
    DATABASE_URL = "sqlite:///./data/question_bank.db"
    
    # Web特定配置
    WEB_HOST = "0.0.0.0"
    WEB_PORT = 8000
    
    # MCP特定配置
    MCP_HOST = "0.0.0.0"
    MCP_PORT = 8001
    
    # 微信小程序配置
    WECHAT_APP_ID = "your-app-id"
    WECHAT_APP_SECRET = "your-app-secret"
```

## 🔧 开发指南

### 添加新功能
1. **修改核心逻辑** → 编辑 `core/` 中的文件
2. **添加Web API** → 编辑 `web/api/` 中的文件
3. **添加MCP工具** → 编辑 `mcp/tools/` 中的文件
4. **添加微信API** → 编辑 `wechat/api/` 中的文件

### 数据流示例
```
微信小程序请求 → wechat/api/questions.py → core/services.py → core/database/
      ↑                                       ↑                    ↑
Web API请求 → web/api/questions.py → 共享同一业务逻辑 → 共享同一数据库
      ↑                                       ↑                    ↑
MCP工具调用 → mcp/tools/questions.py → core/services.py → core/database/
```

## 📊 入口对比表

| 特性 | Web入口 | MCP入口 | 微信小程序入口 |
|------|---------|---------|---------------|
| **目标用户** | 管理员/教师 | AI助手/开发者 | 学生 |
| **使用场景** | 桌面管理 | AI辅助管理 | 移动学习 |
| **交互方式** | Web界面 | 自然语言 | 微信小程序 |
| **功能特点** | 完整管理功能 | AI工具集成 | 移动优化 |
| **技术栈** | FastAPI + HTML | MCP协议 | 微信SDK |
| **端口** | 8000 | 8001 | 8002 |

## 🎨 架构优势

1. **清晰分离**: 三个入口职责明确，互不干扰
2. **代码复用**: 核心逻辑共享，避免重复
3. **独立部署**: 可以单独部署某个入口
4. **易于扩展**: 添加新入口只需实现接口层
5. **维护简单**: 问题定位准确，修改影响小

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/superno188462/question-bank-system.git
cd question-bank-system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库
python start.py init

# 4. 启动Web入口（推荐先体验）
python start.py web

# 5. 访问
# Web界面: http://localhost:8000/static/index.html
# API文档: http://localhost:8000/docs
```

现在架构清晰明了，三个入口的区别一目了然！