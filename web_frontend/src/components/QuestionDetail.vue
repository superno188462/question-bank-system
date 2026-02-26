<template>
  <div class="question-detail">
    <!-- 题目基本信息 -->
    <div class="question-header">
      <div class="question-title">
        <h3>题目详情</h3>
        <div class="question-meta">
          <el-tag size="small" type="info">
            {{ questionType }}
          </el-tag>
          <el-tag size="small">
            {{ categoryName }}
          </el-tag>
          <span class="create-time">
            <el-icon><Clock /></el-icon>
            {{ formatDate(question.created_at) }}
          </span>
        </div>
      </div>
      <div class="question-actions">
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon> 编辑
        </el-button>
        <el-button @click="handleClose">
          <el-icon><Close /></el-icon> 关闭
        </el-button>
      </div>
    </div>

    <!-- 题干 -->
    <div class="section">
      <h4 class="section-title">
        <el-icon><Document /></el-icon> 题干
      </h4>
      <div class="section-content">
        <div class="content-text">{{ question.content }}</div>
      </div>
    </div>

    <!-- 选项（选择题） -->
    <div v-if="question.options && question.options.length > 0" class="section">
      <h4 class="section-title">
        <el-icon><List /></el-icon> 选项
      </h4>
      <div class="section-content">
        <div class="options">
          <div 
            v-for="(option, index) in question.options" 
            :key="index"
            class="option"
            :class="{ 'is-correct': option === question.answer }"
          >
            <div class="option-header">
              <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
              <el-tag 
                v-if="option === question.answer"
                type="success" 
                size="small"
                class="correct-tag"
              >
                正确答案
              </el-tag>
            </div>
            <div class="option-text">{{ option }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 答案 -->
    <div class="section">
      <h4 class="section-title">
        <el-icon><Check /></el-icon> 答案
      </h4>
      <div class="section-content">
        <div class="answer">
          <el-tag 
            :type="question.options && question.options.length > 0 ? 'success' : 'info'"
            size="large"
            class="answer-tag"
          >
            {{ question.answer }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 解析 -->
    <div class="section">
      <div class="section-header">
        <h4 class="section-title">
          <el-icon><Comment /></el-icon> 解析
        </h4>
        <div class="section-actions">
          <el-button
            type="text"
            size="small"
            @click="handleAIExplanation"
            :loading="aiLoading"
            v-if="!question.explanation || question.explanation.trim().length < 50"
          >
            <el-icon><MagicStick /></el-icon> AI生成解析
          </el-button>
        </div>
      </div>
      <div class="section-content">
        <div class="explanation">
          <div v-if="question.explanation" class="explanation-text">
            {{ question.explanation }}
          </div>
          <div v-else class="empty-explanation">
            <el-empty description="暂无解析" :image-size="80">
              <el-button type="primary" @click="handleAIExplanation" :loading="aiLoading">
                <el-icon><MagicStick /></el-icon> AI生成解析
              </el-button>
            </el-empty>
          </div>
        </div>
      </div>
    </div>

    <!-- 标签 -->
    <div v-if="question.tags && question.tags.length > 0" class="section">
      <h4 class="section-title">
        <el-icon><PriceTag /></el-icon> 标签
      </h4>
      <div class="section-content">
        <div class="tags">
          <el-tag
            v-for="tag in question.tags"
            :key="tag.id"
            :style="{ backgroundColor: tag.color + '20', color: tag.color, borderColor: tag.color }"
            size="medium"
            class="tag-item"
          >
            {{ tag.name }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 其他信息 -->
    <div class="section">
      <h4 class="section-title">
        <el-icon><InfoFilled /></el-icon> 其他信息
      </h4>
      <div class="section-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="题目ID">
            {{ question.id }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(question.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(question.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="题目类型">
            {{ questionType }}
          </el-descriptions-item>
          <el-descriptions-item label="选项数量">
            {{ question.options?.length || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="答案长度">
            {{ question.answer.length }} 字符
          </el-descriptions-item>
          <el-descriptions-item label="解析长度">
            {{ question.explanation?.length || 0 }} 字符
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCategoryStore } from '@/stores/category'
import { useQuestionStore } from '@/stores/question'
import dayjs from 'dayjs'

interface Props {
  question: any
}

interface Emits {
  (e: 'close'): void
  (e: 'edit', question: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const categoryStore = useCategoryStore()
const questionStore = useQuestionStore()
const aiLoading = ref(false)

// 题目类型
const questionType = computed(() => {
  return props.question.options && props.question.options.length > 0 ? '选择题' : '填空题'
})

// 分类名称
const categoryName = computed(() => {
  const category = categoryStore.getCategoryById(props.question.category_id)
  return category?.name || '未知分类'
})

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 编辑题目
const handleEdit = () => {
  emit('edit', props.question)
}

// 关闭
const handleClose = () => {
  emit('close')
}

// AI生成解析
const handleAIExplanation = async () => {
  aiLoading.value = true
  try {
    const explanation = await questionStore.getAIExplanation(props.question.id)
    // TODO: 更新题目解析
    ElMessage.success('AI解析生成成功')
  } catch (error) {
    ElMessage.error('AI解析生成失败')
  } finally {
    aiLoading.value = false
  }
}
</script>

<style scoped>
.question-detail {
  padding: 20px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e9ecef;
}

.question-title h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.question-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.create-time {
  font-size: 14px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.question-actions {
  display: flex;
  gap: 12px;
}

.section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-actions {
  display: flex;
  gap: 8px;
}

.section-content {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.content-text {
  font-size: 16px;
  line-height: 1.6;
  color: #495057;
  white-space: pre-wrap;
  word-break: break-word;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option {
  padding: 16px;
  background: white;
  border-radius: 6px;
  border: 1px solid #dee2e6;
  transition: all 0.2s;
}

.option.is-correct {
  border-color: #4caf50;
  background: #f1f8e9;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.1);
}

.option-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.option-label {
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
  min-width: 24px;
}

.correct-tag {
  font-weight: 500;
}

.option-text {
  font-size: 15px;
  line-height: 1.5;
  color: #495057;
  white-space: pre-wrap;
  word-break: break-word;
}

.answer {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.answer-tag {
  font-size: 18px;
  font-weight: 600;
  padding: 12px 24px;
}

.explanation {
  min-height: 100px;
}

.explanation-text {
  font-size: 15px;
  line-height: 1.6;
  color: #495057;
  white-space: pre-wrap;
  word-break: break-word;
}

.empty-explanation {
  text-align: center;
  padding: 40px 0;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  font-weight: 500;
  padding: 6px 12px;
}

:deep(.el-descriptions) {
  margin-top: 8px;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
  background: #f8f9fa;
}

:deep(.el-descriptions__content) {
  font-weight: 400;
}
</style>