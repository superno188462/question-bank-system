# 📱 微信小程序集成指南

## 🎯 概述
本指南将帮助您将题库系统集成到微信小程序中，实现移动端访问。

## 📋 前提条件

### 1. 微信小程序账号
- 注册微信公众平台账号：https://mp.weixin.qq.com
- 完成实名认证
- 创建小程序（选择个人主体）

### 2. 开发环境
- 下载微信开发者工具：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
- Node.js 环境（可选，用于构建）

### 3. 服务器要求
- 已部署的题库系统（支持HTTPS）
- 备案的域名（国内服务器需要）
- SSL证书（必须）

## 🚀 快速开始

### 步骤1：配置微信小程序

#### 1.1 创建小程序
1. 登录微信公众平台
2. 进入"小程序" → "开发" → "开发管理"
3. 点击"开发设置"，获取以下信息：
   - **AppID**: 小程序唯一标识
   - **AppSecret**: 小程序密钥（重要，保密）

#### 1.2 配置服务器域名
在"开发设置" → "服务器域名"中配置：
```
request合法域名:
https://yourdomain.com

uploadFile合法域名:
https://yourdomain.com

downloadFile合法域名:
https://yourdomain.com

socket合法域名:
wss://yourdomain.com (如果需要WebSocket)
```

#### 1.3 配置业务域名（可选）
如果需要网页跳转，配置业务域名。

### 步骤2：配置后端API

#### 2.1 更新配置文件
修改 `wechat-miniprogram/config/api.js`：
```javascript
const API_BASE_URL = 'https://yourdomain.com'; // 您的服务器地址
const WECHAT_APP_ID = 'your_app_id'; // 您的微信小程序AppID
```

#### 2.2 配置微信API密钥
在服务器环境变量中设置：
```bash
export WECHAT_APP_ID=your_app_id
export WECHAT_APP_SECRET=your_app_secret
```

#### 2.3 启动微信API服务
确保 `wechat_api.py` 已正确导入并启用。

### 步骤3：开发小程序

#### 3.1 导入项目
1. 打开微信开发者工具
2. 选择"导入项目"
3. 选择 `question-bank-system/wechat-miniprogram/` 目录
4. 输入您的AppID

#### 3.2 修改配置
1. 修改 `app.js` 中的 `apiBaseUrl`
2. 修改 `config/api.js` 中的服务器地址
3. 根据需要修改页面样式

#### 3.3 开发调试
1. 点击"编译"按钮预览
2. 使用"真机调试"在手机上测试
3. 查看控制台日志

### 步骤4：测试功能

#### 4.1 登录测试
```javascript
// 测试登录
wx.login({
  success: (res) => {
    console.log('登录code:', res.code)
  }
})
```

#### 4.2 API测试
```javascript
// 测试API连接
wx.request({
  url: 'https://yourdomain.com/api/wechat/config',
  success: (res) => {
    console.log('API响应:', res.data)
  }
})
```

#### 4.3 功能测试
- 题目搜索
- 智能对话
- 错题本
- 学习统计

## 🔧 功能模块详解

### 1. 用户系统
#### 微信登录流程：
```
1. 小程序调用 wx.login() 获取 code
2. 发送 code 到服务器 /api/wechat/login
3. 服务器用 code 换取 openid 和 session_key
4. 服务器生成 JWT token 返回给小程序
5. 小程序存储 token 用于后续请求
```

#### 代码示例：
```javascript
// 登录方法
async function login() {
  const res = await wx.login()
  const code = res.code
  
  const result = await app.request({
    url: '/api/wechat/login',
    method: 'POST',
    data: { code }
  })
  
  if (result.token) {
    wx.setStorageSync('token', result.token)
    return result
  }
}
```

### 2. 题目模块
#### API接口：
- `GET /api/wechat/questions/hot` - 热门题目
- `GET /api/wechat/questions/search` - 搜索题目
- `GET /api/questions/{id}` - 题目详情

#### 小程序页面：
- `pages/questions/list` - 题目列表
- `pages/questions/detail` - 题目详情
- `pages/search/index` - 搜索页面

### 3. 聊天模块
#### API接口：
- `POST /api/wechat/chat` - 智能对话

#### 小程序页面：
- `pages/chat/index` - 对话界面

### 4. 学习统计
#### API接口：
- `GET /api/wechat/stats/learning` - 学习统计
- `GET /api/wechat/errorbook/list` - 错题本

#### 小程序页面：
- `pages/profile/index` - 个人中心
- `pages/errorbook/index` - 错题本

## ⚙️ 配置详解

### 1. 小程序配置 (app.json)
```json
{
  "pages": [...],           // 页面路径
  "window": {...},          // 窗口配置
  "tabBar": {...},          // 底部标签栏
  "networkTimeout": {...},  // 网络超时
  "permission": {...}       // 权限配置
}
```

### 2. 服务器配置
#### 环境变量：
```bash
# 微信配置
WECHAT_APP_ID=wx1234567890abcdef
WECHAT_APP_SECRET=your_app_secret_keep_secure

# JWT配置
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7
```

#### Nginx配置：
```nginx
# 微信小程序API
location /api/wechat/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    
    # CORS配置
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
    add_header Access-Control-Allow-Headers 'DNT,User-Agent,X-Requested-With,Content-Type,Authorization';
    
    # 预检请求处理
    if ($request_method = 'OPTIONS') {
        return 204;
    }
}
```

### 3. 安全配置
#### HTTPS强制：
```nginx
# 强制HTTPS
if ($scheme != "https") {
    return 301 https://$host$request_uri;
}
```

#### 请求限制：
```nginx
# 防止滥用
limit_req_zone $binary_remote_addr zone=wechat:10m rate=10r/s;

location /api/wechat/login {
    limit_req zone=wechat burst=20 nodelay;
    proxy_pass http://127.0.0.1:8000;
}
```

## 🔍 调试和测试

### 1. 开发工具调试
```bash
# 查看日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 查看应用日志
sudo journalctl -u question-bank -f
```

### 2. 小程序调试工具
- **Console面板**: 查看日志
- **Network面板**: 监控网络请求
- **Storage面板**: 查看本地存储
- **AppData面板**: 查看页面数据

### 3. 真机调试
1. 点击"真机调试"
2. 扫描二维码
3. 在手机上测试
4. 查看远程日志

## 🚨 常见问题

### 问题1：登录失败
**错误**: `errCode: -1, errMsg: "login:fail"`
**解决**:
1. 检查AppID和AppSecret是否正确
2. 检查服务器时间是否同步
3. 检查网络连接

### 问题2：API请求失败
**错误**: `request:fail url not in domain list`
**解决**:
1. 在微信公众平台配置服务器域名
2. 确保使用HTTPS
3. 检查域名备案（国内服务器）

### 问题3：HTTPS证书问题
**错误**: `SSL certificate problem`
**解决**:
1. 确保证书有效
2. 确保证书链完整
3. 使用Let's Encrypt免费证书

### 问题4：CORS错误
**错误**: `Cross-Origin Request Blocked`
**解决**:
1. 检查Nginx CORS配置
2. 检查FastAPI CORS中间件
3. 确保响应头正确

### 问题5：性能问题
**现象**: 加载缓慢
**解决**:
1. 启用Gzip压缩
2. 配置缓存
3. 优化图片资源
4. 使用CDN

## 📊 发布流程

### 1. 开发版本
```bash
# 1. 在开发者工具中点击"上传"
# 2. 填写版本号和备注
# 3. 提交审核
```

### 2. 审核注意事项
- 确保功能完整
- 无明显的bug
- 符合微信小程序规范
- 个人小程序功能有限制

### 3. 发布上线
1. 审核通过后，点击"发布"
2. 用户可以通过搜索或扫码使用
3. 监控用户反馈和错误日志

## 🔄 更新维护

### 1. 代码更新
```bash
# 更新后端
git pull origin main
sudo systemctl restart question-bank

# 更新小程序
# 在开发者工具中重新上传
```

### 2. 数据备份
```bash
# 备份数据库
cp data/question_bank.db data/question_bank.db.backup.$(date +%Y%m%d)

# 备份上传文件
tar -czf uploads.backup.$(date +%Y%m%d).tar.gz uploads/
```

### 3. 监控告警
```bash
# 监控服务状态
sudo systemctl status question-bank
sudo systemctl status nginx

# 监控日志
tail -f /var/log/nginx/access.log | grep "api/wechat"
```

## 📈 优化建议

### 1. 性能优化
- 使用小程序分包加载
- 图片懒加载
- 数据缓存
- 请求合并

### 2. 用户体验
- 添加加载动画
- 错误友好提示
- 离线功能
- 夜间模式

### 3. 功能扩展
- 添加分享功能
- 消息推送
- 学习小组
- 竞赛模式

## 📞 支持资源

### 官方文档
- 微信小程序开发文档：https://developers.weixin.qq.com/miniprogram/dev/framework/
- FastAPI文档：https://fastapi.tiangolo.com/
- Let's Encrypt文档：https://letsencrypt.org/docs/

### 社区支持
- 微信开放社区
- Stack Overflow
- GitHub Issues

### 本项目支持
- 查看 `wechat-miniprogram/README.md`
- 运行测试脚本
- 查看部署日志

---

**提示**: 对于个人使用的小程序，建议先开发核心功能，通过审核后再逐步添加其他功能。微信对个人小程序有一定限制，请仔细阅读开发规范。