import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
  questionApi, 
  type Question, 
  type QuestionCreate, 
  type QuestionUpdate, 
  type QuestionFilter,
  type PaginatedResponse,
  type PendingQuestion
} from '@/api/question'

export const useQuestionStore = defineStore('question', () => {
  const questions = ref<Question[]>([])
  const currentQuestion = ref<Question | null>(null)
  const pagination = ref<PaginatedResponse | null>(null)
  const pendingQuestions = ref<PendingQuestion[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 获取题目列表
  const fetchQuestions = async (filter: QuestionFilter = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await questionApi.getQuestions(filter)
      questions.value = response.data
      pagination.value = response
    } catch (err: any) {
      error.value = err.message || '获取题目失败'
      console.error('获取题目失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 获取单个题目
  const fetchQuestion = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      currentQuestion.value = await questionApi.getQuestion(id)
    } catch (err: any) {
      error.value = err.message || '获取题目失败'
      console.error('获取题目失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 创建题目
  const createQuestion = async (data: QuestionCreate) => {
    loading.value = true
    error.value = null
    try {
      const newQuestion = await questionApi.createQuestion(data)
      await fetchQuestions() // 重新获取题目列表
      return newQuestion
    } catch (err: any) {
      error.value = err.message || '创建题目失败'
      console.error('创建题目失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新题目
  const updateQuestion = async (id: string, data: QuestionUpdate) => {
    loading.value = true
    error.value = null
    try {
      const updatedQuestion = await questionApi.updateQuestion(id, data)
      await fetchQuestions() // 重新获取题目列表
      return updatedQuestion
    } catch (err: any) {
      error.value = err.message || '更新题目失败'
      console.error('更新题目失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除题目
  const deleteQuestion = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const success = await questionApi.deleteQuestion(id)
      if (success) {
        await fetchQuestions() // 重新获取题目列表
      }
      return success
    } catch (err: any) {
      error.value = err.message || '删除题目失败'
      console.error('删除题目失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 搜索题目
  const searchQuestions = async (keyword: string) => {
    loading.value = true
    error.value = null
    try {
      const results = await questionApi.searchQuestions(keyword)
      return results
    } catch (err: any) {
      error.value = err.message || '搜索题目失败'
      console.error('搜索题目失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // AI提问
  const askAI = async (question: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await questionApi.askAI(question)
      return response
    } catch (err: any) {
      error.value = err.message || 'AI提问失败'
      console.error('AI提问失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取预备题目
  const fetchPendingQuestions = async () => {
    loading.value = true
    error.value = null
    try {
      pendingQuestions.value = await questionApi.getPendingQuestions()
    } catch (err: any) {
      error.value = err.message || '获取预备题目失败'
      console.error('获取预备题目失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 批准预备题目
  const approvePendingQuestion = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const question = await questionApi.approvePendingQuestion(id)
      await fetchPendingQuestions() // 重新获取预备题目
      await fetchQuestions() // 重新获取题目列表
      return question
    } catch (err: any) {
      error.value = err.message || '批准题目失败'
      console.error('批准题目失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 拒绝预备题目
  const rejectPendingQuestion = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const success = await questionApi.rejectPendingQuestion(id)
      if (success) {
        await fetchPendingQuestions() // 重新获取预备题目
      }
      return success
    } catch (err: any) {
      error.value = err.message || '拒绝题目失败'
      console.error('拒绝题目失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取AI解析
  const getAIExplanation = async (questionId: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await questionApi.getAIExplanation(questionId)
      return response.explanation
    } catch (err: any) {
      error.value = err.message || '获取AI解析失败'
      console.error('获取AI解析失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 清空当前题目
  const clearCurrentQuestion = () => {
    currentQuestion.value = null
  }

  return {
    questions,
    currentQuestion,
    pagination,
    pendingQuestions,
    loading,
    error,
    fetchQuestions,
    fetchQuestion,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    searchQuestions,
    askAI,
    fetchPendingQuestions,
    approvePendingQuestion,
    rejectPendingQuestion,
    getAIExplanation,
    clearCurrentQuestion
  }
})