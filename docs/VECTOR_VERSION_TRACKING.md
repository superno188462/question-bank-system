# 向量版本追踪系统

## 📋 功能概述

系统支持智能向量版本追踪，实现：
- ✅ **模型切换无需重启服务** - 配置热更新
- ✅ **智能检测** - 仅当题目内容或模型版本变更时才重新向量化
- ✅ **版本回切优化** - 切换回旧模型时，如题目未变更，无需重新计算
- ✅ **自动向量化** - 创建/更新题目时自动生成向量

---

## 🗄️ 数据库字段

在 `questions` 表中新增以下字段：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| `embedding` | BLOB | 题目向量数据 |
| `embedding_version` | TEXT | 向量化时使用的模型版本 |
| `content_hash` | TEXT | 题目内容的 MD5 哈希 |
| `embedding_updated_at` | TEXT | 向量化时间 |

---

## 🔄 工作流程

### 1. 创建题目

```
用户创建题目
    ↓
保存到数据库
    ↓
检查是否需要向量化
    ├─ 从未向量化 → 生成向量
    ├─ 已向量化 → 跳过
    ↓
完成
```

### 2. 更新题目

```
用户更新题目
    ↓
保存到数据库
    ↓
检查内容是否变更
    ├─ 内容变更 → 重新生成向量
    ├─ 仅更新标签/分类 → 跳过向量化
    ↓
完成
```

### 3. 切换模型

```
用户在设置中切换模型
    ↓
配置立即生效（无需重启）
    ↓
运行重建脚本
    ↓
智能检测每道题
    ├─ 模型版本不匹配 → 重新生成
    ├─ 模型版本匹配 → 跳过
    ↓
完成
```

---

## 🛠️ 使用工具

### 检查向量化状态

```bash
cd /home/zkjiao/usr/github/question-bank-system
uv run python scripts/rebuild_embeddings.py --check
```

**输出示例**：
```
============================================================
向量化状态检查
============================================================

📊 题目统计:
   总题目数：150
   已向量：145
   未向量：5

📦 向量版本分布:
   - mxbai-embed-large: 100 题 (最后更新：2026-03-08T19:30:00)
   - nomic-embed-text: 45 题 (最后更新：2026-03-07T10:00:00)

🎯 当前模型：mxbai-embed-large
   ⚠️  版本不匹配：45 题需要重建
```

---

### 智能重建（推荐）

```bash
uv run python scripts/rebuild_embeddings.py
```

**功能**：
- 仅重建未向量化的题目
- 仅重建模型版本不匹配的题目
- 跳过已匹配的题目

---

### 重建所有题目

```bash
uv run python scripts/rebuild_embeddings.py --all
```

**场景**：
- 强制重新计算所有向量
- 清理向量数据后重建

---

### 仅重建缺失的

```bash
uv run python scripts/rebuild_embeddings.py --missing
```

**场景**：
- 新增题目后补全向量
- 向量数据丢失后恢复

---

### 仅重建版本不匹配的

```bash
uv run python scripts/rebuild_embeddings.py --mismatch
```

**场景**：
- 切换模型后更新向量
- 批量更新到新版本

---

## 📝 使用场景

### 场景 1：首次启用向量功能

```bash
# 1. 配置 Embedding 服务（Web 界面或 config/agent.json）
# 2. 检查状态
uv run python scripts/rebuild_embeddings.py --check

# 3. 重建所有题目向量
uv run python scripts/rebuild_embeddings.py --all
```

---

### 场景 2：切换 Embedding 模型

```bash
# 1. Web 界面修改模型配置（立即生效，无需重启）
# 2. 检查状态
uv run python scripts/rebuild_embeddings.py --check

# 3. 重建版本不匹配的题目
uv run python scripts/rebuild_embeddings.py --mismatch
```

**优势**：
- ✅ 无需重启服务
- ✅ 仅重建需要的题目
- ✅ 支持随时切回旧模型

---

### 场景 3：切回之前的模型

```bash
# 1. Web 界面切换回旧模型（如从 mxbai 切回 nomic）
# 2. 检查状态
uv run python scripts/rebuild_embeddings.py --check

# 3. 智能重建
uv run python scripts/rebuild_embeddings.py
```

**智能检测**：
- 如果题目内容未变更 → 直接使用旧向量 ✅
- 如果题目内容已变更 → 重新生成向量

---

### 场景 4：日常维护

```bash
# 定期检查向量化状态
uv run python scripts/rebuild_embeddings.py --check

# 补全缺失的向量
uv run python scripts/rebuild_embeddings.py --missing
```

---

## 🔍 技术细节

### 智能检测逻辑

```python
def needs_reembedding(question_id, content, options, current_model_version):
    # 1. 检查内容哈希是否变更
    if content_hash != current_hash:
        return True, "题目内容已变更"
    
    # 2. 检查模型版本是否变更
    if embedding_version != current_model_version:
        return True, "模型版本变更"
    
    # 3. 检查向量是否存在
    if not embedding:
        return True, "向量数据丢失"
    
    return False, "无需重新向量化"
```

### 内容哈希计算

```python
def _compute_content_hash(content, options):
    """
    计算题目内容的哈希值
    包含题干和选项，确保完整性
    """
    hash_content = content.strip()
    if options:
        hash_content += f"|{options}"
    return hashlib.md5(hash_content.encode('utf-8')).hexdigest()
```

---

## ⚠️ 注意事项

1. **向量化失败不影响题目操作**
   - 向量化是异步的、可选的
   - 创建/更新题目时，向量化失败不会回滚

2. **模型版本标识**
   - 使用模型名称作为版本标识
   - 如：`mxbai-embed-large`、`nomic-embed-text`

3. **向量存储**
   - 向量直接存储在 `questions` 表中
   - 1024 维向量约 4KB/题

4. **性能优化**
   - 批量重建时显示进度
   - 支持中断后继续

---

## 📊 性能参考

| 题目数量 | 模型 | 耗时 | 速度 |
|---------|------|------|------|
| 100 题 | nomic-embed-text | ~10 秒 | 10 题/秒 |
| 100 题 | mxbai-embed-large | ~15 秒 | 6.7 题/秒 |
| 1000 题 | nomic-embed-text | ~100 秒 | 10 题/秒 |
| 1000 题 | mxbai-embed-large | ~150 秒 | 6.7 题/秒 |

*基于 Ollama 本地部署，实际速度取决于硬件*

---

## 🐛 故障排查

### 问题 1：提示"未配置 Embedding 服务"

**解决**：
1. 访问 Web 界面 → 设置 → 配置 Embedding
2. 或编辑 `config/agent.json`

### 问题 2：重建速度过慢

**解决**：
1. 检查 Ollama 服务是否正常运行
2. 检查 GPU 是否被其他程序占用
3. 考虑使用更小的模型（如 nomic-embed-text）

### 问题 3：版本不匹配题目数量异常

**解决**：
```bash
# 查看详细分布
uv run python scripts/rebuild_embeddings.py --check

# 强制重建所有
uv run python scripts/rebuild_embeddings.py --all
```

---

## 📚 相关文件

| 文件 | 说明 |
|-----|------|
| `core/services/vector_index.py` | 向量索引服务 |
| `agent/services/embedding_service.py` | Embedding 服务 |
| `core/services.py` | 题目服务（集成向量化） |
| `scripts/rebuild_embeddings.py` | 向量重建脚本 |
| `core/database/migrations.py` | 数据库迁移 |

---

## 📅 更新日志

### 2026-03-08
- ✅ 添加向量版本追踪字段
- ✅ 实现智能检测逻辑
- ✅ 创建向量重建脚本
- ✅ 集成到题目创建/更新流程
- ✅ 支持模型热切换
