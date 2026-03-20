# 任务 T014 - 根目录结构整理方案

**任务编号**: T014  
**任务名称**: 整理根目录结构，将临时文件移动到合适的子目录  
**执行时间**: 2026-03-20 09:35  
**执行人**: Architect (nanobot)  
**当前状态**: 根目录文件过多 (29 个 Markdown 文件)  
**目标状态**: 根目录极简 (≤5 个文件)

---

## 执行摘要

### 当前问题

1. **根目录文件过多**: 29 个 Markdown 文件，混杂不堪
2. **临时文件散落**: .coverage, htmlcov/, __pycache__/ 未清理
3. **报告文件混杂**: 架构、代码审查、测试报告混在一起
4. **用户偏好**: 根目录极简（≤5 个文件）

### 整理原则

1. **根目录只保留核心文件**: README, requirements, 启动脚本
2. **报告文件分类归档**: 按类型放入 reports/ 子目录
3. **临时文件清理**: 加入 .gitignore，定期清理
4. **文档统一管理**: 所有文档放入 docs/ 子目录
5. **脚本集中管理**: 所有脚本放入 scripts/ 子目录

---

## 当前根目录文件清单

### Markdown 文件 (29 个)

| 文件名 | 大小 | 类型 | 应移动到 |
|--------|------|------|----------|
| ARCHITECTURE_REVIEW_T003.md | 28K | 架构报告 | reports/architecture/ |
| CODE_REVIEW_REPORT.md | 18K | 代码审查 | reports/code-review/ |
| CODE_REVIEW_REPORT_T003.md | 19K | 代码审查 | reports/code-review/ |
| COMMIT_SUMMARY.md | 2.8K | 文档 | docs/ |
| COVERAGE_PROGRESS_T010.md | 3.8K | 覆盖率报告 | reports/coverage/ |
| DEVELOPER_FIXES_T003.md | 3.0K | 修复报告 | reports/coverage/ |
| FRONTEND_VALIDATION_REPORT.md | 4.6K | 文档 | docs/ |
| QUICK_START_GUIDE.md | 6.3K | 文档 | docs/ |
| T010_COVERAGE_MIDTERM_REPORT.md | 4.2K | 覆盖率报告 | reports/coverage/ |
| T010_COVERAGE_REVIEW_REPORT.md | 12K | 覆盖率报告 | reports/coverage/ |
| T011_TEST_FIX_REVIEW.md | 19K | 测试审查 | reports/testing/ |
| T012_REVIEW_REPORT.md | 14K | 审查报告 | reports/ |
| T013_COVERAGE_REVIEW.md | 29K | 覆盖率报告 | reports/coverage/ |
| TASK_T001_STATUS.md | 3.0K | 任务状态 | reports/tasks/ |
| TASK_T003_STATUS.md | 6.0K | 任务状态 | reports/tasks/ |
| TASK_T003_SUMMARY.md | 12K | 任务总结 | reports/tasks/ |
| TASK_T009_ARCHITECT_ANALYSIS.md | 15K | 架构分析 | reports/architecture/ |
| TASK_T009_STATUS.md | 4.4K | 任务状态 | reports/tasks/ |
| TASK_T010_ARCHITECT_ANALYSIS.md | 19K | 架构分析 | reports/architecture/ |
| TASK_T010_STATUS.md | 5.5K | 任务状态 | reports/tasks/ |
| TASK_T011_ARCHITECT_ANALYSIS.md | 14K | 架构分析 | reports/architecture/ |
| TASK_T011_STATUS.md | 6.3K | 任务状态 | reports/tasks/ |
| TASK_T012_ARCHITECT_ANALYSIS.md | 14K | 架构分析 | reports/architecture/ |
| TASK_T012_STATUS.md | 4.2K | 任务状态 | reports/tasks/ |
| TASK_T013_ARCHITECT_ANALYSIS.md | 15K | 架构分析 | reports/architecture/ |
| TASK_T013_STATUS.md | 5.4K | 任务状态 | reports/tasks/ |
| TROUBLESHOOTING.md | 4.9K | 文档 | docs/ |
| VALIDATION_SUMMARY.md | 4.8K | 文档 | docs/ |
| CODE | 28K | 代码文件 | 删除或归档 |

### Python 文件

| 文件名 | 大小 | 用途 | 应移动到 |
|--------|------|------|----------|
| conftest.py | 247B | pytest 配置 | **保留根目录** ✅ |
| diagnose.py | 1.8K | 诊断脚本 | scripts/ |
| migrate.py | 1.8K | 数据库迁移 | scripts/ |
| start.py | 3.7K | 启动脚本 | **保留根目录** ✅ |
| test_frontend.py | 7.3K | 测试脚本 | tests/ |

### 脚本文件

| 文件名 | 大小 | 用途 | 应移动到 |
|--------|------|------|----------|
| force_restart.sh | 1.2K | 重启脚本 | scripts/ |
| run.sh | 17K | 运行脚本 | **保留根目录** ✅ |
| run_tests.sh | 3.5K | 测试脚本 | scripts/ |
| kill_all_python.ps1 | 1.4K | Windows 脚本 | scripts/ |
| run_web.bat | 1.2K | Windows 脚本 | scripts/ |

### 配置文件

| 文件名 | 大小 | 用途 | 应移动到 |
|--------|------|------|----------|
| pytest.ini | 351B | pytest 配置 | **保留根目录** ✅ |
| requirements.txt | 495B | 依赖列表 | **保留根目录** ✅ |
| .env.example | 1.4K | 环境变量模板 | **保留根目录** ✅ |
| .env | 878B | 环境变量 | **保留根目录** ✅ (但 .gitignore) |
| .gitignore | 1.1K | Git 忽略 | **保留根目录** ✅ |

### 临时文件/目录

| 名称 | 类型 | 处理方式 |
|------|------|----------|
| .coverage | 文件 | 加入 .gitignore，清理 |
| htmlcov/ | 目录 | 加入 .gitignore，清理 |
| __pycache__/ | 目录 | 加入 .gitignore，清理 |
| .pytest_cache/ | 目录 | 加入 .gitignore，保留 |

---

## 目录结构设计方案

### 目标目录结构

```
question-bank-system/
├── README.md                    # ✅ 保留
├── requirements.txt             # ✅ 保留
├── run.sh                       # ✅ 保留
├── start.py                     # ✅ 保留
├── .env.example                 # ✅ 保留
├── .env                         # ✅ 保留（.gitignore）
├── .gitignore                   # ✅ 保留
├── pytest.ini                   # ✅ 保留
├── conftest.py                  # ✅ 保留
│
├── agent/                       # AI 模块
├── core/                        # 核心模块
├── web/                         # Web 模块
├── mcp_server/                  # MCP 服务
├── wechat/                      # 微信服务
├── shared/                      # 共享模块
├── config/                      # 配置文件
├── data/                        # 数据文件
│
├── docs/                        # 文档目录
│   ├── COMMIT_SUMMARY.md
│   ├── FRONTEND_VALIDATION_REPORT.md
│   ├── QUICK_START_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── VALIDATION_SUMMARY.md
│
├── reports/                     # 报告目录
│   ├── architecture/            # 架构报告
│   │   ├── ARCHITECTURE_REVIEW_T003.md
│   │   ├── TASK_T009_ARCHITECT_ANALYSIS.md
│   │   ├── TASK_T010_ARCHITECT_ANALYSIS.md
│   │   ├── TASK_T011_ARCHITECT_ANALYSIS.md
│   │   ├── TASK_T012_ARCHITECT_ANALYSIS.md
│   │   └── TASK_T013_ARCHITECT_ANALYSIS.md
│   ├── code-review/             # 代码审查报告
│   │   ├── CODE_REVIEW_REPORT.md
│   │   └── CODE_REVIEW_REPORT_T003.md
│   ├── coverage/                # 覆盖率报告
│   │   ├── COVERAGE_PROGRESS_T010.md
│   │   ├── DEVELOPER_FIXES_T003.md
│   │   ├── T010_COVERAGE_MIDTERM_REPORT.md
│   │   ├── T010_COVERAGE_REVIEW_REPORT.md
│   │   └── T013_COVERAGE_REVIEW.md
│   ├── tasks/                   # 任务状态报告
│   │   ├── TASK_T001_STATUS.md
│   │   ├── TASK_T003_STATUS.md
│   │   ├── TASK_T003_SUMMARY.md
│   │   ├── TASK_T009_STATUS.md
│   │   ├── TASK_T010_STATUS.md
│   │   ├── TASK_T011_STATUS.md
│   │   ├── TASK_T012_STATUS.md
│   │   └── TASK_T013_STATUS.md
│   ├── testing/                 # 测试报告
│   │   └── T011_TEST_FIX_REVIEW.md
│   └── T012_REVIEW_REPORT.md
│
├── scripts/                     # 脚本目录
│   ├── diagnose.py
│   ├── migrate.py
│   ├── force_restart.sh
│   ├── run_tests.sh
│   ├── kill_all_python.ps1
│   └── run_web.bat
│
├── tests/                       # 测试目录
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   ├── api/
│   └── test_frontend.py
│
└── test/                        # 现有测试目录（保留）
    ├── README.md
    ├── validate_project.py
    └── ...
```

---

## 实施计划

### 阶段 1: 创建目录结构 (5 分钟)

```bash
# 创建 reports 目录结构
mkdir -p reports/{architecture,code-review,coverage,tasks,testing}

# 创建 scripts 目录
mkdir -p scripts

# 确保 docs 目录存在
mkdir -p docs

# 确保 tests 目录结构
mkdir -p tests/{unit,integration,api}
```

### 阶段 2: 移动报告文件 (10 分钟)

```bash
# 移动架构报告
mv ARCHITECTURE_REVIEW_T003.md reports/architecture/
mv TASK_T009_ARCHITECT_ANALYSIS.md reports/architecture/
mv TASK_T010_ARCHITECT_ANALYSIS.md reports/architecture/
mv TASK_T011_ARCHITECT_ANALYSIS.md reports/architecture/
mv TASK_T012_ARCHITECT_ANALYSIS.md reports/architecture/
mv TASK_T013_ARCHITECT_ANALYSIS.md reports/architecture/

# 移动代码审查报告
mv CODE_REVIEW_REPORT.md reports/code-review/
mv CODE_REVIEW_REPORT_T003.md reports/code-review/

# 移动覆盖率报告
mv COVERAGE_PROGRESS_T010.md reports/coverage/
mv DEVELOPER_FIXES_T003.md reports/coverage/
mv T010_COVERAGE_MIDTERM_REPORT.md reports/coverage/
mv T010_COVERAGE_REVIEW_REPORT.md reports/coverage/
mv T013_COVERAGE_REVIEW.md reports/coverage/

# 移动任务状态报告
mv TASK_T001_STATUS.md reports/tasks/
mv TASK_T003_STATUS.md reports/tasks/
mv TASK_T003_SUMMARY.md reports/tasks/
mv TASK_T009_STATUS.md reports/tasks/
mv TASK_T010_STATUS.md reports/tasks/
mv TASK_T011_STATUS.md reports/tasks/
mv TASK_T012_STATUS.md reports/tasks/
mv TASK_T013_STATUS.md reports/tasks/

# 移动测试报告
mv T011_TEST_FIX_REVIEW.md reports/testing/

# 移动其他报告
mv T012_REVIEW_REPORT.md reports/
```

### 阶段 3: 移动文档文件 (5 分钟)

```bash
# 移动文档到 docs/
mv COMMIT_SUMMARY.md docs/
mv FRONTEND_VALIDATION_REPORT.md docs/
mv QUICK_START_GUIDE.md docs/
mv TROUBLESHOOTING.md docs/
mv VALIDATION_SUMMARY.md docs/
```

### 阶段 4: 移动脚本文件 (5 分钟)

```bash
# 移动脚本到 scripts/
mv diagnose.py scripts/
mv migrate.py scripts/
mv force_restart.sh scripts/
mv run_tests.sh scripts/
mv kill_all_python.ps1 scripts/
mv run_web.bat scripts/

# 移动测试文件
mv test_frontend.py tests/
```

### 阶段 5: 清理临时文件 (5 分钟)

```bash
# 清理临时文件
rm -rf .coverage
rm -rf htmlcov/
rm -rf __pycache__/

# 更新 .gitignore（确保已包含）
# .coverage
# htmlcov/
# __pycache__/
# *.pyc
# .pytest_cache/
# .env
```

### 阶段 6: 删除无用文件 (2 分钟)

```bash
# 删除 CODE 文件（看起来是临时文件）
rm CODE
```

### 阶段 7: 验证项目运行 (10 分钟)

```bash
# 验证 pytest 配置
.venv/bin/python -m pytest --version

# 运行简单测试
.venv/bin/python -m pytest core/tests/test_models.py -v

# 验证启动脚本
./run.sh --help 2>&1 | head -10

# 验证迁移脚本
.venv/bin/python scripts/migrate.py --help 2>&1 | head -10
```

---

## 更新引用路径

### 需要更新的文件

1. **文档中的引用**: 检查 docs/ 中是否有引用根目录文件的链接
2. **脚本中的路径**: 检查 scripts/ 中脚本的路径引用
3. **测试中的导入**: 检查 tests/ 中的导入路径

### 更新脚本

```bash
# 查找需要更新的引用
grep -r "ARCHITECTURE_REVIEW" . --include="*.md" --include="*.py"
grep -r "TASK_T00" . --include="*.md" --include="*.py"
grep -r "scripts/migrate" . --include="*.md" --include="*.py"
```

---

## .gitignore 更新

确保 .gitignore 包含以下内容：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
env/
venv/

# Coverage
.coverage
htmlcov/
.coverage.*
*.cover

# Testing
.pytest_cache/
.tox/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Reports (optional - keep in git)
# reports/
```

---

## 验收标准

### 根目录文件清单（目标）

- [ ] README.md ✅
- [ ] requirements.txt ✅
- [ ] run.sh ✅
- [ ] start.py ✅
- [ ] .env.example ✅
- [ ] .env ✅ (在 .gitignore 中)
- [ ] .gitignore ✅
- [ ] pytest.ini ✅
- [ ] conftest.py ✅

**总计**: 9 个文件（符合 ≤10 个文件的目标）

### 目录结构验证

- [ ] reports/ 目录创建完成
- [ ] reports/architecture/ 包含 6 个架构报告
- [ ] reports/code-review/ 包含 2 个代码审查报告
- [ ] reports/coverage/ 包含 5 个覆盖率报告
- [ ] reports/tasks/ 包含 8 个任务状态报告
- [ ] reports/testing/ 包含 1 个测试报告
- [ ] docs/ 包含 5 个文档
- [ ] scripts/ 包含 6 个脚本
- [ ] tests/ 包含 test_frontend.py

### 临时文件清理

- [ ] .coverage 已删除
- [ ] htmlcov/ 已删除
- [ ] __pycache__/ 已删除
- [ ] CODE 文件已删除

### 项目功能验证

- [ ] pytest 正常运行
- [ ] 测试用例通过
- [ ] run.sh 正常运行
- [ ] migrate.py 正常运行
- [ ] 项目可以启动

---

## 风险与缓解

### 风险 1: 路径引用断裂
- **影响**: 高（文档链接失效）
- **概率**: 中
- **缓解**: 
  - 移动前搜索所有引用
  - 更新相对路径
  - 验证文档链接

### 风险 2: 脚本无法运行
- **影响**: 高（功能失效）
- **概率**: 低
- **缓解**:
  - 测试所有脚本
  - 更新路径引用
  - 保留向后兼容

### 风险 3: Git 历史丢失
- **影响**: 中（文件移动记录）
- **概率**: 低
- **缓解**:
  - 使用 git mv 而非 mv
  - 提交时说明文件移动

---

## 交付物

### 目录结构
- reports/ 目录（包含所有报告）
- docs/ 目录（包含所有文档）
- scripts/ 目录（包含所有脚本）
- tests/ 目录（包含测试文件）

### 清理结果
- 根目录文件 ≤ 10 个
- 临时文件已清理
- .gitignore 已更新

### 验证报告
- 项目运行正常
- 测试通过
- 文档链接有效

---

**下一步**:
- [ ] 转交 Developer 执行文件移动
- [ ] 更新所有引用路径
- [ ] 验证项目正常运行
- [ ] 转交 Reviewer 审查

---

*报告生成时间*: 2026-03-20 09:40  
*报告人*: Architect (nanobot)  
*当前根目录文件数*: 29 个 Markdown + 其他  
*目标根目录文件数*: ≤10 个  
*预计完成时间*: 30-40 分钟
