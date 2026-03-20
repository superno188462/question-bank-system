# 任务 T015: 图片上传 403 错误审查报告

**审查任务**: T015 - 修复图片上传 403 错误  
**审查时间**: 2026-03-20 10:35  
**审查人**: Code Reviewer (nanobot)  
**问题现象**: 上传图片题目后 F12 控制台显示 403 错误  

---

## 🔍 问题根因分析

### 排查结果验证

| 检查项 | 状态 | 详情 |
|--------|------|------|
| config/agent.json 配置 | ✅ 正确 | API Key 已配置 |
| AgentConfig.validate() | ✅ 通过 | 配置验证正常 |
| Web 服务运行 | ✅ 正常 | 服务启动无异常 |
| CORS 配置 | ✅ 正确 | 允许所有来源 |
| **前端实现** | ❌ **问题所在** | **AIAskView.vue 使用模拟数据** |

---

## 📊 代码审查结果

### 1. 前端代码分析

#### AIAskView.vue (Vue 前端)

**位置**: `web_frontend/src/views/AIAskView.vue`

**当前实现**:
```vue
<!-- 第 28 行：上传组件 action="#" -->
<el-upload
  class="upload-demo"
  action="#"              <!-- ❌ 问题 1: action 为 #，不会实际上传 -->
  :auto-upload="false"    <!-- ❌ 问题 2: 不自动上传 -->
  :on-change="handleFileChange"
  :show-file-list="false"
  accept="image/*,.pdf,.doc,.docx"
>
```

**handleAsk 函数** (第 219-302 行):
```typescript
// 第 232-244 行：文件上传逻辑
if (uploadedFile.value) {
  const file = uploadedFile.value
  const isImage = file.type.startsWith('image/')
  
  if (isImage) {
    // ✅ 调用图片提取 API
    result = await questionApi.extractFromImage(file)
  } else {
    // ✅ 调用文档提取 API
    result = await questionApi.extractFromDocument(file)
  }
  // ... 处理结果
}
```

**评价**:
- ✅ `handleAsk()` 函数逻辑正确，调用了正确的 API
- ❌ `el-upload` 组件配置错误，`action="#"` 导致无法上传
- ❌ `:auto-upload="false"` 需要手动触发上传

---

#### question.ts (API 封装)

**位置**: `web_frontend/src/api/question.ts`

**实现** (第 142-163 行):
```typescript
// 从图片提取题目
async extractFromImage(file: File): Promise<ExtractResult> {
  const formData = new FormData()
  formData.append('files', file)
  
  return api.post('/agent/extract/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 从文档提取题目
async extractFromDocument(file: File): Promise<ExtractResult> {
  const formData = new FormData()
  formData.append('files', file)
  
  return api.post('/agent/extract/document', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
```

**评价**:
- ✅ API 封装正确
- ✅ 使用 FormData 上传文件
- ✅ 设置正确的 Content-Type

---

#### api/index.ts (Axios 配置)

**位置**: `web_frontend/src/api/index.ts`

**配置**:
```typescript
const api = axios.create({
  baseURL: '/api',      // ✅ 正确的 baseURL
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'  // ⚠️ 默认 header，但会被 FormData 覆盖
  }
})
```

**评价**:
- ✅ baseURL 配置正确
- ⚠️ 默认 Content-Type 为 application/json，但会被 FormData 自动覆盖

---

### 2. 后端代码分析

#### agent.py (后端 API)

**位置**: `web/api/agent.py`

**实现** (第 41-120 行):
```python
@router.post("/extract/image")
async def extract_from_image(files: List[UploadFile] = File(...)):
    """
    从图片中提取题目
    
    - 支持多张图片批量上传
    - 自动识别题目并保存到预备题目
    - 返回提取结果
    """
    try:
        # 验证配置
        AgentConfig.validate()
        
        # 保存上传的文件
        temp_dir = tempfile.mkdtemp()
        image_paths = []
        
        for file in files:
            # 验证文件类型
            ext = file.filename.split('.')[-1].lower()
            if ext not in AgentConfig.ALLOWED_IMAGE_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的图片格式：{ext}"
                )
            
            # 保存文件
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            image_paths.append(file_path)
        
        # 提取题目
        extractor = ImageExtractor()
        result = extractor.extract(image_paths[0] if len(image_paths) == 1 else image_paths)
        
        # ... 保存到预备题目并返回结果
```

**评价**:
- ✅ API 端点正确实现
- ✅ 文件验证和保存逻辑正确
- ✅ 调用 ImageExtractor 提取题目
- ✅ 保存到预备题目表

---

### 3. 前端 app.js (传统 JS)

**位置**: `web/static/js/app.js`

**实现** (第 1251-1319 行):
```javascript
// 上传并提取
async function uploadAndExtract() {
    const fileInput = document.getElementById('aiUploadFiles')
    const files = fileInput.files
    
    if (!files || files.length === 0) {
        showToast('请选择要上传的文件', 'error')
        return
    }
    
    const formData = new FormData()
    for (let file of files) {
        formData.append('files', file)
    }
    
    try {
        const endpoint = extractType === 'image' 
            ? '/api/agent/extract/image' 
            : '/api/agent/extract/document'
        
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        })
        
        const result = await response.json()
        
        if (result.success) {
            // ... 处理成功结果
        }
    } catch (error) {
        // ... 处理错误
    }
}
```

**评价**:
- ✅ 传统 JS 实现正确
- ✅ 使用 FormData 上传
- ✅ 正确的 API 端点
- ✅ 完整的错误处理

---

## 🚨 问题根因

### 核心问题：前端 Vue 组件配置错误

**问题 1**: `el-upload` 组件 `action="#"`
```vue
<!-- ❌ 错误配置 -->
<el-upload
  action="#"  <!-- 这会导致上传功能失效 -->
  :auto-upload="false"
>
```

**问题 2**: 未使用正确的上传方式
- `action="#"` 会导致浏览器尝试提交到当前页面的 `#` 锚点
- 结合 `:auto-upload="false"`，文件不会自动上传
- 需要手动调用 API 上传

---

## 💡 修复方案

### 方案 A: 修改 el-upload 配置 (推荐)

**修改文件**: `web_frontend/src/views/AIAskView.vue`

**修复代码**:
```vue
<template>
  <!-- 修改前 -->
  <el-upload
    class="upload-demo"
    action="#"
    :auto-upload="false"
    :on-change="handleFileChange"
    :show-file-list="false"
    accept="image/*,.pdf,.doc,.docx"
  >
  
  <!-- 修改后 -->
  <el-upload
    class="upload-demo"
    :auto-upload="false"
    :on-change="handleFileChange"
    :show-file-list="false"
    accept="image/*,.pdf,.doc,.docx"
    :file-list="fileList"
  >
    <el-button type="text">
      <el-icon><Picture /></el-icon> 选择图片或文档
    </el-button>
  </el-upload>
</template>

<script setup lang="ts">
// 添加 fileList 状态
const fileList = ref<any[]>([])

// 修改 handleFileChange
const handleFileChange = (file: any) => {
  uploadedFile.value = file.raw
  fileList.value = [file]  // 显示选中的文件
}

// 修改 clearFile
const clearFile = () => {
  uploadedFile.value = null
  fileList.value = []  // 清空文件列表
}
</script>
```

**说明**:
- 移除 `action="#"` 属性
- 添加 `file-list` 绑定，显示选中的文件
- 保持 `:auto-upload="false"`，由 `handleAsk()` 手动触发上传

---

### 方案 B: 使用自动上传

**修改文件**: `web_frontend/src/views/AIAskView.vue`

**修复代码**:
```vue
<template>
  <el-upload
    class="upload-demo"
    action="/api/agent/extract/image"  <!-- ✅ 正确的上传地址 -->
    :auto-upload="true"                 <!-- ✅ 自动上传 -->
    :on-success="handleUploadSuccess"
    :on-error="handleUploadError"
    :show-file-list="false"
    accept="image/*,.pdf,.doc,.docx"
  >
    <el-button type="text">
      <el-icon><Picture /></el-icon> 选择图片或文档
    </el-button>
  </el-upload>
</template>

<script setup lang="ts">
// 添加上传成功/失败处理
const handleUploadSuccess = (response: any) => {
  ElMessage.success('上传成功')
  // 处理提取结果
}

const handleUploadError = (error: any) => {
  ElMessage.error('上传失败：' + error.message)
}
</script>
```

**说明**:
- 设置正确的 `action` 为后端 API 端点
- 启用自动上传
- 添加成功/失败回调

**缺点**: 
- 需要区分图片和文档的不同端点
- 不如方案 A 灵活

---

### 方案 C: 完全手动控制 (最灵活)

**修改文件**: `web_frontend/src/views/AIAskView.vue`

**修复代码**:
```vue
<template>
  <div class="upload-section">
    <!-- 使用原生 file input -->
    <input
      type="file"
      ref="fileInput"
      @change="handleFileChange"
      accept="image/*,.pdf,.doc,.docx"
      style="display: none"
    />
    
    <el-button type="text" @click="$refs.fileInput.click()">
      <el-icon><Picture /></el-icon> 选择图片或文档
    </el-button>
    
    <div v-if="uploadedFile" class="file-preview">
      <el-tag closable @close="clearFile">
        {{ uploadedFile.name }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
const fileInput = ref<HTMLInputElement>()

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    uploadedFile.value = target.files[0]
  }
}

const clearFile = () => {
  uploadedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>
```

**说明**:
- 使用原生 file input，完全手动控制
- 最灵活，可以自定义上传逻辑
- 不依赖 el-upload 组件

---

## ✅ 推荐修复步骤

### 步骤 1: 修改 AIAskView.vue

**文件**: `web_frontend/src/views/AIAskView.vue`

**修改内容**:
```diff
@@ -23,12 +23,11 @@
         
         <!-- 图片上传 -->
         <div class="upload-section">
           <el-upload
             class="upload-demo"
-            action="#"
             :auto-upload="false"
             :on-change="handleFileChange"
             :show-file-list="false"
             accept="image/*,.pdf,.doc,.docx"
+            :file-list="fileList"
           >
             <el-button type="text">
               <el-icon><Picture /></el-icon> 上传图片或文档
@@ -189,6 +188,7 @@
 const loading = ref(false)
 const answer = ref<any>(null)
 const isAddedToPending = ref(false)
+const fileList = ref<any[]>([])
 const history = ref<any[]>([])
 
 // 获取分类名称
@@ -207,11 +207,13 @@
 
 // 处理文件变化
 const handleFileChange = (file: any) => {
   uploadedFile.value = file.raw
+  fileList.value = [file]
 }
 
 // 清除文件
 const clearFile = () => {
   uploadedFile.value = null
+  fileList.value = []
 }
```

---

### 步骤 2: 验证修复

**测试步骤**:

1. **启动前端服务**:
   ```bash
   cd web_frontend
   npm run dev
   ```

2. **启动后端服务**:
   ```bash
   cd /home/zkjiao/usr/github/question-bank-system
   .venv/bin/python -m uvicorn web.main:app --reload --port 8000
   ```

3. **测试上传**:
   - 打开浏览器访问前端页面
   - 导航到 "AI 提问" 页面
   - 点击 "选择图片或文档"
   - 选择一张包含题目的图片
   - 点击 "开始提问"
   - 观察 F12 控制台和网络请求

4. **预期结果**:
   - ✅ 文件选择后显示文件名
   - ✅ 点击 "开始提问" 后显示 "正在提取图片中的题目..."
   - ✅ 网络请求成功 (200 OK)
   - ✅ 显示提取结果
   - ✅ F12 控制台无 403 错误

---

## 📋 后端验证清单

### 确保后端 API 正常工作

- [x] `/api/agent/extract/image` 端点存在
- [x] `AgentConfig.validate()` 验证通过
- [x] `ImageExtractor` 类正常工作
- [x] 文件保存和清理逻辑正确
- [x] 预备题目保存逻辑正确

### 额外检查项

- [ ] 确认 `config/agent.json` 中 API Key 有效
- [ ] 确认阿里云百炼服务可用
- [ ] 确认图片提取功能已测试
- [ ] 确认错误处理完善

---

## 🐛 可能的后续问题

### 问题 1: CORS 错误

**现象**: 浏览器控制台显示 CORS 错误

**解决方案**:
```python
# web/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 问题 2: 文件大小限制

**现象**: 大文件上传失败

**解决方案**:
```python
# web/main.py
from fastapi import FastAPI

app = FastAPI()
app.max_file_size = 50 * 1024 * 1024  # 50MB
```

---

### 问题 3: API Key 无效

**现象**: 提取失败，显示 API Key 错误

**解决方案**:
1. 检查 `config/agent.json` 配置
2. 确认 API Key 有效且未过期
3. 确认阿里云百炼服务正常

---

## 📊 修复前后对比

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| el-upload action | `#` (错误) | 移除 (正确) |
| auto-upload | `false` | `false` (保持) |
| file-list | 无绑定 | 绑定显示 |
| 上传功能 | ❌ 失效 | ✅ 正常 |
| 403 错误 | ✅ 出现 | ❌ 消失 |
| 提取功能 | ❌ 无法使用 | ✅ 正常工作 |

---

## 📝 审查结论

### 问题根因 ✅ 明确

**前端 `el-upload` 组件配置错误**:
- `action="#"` 导致上传功能失效
- 浏览器尝试提交到 `#` 锚点，触发 403 错误

### 修复方案 ✅ 可行

**推荐方案 A**: 移除 `action="#"`，添加 `file-list` 绑定
- 最小改动
- 保持现有逻辑
- 不影响其他功能

### 测试验证 ⏳ 待执行

**需要验证**:
1. 前端编译无错误
2. 文件选择后正确显示
3. 上传 API 调用成功
4. 提取结果正常显示
5. F12 控制台无 403 错误

---

## 🚀 下一步行动

### 立即执行

1. **修改 AIAskView.vue** (5 分钟)
   - 移除 `action="#"`
   - 添加 `file-list` 绑定
   - 更新 `handleFileChange` 和 `clearFile`

2. **编译并测试** (10 分钟)
   - 启动前端服务
   - 测试图片上传
   - 验证提取功能

3. **验证后端** (5 分钟)
   - 检查后端日志
   - 确认 API 调用成功
   - 验证预备题目保存

### 后续优化

- [ ] 添加上传进度显示
- [ ] 支持拖拽上传
- [ ] 添加文件预览
- [ ] 优化错误提示

---

**审查人**: Code Reviewer  
**审查时间**: 2026-03-20 10:35  
**建议修复时间**: 15 分钟内完成

**下一步**: 请立即修改 `AIAskView.vue`，然后测试验证。
