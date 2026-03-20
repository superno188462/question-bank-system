#!/bin/bash
# 题库系统 - 安全修复脚本
# 修复代码审查中发现的关键安全问题

set -e

echo "=========================================="
echo "  题库系统安全修复脚本"
echo "=========================================="
echo ""

# 1. 备份当前配置
echo "📦 步骤 1: 备份当前配置..."
if [ -f "config/agent.json" ]; then
    cp config/agent.json config/agent.json.backup
    echo "  ✅ 已备份 config/agent.json"
else
    echo "  ⚠️  config/agent.json 不存在，跳过备份"
fi

# 2. 创建 .env 文件（如果不存在）
echo ""
echo "🔐 步骤 2: 创建 .env 文件..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# 题库系统环境变量配置
# 请将此文件保留在本地，不要提交到 Git

# AI 服务配置（从阿里云 DashScope 获取）
LLM_API_KEY=your_llm_api_key_here
VISION_API_KEY=your_vision_api_key_here
EMBEDDING_API_KEY=your_embedding_api_key_here

# 应用配置
DEBUG=true
DATABASE_URL=sqlite:///./data/question_bank.db

# 端口配置
WEB_PORT=8000
MCP_PORT=8001
WECHAT_PORT=8002
EOF
    echo "  ✅ 已创建 .env 文件"
    echo "  ⚠️  请编辑 .env 文件，填入你的 API Key"
else
    echo "  ✅ .env 文件已存在"
fi

# 3. 创建 agent.json.example 模板
echo ""
echo "📝 步骤 3: 创建 agent.json.example 模板..."
cat > config/agent.json.example << 'EOF'
{
  "llm": {
    "model_id": "qwen-plus",
    "api_key": "",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
  },
  "vision": {
    "model_id": "qwen-vl-max",
    "api_key": "",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
  },
  "embedding": {
    "model_name": "text-embedding-v3",
    "api_key": "",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
  },
  "settings": {
    "max_questions_per_image": 10,
    "max_questions_per_document": 50,
    "confidence_threshold": 0.6,
    "max_file_size_mb": 50
  },
  "allowed_extensions": {
    "images": ["png", "jpg", "jpeg", "gif", "webp"],
    "documents": ["pdf", "doc", "docx", "txt", "md"]
  }
}
EOF
echo "  ✅ 已创建 config/agent.json.example"

# 4. 更新 .gitignore
echo ""
echo "🔒 步骤 4: 更新 .gitignore..."
if ! grep -q "config/agent.json" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# 敏感配置文件（包含 API Key）" >> .gitignore
    echo "config/agent.json" >> .gitignore
    echo "  ✅ 已将 config/agent.json 添加到 .gitignore"
else
    echo "  ✅ config/agent.json 已在 .gitignore 中"
fi

if ! grep -q "\.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "  ✅ 已将 .env 添加到 .gitignore"
else
    echo "  ✅ .env 已在 .gitignore 中"
fi

# 5. 检查 agent.json 是否已被 Git 跟踪
echo ""
echo "🔍 步骤 5: 检查敏感文件是否已提交到 Git..."
if git ls-files --error-unmatch config/agent.json 2>/dev/null; then
    echo "  ⚠️  警告：config/agent.json 已被 Git 跟踪！"
    echo "  执行以下命令从 Git 历史中移除："
    echo "    git rm --cached config/agent.json"
    echo "    git commit -m 'Remove sensitive config file'"
    echo ""
    echo "  然后重置 API Key（联系 API 提供商）"
else
    echo "  ✅ config/agent.json 未被 Git 跟踪"
fi

# 6. 创建安全配置说明
echo ""
echo "📚 步骤 6: 创建安全配置说明..."
cat > docs/SECURITY_CONFIG.md << 'EOF'
# 安全配置指南

## API Key 管理

### 推荐方式：使用环境变量

1. **编辑 `.env` 文件**
   ```bash
   LLM_API_KEY=your_actual_api_key
   VISION_API_KEY=your_actual_api_key
   EMBEDDING_API_KEY=your_actual_api_key
   ```

2. **代码自动从环境变量读取**
   - `agent/config.py` 会自动从环境变量加载 API Key
   - 如果环境变量存在，优先使用环境变量
   - 如果环境变量不存在，回退到 `config/agent.json`

### 备选方式：使用配置文件

1. **复制模板**
   ```bash
   cp config/agent.json.example config/agent.json
   ```

2. **编辑配置文件**
   ```bash
   vim config/agent.json
   ```

3. **填入你的 API Key**

## 安全注意事项

### ⚠️ 绝对不要

- ❌ 将包含真实 API Key 的文件提交到 Git
- ❌ 在公开场合分享你的 API Key
- ❌ 使用硬编码的 API Key

### ✅ 应该做

- ✅ 使用 `.env` 文件存储敏感信息
- ✅ 将 `.env` 和 `config/agent.json` 添加到 `.gitignore`
- ✅ 定期轮换 API Key
- ✅ 使用 `agent.json.example` 作为模板分享

## 如果 API Key 已泄露

1. **立即重置 API Key**
   - 登录阿里云 DashScope 控制台
   - 删除旧的 API Key
   - 创建新的 API Key

2. **更新配置**
   - 更新 `.env` 文件
   - 重启应用

3. **检查使用记录**
   - 查看 API 使用日志
   - 确认是否有异常使用

## 文件清单

| 文件 | 是否提交到 Git | 说明 |
|------|---------------|------|
| `.env` | ❌ 否 | 环境变量配置（包含 API Key） |
| `config/agent.json` | ❌ 否 | Agent 配置（包含 API Key） |
| `config/agent.json.example` | ✅ 是 | Agent 配置模板（无 API Key） |
| `.env.example` | ✅ 是 | 环境变量模板（无 API Key） |

EOF
echo "  ✅ 已创建 docs/SECURITY_CONFIG.md"

# 7. 总结
echo ""
echo "=========================================="
echo "  安全修复完成！"
echo "=========================================="
echo ""
echo "✅ 已完成："
echo "  1. 备份了当前配置"
echo "  2. 创建了 .env 文件模板"
echo "  3. 创建了 agent.json.example 模板"
echo "  4. 更新了 .gitignore"
echo "  5. 创建了安全配置说明"
echo ""
echo "⚠️  下一步操作："
echo "  1. 编辑 .env 文件，填入你的 API Key"
echo "  2. 如果 config/agent.json 已被 Git 跟踪，执行："
echo "     git rm --cached config/agent.json"
echo "     git commit -m 'Remove sensitive config file'"
echo "  3. 重启应用测试"
echo ""
echo "📚 详细信息请查看：docs/SECURITY_CONFIG.md"
echo ""
