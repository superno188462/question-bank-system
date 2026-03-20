# 任务 T009 - 测试覆盖率分析与技术方案

**任务编号**: T009  
**任务名称**: 测试覆盖率提升 (目标 80%)  
**执行时间**: 2026-03-19 15:30  
**执行人**: Architect (nanobot)  
**当前覆盖率**: 41%  
**目标覆盖率**: 80%  
**差距**: 39%

---

## 执行摘要

### 当前覆盖率状态

| 模块 | 语句数 | 未覆盖 | 覆盖率 | 状态 |
|------|--------|--------|--------|------|
| **总体** | 1924 | 1130 | **41%** | 🔴 严重不足 |
| agent/ | 452 | 319 | 29% | 🔴 严重不足 |
| core/ | 819 | 412 | 50% | 🟡 需改进 |
| web/ | 433 | 383 | 12% | 🔴 严重不足 |

### 覆盖率目标分解

| 模块 | 当前 | 目标 | 需提升 | 优先级 |
|------|------|------|--------|--------|
| **总体** | 41% | 80% | +39% | P0 |
| agent/ | 29% | 75% | +46% | P1 |
| core/ | 50% | 85% | +35% | P0 |
| web/ | 12% | 80% | +68% | P0 |

---

## 一、详细覆盖率分析

### 1.1 Agent 模块 (29% - 需重点改进)

#### agent/config.py (53%)
```
未覆盖行：37-42, 52-59, 66, 97-99, 112-125, 133-134, 140-141, 
         147-148, 156-157, 163-164, 170-171, 179-180, 186-187, 
         193-194, 202-203, 209-210, 216-217, 223-224, 230-231, 
         239-241, 247-249, 256-260, 265, 272, 281, 290, 299-307
```

**问题**:
- 配置加载方法未测试
- 配置刷新方法未测试
- 环境变量覆盖未测试
- 配置验证未测试

**测试需求**: 15 个测试用例

#### agent/extractors/document_extractor.py (16%)
```
未覆盖行：55-57, 69-120, 129-139, 143-144, 148-172, 176-187, 
         192-215, 224-225, 229
```

**问题**:
- PDF 文档提取未测试
- Word 文档提取未测试
- 文本文件提取未测试
- 错误处理未测试

**测试需求**: 20 个测试用例

#### agent/extractors/image_extractor.py (16%)
```
未覆盖行：64-66, 78-152, 171-187, 200-224, 233-234, 238-248, 252
```

**问题**:
- 图片题目提取未测试
- OCR 功能未测试
- 多图片批量处理未测试
- 错误处理未测试

**测试需求**: 18 个测试用例

#### agent/generators/explanation_generator.py (34%)
```
未覆盖行：41-42, 54-81, 97-101, 105-106, 110
```

**问题**:
- 解析生成未测试
- 批量生成未测试

**测试需求**: 8 个测试用例

#### agent/services/embedding_service.py (69%)
```
未覆盖行：56-58, 74-89
```

**问题**:
- 向量化方法未测试
- 批量向量化未测试

**测试需求**: 6 个测试用例

#### agent/services/model_client.py (31%)
```
未覆盖行：25-40, 44-51, 64-81, 98-115, 119, 122, 125
```

**问题**:
- LLM 调用未测试
- Vision 模型调用未测试
- Embedding 调用未测试
- 错误处理未测试

**测试需求**: 12 个测试用例

---

### 1.2 Core 模块 (50% - 需重点改进)

#### core/database/connection.py (86%) ✅
```
未覆盖行：28-30, 56, 75-77, 159-164
```

**问题**:
- 事务回滚未测试
- 连接关闭未测试

**测试需求**: 4 个测试用例

#### core/database/repositories.py (43%)
```
未覆盖行：36, 40, 44, 48, 52, 56, 90, 103-106, 121-148, 
         160-168, 185-201, 205-211, 220-223, 235, 240-247, 
         251-255, 303, 311-313, 346-348, 352-361, 391-392, 
         423-459, 463-472, 476-477, 502-519, 523-529, 533-537, 
         546-547, 556-580, 585-589, 594-610, 615-622, 627-632, 
         637-657, 662, 671, 680-682, 687, 712-728, 733-740, 
         745-750, 755
```

**问题**:
- CategoryRepository 方法覆盖不足
- TagRepository 方法覆盖不足
- QuestionRepository 方法覆盖不足
- StagingQuestionRepository 方法覆盖不足
- 搜索方法未测试
- 批量操作未测试

**测试需求**: 45 个测试用例

#### core/exceptions.py (0%) 🔴
```
未覆盖行：7-83 (全部)
```

**问题**:
- 所有自定义异常未测试

**测试需求**: 8 个测试用例

#### core/models.py (97%) ✅
```
未覆盖行：82, 85, 99, 103
```

**问题**:
- 少量验证逻辑未测试

**测试需求**: 2 个测试用例

#### core/services.py (47%)
```
未覆盖行：24-26, 38-51
```

**问题**:
- 旧服务类未测试 (已迁移到新文件)

**测试需求**: 可忽略 (已废弃)

#### core/services/category_service.py (64%)
```
未覆盖行：47-48, 57-58, 71-77, 94, 107-108
```

**问题**:
- 更新方法未测试
- 删除方法未测试
- 搜索方法未测试

**测试需求**: 8 个测试用例

#### core/services/question_service.py (50%)
```
未覆盖行：53-55, 70, 81-85, 110-111, 115-119, 127-128, 
         146-152, 167, 199-216, 229-248, 260-266, 279-292, 
         305-311, 336-337, 349-350
```

**问题**:
- 向量化逻辑未测试
- 批量操作未测试
- 搜索方法未测试
- 标签管理未测试

**测试需求**: 25 个测试用例

#### core/services/tag_service.py (41%)
```
未覆盖行：20, 32-35, 47-48, 57-58, 70-76, 88-89
```

**问题**:
- 大部分方法未测试

**测试需求**: 10 个测试用例

#### core/services/vector_index.py (37%)
```
未覆盖行：57-60, 83, 94-112, 125-138, 142-151, 173-223, 
         227-241, 257, 266, 283-317
```

**问题**:
- 向量相似度搜索未测试
- 批量向量化未测试
- 重建向量未测试

**测试需求**: 18 个测试用例

---

### 1.3 Web 模块 (12% - 需重点改进)

#### web/config.py (0%) 🔴
```
未覆盖行：5-36 (全部)
```

**问题**:
- Web 配置类未测试

**测试需求**: 5 个测试用例

#### web/main.py (0%) 🔴
```
未覆盖行：5-104 (全部)
```

**问题**:
- FastAPI 应用创建未测试
- 路由注册未测试
- 中间件配置未测试

**测试需求**: 8 个测试用例

#### web/api/agent.py (16%)
```
未覆盖行：50-130, 149-212, 232-248, 254-259, 265-282, 
         294-443, 448-471, 477-483, 489-495, 503-552, 
         569, 583-596, 609-617, 629-661, 672-702
```

**问题**:
- AI 提取 API 未测试
- AI 生成 API 未测试
- 预备题目 API 未测试
- 错误处理未测试

**测试需求**: 35 个测试用例

#### web/tests/test_api.py (0%) 🔴
```
未覆盖行：5-99 (全部)
```

**问题**:
- 测试文件存在但无法导入

**测试需求**: 修复导入问题 + 15 个测试用例

---

## 二、测试用例需求统计

### 按模块分类

| 模块 | 当前用例 | 需补充 | 总计 | 优先级 |
|------|----------|--------|------|--------|
| agent/config | 0 | 15 | 15 | P1 |
| agent/extractors | 0 | 38 | 38 | P1 |
| agent/generators | 0 | 8 | 8 | P2 |
| agent/services | 0 | 18 | 18 | P1 |
| core/database | 6 | 49 | 55 | P0 |
| core/services | 6 | 61 | 67 | P0 |
| core/exceptions | 0 | 8 | 8 | P2 |
| web/config | 0 | 5 | 5 | P2 |
| web/main | 0 | 8 | 8 | P1 |
| web/api | 0 | 50 | 50 | P0 |
| **总计** | **12** | **260** | **272** | - |

### 按优先级分类

| 优先级 | 测试用例数 | 预计工时 | 覆盖模块 |
|--------|------------|----------|----------|
| **P0** | 172 | 3-4 天 | core/*, web/api/* |
| **P1** | 79 | 2-3 天 | agent/*, web/main |
| **P2** | 21 | 1 天 | exceptions, generators |
| **总计** | **272** | **6-8 天** | - |

---

## 三、技术方案

### 3.1 测试框架配置

#### pytest.ini 配置
```ini
[pytest]
testpaths = tests core/tests web/tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --cov=core
    --cov=web
    --cov=agent
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
```

#### 测试目录结构
```
tests/
├── __init__.py
├── conftest.py              # 共享 fixtures
├── unit/                    # 单元测试
│   ├── test_models.py
│   ├── test_exceptions.py
│   ├── test_services/
│   │   ├── test_category_service.py
│   │   ├── test_tag_service.py
│   │   ├── test_question_service.py
│   │   └── test_vector_index.py
│   └── test_repositories/
│       ├── test_category_repo.py
│       ├── test_tag_repo.py
│       └── test_question_repo.py
├── integration/             # 集成测试
│   ├── test_workflow.py
│   ├── test_api_workflow.py
│   └── test_ai_workflow.py
├── api/                     # API 测试
│   ├── test_agent_api.py
│   ├── test_categories_api.py
│   ├── test_tags_api.py
│   └── test_questions_api.py
└── fixtures/                # 测试数据
    ├── categories.json
    ├── tags.json
    └── questions.json

agent/tests/
├── __init__.py
├── test_config.py
├── test_extractors/
│   ├── test_document_extractor.py
│   └── test_image_extractor.py
├── test_generators/
│   └── test_explanation_generator.py
└── test_services/
    ├── test_embedding_service.py
    └── test_model_client.py

web/tests/
├── __init__.py
├── test_main.py
├── test_config.py
└── test_api/
    ├── test_agent.py
    ├── test_categories.py
    ├── test_tags.py
    └── test_questions.py
```

### 3.2 测试工具链

#### 依赖安装
```bash
# 测试框架
uv pip install pytest pytest-cov pytest-asyncio

# Mock 支持
uv pip install pytest-mock

# HTTP 测试
uv pip install httpx respx

# 数据库测试
uv pip install pytest-sqlalchemy
```

#### 测试辅助工具
```python
# tests/conftest.py
import pytest
from core.database.connection import DatabaseConnection
from core.services.category_service import CategoryService
from core.services.question_service import QuestionService
from core.services.tag_service import TagService

@pytest.fixture
def db_connection():
    """数据库连接 fixture"""
    db = DatabaseConnection()
    yield db
    db.close_connection()

@pytest.fixture
def category_service(db_connection):
    """分类服务 fixture"""
    from core.database.repositories import CategoryRepository
    return CategoryService(CategoryRepository())

@pytest.fixture
def question_service(db_connection):
    """题目服务 fixture"""
    from core.database.repositories import QuestionRepository, CategoryRepository, TagRepository
    return QuestionService(
        QuestionRepository(),
        CategoryRepository(),
        TagRepository()
    )

@pytest.fixture
def tag_service(db_connection):
    """标签服务 fixture"""
    from core.database.repositories import TagRepository
    return TagService(TagRepository())
```

### 3.3 测试实现策略

#### 单元测试 (60% 覆盖率)
- 测试所有公共方法
- 测试边界条件
- 测试异常场景
- Mock 外部依赖

#### 集成测试 (20% 覆盖率)
- 测试完整工作流
- 测试数据库交互
- 测试服务间协作

#### API 测试 (20% 覆盖率)
- 测试所有 API 端点
- 测试请求验证
- 测试响应格式
- 测试错误处理

---

## 四、实施计划

### 阶段 1: Core 模块 (P0) - 2-3 天

**目标**: 50% → 85% (+35%)

#### Day 1: Repository 层测试
- [ ] test_category_repo.py (15 用例)
- [ ] test_tag_repo.py (12 用例)
- [ ] test_question_repo.py (22 用例)

#### Day 2: Service 层测试
- [ ] test_category_service.py (8 用例)
- [ ] test_tag_service.py (10 用例)
- [ ] test_question_service.py (25 用例)

#### Day 3: 向量索引与异常
- [ ] test_vector_index.py (18 用例)
- [ ] test_exceptions.py (8 用例)
- [ ] 集成测试补充 (10 用例)

### 阶段 2: Web 模块 (P0) - 2-3 天

**目标**: 12% → 80% (+68%)

#### Day 4: Web 基础测试
- [ ] test_main.py (8 用例)
- [ ] test_config.py (5 用例)
- [ ] 修复 test_api.py 导入问题

#### Day 5-6: API 测试
- [ ] test_categories_api.py (12 用例)
- [ ] test_tags_api.py (10 用例)
- [ ] test_questions_api.py (15 用例)
- [ ] test_agent_api.py (13 用例)

### 阶段 3: Agent 模块 (P1) - 2-3 天

**目标**: 29% → 75% (+46%)

#### Day 7: 配置与提取器
- [ ] test_config.py (15 用例)
- [ ] test_document_extractor.py (20 用例)
- [ ] test_image_extractor.py (18 用例)

#### Day 8: 生成器与服务
- [ ] test_explanation_generator.py (8 用例)
- [ ] test_embedding_service.py (6 用例)
- [ ] test_model_client.py (12 用例)

### 阶段 4: 整合与优化 (P2) - 1 天

**目标**: 确保覆盖率稳定在 80%+

- [ ] 运行完整测试套件
- [ ] 生成覆盖率报告
- [ ] 修复失败测试
- [ ] 优化测试性能
- [ ] 文档化测试规范

---

## 五、质量要求

### 测试代码规范

1. **命名规范**
   - 测试文件：`test_*.py`
   - 测试类：`Test*`
   - 测试方法：`test_*`
   - 测试描述：使用中文或英文清晰描述测试目的

2. **测试结构**
   ```python
   def test_xxx():
       # Given - 准备测试数据
       # When - 执行测试操作
       # Then - 验证测试结果
   ```

3. **断言要求**
   - 使用 `assert` 语句
   - 提供清晰的错误消息
   - 避免多个断言在一个测试中

4. **Fixture 使用**
   - 使用 `@pytest.fixture` 管理测试资源
   - 在 `conftest.py` 中定义共享 fixture
   - 使用 `yield` 进行清理

### 覆盖率要求

| 指标 | 要求 | 检查方式 |
|------|------|----------|
| 行覆盖率 | ≥ 80% | pytest-cov |
| 分支覆盖率 | ≥ 70% | pytest-cov --cov-branch |
| 关键模块 | ≥ 90% | core/services/*, web/api/* |
| 测试通过率 | 100% | pytest 执行结果 |

---

## 六、风险与缓解

### 风险 1: AI 服务依赖
- **问题**: Embedding 和 LLM 调用需要真实 API
- **缓解**: 使用 Mock 模拟 API 响应

### 风险 2: 数据库状态
- **问题**: 测试间数据库状态污染
- **缓解**: 每个测试使用独立数据库或事务回滚

### 风险 3: 测试执行时间
- **问题**: 测试过多导致执行时间长
- **缓解**: 并行执行测试，优化慢测试

### 风险 4: 维护成本
- **问题**: 测试代码维护成本高
- **缓解**: 编写可维护的测试，使用 fixture 复用

---

## 七、验收标准

### 必须满足

- [ ] 总体覆盖率 ≥ 80%
- [ ] 所有测试通过 (100%)
- [ ] 关键模块覆盖率 ≥ 90%
- [ ] 测试执行时间 < 5 分钟

### 建议满足

- [ ] 分支覆盖率 ≥ 70%
- [ ] 集成测试覆盖核心工作流
- [ ] API 测试覆盖所有端点
- [ ] 测试文档完整

---

## 八、交付物

1. **测试代码**
   - 272 个新增测试用例
   - 完整的测试目录结构
   - 共享 fixture 和工具类

2. **文档**
   - 测试覆盖率报告 (HTML + XML)
   - 测试用例清单
   - 测试规范文档

3. **配置**
   - pytest.ini 配置
   - CI/CD 集成配置
   - 预提交钩子配置

---

**下一步**: 
- [ ] 转交 Developer 实施测试用例编写
- [ ] 按优先级分阶段执行
- [ ] 每日检查覆盖率进度

---

*报告生成时间*: 2026-03-19 15:35  
*报告人*: Architect (nanobot)  
*当前覆盖率*: 41%  
*目标覆盖率*: 80%
