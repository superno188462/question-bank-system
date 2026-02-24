// pages/index/index.js

const app = getApp()

Page({
  data: {
    // 轮播图数据
    banners: [
      { id: 1, image: '/assets/banners/banner1.jpg', title: '智能题库' },
      { id: 2, image: '/assets/banners/banner2.jpg', title: 'AI答疑' },
      { id: 3, image: '/assets/banners/banner3.jpg', title: '错题本' }
    ],
    
    // 功能模块
    features: [
      { id: 1, icon: 'search', title: '题目搜索', desc: '快速查找题目', url: '/pages/search/index' },
      { id: 2, icon: 'question', title: '智能问答', desc: 'AI解答疑问', url: '/pages/chat/index' },
      { id: 3, icon: 'book', title: '我的错题', desc: '错题集中练习', url: '/pages/errorbook/index' },
      { id: 4, icon: 'chart', title: '学习统计', desc: '学习进度分析', url: '/pages/profile/index' }
    ],
    
    // 热门题目
    hotQuestions: [],
    
    // 用户信息
    userInfo: null,
    
    // 加载状态
    loading: true
  },

  onLoad() {
    console.log('首页加载')
    this.loadData()
  },

  onShow() {
    // 更新用户信息
    this.setData({
      userInfo: app.globalData.userInfo
    })
  },

  // 加载数据
  async loadData() {
    this.setData({ loading: true })
    
    try {
      // 获取热门题目
      const questions = await app.request({
        url: '/api/questions/hot',
        method: 'GET'
      })
      
      this.setData({
        hotQuestions: questions.slice(0, 5),
        loading: false
      })
      
    } catch (error) {
      console.error('加载数据失败:', error)
      this.setData({ loading: false })
      
      // 显示错误提示
      app.showToast('加载失败，请重试')
    }
  },

  // 跳转到功能页面
  navigateToFeature(e) {
    const { url } = e.currentTarget.dataset
    if (url) {
      wx.navigateTo({
        url
      })
    }
  },

  // 搜索题目
  onSearch() {
    wx.navigateTo({
      url: '/pages/search/index'
    })
  },

  // 开始对话
  startChat() {
    wx.switchTab({
      url: '/pages/chat/index'
    })
  },

  // 查看题目详情
  viewQuestionDetail(e) {
    const { id } = e.currentTarget.dataset
    if (id) {
      wx.navigateTo({
        url: `/pages/questions/detail?id=${id}`
      })
    }
  },

  // 下拉刷新
  onPullDownRefresh() {
    console.log('下拉刷新')
    this.loadData().finally(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 分享功能
  onShareAppMessage() {
    return {
      title: '智能题库小程序',
      path: '/pages/index/index',
      imageUrl: '/assets/share.jpg'
    }
  },

  // 分享到朋友圈
  onShareTimeline() {
    return {
      title: '智能题库小程序',
      query: '',
      imageUrl: '/assets/share.jpg'
    }
  }
})