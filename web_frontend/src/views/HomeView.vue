<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <h1 class="logo">📚 题库管理系统</h1>
      </div>
      <div class="header-right">
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          @select="handleMenuSelect"
          class="nav-menu"
        >
          <el-menu-item index="/categories">
            <el-icon><Folder /></el-icon>
            <span>分类管理</span>
          </el-menu-item>
          <el-menu-item index="/questions">
            <el-icon><Document /></el-icon>
            <span>题目管理</span>
          </el-menu-item>
          <el-menu-item index="/ai-ask">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI提问</span>
          </el-menu-item>
          <el-menu-item index="/pending-questions">
            <el-icon><Clock /></el-icon>
            <span>预备题目</span>
            <el-badge v-if="pendingCount > 0" :value="pendingCount" class="badge" />
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 侧边栏 - 分类树 -->
      <el-aside class="sidebar" width="280px">
        <div class="sidebar-header">
          <h3><el-icon><FolderOpened /></el-icon> 分类目录</h3>
          <el-button 
            type="primary" 
            size="small" 
            @click="handleAddCategory"
            class="add-category-btn"
          >
            <el-icon><Plus /></el-icon> 添加分类
          </el-button>
        </div>
        <div class="category-tree">
          <CategoryTree 
            :categories="categoryTree"
            @select="handleCategorySelect"
            @edit="handleCategoryEdit"
            @delete="handleCategoryDelete"
          />
        </div>
      </el-aside>

      <!-- 内容区域 -->
      <el-main class="content">
        <!-- 面包屑导航 -->
        <div class="breadcrumb" v-if="breadcrumbs.length > 0">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item 
              v-for="category in breadcrumbs" 
              :key="category.id"
              @click="handleBreadcrumbClick(category)"
              class="breadcrumb-item"
            >
              {{ category.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <!-- 路由视图 -->
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="$route.path" />
          </transition>
        </router-view>
      </el-main>
    </div>

    <!-- 添加分类对话框 -->
    <el-dialog
      v-model="categoryDialogVisible"
      title="添加分类"
      width="500px"
    >
      <CategoryForm
        v-if="categoryDialogVisible"
        :parent-id="selectedCategoryId"
        @submit="handleCategorySubmit"
        @cancel="categoryDialogVisible = false"
      />
    </el-dialog>

    <!-- 编辑分类对话框 -->
    <el-dialog
      v-model="editCategoryDialogVisible"
      title="编辑分类"
      width="500px"
    >
      <CategoryForm
        v-if="editCategoryDialogVisible && editingCategory"
        :category="editingCategory"
        @submit="handleCategoryUpdate"
        @cancel="editCategoryDialogVisible = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCategoryStore } from '@/stores/category'
import { useQuestionStore } from '@/stores/question'
import CategoryTree from '@/components/CategoryTree.vue'
import CategoryForm from '@/components/CategoryForm.vue'

const route = useRoute()
const router = useRouter()
const categoryStore = useCategoryStore()
const questionStore = useQuestionStore()

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 面包屑导航
const breadcrumbs = computed(() => {
  const categoryId = route.query.category_id as string
  if (categoryId) {
    return categoryStore.getBreadcrumbs(categoryId)
  }
  return []
})

// 预备题目数量
const pendingCount = computed(() => questionStore.pendingQuestions.length)

// 分类树
const categoryTree = computed(() => categoryStore.categoryTree)

// 对话框状态
const categoryDialogVisible = ref(false)
const editCategoryDialogVisible = ref(false)
const selectedCategoryId = ref<string | undefined>()
const editingCategory = ref<any>(null)

// 菜单选择
const handleMenuSelect = (index: string) => {
  router.push(index)
}

// 分类选择
const handleCategorySelect = (category: any) => {
  router.push({
    path: '/questions',
    query: { category_id: category.id }
  })
}

// 面包屑点击
const handleBreadcrumbClick = (category: any) => {
  router.push({
    path: '/questions',
    query: { category_id: category.id }
  })
}

// 添加分类
const handleAddCategory = () => {
  selectedCategoryId.value = route.query.category_id as string
  categoryDialogVisible.value = true
}

// 编辑分类
const handleCategoryEdit = (category: any) => {
  editingCategory.value = category
  editCategoryDialogVisible.value = true
}

// 删除分类
const handleCategoryDelete = async (category: any) => {
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

// 提交分类
const handleCategorySubmit = async (data: any) => {
  try {
    await categoryStore.createCategory(data)
    categoryDialogVisible.value = false
    ElMessage.success('添加成功')
  } catch (error) {
    // 错误已在store中处理
  }
}

// 更新分类
const handleCategoryUpdate = async (data: any) => {
  try {
    await categoryStore.updateCategory(editingCategory.value.id, data)
    editCategoryDialogVisible.value = false
    ElMessage.success('更新成功')
  } catch (error) {
    // 错误已在store中处理
  }
}

// 监听路由变化，更新面包屑
watch(() => route.query.category_id, () => {
  // 面包屑会自动更新
})
</script>

<style scoped>
.home-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-left .logo {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.nav-menu {
  background: transparent;
  border-bottom: none;
}

.nav-menu :deep(.el-menu-item) {
  color: white !important;
  font-weight: 500;
}

.nav-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
}

.nav-menu :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.2) !important;
  border-bottom: 2px solid white;
}

.badge {
  margin-left: 8px;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  background: #f8f9fa;
  border-right: 1px solid #e9ecef;
  padding: 20px;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.sidebar-header h3 {
  margin: 0;
  color: #495057;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-category-btn {
  font-size: 12px;
  padding: 4px 8px;
}

.category-tree {
  height: calc(100vh - 120px);
  overflow-y: auto;
}

.content {
  padding: 20px;
  overflow-y: auto;
}

.breadcrumb {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.breadcrumb-item {
  cursor: pointer;
  transition: color 0.2s;
}

.breadcrumb-item:hover {
  color: #409eff;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>