# 脚本使用指南

## 新增脚本说明

### 1. 项目验证脚本 (`validate_and_commit.sh`)
**用途**: 验证项目结构、测试功能、提交到Git

```bash
# 检查项目状态
./scripts/validate_and_commit.sh status

# 验证项目结构
./scripts/validate_and_commit.sh validate

# 测试基本功能
./scripts/validate_and_commit.sh test

# 显示验证报告
./scripts/validate_and_commit.sh report

# 完整验证并提交
./scripts/validate_and_commit.sh full

# 提交更改
./scripts/validate_and_commit.sh commit "提交说明"
```

### 2. 快速启动脚本 (`launch_project.sh`)
**用途**: 一键启动所有服务（推荐）

```bash
# 一键启动所有服务
./scripts/launch_project.sh start

# 查看服务状态
./scripts/launch_project.sh status

# 停止所有服务
./scripts/launch_project.sh stop

# 重启服务
./scripts/launch_project.sh restart

# 查看日志
./scripts/launch_project.sh logs
```

### 3. 完整启动脚本 (`quick_start_project.sh`)
**用途**: 完整的环境配置和启动

```bash
# 安装依赖和初始化环境
./scripts/quick_start_project.sh setup

# 启动所有服务
./scripts/quick_start_project.sh start

# 一键完成所有操作
./scripts/quick_start_project.sh full

# 查看服务状态
./scripts/quick_start_project.sh status

# 停止所有服务
./scripts/quick_start_project.sh stop
```

## 脚本功能对比

| 脚本 | 主要功能 | 适用场景 | 特点 |
|------|----------|----------|------|
| `validate_and_commit.sh` | 项目验证、质量保证、Git提交 | 开发完成后的验证和提交 | 全面的验证检查，确保项目质量 |
| `launch_project.sh` | 快速启动服务 | 日常开发和使用 | 极简启动，后台运行，状态监控 |
| `quick_start_project.sh` | 完整环境配置和启动 | 新环境部署 | 环境检查、依赖安装、服务启动 |

## 快速开始

### 新用户快速启动
```bash
# 1. 克隆项目
git clone git@github.com:superno188462/question-bank-system.git
cd question-bank-system

# 2. 一键启动（推荐）
./scripts/launch_project.sh start

# 3. 验证服务状态
./scripts/launch_project.sh status
```

### 开发者工作流程
```bash
# 1. 开发完成后验证项目
./scripts/validate_and_commit.sh validate

# 2. 测试功能
./scripts/validate_and_commit.sh test

# 3. 提交代码
./scripts/validate_and_commit.sh commit "功能描述"

# 4. 启动服务测试
./scripts/launch_project.sh start
```

## 服务访问地址

成功启动后可以访问：

```
🌐 Web管理界面: http://localhost:8000
📚 API文档:      http://localhost:8000/docs
📱 微信API:      http://localhost:8001
🤖 MCP接口:      http://localhost:8002
```

## 常用命令组合

### 开发环境
```bash
# 启动开发环境
./scripts/launch_project.sh start

# 查看日志
./scripts/launch_project.sh logs

# 停止服务
./scripts/launch_project.sh stop
```

### 质量保证
```bash
# 运行完整验证
./scripts/validate_and_commit.sh full

# 查看验证报告
./scripts/validate_and_commit.sh report
```

### 生产部署
```bash
# 完整环境配置
./scripts/quick_start_project.sh full

# 监控服务状态
./scripts/quick_start_project.sh status
```

## 脚本位置

所有脚本都在 `scripts/` 目录下：

```
scripts/
├── validate_and_commit.sh    # 项目验证和提交
├── launch_project.sh         # 快速启动（推荐）
├── quick_start_project.sh    # 完整启动
├── pre_commit_test.sh        # 预提交测试
├── post_commit_check.sh      # 提交后检查
└── ... 其他脚本
```

## 注意事项

1. **权限问题**: 首次使用需要给脚本执行权限
   ```bash
   chmod +x scripts/*.sh
   ```

2. **Python环境**: 需要Python 3.8+，脚本会自动检查

3. **端口冲突**: 如果端口8000、8001、8002被占用，脚本会尝试停止占用进程

4. **数据库**: 首次运行会自动创建数据库和示例数据

5. **日志文件**: 服务日志保存在项目根目录的 `.log` 文件中

## 故障排除

### 常见问题

1. **脚本无法执行**
   ```bash
   # 添加执行权限
   chmod +x scripts/*.sh
   ```

2. **Python命令找不到**
   ```bash
   # 检查Python安装
   python3 --version
   
   # 或者创建别名
   alias python=python3
   ```

3. **端口被占用**
   ```bash
   # 查看占用进程
   lsof -ti:8000
   
   # 或者使用脚本自动处理
   ./scripts/launch_project.sh restart
   ```

4. **依赖安装失败**
   ```bash
   # 手动安装依赖
   pip install -r config/requirements.txt
   
   # 或者使用uv（更快）
   uv pip install -r config/requirements.txt
   ```

### 获取帮助
```bash
# 查看脚本帮助
./scripts/validate_and_commit.sh help
./scripts/launch_project.sh help
./scripts/quick_start_project.sh help
```

## 更新日志

### 2026-02-25
- 新增 `validate_and_commit.sh`: 项目验证和提交脚本
- 新增 `launch_project.sh`: 快速启动脚本
- 新增 `quick_start_project.sh`: 完整启动脚本
- 新增本使用指南

---

通过这些脚本，你可以更方便地管理、验证和启动题库系统项目！