# AI Agent 配置系统

## 📖 概述

AI Agent 配置系统支持热更新，无需重启服务即可修改配置。

## 📁 配置文件

- **配置文件**: `config/agent.json`（包含敏感信息，不提交到 Git）
- **示例文件**: `config/agent.json.example`（提交到 Git 的模板）

## 🌐 Web 配置界面

### 访问方式

1. 启动服务：`python start.py web`
2. 访问配置页面：http://localhost:8000/agent-config

### 功能

- ✅ 查看当前配置（API Key 部分掩码）
- ✅ 修改 LLM/Vision/Embedding 配置
- ✅ 调整高级设置（提取数量、置信度等）
- ✅ 测试 API 连接
- ✅ 重置为默认配置
- ✅ 保存后立即生效（热更新）

## 🔧 API 接口

### 获取配置

```bash
GET /api/agent/config
```

响应示例：
```json
{
  "success": true,
  "data": {
    "llm": {
      "model_id": "qwen-plus",
      "api_key": "sk-sp-48ff...3375a",
      "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    },
    ...
  }
}
```

### 更新配置

```bash
PUT /api/agent/config
Content-Type: application/json

{
  "llm": {
    "model_id": "qwen-max"
  }
}
```

### 测试配置

```bash
POST /api/agent/config/test
```

## 📝 配置项说明

### LLM 模型配置

| 字段 | 说明 | 默认值 |
|-----|------|--------|
| `model_id` | 模型 ID | `qwen-plus` |
| `api_key` | API Key | - |
| `base_url` | API 地址 | 阿里云百炼 |

### 视觉模型配置

| 字段 | 说明 | 默认值 |
|-----|------|--------|
| `model_id` | 模型 ID | `qwen-vl-max` |
| `api_key` | API Key | - |
| `base_url` | API 地址 | 阿里云百炼 |

### Embedding 模型配置

| 字段 | 说明 | 默认值 |
|-----|------|--------|
| `model_name` | 模型名称 | `text-embedding-v3` |
| `api_key` | API Key | - |
| `base_url` | API 地址 | 阿里云百炼 |

### 高级设置

| 字段 | 说明 | 默认值 |
|-----|------|--------|
| `max_questions_per_image` | 单张图片最多题目数 | 10 |
| `max_questions_per_document` | 单个文档最多题目数 | 50 |
| `confidence_threshold` | 置信度阈值 | 0.6 |
| `max_file_size_mb` | 最大文件大小 (MB) | 50 |

## 🔐 安全说明

1. **API Key 保护**: 配置文件已添加到 `.gitignore`，不会提交到 Git
2. **API 返回掩码**: Web API 返回的 API Key 会部分掩码（`sk-sp-48ff...3375a`）
3. **首次配置**: 从 `.env` 或示例文件复制配置，然后修改 API Key

## 🚀 热更新机制

配置系统使用缓存 + 文件修改时间检测：

1. 首次读取时加载配置到缓存
2. 每次访问时检查文件修改时间
3. 文件变化时自动重新加载
4. 支持手动刷新：`AgentConfig.refresh()`

## 📋 使用示例

### Python 代码读取配置

```python
from agent.config import AgentConfig

# 读取配置（自动热加载）
api_key = AgentConfig.LLM_API_KEY
model = AgentConfig.LLM_MODEL_ID

# 获取完整配置字典
config = AgentConfig.get_full_config()

# 强制刷新配置
AgentConfig.refresh()
```

### 验证配置

```python
# 检查是否已配置
if AgentConfig.is_configured():
    print("✅ 配置已完成")
else:
    print("❌ 请先配置 API Key")

# 验证配置完整性
try:
    AgentConfig.validate()
except ValueError as e:
    print(f"配置错误：{e}")
```

## 🔗 相关链接

- [阿里云百炼控制台](https://dashscope.console.aliyun.com/)
- [千问模型文档](https://help.aliyun.com/zh/dashscope/)
- [API 参考文档](http://localhost:8000/docs)
