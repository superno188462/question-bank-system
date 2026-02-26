<template>
  <div class="pending-questions-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Clock /></el-icon> 预备题目审核
        <el-badge v-if="pendingCount > 0" :value="pendingCount" class="badge" />
      </h2>
      <p class="page-description">审核AI生成的题目，确认无误后添加到正式题库</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="stat-card pending">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.pending }}</div>
                <div class="stat-label">待审核</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card approved">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.approved }}</div>
                <div class="stat-label">已批准</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card rejected">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><CircleClose /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.rejected }}</div>
                <div class="stat-label">已拒绝</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filter" inline>
        <el-form-item label="状态">
          <el-select v-model="filter.status" placeholder="全部状态" clearable style="width: 120px;">
            <el-option label="待审核" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="关键词">
          <el-input
            v-model="filter.keyword"
            placeholder="搜索题干内容"
            prefix-icon="Search"
            clearable
            @keyup.enter="handleSearch"
            style="width: 200px;"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预备题目列表 -->
    <el-card class="pending-list-card">
      <template #header>
        <div class="list-header">
          <span>预备题目列表 ({{ filteredPendingQuestions.length }} 条)</span>
          <div class="batch-actions">
            <el-button 
              type="success" 
              size="small" 
              :disabled="selectedQuestions.length === 0"
              @click="handleBatchApprove"
            >
              <el-icon><Check /></el-icon> 批量批准
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              :disabled="selectedQuestions.length === 0"
              @click="handleBatchReject"
            >
              <el-icon><Close /></el-icon> 批量拒绝
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="filteredPendingQuestions"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="content" label="题干" min-width="300">
          <template #default="{ row }">
            <div class="question-content">
              <div class="content-text">{{ row.content }}</div>
              <div v-if="row.options?.length > 0" class="options-preview">
                <span class="option-count">{{ row.options.length }} 个选项</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="answer" label="答案" width="150">
          <template #default="{ row }">
            <el-tag size="small" type="success">
              {{ row.answer }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="category_id" label="建议分类" width="150">
          <template #default="{ row }">
            <el-select
              v-model="row.category_id"
              placeholder="选择分类"
              size="small"
              style="width: 130px;"
            >
              <el-option
                v-for="category in allCategories"
                :key="category.id"
                :label="category.name"
                :value="category.id"
              />
            </el-select>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleView(row)"
              title="查看详情"
            >
              <el-icon><View /></el-icon>
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              size="small"
              @click="handleApprove(row)"
              title="批准"
            >
              <el-icon><Check /></el-icon>
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="danger"
              size="small"
              @click="handleReject(row)"
              title="拒绝"
            >
              <el-icon><Close /></el-icon>
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleEdit(row)"
              title="编辑"
            >
              <el-icon><Edit /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 查看/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
    >
      <div v-if="currentQuestion" class="question-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>题目信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(currentQuestion.status)">
                {{ getStatusText(currentQuestion.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(currentQuestion.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 编辑表单 -->
        <div class="detail-section">
          <h4>编辑题目</h4>
          <el-form :model="editForm" label-width="80px">
            <el-form-item label="题干">
              <el-input
                v-model="editForm.content"
                type="textarea"
                :rows="3"
                placeholder="请输入题干"
              />
            </el-form-item>
            
            <el-form-item label="选项" v-if="editForm.options?.length > 0">
              <div class="edit-options">
                <div
                  v-for="(opt, idx) in editForm.options"
                  :key="idx"
                  class="edit-option"
                >
                  <span class="option-label">{{ String.fromCharCode(65 + idx) }}.</span>
                  <el-input v-model="editForm.options[idx]" size="small" />
                </div>
              </div>
            </el-form-item>
            
            <el-form-item label="答案">
              <el-input v-model="editForm.answer" placeholder="请输入答案" />
            </el-form-item>
            
            <el-form-item label="解析">
              <el-input
                v-model="editForm.explanation"
                type="textarea"
                :rows="4"
                placeholder="请输入解析"
              />
            </el-form-item>
            
            <el-form-item label="分类">
              <el-cascader
                v-model="editForm.category_id"
                :options="categoryTree"
                :props="{ value: 'id', label: 'name', children: 'children', checkStrictly: true }"
                placeholder="选择分类"
                style="width: 100%;"
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- AI生成数据预览 -->
        <div class="detail-section" v-if="currentQuestion.ai_generated_data">
          <h4>AI生成原始数据</h4>
          <el-collapse>
            <el-collapse-item title="查看原始数据">
              <pre class="json-preview">{{ JSON.stringify(currentQuestion.ai_generated_data, null, 2) }}</pre>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveEdit">保存修改</el-button>
          <el-button 
            v-if="currentQuestion?.status === 'pending'"
            type="success" 
            @click="handleApproveAndClose"
          >
            批准并关闭
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useCategoryStore } from '@/stores/category'
import { useQuestionStore } from '@/stores/question'
import dayjs from 'dayjs'

const categoryStore = useCategoryStore()
const questionStore = useQuestionStore()

// 状态
const loading = ref(false)
const selectedQuestions = ref<any[]>([])
const dialogVisible = ref(false)
const currentQuestion = ref<any>(null)
const isEditing = ref(false)

// 筛选条件
const filter = reactive({
  status: '',
  keyword: ''
})

// 编辑表单
const editForm = reactive({
  content: '',
  options: [] as string[],
  answer: '',
  explanation: '',
  category_id: ''
})

// 统计数据
const stats = reactive({
  pending: 0,
  approved: 0,
  rejected: 0
})

// 模拟预备题目数据
const pendingQuestions = ref<any[]>([
  {
    id: '1',
    content: 'Python中如何定义一个函数？',
    options: ['使用 def 关键字', '使用 function 关键字', '使用 func 关键字', '使用 define 关键字'],
    answer: '使用 def 关键字',
    explanation: '在Python中，使用def关键字来定义函数。',
    category_id: '',
    status: 'pending',
    created_at: new Date().toISOString(),
    ai_generated_data: {
      source: 'AI提问',
      confidence: 0.95
    }
  },
  {
    id: '2',
    content: 'JavaScript中var和let的区别是什么？',
    options: ['没有区别', 'let有块级作用域', 'var有块级作用域', 'let只能在函数内使用'],
    answer: 'let有块级作用域',
    explanation: 'let声明的变量具有块级作用域，而var声明的变量具有函数作用域。',
    category_id: '',
    status: 'pending',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    ai_generated_data: {
      source: 'AI提问',
      confidence: 0.88
    }
  }
])

// 计算属性
const pendingCount = computed(() => stats.pending)

const allCategories = computed(() => categoryStore.getAllCategoriesFlat)

const categoryTree = computed(() => categoryStore.categoryTree)

const filteredPendingQuestions = computed(() => {
  let result = pendingQuestions.value
  
  if (filter.status) {
    result = result.filter(q => q.status === filter.status)
  }
  
  if (filter.keyword) {
    const keyword = filter.keyword.toLowerCase()
    result = result.filter(q => 
      q.content.toLowerCase().includes(keyword) ||
      q.answer.toLowerCase().includes(keyword)
    )
  }
  
  return result
})

const dialogTitle = computed(() => {
  return isEditing.value ? '编辑预备题目' : '查看预备题目'
})

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待审核',
    approved: '已批准',
    rejected: '已拒绝'
  }
  return texts[status] || status
}

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 搜索
const handleSearch = () => {
  // 搜索逻辑已在计算属性中实现
}

// 重置筛选
const handleReset = () => {
  filter.status = ''
  filter.keyword = ''
}

// 选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedQuestions.value = selection
}

// 查看
const handleView = (question: any) => {
  currentQuestion.value = question
  isEditing.value = false
  initEditForm(question)
  dialogVisible.value = true
}

// 编辑
const handleEdit = (question: any) => {
  currentQuestion.value = question
  isEditing.value = true
  initEditForm(question)
  dialogVisible.value = true
}

// 初始化编辑表单
const initEditForm = (question: any) => {
  editForm.content = question.content
  editForm.options = [...(question.options || [])]
  editForm.answer = question.answer
  editForm.explanation = question.explanation
  editForm.category_id = question.category_id
}

// 保存编辑
const handleSaveEdit = () => {
  if (currentQuestion.value) {
    currentQuestion.value.content = editForm.content
    currentQuestion.value.options = editForm.options
    currentQuestion.value.answer = editForm.answer
    currentQuestion.value.explanation = editForm.explanation
    currentQuestion.value.category_id = editForm.category_id
    
    ElMessage.success('保存成功')
    dialogVisible.value = false
  }
}

// 批准
const handleApprove = async (question: any) => {
  try {
    await ElMessageBox.confirm('确定要批准这道题目吗？', '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // TODO: 调用API批准题目
    question.status = 'approved'
    updateStats()
    ElMessage.success('批准成功')
  } catch (error) {
    // 用户取消
  }
}

// 拒绝
const handleReject = async (question: any) => {
  try {
    await ElMessageBox.confirm('确定要拒绝这道题目吗？', '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // TODO: 调用API拒绝题目
    question.status = 'rejected'
    updateStats()
    ElMessage.success('已拒绝')
  } catch (error) {
    // 用户取消
  }
}

// 批准并关闭
const handleApproveAndClose = async () => {
  await handleSaveEdit()
  if (currentQuestion.value) {
    await handleApprove(currentQuestion.value)
    dialogVisible.value = false
  }
}

// 批量批准
const handleBatchApprove = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要批准选中的 ${selectedQuestions.value.length} 道题目吗？`,
      '批量批准',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    selectedQuestions.value.forEach(q => {
      q.status = 'approved'
    })
    updateStats()
    ElMessage.success('批量批准成功')
    selectedQuestions.value = []
  } catch (error) {
    // 用户取消
  }
}

// 批量拒绝
const handleBatchReject = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要拒绝选中的 ${selectedQuestions.value.length} 道题目吗？`,
      '批量拒绝',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    selectedQuestions.value.forEach(q => {
      q.status = 'rejected'
    })
    updateStats()
    ElMessage.success('批量拒绝成功')
    selectedQuestions.value = []
  } catch (error) {
    // 用户取消
  }
}

// 更新统计
const updateStats = () => {
  stats.pending = pendingQuestions.value.filter(q => q.status === 'pending').length
  stats.approved = pendingQuestions.value.filter(q => q.status === 'approved').length
  stats.rejected = pendingQuestions.value.filter(q => q.status === 'rejected').length
}

// 组件挂载
onMounted(() => {
  updateStats()
})
</script>

<style scoped>
.pending-questions-view {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 12px;
}

.badge {
  margin-left: 8px;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.stat-card.pending .stat-icon {
  background: #fff3e0;
  color: #f57c00;
}

.stat-card.approved .stat-icon {
  background: #e8f5e9;
  color: #388e3c;
}

.stat-card.rejected .stat-icon {
  background: #ffebee;
  color: #d32f2f;
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-icon .el-icon {
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.filter-card {
  margin-bottom: 24px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.pending-list-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.batch-actions {
  display: flex;
  gap: 8px;
}

.question-content {
  line-height: 1.6;
}

.content-text {
  margin-bottom: 4px;
  word-break: break-word;
}

.options-preview {
  font-size: 12px;
  color: #909399;
}

.option-count {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 4px;
}

.question-detail {
  max-height: 600px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.edit-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.edit-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-label {
  font-weight: bold;
  color: #409eff;
  min-width: 24px;
}

.json-preview {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  font-family: monospace;
  font-size: 12px;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>