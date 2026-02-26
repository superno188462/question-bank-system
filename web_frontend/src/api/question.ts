import api from './index'

export interface Question {
  id: string
  content: string
  options: string[]
  answer: string
  explanation: string
  category_id: string
  tags: Tag[]
  created_at: string
  updated_at: string
}

export interface Tag {
  id: string
  name: string
  color: string
  created_at: string
}

export interface QuestionCreate {
  content: string
  options: string[]
  answer: string
  explanation: string
  category_id: string
  tag_ids?: string[]
}

export interface QuestionUpdate {
  content?: string
  options?: string[]
  answer?: string
  explanation?: string
  category_id?: string
  tag_ids?: string[]
}

export interface QuestionFilter {
  category_id?: string
  tag_id?: string
  keyword?: string
  page?: number
  limit?: number
}

export interface PaginatedResponse {
  data: Question[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface PendingQuestion {
  id: string
  content: string
  ai_generated_data: any
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  updated_at: string
}

export const questionApi = {
  // 获取题目列表
  async getQuestions(filter: QuestionFilter = {}): Promise<PaginatedResponse> {
    const params = new URLSearchParams()
    if (filter.category_id) params.append('category_id', filter.category_id)
    if (filter.tag_id) params.append('tag_id', filter.tag_id)
    if (filter.keyword) params.append('keyword', filter.keyword)
    if (filter.page) params.append('page', filter.page.toString())
    if (filter.limit) params.append('limit', filter.limit.toString())
    
    return api.get(`/questions?${params.toString()}`)
  },

  // 获取单个题目
  async getQuestion(id: string): Promise<Question> {
    return api.get(`/questions/${id}`)
  },

  // 创建题目
  async createQuestion(data: QuestionCreate): Promise<Question> {
    return api.post('/questions', data)
  },

  // 更新题目
  async updateQuestion(id: string, data: QuestionUpdate): Promise<Question> {
    return api.put(`/questions/${id}`, data)
  },

  // 删除题目
  async deleteQuestion(id: string): Promise<boolean> {
    return api.delete(`/questions/${id}`)
  },

  // 搜索题目
  async searchQuestions(keyword: string): Promise<Question[]> {
    return api.get(`/questions/search?keyword=${encodeURIComponent(keyword)}`)
  },

  // AI提问功能
  async askAI(question: string): Promise<{
    answer: string
    related_questions: Question[]
    suggested_question?: QuestionCreate
  }> {
    return api.post('/ai/ask', { question })
  },

  // 获取预备题目列表
  async getPendingQuestions(): Promise<PendingQuestion[]> {
    return api.get('/pending-questions')
  },

  // 批准预备题目
  async approvePendingQuestion(id: string): Promise<Question> {
    return api.post(`/pending-questions/${id}/approve`)
  },

  // 拒绝预备题目
  async rejectPendingQuestion(id: string): Promise<boolean> {
    return api.delete(`/pending-questions/${id}`)
  },

  // 获取AI解析
  async getAIExplanation(questionId: string): Promise<{ explanation: string }> {
    return api.get(`/questions/${id}/ai-explanation`)
  }
}