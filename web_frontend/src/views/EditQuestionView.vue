<template>
  <div class="edit-question-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Edit /></el-icon> 编辑题目
      </h2>
      <p class="page-description">修改题目信息</p>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 题目表单 -->
    <el-card v-else-if="question" class="form-card">
      <QuestionForm
        :question="question"
        :show-ai-button="true"
        @submit="handleSubmit"
        @cancel="handleCancel"
        @ai-explanation="handleAIExplanation"
      />
    </el-card>

    <!-- 未找到 -->
    <el-result
      v-else
      icon="error"
      title="题目不存在"
      sub-title="请检查题目ID是否正确"
    >
      <template #extra>
        <el-button type="primary" @click="router.push('/questions')">
          返回题目列表
        </el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuestionStore } from '@/stores/question'
import QuestionForm from '@/components/QuestionForm.vue'

const route = useRoute()
const router = useRouter()
const questionStore = useQuestionStore()

// 状态
const loading = ref(true)
const question = ref<any>(null)

// 获取题目ID
const questionId = route.params.id as string

// 加载题目
const loadQuestion = async () => {
  loading.value = true
  try {
    question.value = await questionStore.getQuestion(questionId)
  } catch (error) {
    ElMessage.error('加载题目失败')
  } finally {
    loading.value = false
  }
}

// 提交表单
const handleSubmit = async (data: any) => {
  try {
    await questionStore.updateQuestion(questionId, data)
    ElMessage.success('题目更新成功')
    
    // 跳转到题目列表
    router.push('/questions')
  } catch (error) {
    // 错误已在store中处理
  }
}

// 取消
const handleCancel = () => {
  router.back()
}

// AI生成解析
const handleAIExplanation = async () => {
  try {
    const result = await questionStore.getAIExplanation(questionId)
    if (result.explanation) {
      question.value.explanation = result.explanation
      ElMessage.success('AI解析生成成功')
    }
  } catch (error) {
    ElMessage.error('AI解析生成失败')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadQuestion()
})
</script>

<style scoped>
.edit-question-view {
  padding: 20px;
  max-width: 1000px;
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

.loading-container {
  padding: 40px;
}

.form-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}
</style>