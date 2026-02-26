<template>
  <div class="category-view">
    <!-- 页面标题和操作 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><FolderOpened /></el-icon> 分类管理
      </h2>
      <div class="page-actions">
        <el-button type="primary" @click="handleAddCategory">
          <el-icon><Plus /></el-icon> 添加分类
        </el-button>
        <el-button @click="refreshCategories">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>
    </div>

    <!-- 分类统计 -->
    <div class="category-stats">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #e3f2fd;">
                <el-icon><Folder /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ totalCategories }}</div>
                <div class="stat-label">总分类数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #f3e5f5;">
                <el-icon><FolderOpened /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ rootCategories }}</div>
                <div class="stat-label">一级分类</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #e8f5e8;">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ totalQuestions }}</div>
                <div class="stat-label">总题目数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #fff3e0;">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ maxDepth }}</div>
                <div class="stat-label">最大深度</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分类表格 -->
    <el-card class="category-table-card">
      <template #header>
        <div class="table-header">
          <span>分类列表</span>
          <div class="table-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索分类名称或描述"
              prefix-icon="Search"
              style="width: 200px; margin-right: 10px;"
              clearable
              @input="handleSearch"
            />
            <el-button-group>
              <el-button :type="viewMode === 'tree' ? 'primary' : 'default'" @click="viewMode = 'tree'">
                <el-icon><Menu /></el-icon> 树形视图
              </el-button>
              <el-button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'">
                <el-icon><List /></el-icon> 列表视图
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>

      <!-- 树形视图 -->
      <div v-if="viewMode === 'tree'" class="tree-view">
        <CategoryTree
          :categories="filteredCategoryTree"
          @select="handleCategorySelect"
          @add-child="handleAddChildCategory"
          @edit="handleEditCategory"
          @delete="handleDeleteCategory"
        />
      </div>

      <!-- 列表视图 -->
      <div v-else class="list-view">
        <el-table
          :data="filteredCategories"
          v-loading="loading"
          style="width: 100%"
          row-key="id"
          :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        >
          <el-table-column prop="name" label="分类名称" min-width="200">
            <template #default="{ row }">
              <div class="category-name-cell">
                <el-icon class="folder-icon">
                  <Folder v-if="!row.children || row.children.length === 0" />
                  <FolderOpened v-else />
                </el-icon>
                <span>{{ row.name }}</span>
                <span v-if="row.description" class="category-description">
                  - {{ row.description }}
                </span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="path" label="路径" min-width="250">
            <template #default="{ row }">
              <el-breadcrumb separator="/">
                <el-breadcrumb-item 
                  v-for="category in getCategoryPath(row)" 
                  :key="category.id"
                >
                  {{ category.name }}
                </el-breadcrumb-item>
              </el-breadcrumb>
            </template>
          </el-table-column>
          
          <el-table-column prop="question_count" label="题目数量" width="120">
            <template #default="{ row }">
              <el-tag size="small" type="info">
                {{ getQuestionCount(row) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                @click="handleAddChildCategory(row)"
                title="添加子分类"
              >
                <el-icon><Plus /></el-icon>
              </el-button>
              <el-button
                type="warning"
                size="small"
                @click="handleEditCategory(row)"
                title="编辑"
              >
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="handleDeleteCategory(row)"
                title="删除"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 添加分类对话框 -->
    <el-dialog
      v-model="addDialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <CategoryForm
        v-if="addDialogVisible"
        :parent-id="selectedParentId"
        @submit="handleCategorySubmit"
        @cancel="addDialogVisible = false"
      />
    </el-dialog>

    <!-- 编辑分类对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑分类"
      width="500px"
    >
      <CategoryForm
        v-if="editDialogVisible && editingCategory"
        :category="editingCategory"
        @submit="handleCategoryUpdate"
        @cancel="editDialogVisible = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCategoryStore } from '@/stores/category'
import { useQuestionStore } from '@/stores/question'
import CategoryTree from '@/components/CategoryTree.vue'
import CategoryForm from '@/components/CategoryForm.vue'
import dayjs from 'dayjs'

const router = useRouter()
const categoryStore = useCategoryStore()
const questionStore = useQuestionStore()

// 视图模式
const viewMode = ref<'tree' | 'list'>('tree')

// 搜索关键词
const searchKeyword = ref('')

// 对话框状态
const addDialogVisible = ref(false)
const editDialogVisible = ref(false)
const selectedParentId = ref<string | undefined>()
const editingCategory = ref<any>(null)

// 统计信息
const totalCategories = computed(() => categoryStore.getAllCategoriesFlat.length)
const rootCategories = computed(() => categoryStore.categoryTree.length)
const totalQuestions = computed(() => questionStore.questions.length)

// 计算最大深度
const maxDepth = computed(() => {
  const calculateDepth = (nodes: any[], depth = 1): number => {
    let max = depth
    nodes.forEach(node => {
      if (node.children && node.children.length > 0) {
        const childDepth = calculateDepth(node.children, depth + 1)
        max = Math.max(max, childDepth)
      }
    })
    return max
  }
  return calculateDepth(categoryStore.categoryTree)
})

// 过滤后的分类树
const filteredCategoryTree = computed(() => {
  if (!searchKeyword.value.trim()) {
    return categoryStore.categoryTree
  }

  const keyword = searchKeyword.value.toLowerCase()
  
  const filterTree = (nodes: any[]): any[] => {
    return nodes.filter(node => {
      const matches = 
        node.name.toLowerCase().includes(keyword) ||
        (node.description && node.description.toLowerCase().includes(keyword))
      
      // 如果节点匹配，或者有匹配的子节点，就保留
      if (matches) return true
      
      if (node.children && node.children.length > 0) {
        const filteredChildren = filterTree(node.children)
        if (filteredChildren.length > 0) {
          node.children = filteredChildren
          return true
        }
      }
      
      return false
    })
  }
  
  return filterTree([...categoryStore.categoryTree])
})

// 过滤后的分类列表
const filteredCategories = computed(() => {
  if (!searchKeyword.value.trim()) {
    return categoryStore.getAllCategoriesFlat
  }

  const keyword = searchKeyword.value.toLowerCase()
  return categoryStore.getAllCategoriesFlat.filter(category => 
    category.name.toLowerCase().includes(keyword) ||
    (category.description && category.description.toLowerCase().includes(keyword))
  )
})

// 对话框标题
const dialogTitle = computed(() => {
  return selectedParentId.value ? '添加子分类' : '添加分类'
})

// 获取分类路径
const getCategoryPath = (category: any) => {
  return categoryStore.getBreadcrumbs(category.id)
}

// 获取题目数量（需要后端支持，这里先模拟）
const getQuestionCount = (category: any) => {
  // TODO: 需要后端API支持获取分类下的题目数量
  return 0
}

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 刷新分类
const refreshCategories = () => {
  categoryStore.fetchCategories()
  questionStore.fetchQuestions()
}

// 添加分类
const handleAddCategory = () => {
  selectedParentId.value = undefined
  addDialogVisible.value = true
}

// 添加子分类
const handleAddChildCategory = (category: any) => {
  selectedParentId.value = category.id
  addDialogVisible.value = true
}

// 编辑分类
const handleEditCategory = (category: any) => {
  editingCategory.value = category
  editDialogVisible.value = true
}

// 删除分类
const handleDeleteCategory = async (category: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类 "${category.name}" 吗？此操作将删除所有子分类和题目。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await categoryStore.deleteCategory(category.id)
    ElMessage.success('删除成功')
  } catch (error) {
    // 用户取消删除
  }
}

// 选择分类
const handleCategorySelect = (category: any) => {
  router.push({
    path: '/questions',
    query: { category_id: category.id }
  })
}

// 搜索
const handleSearch = () => {
  // 搜索逻辑已在计算属性中实现
}

// 提交分类
const handleCategorySubmit = async (data: any) => {
  try {
    await categoryStore.createCategory(data)
    addDialogVisible.value = false
    ElMessage.success('添加成功')
  } catch (error) {
    // 错误已在store中处理
  }
}

// 更新分类
const handleCategoryUpdate = async (data: any) => {
  try {
    await categoryStore.updateCategory(editingCategory.value.id, data)
    editDialogVisible.value = false
    ElMessage.success('更新成功')
  } catch (error) {
    // 错误已在store中处理
  }
}

// 组件挂载时加载数据
onMounted(() => {
  refreshCategories()
})
</script>

<style scoped>
.category-view {
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

.page-actions {
  display: flex;
  gap: 12px;
}

.category-stats {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
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
  color: #1976d2;
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

.category-table-card {
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

.tree-view {
  min-height: 400px;
}

.list-view {
  min-height: 400px;
}

.category-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.folder-icon {
  color: #ff9800;
}

.category-description {
  color: #909399;
  font-size: 12px;
  margin-left: 8px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>