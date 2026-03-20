# 任务 T015 - 图片上传 403 错误修复方案

**任务编号**: T015  
**任务名称**: 修复图片上传 403 错误  
**执行时间**: 2026-03-20 09:45  
**执行人**: Architect (nanobot)  
**问题现象**: 上传题目图片后 F12 控制台显示 403 错误  
**优先级**: 🔴 P0 (阻塞功能)

---

## 执行摘要

### 问题现象

1. **用户操作**: 上传题目图片
2. **错误表现**: F12 控制台显示 `error 403 for url`
3. **功能影响**: 图片提取失败，无法使用 AI 提取功能

### 根本原因

经过分析，发现以下问题：

1. **🔴 API Key 未配置** (主要原因)
   - `.env` 文件中 `VISION_API_KEY=YOUR_VISION_API_KEY_HERE` (占位符)
   - `config/agent.json` 中 `vision.api_key=YOUR_VISION_API_KEY_HERE` (占位符)
   - 导致阿里云百炼 API 调用被拒绝 (403 Forbidden)

2. **🟡 配置验证逻辑问题**
   - `AgentConfig.validate()` 会抛出异常，但前端可能未正确处理
   - 错误信息未清晰传达给用户

3. **🟡 前端错误处理不足**
   - 可能未显示详细的错误信息
   - 用户不知道是 API Key 问题

---

## 问题分析

### 1. API Key 配置状态

#### .env 文件检查
```bash
# 当前配置
VISION_API_KEY=YOUR_VISION_API_KEY_HERE  # ❌ 占位符，需要替换为真实 API Key
LLM_API_KEY=YOUR_LLM_API_KEY_HERE        # ❌ 占位符
EMBED_API_KEY=YOUR_EMBEDDING_API_KEY_HERE # ❌ 占位符
```

#### config/agent.json 检查
```json
{
  "vision": {
    "model_id": "qwen-vl-max",
    "api_key": "YOUR_VISION_API_KEY_HERE",  // ❌ 占位符
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
  },
  "llm": {
    "model_id": "qwen-plus",
    "api_key": "YOUR_LLM_API_KEY_HERE",  // ❌ 占位符
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
  }
}
```

### 2. 403 错误来源分析

#### 可能的 403 错误点

| 错误点 | 位置 | 原因 | 概率 |
|--------|------|------|------|
| **阿里云 API 调用** | agent/services/model_client.py | API Key 无效/未配置 | 90% |
| **CORS 跨域** | web/main.py | CORS 配置问题 | 5% |
| **文件权限** | web/api/agent.py | 上传目录无权限 | 3% |
| **API 路由** | web/api/agent.py | 路由未注册 | 2% |

#### 代码分析

```python
# web/api/agent.py: extract_from_image
async def extract_from_image(files: List[UploadFile] = File(...)):
    try:
        # 1. 验证配置
        AgentConfig.validate()  # ✅ 会检查 API Key
        
        # 2. 保存上传文件
        temp_dir = tempfile.mkdtemp()
        # ...
        
        # 3. 提取题目
        extractor = ImageExtractor()
        result = extractor.extract(image_paths[0])  # ❌ 这里调用 API
        
        # ...
```

```python
# agent/extractors/image_extractor.py
def extract(self, image_path: str) -> Dict:
    # 调用 Vision API
    response = self.model_client.call_vision(image_path)  # ❌ 403 错误发生在这里
```

```python
# agent/services/model_client.py
def call_vision(self, image_path: str) -> Dict:
    # 使用 VISION_API_KEY 调用阿里云 API
    response = openai.ChatCompletion.create(
        model=self.vision_model_id,
        messages=[...],
        api_key=self.vision_api_key  # ❌ 如果是占位符，API 会返回 403
    )
```

### 3. CORS 配置检查

```python
# web/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ 允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**结论**: CORS 配置正确，不是 403 错误的原因。

### 4. 文件权限检查

```python
# web/api/agent.py
temp_dir = tempfile.mkdtemp()  # ✅ 使用系统临时目录，权限正确
file_path = os.path.join(temp_dir, file.filename)
with open(file_path, "wb") as f:  # ✅ 写入权限正常
    content = await file.read()
    f.write(content)
```

**结论**: 文件权限正常，不是 403 错误的原因。

---

## 解决方案

### 方案 1: 配置 API Key (推荐) ⭐

**步骤**:

1. **获取阿里云 API Key**
   - 访问阿里云百炼控制台：https://bailian.console.aliyun.com/
   - 创建/获取 API Key
   - 确保开通以下服务：
     - qwen-vl-max (视觉模型)
     - qwen-plus (文本模型)
     - text-embedding-v3 (Embedding 模型，可选)

2. **更新 .env 文件**
   ```bash
   # 编辑 .env 文件
   VISION_API_KEY=sk-xxxxxxxxxxxxxxxx  # 替换为真实 API Key
   LLM_API_KEY=sk-xxxxxxxxxxxxxxxx     # 替换为真实 API Key
   EMBED_API_KEY=sk-xxxxxxxxxxxxxxxx   # 替换为真实 API Key（如使用）
   ```

3. **更新 config/agent.json**
   ```json
   {
     "vision": {
       "model_id": "qwen-vl-max",
       "api_key": "sk-xxxxxxxxxxxxxxxx",
       "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
     },
     "llm": {
       "model_id": "qwen-plus",
       "api_key": "sk-xxxxxxxxxxxxxxxx",
       "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
     }
   }
   ```

4. **重启 Web 服务**
   ```bash
   # 停止服务
   pkill -f "uvicorn web.main:app"
   
   # 启动服务
   ./run.sh
   ```

5. **验证配置**
   ```bash
   # 测试 API 端点
   curl -X POST http://localhost:8000/api/agent/extract/image \
     -F "file=@test_image.png"
   ```

**预计工时**: 10-15 分钟

---

### 方案 2: 改进错误提示 (辅助)

**问题**: 当前错误提示不够清晰，用户不知道是 API Key 问题

**改进方案**:

1. **后端错误处理**
   ```python
   # web/api/agent.py
   @router.post("/extract/image")
   async def extract_from_image(files: List[UploadFile] = File(...)):
       try:
           # 验证配置
           AgentConfig.validate()
       except ValueError as e:
           # 返回清晰的错误信息
           raise HTTPException(
               status_code=400,
               detail={
                   "error": "配置错误",
                   "message": str(e),
                   "solution": "请在 Web 设置页面配置 API Key，或编辑 .env 文件"
               }
           )
       
       # ... 其余代码
   ```

2. **前端错误显示**
   ```javascript
   // web/static/js/app.js
   async function uploadAndExtract() {
       try {
           const response = await fetch(endpoint, {
               method: 'POST',
               body: formData
           });
           
           if (!response.ok) {
               const error = await response.json();
               if (response.status === 400 && error.detail?.error === "配置错误") {
                   // 显示配置错误提示
                   showConfigError(error.detail);
               } else {
                   // 显示一般错误
                   showError(error);
               }
               return;
           }
           
           // ... 处理成功
       } catch (err) {
           showError(err);
       }
   }
   
   function showConfigError(detail) {
       // 显示配置向导
       showModal({
           title: "API Key 未配置",
           message: detail.message,
           solution: detail.solution,
           actions: [
               { text: "去配置", onclick: "openSettingsPage()" },
               { text: "取消", onclick: "closeModal()" }
           ]
       });
   }
   ```

**预计工时**: 30-60 分钟

---

### 方案 3: 添加配置检查页面 (长期)

**功能**: 在 Web 界面添加配置检查功能

**实现**:

1. **后端 API**
   ```python
   # web/api/agent.py
   @router.get("/config/status")
   async def get_config_status():
       """获取配置状态"""
       return {
           "llm_configured": bool(AgentConfig.LLM_API_KEY and AgentConfig.LLM_API_KEY != "YOUR_LLM_API_KEY_HERE"),
           "vision_configured": bool(AgentConfig.VISION_API_KEY and AgentConfig.VISION_API_KEY != "YOUR_VISION_API_KEY_HERE"),
           "embed_configured": bool(AgentConfig.EMBED_API_KEY and AgentConfig.EMBED_API_KEY != "YOUR_EMBEDDING_API_KEY_HERE"),
           "all_configured": AgentConfig.is_configured()
       }
   ```

2. **前端检查**
   ```javascript
   // 页面加载时检查配置
   async function checkConfig() {
       const status = await fetch('/api/agent/config/status');
       const data = await status.json();
       
       if (!data.all_configured) {
           showConfigWarning(data);
       }
   }
   ```

**预计工时**: 1-2 小时

---

## 实施计划

### 阶段 1: 立即修复 (P0) - 15 分钟

**目标**: 配置 API Key，解决 403 错误

- [ ] 获取阿里云 API Key
- [ ] 更新 .env 文件
- [ ] 更新 config/agent.json
- [ ] 重启 Web 服务
- [ ] 验证图片上传功能

**验收标准**:
- 图片上传成功
- F12 控制台无 403 错误
- AI 提取功能正常

### 阶段 2: 改进错误提示 (P1) - 1 小时

**目标**: 改善用户体验，清晰显示配置错误

- [ ] 后端添加详细错误信息
- [ ] 前端显示配置错误提示
- [ ] 添加配置向导链接

**验收标准**:
- 配置错误时显示清晰提示
- 提供解决方案链接
- 用户知道如何修复

### 阶段 3: 配置检查功能 (P2) - 2 小时

**目标**: 预防配置问题

- [ ] 添加配置状态 API
- [ ] 前端页面加载时检查配置
- [ ] 显示配置警告
- [ ] 提供配置入口

**验收标准**:
- 未配置时显示警告
- 提供一键配置入口
- 配置状态实时更新

---

## 验证步骤

### 1. 验证 API Key 配置

```bash
# 检查 .env 文件
cat .env | grep API_KEY

# 应该显示真实 API Key（不是占位符）
VISION_API_KEY=sk-xxxxxxxxxxxxxxxx
LLM_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### 2. 验证 Web 服务

```bash
# 检查服务日志
tail -f logs/web.log

# 应该看到
✅ 已加载环境变量：/path/to/.env
✅ 数据库检查完成
```

### 3. 测试图片上传

```bash
# 使用 curl 测试
curl -X POST http://localhost:8000/api/agent/extract/image \
  -F "file=@test_image.png" \
  -H "Accept: application/json"

# 应该返回
{
  "success": true,
  "questions": [...],
  "message": "提取成功"
}
```

### 4. 前端验证

1. 打开浏览器 F12 控制台
2. 上传测试图片
3. 检查 Network 标签
   - 请求应该返回 200 OK
   - 无 403 错误
4. 检查 Console 标签
   - 无错误信息

---

## 风险与缓解

### 风险 1: API Key 泄露
- **影响**: 高 (安全风险)
- **概率**: 中
- **缓解**:
  - .env 文件加入 .gitignore
  - config/agent.json 使用示例文件
  - 文档中强调不要提交真实 API Key

### 风险 2: API Key 无效
- **影响**: 高 (功能不可用)
- **概率**: 低
- **缓解**:
  - 测试 API Key 是否有效
  - 检查阿里云账户余额
  - 确认服务已开通

### 风险 3: CORS 问题
- **影响**: 中 (跨域请求失败)
- **概率**: 低
- **缓解**:
  - 已配置允许所有源
  - 检查浏览器控制台
  - 验证请求头

---

## 验收标准

### 功能验收
- [ ] 图片上传成功
- [ ] AI 提取功能正常
- [ ] F12 控制台无 403 错误
- [ ] 返回提取结果

### 配置验收
- [ ] .env 文件配置正确
- [ ] config/agent.json 配置正确
- [ ] API Key 不是占位符
- [ ] Web 服务正常启动

### 错误处理验收
- [ ] 配置错误时显示清晰提示
- [ ] 提供解决方案
- [ ] 前端错误处理完善

---

## 交付物

### 配置文件
- 更新后的 .env 文件
- 更新后的 config/agent.json

### 代码修复
- web/api/agent.py (错误处理改进)
- web/static/js/app.js (错误显示改进)

### 文档
- 配置指南更新
- 故障排除文档

---

**下一步**:
- [ ] 转交 Developer 配置 API Key
- [ ] 验证图片上传功能
- [ ] 转交 Tester 全面测试
- [ ] 转交 Reviewer 审查

---

*报告生成时间*: 2026-03-20 09:50  
*报告人*: Architect (nanobot)  
*问题优先级*: P0 (阻塞功能)  
*预计修复时间*: 15-30 分钟
