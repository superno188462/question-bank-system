// app.js - 小程序入口文件

App({
  onLaunch() {
    // 小程序启动时执行
    console.log('小程序启动')
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 获取系统信息
    this.getSystemInfo()
    
    // 初始化网络请求
    this.initNetwork()
  },

  onShow() {
    // 小程序显示时执行
    console.log('小程序显示')
  },

  onHide() {
    // 小程序隐藏时执行
    console.log('小程序隐藏')
  },

  // 全局数据
  globalData: {
    userInfo: null,
    token: null,
    systemInfo: null,
    apiBaseUrl: 'https://yourdomain.com', // 修改为您的服务器地址
    isConnected: true
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
      console.log('已登录，token:', token)
    } else {
      console.log('未登录')
    }
  },

  // 获取系统信息
  getSystemInfo() {
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res
        console.log('系统信息:', res)
      }
    })
  },

  // 初始化网络
  initNetwork() {
    // 监听网络状态
    wx.onNetworkStatusChange((res) => {
      this.globalData.isConnected = res.isConnected
      console.log('网络状态变化:', res)
    })

    // 获取当前网络状态
    wx.getNetworkType({
      success: (res) => {
        this.globalData.isConnected = res.networkType !== 'none'
        console.log('当前网络类型:', res.networkType)
      }
    })
  },

  // 统一请求方法
  request(options) {
    const { url, method = 'GET', data = {}, header = {} } = options
    
    // 添加认证头
    if (this.globalData.token) {
      header['Authorization'] = `Bearer ${this.globalData.token}`
    }
    
    // 添加内容类型
    if (!header['Content-Type']) {
      header['Content-Type'] = 'application/json'
    }
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.apiBaseUrl}${url}`,
        method,
        data,
        header,
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(res)
          }
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  },

  // 登录方法
  login() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          if (res.code) {
            // 发送 code 到服务器换取 token
            this.request({
              url: '/api/wechat/login',
              method: 'POST',
              data: { code: res.code }
            }).then(response => {
              if (response.token) {
                this.globalData.token = response.token
                wx.setStorageSync('token', response.token)
                resolve(response)
              } else {
                reject(new Error('登录失败'))
              }
            }).catch(err => {
              reject(err)
            })
          } else {
            reject(new Error('获取code失败'))
          }
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  },

  // 获取用户信息
  getUserInfo() {
    return new Promise((resolve, reject) => {
      wx.getUserProfile({
        desc: '用于完善会员资料',
        success: (res) => {
          this.globalData.userInfo = res.userInfo
          resolve(res.userInfo)
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  },

  // 显示提示
  showToast(title, icon = 'none', duration = 2000) {
    wx.showToast({
      title,
      icon,
      duration
    })
  },

  // 显示加载
  showLoading(title = '加载中...') {
    wx.showLoading({
      title,
      mask: true
    })
  },

  // 隐藏加载
  hideLoading() {
    wx.hideLoading()
  },

  // 显示模态框
  showModal(title, content, showCancel = true) {
    return new Promise((resolve) => {
      wx.showModal({
        title,
        content,
        showCancel,
        success: (res) => {
          resolve(res.confirm)
        }
      })
    })
  }
})