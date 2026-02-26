<template>
  <div class="create-question-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Plus /></el-icon> 添加新题目
      </h2>
      <p class="page-description">手动录入题目，支持选择题和填空题</p>
    </div>

    <!-- 题目表单 -->
    <el-card class="form-card">
      <QuestionForm
        @submit="handleSubmit"
        @cancel="handleCancel"
        @ai-explanation="handleAIExplanation"
      />
    </el-card>

    <!-- 快速提示 -->
    <el-card class="tips-card">
      <template #header>
        <div class="tips-header">
          <el-icon><InfoFilled /></el-icon>
          <span>录入提示</span>
        </div>
      </template>
      
      <div class="tips-content">
        <el-collapse>
          <el-collapse-item title="如何选择题目类型？" name="1">
            <ul>
              <li><strong>选择题：</strong>有多个选项供选择，答案必须是其中一个选项</li>
              <li><strong>填空题：</strong>没有选项，用户需要直接输入答案</li>
            </ul>
          </el-collapse-item>
          
          <el-collapse-item title="如何写好题目解析？" name="2">
            <ul>
              <li>解释为什么这个答案是正确的</li>
              <li>可以补充相关的知识点</li>
              <li>如果有常见错误，可以指出并纠正</li>
            </ul>
          </el-collapse-item>
          
          <el-collapse-item title="分类和标签的使用" name="3">
            <ul>
              <li><strong>分类：</strong>用于组织题目的层级结构，必须选择一个</li>
              <li><strong>标签：</strong>用于标记题目的属性（难度、重点等），可选</li>
            </ul>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useQuestionStore } from '@/stores/question'
import QuestionForm from '@/components/QuestionForm.vue'

const router = useRouter()
const questionStore = useQuestionStore()

// 提交表单
const handleSubmit = async (data: any) => {
  try {
    await questionStore.createQuestion(data)
    ElMessage.success('题目创建成功')
    
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
const handleAIExplanation = () => {
  ElMessage.info('AI解析功能开发中...')
}
</script>

<style scoped>
.create-question-view {
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

.form-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.tips-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.tips-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.tips-content ul {
  margin: 0;
  padding-left: 20px;
}

.tips-content li {
  margin-bottom: 8px;
  line-height: 1.6;
}

.tips-content li:last-child {
  margin-bottom: 0;
}

:deep(.el-collapse-item__header) {
  font-weight: 500;
}
</style>