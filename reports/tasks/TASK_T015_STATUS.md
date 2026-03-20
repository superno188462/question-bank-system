# 任务 T015 状态

**任务**: 用户上传图片题目后 F12 控制台显示 403 错误  
**开始时间**: 2026-03-20 10:25  
**状态**: ✅ 开发已完成，等待测试验证  
**完成时间**: 2026-03-20 10:35  

---

## 问题摘要

### 现象
- 用户上传题目图片
- F12 控制台显示 403 错误
- 图片提取失败

### 根本原因
- ❌ 前端未实现图片提取功能（TODO 状态）
- ❌ 缺少 API 接口调用代码
- ❌ 使用模拟数据而非真实 API

---

## 修复内容

### 1. 新增 API 接口

**文件**: `web_frontend/src/api/question.ts`

```typescript
// 从图片提取题目
async extractFromImage(file: File): Promise<ExtractResult>

// 从文档提取题目
async extractFromDocument(file: File): Promise<ExtractResult>
```

### 2. 实现前端功能

**文件**: `web_frontend/src/views/AIAskView.vue`

**修改**:
- ✅ 实现 `handleAsk()` 函数调用真实 API
- ✅ 支持图片上传和提取
- ✅ 支持文档上传和提取
- ✅ 完善的错误处理
- ✅ 友好的用户提示

---

## 修改文件

| 文件 | 修改类型 | 行数 | 说明 |
|------|---------|------|------|
| `web_frontend/src/api/question.ts` | 修改 | +40 | 新增 API 方法 |
| `web_frontend/src/views/AIAskView.vue` | 重写 | 640 | 实现真实功能 |

---

## 功能流程

### 图片上传流程

```
用户选择图片
    ↓
前端验证文件类型
    ↓
调用 /api/agent/extract/image
    ↓
后端保存图片到临时文件
    ↓
调用 ImageExtractor 提取
    ↓
返回提取结果
    ↓
前端展示结果和置信度
```

### 错误处理流程

```
API 调用失败
    ↓
捕获异常
    ↓
检查错误类型
    ↓
显示友好错误提示
    ↓
记录错误日志
```

---

## 测试验证

### 待验证项

- [ ] 前端编译通过
- [ ] 图片上传功能正常
- [ ] 文档上传功能正常
- [ ] 错误提示正确显示
- [ ] 提取结果正确展示

### 测试命令

```bash
# 启动前端
cd web_frontend
npm run dev

# 启动后端
cd /home/zkjiao/usr/github/question-bank-system
uv run uvicorn web.main:app --reload --port 8000

# 访问
http://localhost:5173/ai-ask
```

---

## 技术要点

### 1. FormData 上传

```typescript
const formData = new FormData()
formData.append('files', file)

return api.post('/agent/extract/image', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})
```

### 2. 文件类型判断

```typescript
const isImage = file.type.startsWith('image/')
if (isImage) {
  result = await questionApi.extractFromImage(file)
} else {
  result = await questionApi.extractFromDocument(file)
}
```

### 3. 错误处理

```typescript
try {
  result = await questionApi.extractFromImage(file)
  
  if (result.error) {
    throw new Error(result.error)
  }
  
  if (result.total_count === 0) {
    throw new Error('未能从文件中提取到题目')
  }
} catch (error: any) {
  ElMessage.error(error.message || '操作失败，请重试')
}
```

---

## 后端接口状态

| 接口 | 路径 | 状态 | 说明 |
|------|------|------|------|
| 图片提取 | POST /api/agent/extract/image | ✅ 已实现 | 从图片提取题目 |
| 文档提取 | POST /api/agent/extract/document | ✅ 已实现 | 从文档提取题目 |
| AI 问答 | POST /api/ai/ask | ✅ 已实现 | 文本问答 |

---

## 下一步行动

### 立即行动
- [ ] 编译前端代码
- [ ] 测试图片上传功能
- [ ] 测试文档上传功能

### 短期优化
- [ ] 添加上传进度提示
- [ ] 支持批量上传
- [ ] 添加图片预览

### 中期优化
- [ ] 实现添加到预备题库
- [ ] 支持手动编辑提取结果
- [ ] 保存提取历史

---

## 输出文档

| 文档 | 状态 | 路径 |
|------|------|------|
| 修复报告 | ✅ 完成 | docs/FIX_REPORT_T015.md |
| 任务状态 | ✅ 完成 | TASK_T015_STATUS.md |

---

*最后更新*: 2026-03-20 10:35  
*更新人*: Developer (nanobot)  
*任务状态*: ✅ **开发已完成，等待测试验证**
