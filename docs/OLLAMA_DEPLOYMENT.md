# Ollama 部署手册

> 用于题库系统的本地 Embedding 服务  
> 更新时间：2026-03-08

---

## 一、快速开始（3 步完成）

```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 拉取模型
ollama pull mxbai-embed-large

# 3. 启动服务
ollama serve
```

---

## 二、详细安装步骤

### 方式 A：官方脚本安装（推荐，需 sudo）

```bash
# 一键安装
curl -fsSL https://ollama.com/install.sh | sh

# 验证安装
ollama --version

# 启动服务（systemd 自动管理）
sudo systemctl start ollama
sudo systemctl enable ollama
```

**优点**：简单快速，自动配置 systemd 服务  
**缺点**：需要 sudo 权限，下载可能较慢

---

### 方式 B：手动下载安装（无需 sudo）

#### 1. 下载 Ollama

选择以下任一方式：

**官方下载**（可能较慢）：
```bash
wget https://github.com/ollama/ollama/releases/download/v0.5.4/ollama-linux-amd64.tgz -O /tmp/ollama.tgz
```

**国内镜像**（推荐）：
```bash
# 使用镜像站下载
wget https://ghp.ci/https://github.com/ollama/ollama/releases/download/v0.5.4/ollama-linux-amd64.tgz -O /tmp/ollama.tgz
```

**手动下载**（最可靠）：
1. 浏览器访问：https://github.com/ollama/ollama/releases/tag/v0.5.4
2. 下载 `ollama-linux-amd64.tgz`
3. 上传到服务器 `/tmp/ollama.tgz`

#### 2. 解压安装

```bash
# 创建目录（用户目录，无需 sudo）
mkdir -p /home/zkjiao/usr/ollama

# 解压
tar -xzf /tmp/ollama.tgz -C /home/zkjiao/usr/ollama/

# 添加到 PATH（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export PATH="/home/zkjiao/usr/ollama:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 验证
ollama --version
```

---

### 方式 C：Snap 安装（最快，需 sudo）

```bash
sudo snap install ollama
```

**优点**：下载快，自动更新  
**缺点**：需要 snap 支持

---

## 三、拉取 Embedding 模型

```bash
# 拉取模型（约 1-2GB，首次需要时间）
ollama pull mxbai-embed-large
```

**模型信息**：
| 属性 | 值 |
|------|-----|
| 名称 | mxbai-embed-large |
| 维度 | 1024 |
| 大小 | ~1.5GB |
| 许可 | Apache 2.0 |
| 特点 | 中文优化，MTEB Top 10 |

**如果下载慢**：
- 使用国内网络环境
- 或使用代理
- 或等待网络空闲时段

---

## 四、启动服务

### 方式 A：前台运行（测试用）

```bash
ollama serve
```

保持终端开启，Ctrl+C 停止。

### 方式 B：后台运行（生产用）

```bash
# 使用 nohup
nohup ollama serve > /tmp/ollama.log 2>&1 &

# 验证
curl http://localhost:11434/api/tags
```

### 方式 C：systemd 服务（安装脚本自动配置）

```bash
sudo systemctl start ollama
sudo systemctl enable ollama
sudo systemctl status ollama
```

---

## 五、验证服务

```bash
# 1. 检查服务状态
curl http://localhost:11434/api/tags

# 预期输出：{"models":[...]}

# 2. 测试 Embedding
curl http://localhost:11434/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ollama" \
  -d '{
    "model": "mxbai-embed-large",
    "input": "你好，世界"
  }'

# 预期输出：包含 embedding 数组的 JSON
```

---

## 六、集成到题库系统

### 1. 确认配置

题库系统配置文件：`config/agent.json`

```json
{
  "embedding": {
    "model_name": "mxbai-embed-large",
    "api_key": "ollama",
    "base_url": "http://localhost:11434/v1"
  }
}
```

**注意**：配置修改后自动热更新，无需重启服务。

### 2. SSL 验证配置（重要）

如果遇到 SSL 证书验证错误（如使用阿里云 API），需要禁用 SSL 验证：

**方式一：环境变量（推荐）**
```bash
# 创建 .env 文件
cd /home/zkjiao/usr/github/question-bank-system
cp .env.example .env

# 编辑 .env 文件，设置
VERIFY_SSL=false

# 重启服务
pkill -f "uvicorn.*8000"
nohup uv run uvicorn web.main:app --host 0.0.0.0 --port 8000 > /tmp/question-bank.log 2>&1 &
```

**方式二：启动时设置**
```bash
VERIFY_SSL=false nohup uv run uvicorn web.main:app --host 0.0.0.0 --port 8000 > /tmp/question-bank.log 2>&1 &
```

**⚠️ 安全提示**：
- `VERIFY_SSL=false` 仅适用于开发环境
- 生产环境应安装正确的 CA 证书，并设置 `VERIFY_SSL=true`

### 2. 重建向量

```bash
cd /home/zkjiao/usr/github/question-bank-system

# 检查当前状态
uv run python scripts/rebuild_embeddings.py --check

# 智能重建（推荐）
uv run python scripts/rebuild_embeddings.py

# 强制重建所有
uv run python scripts/rebuild_embeddings.py --all
```

### 3. 验证向量化

```bash
# 查看题目向量状态
curl http://localhost:8000/api/questions | jq '.[].embedding'

# 应看到非 null 的向量数据
```

---

## 七、常见问题排查

### Q1: 端口被占用

```bash
# 查看占用端口的进程
lsof -i :11434

# 清理
pkill -f ollama

# 重启
ollama serve
```

### Q2: 服务启动失败

```bash
# 查看日志
tail -f /tmp/ollama.log

# 检查权限
ls -la /home/zkjiao/usr/ollama/ollama

# 重新赋予执行权限
chmod +x /home/zkjiao/usr/ollama/ollama
```

### Q3: 模型下载失败/超时

```bash
# 检查网络连接
ping ollama.com

# 使用代理（如果有）
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
ollama pull mxbai-embed-large

# 或等待网络好转后重试
```

### Q4: 内存不足

```bash
# 查看内存使用
free -h

# mxbai-embed-large 需要约 1-2GB 内存
# 关闭其他占用内存的程序
```

### Q5: 向量化失败

```bash
# 检查 Ollama 服务
curl http://localhost:11434/api/tags

# 检查模型是否存在
ollama list

# 重新拉取模型
ollama pull mxbai-embed-large

# 重试向量化
uv run python scripts/rebuild_embeddings.py --all
```

---

## 八、监控与维护

```bash
# 查看模型列表
ollama list

# 查看运行中的模型
ollama ps

# 查看日志
tail -f /tmp/ollama.log

# 停止服务
pkill -f ollama

# 卸载模型
ollama rm mxbai-embed-large
```

---

## 九、完整部署检查清单

- [ ] Ollama 已安装 (`ollama --version`)
- [ ] 模型已拉取 (`ollama list` 显示 mxbai-embed-large)
- [ ] 服务已启动 (`curl http://localhost:11434/api/tags`)
- [ ] Embedding 测试通过 (返回向量数据)
- [ ] 题库系统配置正确 (`config/agent.json`)
- [ ] 向量重建完成 (`scripts/rebuild_embeddings.py`)
- [ ] 问答功能测试通过

---

## 十、参考链接

- Ollama 官网：https://ollama.com
- Ollama GitHub：https://github.com/ollama/ollama
- mxbai-embed-large：https://huggingface.co/mixedbread-ai/mxbai-embed-large-v1
- 题库系统文档：`/home/zkjiao/usr/github/question-bank-system/docs/`

---

**部署时间估算**：
- 安装 Ollama：1-5 分钟（取决于网络）
- 拉取模型：5-15 分钟（约 1.5GB）
- 重建向量：1-2 分钟（12 题）

**如遇问题**：查看日志 `/tmp/ollama.log` 或题库日志 `/tmp/question-bank.log`
