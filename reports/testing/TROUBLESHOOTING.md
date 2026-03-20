# 故障排除指南

## 问题：分类目录和题目一直处于加载状态

### 问题现象
- 页面可以正常打开
- CSS 和 JS 文件加载成功（返回 200）
- 但分类目录和题目列表一直显示加载动画

### 可能原因和解决方案

#### 原因 1：JavaScript 代码错误（已修复 ✅）
**问题**：`app.js` 文件中有重复的函数定义，导致 JavaScript 执行中断。

**解决方案**：
```bash
# 更新到最新版本
git pull origin master
```

#### 原因 2：浏览器缓存旧版本文件
**问题**：浏览器缓存了旧版本的 JavaScript 文件。

**解决方案**：
1. **强制刷新页面**：
   - Windows: `Ctrl + F5` 或 `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`
   
2. **清除浏览器缓存**：
   - Chrome: 设置 → 隐私和安全 → 清除浏览数据
   - Edge: 设置 → 隐私、搜索和服务 → 清除浏览数据
   - Firefox: 选项 → 隐私与安全 → 清除数据

3. **使用无痕模式**：
   - Chrome/Edge: `Ctrl + Shift + N`
   - Firefox: `Ctrl + Shift + P`

#### 原因 3：API 路径配置错误
**问题**：前端 JavaScript 无法正确访问 API 端点。

**检查方法**：
1. 打开浏览器开发者工具（F12）
2. 切换到 **Console（控制台）** 标签
3. 查看是否有错误信息

**预期日志**：
```
📚 题库管理系统已加载
🔗 API 基础路径：/api
📡 健康检查：/health
✅ API 连接正常：{status: "healthy", service: "web"}
```

**如果看到错误**：
- `404 Not Found`：检查 API 路由配置
- `CORS error`：检查后端 CORS 设置
- `Network error`：检查服务是否正常运行

#### 原因 4：服务未正确启动
**检查方法**：
```bash
# 检查服务是否运行
curl http://localhost:8000/health

# 检查 API 是否正常
curl http://localhost:8000/api/categories/tree
```

**预期响应**：
```json
{"status":"healthy","service":"web"}
```

```json
[{"id":"...","name":"数学","description":"数学相关题目",...}, ...]
```

### 完整诊断步骤

#### 步骤 1：检查服务状态
```bash
# Windows PowerShell
curl http://localhost:8000/health

# 或者在浏览器访问
http://localhost:8000/health
```

#### 步骤 2：检查浏览器控制台
1. 按 `F12` 打开开发者工具
2. 切换到 **Console** 标签
3. 查看错误信息

#### 步骤 3：检查网络请求
1. 按 `F12` 打开开发者工具
2. 切换到 **Network** 标签
3. 刷新页面
4. 查看以下请求：
   - `GET /api/categories/tree` - 应该返回 200
   - `GET /api/questions?page=1&limit=10` - 应该返回 200

#### 步骤 4：查看服务器日志
服务启动后，控制台应该显示类似日志：
```
INFO:     127.0.0.1:61969 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:61969 - "GET /static/css/style.css HTTP/1.1" 200 OK
INFO:     127.0.0.1:53210 - "GET /static/js/app.js HTTP/1.1" 200 OK
INFO:     127.0.0.1:53210 - "GET /api/categories/tree HTTP/1.1" 200 OK
INFO:     127.0.0.1:53210 - "GET /api/questions?page=1&limit=10 HTTP/1.1" 200 OK
```

**注意**：如果看到 `/css/style.css` 而不是 `/static/css/style.css`，说明 HTML 文件版本不正确。

### 快速修复方案

#### 方案 A：更新代码（推荐）
```bash
# 进入项目目录
cd D:\zkjiao\github\question-bank-system-master

# 拉取最新代码
git pull origin master

# 重启服务
./run.sh web
```

#### 方案 B：清除缓存
1. 停止服务（Ctrl+C）
2. 清除浏览器缓存
3. 重启服务
4. 使用无痕模式访问

#### 方案 C：手动修复（临时）
如果无法更新代码，可以手动修改浏览器中的 JavaScript：

1. 按 `F12` 打开开发者工具
2. 切换到 **Console** 标签
3. 粘贴以下代码并回车：
```javascript
// 手动加载分类树
fetch('/api/categories/tree')
    .then(r => r.json())
    .then(data => {
        console.log('分类数据:', data);
        // 在控制台查看分类数据
    });

// 手动加载题目
fetch('/api/questions?page=1&limit=10')
    .then(r => r.json())
    .then(data => {
        console.log('题目数据:', data);
        // 在控制台查看题目数据
    });
```

### 联系支持

如果以上方法都无法解决问题，请提供以下信息：

1. **浏览器控制台错误**（F12 → Console）
2. **网络请求状态**（F12 → Network）
3. **服务器日志**（启动服务的控制台输出）
4. **浏览器版本和操作系统**

---

## 最新更新（2026-03-04）

### 修复内容
- ✅ 修复 `app.js` 中重复函数定义的问题
- ✅ 添加页面加载调试信息
- ✅ 优化错误提示

### 如何更新
```bash
git pull origin master
```

### 验证修复
1. 重启服务：`./run.sh web`
2. 打开浏览器访问：http://localhost:8000
3. 按 F12 查看控制台，应该看到：
   ```
   📚 题库管理系统已加载
   🔗 API 基础路径：/api
   ✅ API 连接正常：{status: "healthy", service: "web"}
   ```
4. 分类目录和题目应该正常显示

---
*最后更新：2026-03-04*
