# Ollama 配置指南

## 1. 安装 Ollama

### 方法一：官方脚本（推荐）
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 方法二：手动下载
```bash
# 下载
wget https://github.com/ollama/ollama/releases/download/v0.5.4/ollama-linux-amd64.tgz -O /tmp/ollama.tgz

# 解压
tar -xzf /tmp/ollama.tgz -C /tmp/

# 移动
sudo mv /tmp/ollama /usr/local/bin/

# 验证
ollama --version
```

## 2. 拉取 Embedding 模型

```bash
ollama pull mxbai-embed-large
```

模型信息：
- **名称**: mxbai-embed-large
- **维度**: 1024
- **特点**: 中文优化，MTEB Top 10，Apache 2.0 许可

## 3. 启动 Ollama 服务

### 前台运行（测试用）
```bash
ollama serve
```

### 后台运行（生产用）
```bash
# 使用 systemd（推荐）
sudo systemctl enable ollama
sudo systemctl start ollama

# 或使用 nohup
nohup ollama serve > /tmp/ollama.log 2>&1 &
```

## 4. 验证服务

```bash
# 检查服务状态
curl http://localhost:11434/api/tags

# 测试 Embedding
curl http://localhost:11434/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ollama" \
  -d '{
    "model": "mxbai-embed-large",
    "input": "你好，世界"
  }'
```

## 5. 题库系统配置

配置文件：`config/agent.json`

```json
{
  "embedding": {
    "model_name": "mxbai-embed-large",
    "api_key": "ollama",
    "base_url": "http://localhost:11434/v1"
  }
}
```

**注意**: 配置修改后无需重启服务，自动热更新。

## 6. 重建向量

```bash
cd /home/zkjiao/usr/github/question-bank-system

# 检查状态
uv run python scripts/rebuild_embeddings.py --check

# 智能重建（仅缺失和版本不匹配的）
uv run python scripts/rebuild_embeddings.py

# 重建所有
uv run python scripts/rebuild_embeddings.py --all
```

## 7. 常见问题

### Q: 服务启动失败
```bash
# 检查端口占用
lsof -i :11434

# 清理端口
pkill -f ollama
```

### Q: 模型下载慢
```bash
# 使用镜像（如果可用）
export OLLAMA_MIRROR=https://mirror.example.com
ollama pull mxbai-embed-large
```

### Q: 内存不足
mxbai-embed-large 约需 1-2GB 内存，确保系统有足够资源。

## 8. 监控

```bash
# 查看日志
tail -f /tmp/ollama.log

# 查看模型列表
ollama list

# 查看运行状态
ollama ps
```

---

**配置时间**: 2026-03-08  
**模型**: mxbai-embed-large (1024 维)  
**服务地址**: http://localhost:11434
