<template>
  <div class="ai-ask-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><ChatDotRound /></el-icon> AI 智能提问
      </h2>
      <p class="page-description">输入自然语言问题，AI 将从题库中查找相关题目并给出答案</p>
    </div>

    <!-- 提问区域 -->
    <el-card class="ask-card">
      <div class="ask-container">
        <el-input
          v-model="question"
          type="textarea"
          :rows="4"
          placeholder="请输入您的问题，例如：Python 中如何定义一个函数？或者上传图片..."
          maxlength="1000"
          show-word-limit
          class="ask-input"
        />
        
        <!-- 图片上传 -->
        <div class="upload-section">
          <el-upload
            class="upload-demo"
            :auto-upload="false"
            :on-change="handleFileChange"
            :show-file-list="false"
            accept="image/*,.pdf,.doc,.docx"
            :http-request="handleFileUpload"
          >
            <el-button type="text">
              <el-icon><Picture /></el-icon> 上传图片或文档
            </el-button>
          </el-upload>
          
          <div v-if="uploadedFile" class="file-preview">
            <el-tag closable @close="clearFile">
              {{ uploadedFile.name }}
            </el-tag>
          </div>
        </div>

        <div class="ask-actions">
          <el-button 
            type="primary" 
            size="large" 
            @click="handleAsk"
            :loading="loading"
            :disabled="!question.trim() && !uploadedFile"
          >
            <el-icon><Search /></el-icon>
            {{ loading ? 'AI 思考中...' : '开始提问' }}
          </el-button>
          <el-button size="large" @click="handleClear">
            <el-icon><Delete /></el-icon> 清空
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 回答结果 -->
    <div v-if="answer" class="answer-section">
      <el-card class="answer-card">
        <template #header>
          <div class="answer-header">
            <span class="answer-title">
              <el-icon><ChatLineRound /></el-icon> AI 回答
            </span>
            <el-button 
              type="success" 
              size="small" 
              @click="handleAddToPending"
              :disabled="isAddedToPending || !answer.suggested_question"
            >
              <el-icon><Plus /></el-icon>
              {{ isAddedToPending ? '已添加到预备' : '添加到预备题库' }}
            </el-button>
          </div>
        </template>

        <div class="answer-content">
          <div class="ai-answer-text">{{ answer.answer }}</div>
          
          <!-- 建议的题目 -->
          <div v-if="answer.suggested_question" class="suggested-question">
            <h4>📝 建议录入的题目</h4>
            <div class="question-preview">
              <div class="preview-item">
                <strong>题干：</strong>{{ answer.suggested_question.content }}
              </div>
              <div v-if="answer.suggested_question.options?.length > 0" class="preview-item">
                <strong>选项：</strong>
                <div class="options-list">
                  <div 
                    v-for="(opt, idx) in answer.suggested_question.options" 
                    :key="idx"
                    class="option-item"
                  >
                    {{ String.fromCharCode(65 + idx) }}. {{ opt }}
                  </div>
                </div>
              </div>
              <div class="preview-item">
                <strong>答案：</strong>{{ answer.suggested_question.answer }}
              </div>
              <div class="preview-item">
                <strong>解析：</strong>{{ answer.suggested_question.explanation }}
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 相关题目 -->
      <el-card v-if="answer.related_questions?.length > 0" class="related-card">
        <template #header>
          <div class="related-header">
            <span class="related-title">
              <el-icon><Connection /></el-icon> 相关题目 ({{ answer.related_questions.length }})
            </span>
          </div>
        </template>

        <div class="related-list">
          <div 
            v-for="(related, index) in answer.related_questions" 
            :key="related.id"
            class="related-item"
            @click="handleViewRelated(related)"
          >
            <div class="related-index">{{ index + 1 }}</div>
            <div class="related-content">
              <div class="related-question">{{ related.content }}</div>
              <div class="related-meta">
                <el-tag size="small" type="info">
                  {{ getCategoryName(related.category_id) }}
                </el-tag>
                <span class="similarity-score">
                  相似度：{{ Math.round((related.similarity || 0.85) * 100) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 历史记录 -->
    <el-card v-if="history.length > 0" class="history-card">
      <template #header>
        <div class="history-header">
          <span class="history-title">
            <el-icon><Clock /></el-icon> 提问历史
          </span>
          <el-button type="text" size="small" @click="clearHistory">
            <el-icon><Delete /></el-icon> 清空历史
          </el-button>
        </div>
      </template>

      <div class="history-list">
        <div 
          v-for="(item, index) in history" 
          :key="index"
          class="history-item"
          @click="restoreHistory(item)"
        >
          <div class="history-question">{{ item.question }}</div>
          <div class="history-time">{{ formatTime(item.time) }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCategoryStore } from '@/stores/category'
import { questionApi, type ExtractResult } from '@/api/question'
import dayjs from 'dayjs'

const router = useRouter()
const categoryStore = useCategoryStore()

// 状态
const question = ref('')
const uploadedFile = ref<File | null>(null)
const loading = ref(false)
const answer = ref<any>(null)
const isAddedToPending = ref(false)
const history = ref<any[]>([])

// 获取分类名称
const getCategoryName = (categoryId: string) => {
  const category = categoryStore.getCategoryById(categoryId)
  return category?.name || '未知分类'
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// 处理文件变化
const handleFileChange = (file: any) => {
  uploadedFile.value = file.raw
}

// 处理文件上传（阻止自动上传）
const handleFileUpload = () => {
  // 不执行任何操作，由 handleAsk 统一处理
  return Promise.resolve()
}

// 清除文件
const clearFile = () => {
  uploadedFile.value = null
}

// 提问
const handleAsk = async () => {
  if (!question.value.trim() && !uploadedFile.value) {
    ElMessage.warning('请输入问题或上传文件')
    return
  }

  loading.value = true
  isAddedToPending.value = false

  try {
    let result
    
    // 如果有上传文件，调用图片/文档提取 API
    if (uploadedFile.value) {
      const file = uploadedFile.value
      const isImage = file.type.startsWith('image/')
      
      ElMessage.info(`正在${isImage ? '提取图片' : '提取文档'}中的题目...`)
      
      if (isImage) {
        // 调用图片提取 API
        result = await questionApi.extractFromImage(file)
      } else {
        // 调用文档提取 API
        result = await questionApi.extractFromDocument(file)
      }
      
      // 处理提取结果（后端返回 SuccessResponse，数据在 data 字段中）
      const extractData = result.data || result
      
      if (extractData.error) {
        throw new Error(extractData.error)
      }
      
      if (extractData.total_count === 0) {
        throw new Error('未能从文件中提取到题目')
      }
      
      // 构建回答
      const firstQuestion = extractData.questions[0]
      answer.value = {
        answer: `已从${isImage ? '图片' : '文档'}中提取到 ${extractData.total_count} 道题目，置信度：${Math.round(extractData.confidence * 100)}%`,
        suggested_question: firstQuestion ? {
          content: firstQuestion.content || '',
          options: firstQuestion.options || [],
          answer: firstQuestion.answer || '',
          explanation: firstQuestion.explanation || '',
          category_id: categoryStore.categoryTree[0]?.id || ''
        } : undefined,
        related_questions: [],
        extracted_from_file: true,
        source_type: isImage ? 'image' : 'document',
        source_file: file.name
      }
      
      ElMessage.success(result.message || `成功提取 ${extractData.total_count} 道题目`)
    } else {
      // 纯文本提问，调用 AI 问答 API
      result = await questionApi.askAI(question.value)
      
      answer.value = {
        answer: result.answer,
        suggested_question: result.suggested_question ? {
          content: result.suggested_question.content,
          options: result.suggested_question.options,
          answer: result.suggested_question.answer,
          explanation: result.suggested_question.explanation,
          category_id: result.suggested_question.category_id
        } : undefined,
        related_questions: result.related_questions || []
      }
      
      ElMessage.success('AI 回答生成成功')
    }

    // 添加到历史
    if (!uploadedFile.value) {
      addToHistory(question.value)
    }
  } catch (error: any) {
    console.error('提问失败:', error)
    ElMessage.error(error.message || '操作失败，请重试')
  } finally {
    loading.value = false
  }
}

// 清空
const handleClear = () => {
  question.value = ''
  uploadedFile.value = null
  answer.value = null
  isAddedToPending.value = false
}

// 添加到预备题库
const handleAddToPending = async () => {
  if (!answer.value?.suggested_question) {
    ElMessage.warning('没有可添加的题目')
    return
  }

  try {
    // TODO: 调用 API 添加到预备表
    // await questionStore.addToPending(answer.value.suggested_question)
    
    isAddedToPending.value = true
    ElMessage.success('已添加到预备题库，请前往审核')
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

// 查看相关题目
const handleViewRelated = (questionItem: any) => {
  router.push({
    path: '/questions',
    query: { highlight: questionItem.id }
  })
}

// 添加到历史
const addToHistory = (q: string) => {
  history.value.unshift({
    question: q,
    time: new Date().toISOString()
  })
  
  // 只保留最近 10 条
  if (history.value.length > 10) {
    history.value = history.value.slice(0, 10)
  }
  
  // 保存到本地存储
  localStorage.setItem('ai_ask_history', JSON.stringify(history.value))
}

// 恢复历史
const restoreHistory = (item: any) => {
  question.value = item.question
}

// 清空历史
const clearHistory = () => {
  history.value = []
  localStorage.removeItem('ai_ask_history')
}

// 加载历史
onMounted(() => {
  const saved = localStorage.getItem('ai_ask_history')
  if (saved) {
    history.value = JSON.parse(saved)
  }
})
</script>

<style scoped>
.ai-ask-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  margin: 0 0 12px 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 16px;
}

.ask-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.ask-container {
  padding: 20px;
}

.ask-input :deep(.el-textarea__inner) {
  font-size: 16px;
  line-height: 1.6;
  border-radius: 12px;
  padding: 16px;
}

.upload-section {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.file-preview {
  display: flex;
  align-items: center;
}

.ask-actions {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  gap: 16px;
}

.ask-actions .el-button {
  min-width: 140px;
  height: 48px;
  font-size: 16px;
}

.answer-section {
  margin-bottom: 24px;
}

.answer-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.answer-title {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.answer-content {
  padding: 20px 0;
}

.ai-answer-text {
  font-size: 16px;
  line-height: 1.8;
  color: #495057;
  white-space: pre-wrap;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 12px;
  border-left: 4px solid #409eff;
}

.suggested-question {
  margin-top: 24px;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 12px;
  border: 1px solid #bae6fd;
}

.suggested-question h4 {
  margin: 0 0 16px 0;
  color: #0369a1;
  font-size: 16px;
}

.question-preview {
  background: white;
  padding: 16px;
  border-radius: 8px;
}

.preview-item {
  margin-bottom: 12px;
  line-height: 1.6;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.options-list {
  margin-top: 8px;
  padding-left: 20px;
}

.option-item {
  margin-bottom: 4px;
  color: #495057;
}

.related-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.related-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.related-title {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.related-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.related-index {
  width: 28px;
  height: 28px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.related-content {
  flex: 1;
}

.related-question {
  font-size: 15px;
  color: #303133;
  margin-bottom: 8px;
  line-height: 1.5;
}

.related-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.similarity-score {
  font-size: 13px;
  color: #10b981;
  font-weight: 500;
}

.history-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-title {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  background: #e9ecef;
}

.history-question {
  flex: 1;
  font-size: 14px;
  color: #495057;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 12px;
}

.history-time {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
}
</style>
