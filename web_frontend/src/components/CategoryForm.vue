<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
    class="category-form"
  >
    <el-form-item label="分类名称" prop="name">
      <el-input
        v-model="form.name"
        placeholder="请输入分类名称"
        maxlength="100"
        show-word-limit
      />
    </el-form-item>

    <el-form-item label="上级分类" prop="parent_id">
      <el-select
        v-model="form.parent_id"
        placeholder="请选择上级分类（可选）"
        clearable
        filterable
        class="full-width"
      >
        <el-option label="无上级分类" :value="undefined" />
        <el-option
          v-for="category in allCategories"
          :key="category.id"
          :label="getCategoryLabel(category)"
          :value="category.id"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="分类描述" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="3"
        placeholder="请输入分类描述（可选）"
        maxlength="500"
        show-word-limit
      />
    </el-form-item>

    <el-form-item>
      <div class="form-actions">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          确定
        </el-button>
      </div>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useCategoryStore } from '@/stores/category'

interface Props {
  category?: any
  parentId?: string
}

interface Emits {
  (e: 'submit', data: any): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const categoryStore = useCategoryStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

// 表单数据
const form = reactive({
  name: '',
  description: '',
  parent_id: undefined as string | undefined
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 100, message: '分类名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '分类描述不能超过 500 个字符', trigger: 'blur' }
  ]
}

// 所有分类（扁平化）
const allCategories = computed(() => categoryStore.getAllCategoriesFlat)

// 获取分类显示标签
const getCategoryLabel = (category: any) => {
  const breadcrumbs = categoryStore.getBreadcrumbs(category.id)
  return breadcrumbs.map(c => c.name).join(' / ')
}

// 初始化表单
const initForm = () => {
  if (props.category) {
    // 编辑模式
    form.name = props.category.name
    form.description = props.category.description || ''
    form.parent_id = props.category.parent_id
  } else {
    // 添加模式
    form.name = ''
    form.description = ''
    form.parent_id = props.parentId
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    loading.value = true
    
    // 准备提交数据
    const submitData = {
      name: form.name.trim(),
      description: form.description?.trim() || undefined,
      parent_id: form.parent_id || undefined
    }

    emit('submit', submitData)
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    loading.value = false
  }
}

// 取消
const handleCancel = () => {
  emit('cancel')
}

// 组件挂载时初始化
onMounted(() => {
  initForm()
})

// 监听props变化
watch(() => props.category, () => {
  initForm()
})

watch(() => props.parentId, () => {
  if (!props.category) {
    form.parent_id = props.parentId
  }
})
</script>

<style scoped>
.category-form {
  padding: 20px 0;
}

.full-width {
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  width: 100%;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input__count) {
  font-size: 12px;
}
</style>