# 验证脚本

本目录包含题库系统的验证脚本，用于确保项目修改后仍然正常工作。

## 📋 验证脚本说明

### 1. `validate_project.py` - 完整验证脚本
**用途**: 全面的项目验证，包括结构、导入、服务等
**用法**:
```bash
# 运行所有验证
python test/validate_project.py

# 运行特定验证
python test/validate_project.py structure    # 项目结构
python test/validate_project.py imports      # Python导入
python test/validate_project.py script       # 运行脚本
python test/validate_project.py database     # 数据库
python test/validate_project.py web          # Web服务
python test/validate_project.py mcp          # MCP服务
python test/validate_project.py wechat       # 微信服务
```

### 2. `quick_validate.sh` - 快速验证脚本
**用途**: 快速验证项目基本功能
**用法**:
```bash
bash test/quick_validate.sh
```

### 3. `pre_commit_validate.sh` - 预提交验证脚本
**用途**: 提交代码前的完整验证，生成验证报告
**用法**:
```bash
bash test/pre_commit_validate.sh
```

## 🚀 验证项目

### 项目结构验证
- ✅ 检查必要的目录和文件是否存在
- ✅ 检查配置文件是否完整
- ✅ 检查运行脚本是否可执行

### Python导入验证
- ✅ 检查核心模块能否正常导入
- ✅ 检查各入口模块能否正常导入
- ✅ 检查共享配置能否正常导入

### 运行脚本验证
- ✅ 检查 `run.sh` 是否可执行
- ✅ 检查帮助命令是否正常
- ✅ 检查各服务启动命令

### 数据库验证
- ✅ 检查数据库表能否正常创建
- ✅ 检查数据库文件是否存在
- ✅ 检查数据库连接

### 服务验证
- ✅ Web服务启动和健康检查
- ✅ MCP服务启动和健康检查
- ✅ 微信服务启动和健康检查
- ✅ API端点访问测试

## 📊 验证流程

### 开发时验证
```bash
# 快速验证（推荐）
bash test/quick_validate.sh

# 完整验证
python test/validate_project.py
```

### 提交前验证
```bash
# 自动运行（通过Git钩子）
git commit -m "提交信息"

# 手动运行
bash test/pre_commit_validate.sh
```

### CI/CD集成
```bash
# 在CI/CD流水线中添加
python test/validate_project.py
```

## 🔧 Git预提交钩子

项目已配置Git预提交钩子，每次提交前会自动运行验证。

**钩子位置**: `.git/hooks/pre-commit`
**功能**: 自动运行 `pre_commit_validate.sh`
**效果**: 如果验证失败，提交将被阻止

### 临时跳过验证
```bash
# 使用--no-verify参数
git commit --no-verify -m "紧急提交"
```

## 📁 日志和报告

验证脚本会生成日志和报告：

### 日志目录
```
test/logs/
├── validation_20260225_113000.log    # 验证日志
└── validation_report_20260225_113000.md  # 验证报告
```

### 报告内容
- 验证时间和项目信息
- 验证结果汇总
- 系统信息
- 建议和改进点

## 🛠️ 维护验证脚本

### 添加新验证
1. 在 `validate_project.py` 的 `ProjectValidator` 类中添加新方法
2. 在 `run_all_tests` 方法中添加测试项
3. 更新 `quick_validate.sh` 和 `pre_commit_validate.sh`

### 更新验证规则
1. 修改 `test_project_structure` 方法中的目录和文件列表
2. 更新 `test_python_imports` 方法中的导入列表
3. 调整服务验证的超时时间和检查逻辑

### 调试验证失败
1. 查看验证日志: `test/logs/validation_*.log`
2. 运行单个验证: `python test/validate_project.py <测试名>`
3. 检查服务日志: `/tmp/web_test.log` 等临时文件

## 📝 最佳实践

1. **每次修改后运行验证**
   ```bash
   # 修改代码后
   bash test/quick_validate.sh
   ```

2. **提交前运行完整验证**
   ```bash
   # 提交前
   bash test/pre_commit_validate.sh
   ```

3. **定期更新验证脚本**
   - 当项目结构变化时更新验证规则
   - 当添加新功能时添加新的验证项
   - 定期检查验证脚本的完整性

4. **查看验证报告**
   - 关注验证报告中的建议
   - 根据报告改进项目质量
   - 保存重要版本的验证报告

## 🚨 常见问题

### 验证失败怎么办？
1. 查看详细的错误信息
2. 检查相关文件是否存在
3. 检查Python导入路径
4. 检查服务端口是否被占用

### 验证太慢怎么办？
1. 使用 `quick_validate.sh` 进行快速验证
2. 调整服务启动的超时时间
3. 只运行必要的验证项

### 如何禁用验证？
1. 临时禁用: `git commit --no-verify`
2. 移除钩子: `rm .git/hooks/pre-commit`
3. 修改钩子: 注释掉验证代码

## 📞 支持

如果验证脚本有问题，请检查：
1. 项目结构是否符合预期
2. Python环境是否正确
3. 依赖是否已安装
4. 端口是否被占用

或者联系项目维护者。