<template>
  <div class="category-tree">
    <div 
      v-for="category in categories" 
      :key="category.id"
      class="category-node"
    >
      <!-- 分类项 -->
      <div 
        class="category-item"
        :class="{ 'is-active': isActive(category.id) }"
        @click="handleSelect(category)"
      >
        <div class="category-content">
          <el-icon class="folder-icon">
            <Folder v-if="!category.children || category.children.length === 0" />
            <FolderOpened v-else />
          </el-icon>
          <span class="category-name">{{ category.name }}</span>
          <span class="category-description" v-if="category.description">
            - {{ category.description }}
          </span>
        </div>
        
        <div class="category-actions">
          <el-button 
            type="text" 
            size="small" 
            @click.stop="handleAddChild(category)"
            title="添加子分类"
          >
            <el-icon><Plus /></el-icon>
          </el-button>
          <el-button 
            type="text" 
            size="small" 
            @click.stop="handleEdit(category)"
            title="编辑"
          >
            <el-icon><Edit /></el-icon>
          </el-button>
          <el-button 
            type="text" 
            size="small" 
            @click.stop="handleDelete(category)"
            title="删除"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 子分类 -->
      <div 
        v-if="category.children && category.children.length > 0 && expandedNodes[category.id]"
        class="children-container"
      >
        <CategoryTree
          :categories="category.children"
          :active-category-id="activeCategoryId"
          @select="$emit('select', $event)"
          @add-child="$emit('add-child', $event)"
          @edit="$emit('edit', $event)"
          @delete="$emit('delete', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'

interface Category {
  id: string
  name: string
  description?: string
  children?: Category[]
}

interface Props {
  categories: Category[]
  activeCategoryId?: string
}

interface Emits {
  (e: 'select', category: Category): void
  (e: 'add-child', category: Category): void
  (e: 'edit', category: Category): void
  (e: 'delete', category: Category): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 展开的节点
const expandedNodes = ref<Record<string, boolean>>({})

// 判断是否激活
const isActive = (categoryId: string) => {
  return props.activeCategoryId === categoryId
}

// 选择分类
const handleSelect = (category: Category) => {
  // 如果有子分类，切换展开状态
  if (category.children && category.children.length > 0) {
    expandedNodes.value[category.id] = !expandedNodes.value[category.id]
  }
  emit('select', category)
}

// 添加子分类
const handleAddChild = (category: Category) => {
  emit('add-child', category)
}

// 编辑分类
const handleEdit = (category: Category) => {
  emit('edit', category)
}

// 删除分类
const handleDelete = (category: Category) => {
  emit('delete', category)
}
</script>

<style scoped>
.category-tree {
  width: 100%;
}

.category-node {
  margin-bottom: 4px;
}

.category-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.category-item:hover {
  background: #e9ecef;
}

.category-item.is-active {
  background: #e3f2fd;
  color: #1976d2;
  font-weight: 500;
}

.category-content {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.folder-icon {
  margin-right: 8px;
  font-size: 16px;
  flex-shrink: 0;
}

.category-name {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.category-description {
  font-size: 12px;
  color: #6c757d;
  margin-left: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.category-actions {
  display: flex;
  opacity: 0;
  transition: opacity 0.2s;
}

.category-item:hover .category-actions {
  opacity: 1;
}

.category-actions .el-button {
  padding: 4px;
  margin-left: 2px;
}

.children-container {
  margin-left: 24px;
  border-left: 2px solid #dee2e6;
  padding-left: 12px;
}
</style>