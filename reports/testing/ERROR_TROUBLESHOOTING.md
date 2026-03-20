# AI 题目提取错误排查指南

> 更新时间：2026-03-10

---

## 常见错误及解决方案

### 1. SSL 证书验证失败

**错误信息**：
```
SSL 证书验证失败
API 服务器的 SSL 证书不受信任。请联系管理员检查 VERIFY_SSL 配置或安装正确的 CA 证书。
```

**原因**：
- API 提供商使用自签名证书
- 系统缺少 CA 证书
- 网络中间人代理

**解决方案**：

**开发环境**（推荐）：

**Linux/Mac**：
```bash
# 方式 1：创建 .env 文件（自动加载）
cd /home/zkjiao/usr/github/question-bank-system
cp .env.example .env
# 编辑 .env，设置 VERIFY_SSL=false
# 重启服务后自动生效

# 方式 2：启动时设置
VERIFY_SSL=false uv run uvicorn web.main:app --host 0.0.0.0 --port 8000
```

**Windows**：
```cmd
REM 方式 1：创建 .env 文件（推荐）
cd D:\zkjiao\github\question-bank-system
copy .env.example .env
REM 编辑 .env，设置 VERIFY_SSL=false
REM 重启服务后自动生效

REM 方式 2：命令行设置（临时）
set VERIFY_SSL=false
python -m web.main
```

**PowerShell**：
```powershell
# 方式 1：创建 .env 文件
cd D:\zkjiao\github\question-bank-system
Copy-Item .env.example .env
# 编辑 .env，设置 VERIFY_SSL=false

# 方式 2：命令行设置
$env:VERIFY_SSL="false"
python -m web.main
```

**生产环境**：
```bash
# 安装 CA 证书
sudo apt-get install ca-certificates
sudo update-ca-certificates

# 设置 VERIFY_SSL=true
```

---

### 2. JSON 解析失败

**错误信息**：
```
JSON 解析失败：Expecting value: line 1 column 1 (char 0)
```

**原因**：
- 模型返回的内容不是有效 JSON
- 模型返回了额外说明文字
- 模型响应格式错误

**解决方案**：
1. 检查图片质量是否清晰
2. 检查模型配置是否正确
3. 查看日志获取模型原始响应
4. 尝试更换模型（如 qwen-vl-max → qwen-vl-plus）

**查看原始响应**：
```bash
tail -f /tmp/question-bank.log | grep "raw_response"
```

---

### 3. 网络连接失败

**错误信息**：
```
网络连接失败，请检查网络或 API 服务是否可用
```

**原因**：
- 网络不通
- API 服务宕机
- 防火墙阻止

**解决方案**：
```bash
# 测试网络连通性
ping dashscope.aliyuncs.com

# 测试 API 端点
curl -I https://dashscope.aliyuncs.com/compatible-mode/v1

# 检查代理配置
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

---

### 4. API Key 无效

**错误信息**：
```
认证失败
API Key 无效或已过期
```

**原因**：
- API Key 填写错误
- API Key 已过期
- API Key 权限不足

**解决方案**：
1. 访问设置页面（http://localhost:8000 → ⚙️ 设置）
2. 检查 LLM 和 Vision 的 API Key 配置
3. 登录阿里云百炼控制台重新生成 API Key
4. 测试配置是否有效

---

### 5. 模型不可用

**错误信息**：
```
模型不可用
指定的模型不可用
```

**原因**：
- 模型名称填写错误
- 模型未开通
- 模型已下线

**解决方案**：
1. 检查模型配置是否正确
2. 登录阿里云百炼控制台确认模型状态
3. 参考官方文档选择可用模型

**可用模型参考**：
- LLM：qwen-plus, qwen-turbo, qwen-max
- Vision：qwen-vl-max, qwen-vl-plus

---

### 6. 提取 0 道题目

**错误信息**：
```
成功提取 0 道题目
```

**可能原因**：
1. **图片中没有题目** - 上传了空白或无关图片
2. **图片质量太差** - 模糊、反光、角度倾斜
3. **手写体识别困难** - 目前主要支持印刷体
4. **置信度低于阈值** - 默认 0.6，可在设置中调整

**解决方案**：
1. 检查图片是否包含清晰的题目
2. 重新拍摄或扫描图片
3. 调整置信度阈值（设置 → 高级设置）
4. 查看错误详情获取具体原因

---

## 查看错误详情的三种方式

### 方式一：前端提示（推荐）

上传提取失败时，前端会显示：
- ❌ **错误名称** - 如"证书验证失败"
- **错误详情** - 具体原因说明
- 💡 **解决方案** - 建议的处理方法

### 方式二：查看日志

```bash
# 实时查看日志
tail -f /tmp/question-bank.log

# 查看最近 100 行
tail -100 /tmp/question-bank.log

# 搜索错误
grep -i "error\|extract" /tmp/question-bank.log
```

### 方式三：浏览器开发者工具

1. 按 F12 打开开发者工具
2. 切换到 Network（网络）标签
3. 上传文件并提取
4. 查看请求响应中的详细错误信息

---

## 调试技巧

### 1. 测试 API 连通性

```bash
# 测试阿里云 API
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-plus","messages":[{"role":"user","content":"你好"}]}'
```

### 2. 测试图片提取

```bash
# 使用 curl 测试
curl -X POST http://localhost:8000/api/agent/extract/image \
  -F "files=@/path/to/your/image.jpg"
```

### 3. 临时提高日志级别

编辑 `web/main.py`，设置日志级别为 DEBUG：
```python
logging.basicConfig(level=logging.DEBUG)
```

---

## 配置检查清单

遇到问题时，按以下顺序检查：

- [ ] 服务是否正常运行（`curl http://localhost:8000/health`）
- [ ] API Key 是否配置（设置 → AI 模型配置）
- [ ] SSL 验证配置是否正确（`.env` 文件中 `VERIFY_SSL=false`）
- [ ] 网络是否连通（`ping dashscope.aliyuncs.com`）
- [ ] 模型是否可用（阿里云控制台确认）
- [ ] 图片质量是否清晰
- [ ] 日志中是否有详细错误信息

---

## 获取帮助

如果以上方法都无法解决问题：

1. **查看完整日志**：`/tmp/question-bank.log`
2. **检查配置**：`config/agent.json`
3. **提交 Issue**：https://github.com/superno188462/question-bank-system/issues
4. **提供信息**：
   - 错误截图
   - 日志片段（脱敏 API Key）
   - 复现步骤

---

## 附录：错误代码对照表

| 错误名称 | 错误代码 | 说明 |
|---------|---------|------|
| 证书验证失败 | SSL_ERROR | SSL/TLS 证书问题 |
| 网络连接失败 | NETWORK_ERROR | 网络不通或超时 |
| 认证失败 | AUTH_ERROR | API Key 无效 |
| 模型不可用 | MODEL_ERROR | 模型不存在或未开通 |
| JSON 解析失败 | PARSE_ERROR | 模型响应格式错误 |
| 提取失败 | EXTRACT_ERROR | 未知提取错误 |
