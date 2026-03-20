<template>
  <div class="question-view">
    <!-- 页面标题和操作 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Document /></el-icon> {{ t('question.management') }}
        <span v-if="currentCategory" class="current-category">
          - {{ currentCategory.name }}
        </span>
      </h2>
      <div class="page-actions">
        <el-button type="primary" @click="handleCreateQuestion">
          <el-icon><Plus /></el-icon> {{ t('question.addQuestion') }}
        </el-button>
        <el-button @click="refreshQuestions">
          <el-icon><Refresh /></el-icon> {{ t('common.refresh') }}
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filter" inline>
        <el-form-item :label="t('question.keyword')">
          <el-input
            v-model="filter.keyword"
            :placeholder="t('question.searchPlaceholder')"
            prefix-icon="Search"
            clearable
            @keyup.enter="handleSearch"
            style="width: 200px;"
          />
        </el-form-item>
        
        <el-form-item :label="t('question.tags')">
          <el-select
            v-model="filter.tag_id"
            :placeholder="t('question.selectTag')"
            clearable
            style="width: 120px;"
          >
            <el-option
              v-for="tag in availableTags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            >
              <div class="tag-option">
                <span class="tag-color" :style="{ backgroundColor: tag.color }"></span>
                <span>{{ tag.name }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item :label="t('question.type')">
          <el-select
            v-model="filter.question_type"
            :placeholder="t('question.selectType')"
            clearable
            style="width: 120px;"
          >
            <el-option :label="t('question.choice')" value="choice" />
            <el-option :label="t('question.blank')" value="blank" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> {{ t('common.search') }}
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon> {{ t('common.reset') }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 题目表格 -->
    <el-card class="question-table-card">
      <template #header>
        <div class="table-header">
          <span>{{ t('question.questionList') }} ({{ pagination?.total || 0 }} {{ t('common.items') }})</span>
          <div class="table-actions">
            <el-pagination
              v-model:current-page="filter.page"
              v-model:page-size="filter.limit"
              :page-sizes="[10, 20, 50, 100]"
              :total="pagination?.total || 0"
              layout="total, sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </template>

      <el-table
        :data="questions"
        v-loading="loading"
        style="width: 100%"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="content" :label="t('question.content')" min-width="300">
          <template #default="{ row }">
            <div class="question-content">
              <div class="content-text" v-html="formatContent(row.content)"></div>
              <div v-if="row.options && row.options.length > 0" class="options">
                <div 
                  v-for="(option, index) in row.options" 
                  :key="index"
                  class="option"
                  :class="{ 'is-correct': option === row.answer }"
                >
                  <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
                  <span class="option-text">{{ option }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="answer" :label="t('question.answer')" width="120">
          <template #default="{ row }">
            <el-tag 
              :type="row.options && row.options.length > 0 ? 'success' : 'info'"
              size="small"
            >
              {{ row.answer }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="category" :label="t('question.category')" width="150">
          <template #default="{ row }">
            <el-tag size="small">
              {{ getCategoryName(row.category_id) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="tags" :label="t('question.tags')" width="150">
          <template #default="{ row }">
            <div class="tags">
              <el-tag
                v-for="tag in row.tags"
                :key="tag.id"
                :style="{ backgroundColor: tag.color + '20', color: tag.color, borderColor: tag.color }"
                size="small"
                class="tag-item"
              >
                {{ tag.name }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" :label="t('question.createdAt')" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column :label="t('common.actions')" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleViewQuestion(row)"
              :title="t('common.view')"
            >
              <el-icon><View /></el-icon>
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleEditQuestion(row)"
              :title="t('common.edit')"
            >
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDeleteQuestion(row)"
              :title="t('common.delete')"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 查看题目对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      :title="t('question.viewQuestion')"
      width="800px"
    >
      <QuestionDetail
        v-if="viewDialogVisible && viewingQuestion"
        :question="viewingQuestion"
        @close="viewDialogVisible = false"
        @edit="handleEditFromView"
      />
    </el-dialog>

    <!-- 添加/编辑题目对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="dialogTitle"
      width="800px"
    >
      <QuestionForm
        v-if="editDialogVisible"
        :question="editingQuestion"
        :show-ai-button="true"
        @submit="handleQuestionSubmit"
        @cancel="editDialogVisible = false"
        @ai-explanation="handleAIExplanation"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCategoryStore } from '@/stores/category'
import { useQuestionStore } from '@/stores/question'
import QuestionForm from '@/components/QuestionForm.vue'
import QuestionDetail from '@/components/QuestionDetail.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const categoryStore = useCategoryStore()
const questionStore = useQuestionStore()

// 筛选条件
const filter = reactive({
  category_id: route.query.category_id as string || '',
  tag_id: '',
  keyword: '',
  question_type: '',
  page: 1,
  limit: 20,
  sort: 'created_at',
  order: 'desc'
})

// 对话框状态
const viewDialogVisible = ref(false)
const editDialogVisible = ref(false)
const viewingQuestion = ref<any>(null)
const editingQuestion = ref<any>(null)

// 可用标签（需要从 API 获取，这里先模拟）
const availableTags = ref([
  { id: '1', name: t('difficulty.easy'), color: '#10b981' },
  { id: '2', name: t('difficulty.medium'), color: '#f59e0b' },
  { id: '3', name: t('difficulty.hard'), color: '#ef4444' },
  { id: '4', name: t('difficulty.keyPoint'), color: '#8b5cf6' },
  { id: '5', name: t('difficulty.examPoint'), color: '#3b82f6' }
])

// 计算属性
const questions = computed(() => questionStore.questions)
const pagination = computed(() => questionStore.pagination)
const loading = computed(() => questionStore.loading)

// 当前分类
const currentCategory = computed(() => {
  if (filter.category_id) {
    return categoryStore.getCategoryById(filter.category_id)
  }
  return null
})

// 对话框标题
const dialogTitle = computed(() => {
  return editingQuestion.value ? t('question.editQuestion') : t('question.addQuestion')
})

// 获取分类名称
const getCategoryName = (categoryId: string) => {
  const category = categoryStore.getCategoryById(categoryId)
  return category?.name || t('common.noData')
}

// 格式化内容（高亮关键词）
const formatContent = (content: string) => {
  if (!filter.keyword) return content
  
  const keyword = filter.keyword
  const regex = new RegExp(`(${keyword})`, 'gi')
  return content.replace(regex, '<mark>$1</mark>')
}

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format(t('time.format'))
}

// 刷新题目
const refreshQuestions = () => {
  questionStore.fetchQuestions(filter)
}

// 搜索
const handleSearch = () => {
  filter.page = 1
  refreshQuestions()
}

// 重置筛选
const handleReset = () => {
  filter.category_id = route.query.category_id as string || ''
  filter.tag_id = ''
  filter.keyword = ''
  filter.question_type = ''
  filter.page = 1
  refreshQuestions()
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  filter.limit = size
  filter.page = 1
  refreshQuestions()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  filter.page = page
  refreshQuestions()
}

// 排序变化
const handleSortChange = ({ prop, order }: any) => {
  if (prop) {
    filter.sort = prop
    filter.order = order === 'ascending' ? 'asc' : 'desc'
    refreshQuestions()
  }
}

// 创建题目
const handleCreateQuestion = () => {
  editingQuestion.value = null
  editDialogVisible.value = true
}

// 查看题目
const handleViewQuestion = (question: any) => {
  viewingQuestion.value = question
  viewDialogVisible.value = true
}

// 编辑题目
const handleEditQuestion = (question: any) => {
  editingQuestion.value = question
  editDialogVisible.value = true
}

// 从查看对话框编辑
const handleEditFromView = (question: any) => {
  viewDialogVisible.value = false
  editingQuestion.value = question
  editDialogVisible.value = true
}

// 删除题目
const handleDeleteQuestion = async (question: any) => {
  try {
    await ElMessageBox.confirm(
      t('question.confirmDelete'),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )
    
    await questionStore.deleteQuestion(question.id)
    ElMessage.success(t('question.deleteSuccess'))
  } catch (error) {
    // 用户取消删除
  }
}

// 提交题目
const handleQuestionSubmit = async (data: any) => {
  try {
    if (editingQuestion.value) {
      await questionStore.updateQuestion(editingQuestion.value.id, data)
      ElMessage.success(t('question.updateSuccess'))
    } else {
      await questionStore.createQuestion(data)
      ElMessage.success(t('question.createSuccess'))
    }
    editDialogVisible.value = false
  } catch (error) {
    // 错误已在 store 中处理
  }
}

// AI 生成解析
const handleAIExplanation = async () => {
  ElMessage.info(t('ai.explanationGenerating'))
}

// 监听路由变化
watch(() => route.query.category_id, (newCategoryId) => {
  filter.category_id = newCategoryId as string || ''
  filter.page = 1
  refreshQuestions()
})

// 组件挂载时加载数据
onMounted(() => {
  refreshQuestions()
})
</script>

<style scoped>
.question-view {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
}

.current-category {
  color: #409eff;
  font-weight: 500;
}

.page-actions {
  display: flex;
  gap: 12px;
}

.filter-card {
  margin-bottom: 24px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.question-table-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.question-content {
  line-height: 1.6;
}

.content-text {
  margin-bottom: 8px;
  word-break: break-word;
}

.content-text mark {
  background-color: #ffd700;
  padding: 0 2px;
  border-radius: 2px;
}

.options {
  margin-top: 8px;
  padding-left: 20px;
}

.option {
  margin-bottom: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f8f9fa;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.option.is-correct {
  background: #e8f5e8;
  border-left: 3px solid #4caf50;
}

.option-label {
  font-weight: bold;
  color: #409eff;
  min-width: 20px;
}

.option-text {
  flex: 1;
  word-break: break-word;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag-item {
  margin: 2px;
}

.tag-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

:deep(.el-dialog) {
  border-radius: 12px;
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid #e9ecef;
  margin-right: 0;
}

:deep(.el-dialog__body) {
  padding: 20px;
}
</style>
