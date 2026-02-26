<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
    class="question-form"
  >
    <!-- 题干 -->
    <el-form-item label="题干" prop="content">
      <el-input
        v-model="form.content"
        type="textarea"
        :rows="3"
        placeholder="请输入题目内容"
        maxlength="1000"
        show-word-limit
      />
    </el-form-item>

    <!-- 题目类型 -->
    <el-form-item label="题目类型" prop="question_type">
      <el-radio-group v-model="questionType" @change="handleTypeChange">
        <el-radio label="choice">选择题</el-radio>
        <el-radio label="blank">填空题</el-radio>
      </el-radio-group>
    </el-form-item>

    <!-- 选项（仅选择题显示） -->
    <el-form-item 
      v-if="questionType === 'choice'" 
      label="选项" 
      prop="options"
    >
      <div class="options-container">
        <div 
          v-for="(option, index) in form.options" 
          :key="index"
          class="option-item"
        >
          <el-input
            v-model="form.options[index]"
            :placeholder="`选项 ${String.fromCharCode(65 + index)}`"
            class="option-input"
            maxlength="500"
            show-word-limit
          >
            <template #prepend>
              <span class="option-label">{{ String.fromCharCode(65 + index) }}</span>
            </template>
            <template #append>
              <el-button
                type="danger"
                :icon="Delete"
                circle
                size="small"
                @click="removeOption(index)"
                :disabled="form.options.length <= 2"
              />
            </template>
          </el-input>
        </div>
        
        <el-button
          type="primary"
          plain
          @click="addOption"
          :disabled="form.options.length >= 10"
          class="add-option-btn"
        >
          <el-icon><Plus /></el-icon> 添加选项
        </el-button>
      </div>
    </el-form-item>

    <!-- 答案 -->
    <el-form-item 
      :label="questionType === 'choice' ? '正确答案' : '填空答案'" 
      prop="answer"
    >
      <div v-if="questionType === 'choice'" class="answer-choice">
        <el-radio-group v-model="form.answer">
          <el-radio
            v-for="(option, index) in form.options"
            :key="index"
            :label="option"
            :disabled="!option.trim()"
          >
            {{ String.fromCharCode(65 + index) }}. {{ option }}
          </el-radio>
        </el-radio-group>
      </div>
      <el-input
        v-else
        v-model="form.answer"
        placeholder="请输入填空答案"
        maxlength="500"
        show-word-limit
      />
    </el-form-item>

    <!-- 解析 -->
    <el-form-item label="题目解析" prop="explanation">
      <el-input
        v-model="form.explanation"
        type="textarea"
        :rows="4"
        placeholder="请输入题目解析"
        maxlength="2000"
        show-word-limit
      />
      <div class="ai-explanation-hint" v-if="showAIButton">
        <el-button
          type="text"
          size="small"
          @click="handleAIExplanation"
          :loading="aiLoading"
        >
          <el-icon><MagicStick /></el-icon> AI生成解析
        </el-button>
      </div>
    </el-form-item>

    <!-- 分类 -->
    <el-form-item label="所属分类" prop="category_id">
      <el-cascader
        v-model="selectedCategoryPath"
        :options="categoryTree"
        :props="cascaderProps"
        placeholder="请选择分类"
        clearable
        filterable
        class="full-width"
        @change="handleCategoryChange"
      />
    </el-form-item>

    <!-- 标签 -->
    <el-form-item label="题目标签" prop="tag_ids">
      <el-select
        v-model="form.tag_ids"
        multiple
        placeholder="请选择标签（可选）"
        filterable
        allow-create
        class="full-width"
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

    <!-- 表单操作 -->
    <el-form-item>
      <div class="form-actions">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          {{ submitButtonText }}
        </el-button>
      </div>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { Delete, Plus, MagicStick } from '@element-plus/icons-vue'
import { useCategoryStore } from '@/stores/category'

interface Props {
  question?: any
  showAIButton?: boolean
}

interface Emits {
  (e: 'submit', data: any): void
  (e: 'cancel'): void
  (e: 'ai-explanation'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const categoryStore = useCategoryStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const aiLoading = ref(false)

// 题目类型
const questionType = ref<'choice' | 'blank'>('choice')

// 表单数据
const form = reactive({
  content: '',
  options: ['', '', '', ''],
  answer: '',
  explanation: '',
  category_id: '',
  tag_ids: [] as string[]
})

// 选择的分类路径
const selectedCategoryPath = ref<string[]>([])

// 表单验证规则
const rules: FormRules = {
  content: [
    { required: true, message: '请输入题干内容', trigger: 'blur' },
    { min: 1, max: 1000, message: '题干内容长度在 1 到 1000 个字符', trigger: 'blur' }
  ],
  options: [
    {
      validator: (rule, value, callback) => {
        if (questionType.value === 'choice') {
          const validOptions = value.filter((opt: string) => opt.trim().length > 0)
          if (validOptions.length < 2) {
            callback(new Error('选择题至少需要两个有效选项'))
          } else if (validOptions.length !== value.length) {
            callback(new Error('所有选项都不能为空'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  answer: [
    { required: true, message: '请输入答案', trigger: 'blur' },
    { min: 1, max: 500, message: '答案长度在 1 到 500 个字符', trigger: 'blur' }
  ],
  explanation: [
    { required: true, message: '请输入题目解析', trigger: 'blur' },
    { min: 1, max: 2000, message: '解析长度在 1 到 2000 个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ]
}

// 分类树
const categoryTree = computed(() => categoryStore.categoryTree)

// 级联选择器配置
const cascaderProps = {
  value: 'id',
  label: 'name',
  children: 'children',
  checkStrictly: true,
  emitPath: false
}

// 可用标签（需要从API获取，这里先模拟）
const availableTags = ref([
  { id: '1', name: '易', color: '#10b981' },
  { id: '2', name: '中', color: '#f59e0b' },
  { id: '3', name: '难', color: '#ef4444' },
  { id: '4', name: '重点', color: '#8b5cf6' },
  { id: '5', name: '考点', color: '#3b82f6' }
])

// 提交按钮文本
const submitButtonText = computed(() => {
  return props.question ? '更新题目' : '创建题目'
})

// 初始化表单
const initForm = () => {
  if (props.question) {
    // 编辑模式
    form.content = props.question.content
    form.options = props.question.options || []
    form.answer = props.question.answer
    form.explanation = props.question.explanation
    form.category_id = props.question.category_id
    form.tag_ids = props.question.tags?.map((tag: any) => tag.id) || []
    
    // 设置题目类型
    questionType.value = form.options.length > 0 ? 'choice' : 'blank'
    
    // 设置分类路径
    const breadcrumbs = categoryStore.getBreadcrumbs(props.question.category_id)
    selectedCategoryPath.value = breadcrumbs.map(c => c.id)
  } else {
    // 添加模式
    form.content = ''
    form.options = ['', '', '', '']
    form.answer = ''
    form.explanation = ''
    form.category_id = ''
    form.tag_ids = []
    questionType.value = 'choice'
    selectedCategoryPath.value = []
  }
}

// 添加选项
const addOption = () => {
  if (form.options.length < 10) {
    form.options.push('')
  }
}

// 删除选项
const removeOption = (index: number) => {
  if (form.options.length > 2) {
    form.options.splice(index, 1)
    
    // 如果删除的是当前答案对应的选项，清空答案
    if (form.answer === form.options[index]) {
      form.answer = ''
    }
  }
}

// 题目类型变化
const handleTypeChange = (type: 'choice' | 'blank') => {
  if (type === 'blank') {
    form.options = []
    form.answer = ''
  } else {
    form.options = ['', '', '', '']
  }
}

// 分类变化
const handleCategoryChange = (value: string[]) => {
  if (value && value.length > 0) {
    form.category_id = value[value.length - 1]
  } else {
    form.category_id = ''
  }
}

// AI生成解析
const handleAIExplanation = () => {
  emit('ai-explanation')
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
      content: form.content.trim(),
      options: questionType.value === 'choice' ? form.options.map(opt => opt.trim()) : [],
      answer: form.answer.trim(),
      explanation: form.explanation.trim(),
      category_id: form.category_id,
      tag_ids: form.tag_ids
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
watch(() => props.question, () => {
  initForm()
})
</script>

<style scoped>
.question-form {
  padding: 20px 0;
}

.full-width {
  width: 100%;
}

.options-container {
  width: 100%;
}

.option-item {
  margin-bottom: 12px;
}

.option-item:last-child {
  margin-bottom: 16px;
}

.option-input {
  width: 100%;
}

.option-label {
  display: inline-block;
  width: 24px;
  text-align: center;
  font-weight: bold;
  color: #409eff;
}

.add-option-btn {
  width: 100%;
}

.answer-choice {
  width: 100%;
}

.answer-choice :deep(.el-radio) {
  display: block;
  margin-bottom: 8px;
  line-height: 1.5;
}

.answer-choice :deep(.el-radio__label) {
  white-space: normal;
  word-break: break-word;
}

.ai-explanation-hint {
  margin-top: 8px;
  text-align: right;
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