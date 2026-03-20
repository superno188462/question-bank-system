# 浏览器翻译功能文档

## 功能概述

题库系统现已支持多语言界面翻译功能，目前支持：
- 🇨🇳 中文（简体）- zh-CN
- 🇺🇸 英文（English）- en-US

## 已实现功能

### 1. 多语言支持 (vue-i18n)
- 集成 vue-i18n v9
- 支持 Composition API
- 自动检测浏览器语言
- 语言设置持久化（localStorage）

### 2. 语言切换组件
- 位置：页面右上角导航栏
- 组件：`LanguageSwitcher.vue`
- 功能：一键切换中英文界面
- 提示：切换成功后显示提示消息

### 3. 翻译配置文件
- 中文：`src/locales/zh-CN.ts`
- 英文：`src/locales/en-US.ts`
- 配置：`src/i18n/index.ts`

### 4. 翻译工具服务
- 文件：`src/utils/translator.ts`
- 功能：
  - 文本翻译（支持外部 API 集成）
  - 批量翻译
  - 题目内容翻译
  - 语言检测
  - 页面内容翻译（实验性）

### 5. 已国际化的页面
- ✅ HomeView.vue - 主页面导航和布局
- ✅ QuestionView.vue - 题目管理页面

## 使用方法

### 切换语言
1. 点击页面右上角的地球图标 🌐
2. 选择目标语言（中文或 English）
3. 界面将自动切换为所选语言

### 添加新的翻译文本

1. 在 `src/locales/zh-CN.ts` 和 `src/locales/en-US.ts` 中添加翻译键值对：

```typescript
// zh-CN.ts
export default {
  // ... 现有翻译
  myNewFeature: {
    title: '新功能标题',
    description: '新功能描述'
  }
}

// en-US.ts
export default {
  // ... 现有翻译
  myNewFeature: {
    title: 'New Feature Title',
    description: 'New Feature Description'
  }
}
```

2. 在组件中使用：

```vue
<template>
  <h1>{{ t('myNewFeature.title') }}</h1>
  <p>{{ t('myNewFeature.description') }}</p>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>
```

### 集成外部翻译 API（可选）

编辑 `src/utils/translator.ts`：

```typescript
const TRANSLATION_API = {
  enabled: true, // 启用外部翻译
  endpoint: 'https://api.translation-service.com/translate',
  apiKey: 'your-api-key'
}
```

## 文件结构

```
web_frontend/src/
├── i18n/
│   └── index.ts          # i18n 配置
├── locales/
│   ├── zh-CN.ts          # 中文翻译
│   └── en-US.ts          # 英文翻译
├── components/
│   └── LanguageSwitcher.vue  # 语言切换组件
├── utils/
│   └── translator.ts     # 翻译工具服务
├── views/
│   ├── HomeView.vue      # 主页面（已国际化）
│   └── QuestionView.vue  # 题目页面（已国际化）
└── main.ts               # 应用入口（已集成 i18n）
```

## 待完成功能

### 需要国际化的其他页面
- [ ] CategoryView.vue - 分类管理
- [ ] CreateQuestionView.vue - 创建题目
- [ ] EditQuestionView.vue - 编辑题目
- [ ] AIAskView.vue - AI 提问
- [ ] PendingQuestionsView.vue - 预备题目

### 需要国际化的组件
- [ ] CategoryForm.vue - 分类表单
- [ ] CategoryTree.vue - 分类树
- [ ] QuestionForm.vue - 题目表单
- [ ] QuestionDetail.vue - 题目详情

### 高级功能
- [ ] 题目内容实时翻译（题干、选项、解析）
- [ ] 批量翻译题目
- [ ] 翻译历史记录
- [ ] 更多语言支持（日语、韩语等）

## 技术细节

### 依赖
- vue-i18n: ^9.0.0
- Vue 3 Composition API
- Element Plus

### 语言检测顺序
1. localStorage 中保存的用户选择
2. 浏览器语言设置
3. 默认语言（zh-CN）

### 性能优化
- 翻译文本缓存
- 懒加载语言包（未来扩展）
- 避免不必要的重新渲染

## 测试

### 手动测试
1. 启动前端开发服务器：
   ```bash
   cd web_frontend
   npm run dev
   ```

2. 访问 http://localhost:5173

3. 测试语言切换功能

### 自动化测试（待实现）
- 语言切换测试
- 翻译文本渲染测试
- localStorage 持久化测试

## 常见问题

### Q: 切换语言后部分文本未更新？
A: 确保使用了 `t()` 函数而不是硬编码文本。

### Q: 如何添加新语言？
A: 
1. 在 `src/locales/` 创建新语言文件（如 `ja-JP.ts`）
2. 在 `src/i18n/index.ts` 中注册新语言
3. 在 `LanguageSwitcher.vue` 中添加语言选项

### Q: 翻译 API 如何使用？
A: 目前翻译 API 功能已预留，配置 `TRANSLATION_API.enabled = true` 并填写端点和密钥即可。

## 更新日志

### v1.0.0 (2026-03-16)
- ✅ 初始版本
- ✅ 集成 vue-i18n
- ✅ 中英文翻译
- ✅ 语言切换组件
- ✅ HomeView 和 QuestionView 国际化
- ✅ 翻译工具服务
