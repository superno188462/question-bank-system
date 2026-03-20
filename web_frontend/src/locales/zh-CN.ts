// 中文（简体）翻译
export default {
  // 通用
  common: {
    loading: '加载中...',
    submit: '提交',
    cancel: '取消',
    confirm: '确认',
    delete: '删除',
    edit: '编辑',
    view: '查看',
    save: '保存',
    close: '关闭',
    refresh: '刷新',
    search: '搜索',
    reset: '重置',
    add: '添加',
    create: '创建',
    update: '更新',
    success: '成功',
    error: '错误',
    warning: '警告',
    info: '提示',
    noData: '暂无数据',
    actions: '操作',
    total: '共',
    items: '条'
  },

  // 导航和标题
  nav: {
    title: '题库管理系统',
    categories: '分类管理',
    questions: '题目管理',
    aiAsk: 'AI 提问',
    pendingQuestions: '预备题目',
    categoryDirectory: '分类目录',
    addCategory: '添加分类'
  },

  // 题目管理
  question: {
    management: '题目管理',
    addQuestion: '添加题目',
    editQuestion: '编辑题目',
    viewQuestion: '题目详情',
    deleteQuestion: '删除题目',
    questionList: '题目列表',
    content: '题干',
    options: '选项',
    answer: '答案',
    explanation: '解析',
    category: '分类',
    tags: '标签',
    type: '题目类型',
    choice: '选择题',
    blank: '填空题',
    createdAt: '创建时间',
    updatedAt: '更新时间',
    keyword: '关键词',
    searchPlaceholder: '搜索题干、答案或解析',
    selectTag: '选择标签',
    selectType: '选择类型',
    confirmDelete: '确定要删除题目吗？此操作不可恢复。',
    deleteSuccess: '删除成功',
    createSuccess: '创建成功',
    updateSuccess: '更新成功'
  },

  // 分类管理
  category: {
    management: '分类管理',
    addCategory: '添加分类',
    editCategory: '编辑分类',
    deleteCategory: '删除分类',
    categoryName: '分类名称',
    parentCategory: '上级分类',
    noParent: '无（顶级分类）',
    confirmDelete: '确定要删除分类 "{name}" 吗？此操作将删除所有子分类和题目。',
    deleteSuccess: '删除成功',
    addSuccess: '添加成功',
    updateSuccess: '更新成功'
  },

  // AI 功能
  ai: {
    title: 'AI 提问',
    generate: 'AI 生成',
    generateExplanation: 'AI 生成解析',
    generating: '生成中...',
    askAI: '向 AI 提问',
    explanationGenerating: 'AI 生成解析功能开发中...'
  },

  // 表单验证
  validation: {
    required: '{field} 不能为空',
    minLength: '{field} 长度不能少于 {min} 个字符',
    maxLength: '{field} 长度不能超过 {max} 个字符',
    invalid: '{field} 格式不正确'
  },

  // 语言切换
  language: {
    switch: '切换语言',
    switched: '已切换至 {lang}',
    chinese: '中文',
    english: 'English',
    current: '当前语言'
  },

  // 时间格式
  time: {
    format: 'YYYY-MM-DD HH:mm',
    justNow: '刚刚',
    minutesAgo: '{n} 分钟前',
    hoursAgo: '{n} 小时前',
    daysAgo: '{n} 天前'
  },

  // 难度标签
  difficulty: {
    easy: '易',
    medium: '中',
    hard: '难',
    keyPoint: '重点',
    examPoint: '考点'
  }
}
