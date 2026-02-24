# 题库系统 - API接口设计

## 🎯 设计原则
1. **分层设计**：三个入口有不同的API需求
2. **RESTful风格**：多客户端通用
3. **JSON格式**：统一数据格式
4. **错误处理**：标准错误响应
5. **分页支持**：大数据量处理

## 🏗️ 三个入口的API区别

### 1. 🌐 **Web入口 API** (`web/` - 端口8000)
**目标用户**：管理员、教师
**特点**：完整的管理功能，包含增删改查

#### 分类管理
```
GET    /api/categories           # 获取所有分类
POST   /api/categories           # 创建分类
GET    /api/categories/{id}      # 获取分类详情
PUT    /api/categories/{id}      # 更新分类
DELETE /api/categories/{id}      # 删除分类
```

#### 标签管理
```
GET    /api/tags                 # 获取所有标签
POST   /api/tags                 # 创建标签
DELETE /api/tags/{id}            # 删除标签
```

#### 题目管理
```
GET    /api/questions            # 获取题目列表（支持筛选）
POST   /api/questions            # 创建题目
GET    /api/questions/{id}       # 获取题目详情
PUT    /api/questions/{id}       # 更新题目
DELETE /api/questions/{id}       # 删除题目
```

### 2. 📱 **微信入口 API** (`wechat/` - 端口8002)
**目标用户**：学生
**特点**：只读和练习功能，不包含管理功能

#### 题目获取
```
GET    /api/questions            # 获取题目列表（不含答案）
GET    /api/questions/{id}       # 获取题目（不含答案）
POST   /api/questions/{id}/answer # 提交答案，返回是否正确
```

#### 练习管理
```
GET    /api/practice/session     # 创建练习会话
POST   /api/practice/submit      # 提交练习答案
GET    /api/practice/history     # 获取练习历史
```

#### 用户认证
```
POST   /api/auth/wechat-login    # 微信登录
GET    /api/auth/profile         # 获取用户信息
```

### 3. 🤖 **MCP入口 API** (`mcp/` - 端口8001)
**目标用户**：AI助手、开发者
**特点**：通过MCP协议访问，自然语言交互

#### MCP工具
```
工具名称：search_questions
描述：搜索题目
参数：keyword (string) - 搜索关键词

工具名称：add_question
描述：添加题目
参数：content (string) - 题目内容
      options (array) - 选项列表
      answer (string) - 正确答案

工具名称：get_question_categories
描述：获取题目分类
参数：无
```

## 📋 通用API规范

### 请求格式
```json
// GET请求示例
GET /api/questions?page=1&limit=10&category=数学

// POST请求示例
POST /api/questions
Content-Type: application/json

{
  "content": "1+1=?",
  "question_type": "single_choice",
  "options": ["1", "2", "3", "4"],
  "answer": "2",
  "category_id": "math_001",
  "tags": ["基础", "数学"],
  "difficulty": "easy"
}
```

### 响应格式
```json
// 成功响应
{
  "success": true,
  "data": {
    "id": "question_001",
    "content": "1+1=?",
    // ...其他字段
  }
}

// 错误响应
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "题目内容不能为空"
  }
}
```

### 分页响应
```json
{
  "success": true,
  "data": {
    "items": [...],      // 当前页数据
    "total": 100,        // 总记录数
    "page": 1,           // 当前页码
    "limit": 10,         // 每页数量
    "pages": 10          // 总页数
  }
}
```

## 🔒 安全规范

### 1. 输入验证
- 所有输入必须验证
- 防止SQL注入
- 防止XSS攻击

### 2. 权限控制
- **Web入口**：需要管理员权限（未来实现）
- **微信入口**：需要微信登录
- **MCP入口**：需要API密钥（未来实现）

### 3. 速率限制
- 防止暴力请求
- 每个IP限制请求频率

## 📊 性能优化

### 1. 缓存策略
- 热门数据缓存
- 分类和标签缓存

### 2. 数据库优化
- 索引优化
- 查询优化
- 分页查询

### 3. 响应压缩
- GZIP压缩
- 减少传输数据量

## 🚀 部署配置

### Web入口配置
```python
# web/config.py
WEB_HOST = "0.0.0.0"
WEB_PORT = 8000
DEBUG = True
```

### 微信入口配置
```python
# shared/config.py
WECHAT_HOST = "0.0.0.0"
WECHAT_PORT = 8002
WECHAT_APP_ID = os.getenv("WECHAT_APP_ID")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET")
```

### MCP入口配置
```python
# shared/config.py
MCP_HOST = "0.0.0.0"
MCP_PORT = 8001
```

## 📝 版本管理

### API版本
```
/v1/api/questions    # 版本1
/v2/api/questions    # 版本2（未来）
```

### 向后兼容
- 新版本必须兼容旧版本
- 废弃的API需要标记为deprecated
- 提供迁移指南

## 🔧 测试规范

### 单元测试
```python
# 测试API端点
def test_get_questions():
    response = client.get("/api/questions")
    assert response.status_code == 200
```

### 集成测试
```python
# 测试完整流程
def test_create_and_get_question():
    # 创建题目
    # 获取题目
    # 验证数据
```

### 性能测试
```python
# 测试API性能
def test_api_performance():
    # 测试并发请求
    # 测试响应时间
```

---
*最后更新：2026-02-24*
*版本：2.0（多入口架构版本）*