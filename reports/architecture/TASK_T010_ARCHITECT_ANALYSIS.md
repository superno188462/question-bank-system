# 任务 T010 - 测试覆盖率提升技术方案 (46% → 90%)

**任务编号**: T010  
**任务名称**: 测试覆盖率提升至 90%  
**执行时间**: 2026-03-19 18:45  
**执行人**: Architect (nanobot)  
**当前覆盖率**: 46%  
**目标覆盖率**: 90%  
**差距**: +44%

---

## 执行摘要

### 覆盖率现状分析

| 模块 | 语句数 | 未覆盖 | 覆盖率 | 状态 | 优先级 |
|------|--------|--------|--------|------|--------|
| **总体** | 4234 | 2267 | **46%** | 🔴 严重不足 | P0 |
| **web/** | 660 | 610 | **8%** | 🔴 严重不足 | P0 |
| **agent/tests/** | 1089 | 1089 | **0%** | 🔴 未执行 | P0 |
| **agent/** (不含测试) | 452 | 315 | **30%** | 🔴 严重不足 | P1 |
| **core/** | 1777 | 250 | **86%** | ✅ 良好 | P2 |

### 关键发现

1. **web/ 模块覆盖率极低 (8%)**
   - web/main.py: 0% (51 行未覆盖)
   - web/config.py: 0% (17 行未覆盖)
   - web/api/agent.py: 16% (262 行未覆盖)
   - web/tests/ 测试文件存在但无法执行 (导入错误)

2. **agent/tests/ 测试文件无法执行 (0%)**
   - 5 个测试文件，1089 行代码
   - 存在导入错误，需要修复
   - 测试文件已创建但未集成到测试套件

3. **core/ 模块覆盖率良好 (86%)**
   - 大部分核心服务已测试
   - vector_index.py 覆盖率较低 (37%)
   - 少量边界情况未覆盖

### 覆盖率目标分解

| 模块 | 当前 | 目标 | 需提升 | 工作量估算 |
|------|------|------|--------|------------|
| **总体** | 46% | 90% | +44% | 10-15 天 |
| **web/** | 8% | 90% | +82% | 5-7 天 |
| **agent/tests/** | 0% | 90% | +90% | 3-4 天 |
| **agent/** | 30% | 90% | +60% | 2-3 天 |
| **core/** | 86% | 95% | +9% | 1-2 天 |

---

## 一、详细覆盖率分析

### 1.1 Web 模块 (8% - 最优先)

#### web/main.py (0%) 🔴
```python
未覆盖行：5-104 (全部)
```

**问题分析**:
- FastAPI 应用创建函数未测试
- 路由注册未测试
- 中间件配置未测试
- 静态文件挂载未测试

**测试需求**: 12 个测试用例
- test_create_web_app (应用创建)
- test_cors_middleware (CORS 配置)
- test_static_files (静态文件)
- test_templates (模板配置)
- test_root_endpoint (根路由)
- test_api_routes (API 路由注册)
- test_database_migration (数据库迁移)
- test_error_handlers (错误处理)
- test_startup_events (启动事件)
- test_shutdown_events (关闭事件)
- test_health_check (健康检查)
- test_docs_endpoint (文档端点)

**预计工时**: 0.5 天

#### web/config.py (0%) 🔴
```python
未覆盖行：5-36 (全部)
```

**问题分析**:
- WebConfig 类未测试
- 配置加载未测试
- 环境变量覆盖未测试

**测试需求**: 8 个测试用例
- test_web_config_init (初始化)
- test_web_config_defaults (默认值)
- test_web_config_env_override (环境变量覆盖)
- test_web_config_database_url (数据库 URL)
- test_web_config_debug_mode (调试模式)
- test_web_config_cors_settings (CORS 设置)
- test_web_config_static_files (静态文件配置)
- test_web_config_templates (模板配置)

**预计工时**: 0.25 天

#### web/api/agent.py (16%) 🔴
```python
未覆盖行：50-130, 149-212, 232-248, 254-259, 265-282, 
         294-443, 448-471, 477-483, 489-495, 503-552, 
         569, 583-596, 609-617, 629-661, 672-702
```

**问题分析**:
- AI 提取 API 端点未测试
- 预备题目 API 未测试
- 批量操作 API 未测试
- 错误处理未测试
- 文件上传未测试

**测试需求**: 45 个测试用例

**API 端点测试**:
1. POST /api/agent/extract/image (图片提取) - 8 用例
2. POST /api/agent/extract/document (文档提取) - 8 用例
3. POST /api/agent/extract/batch (批量提取) - 6 用例
4. POST /api/agent/staging/approve (预备题目入库) - 6 用例
5. GET /api/agent/staging/list (预备题目列表) - 4 用例
6. DELETE /api/agent/staging/delete (预备题目删除) - 4 用例
7. POST /api/agent/generate/explanation (解析生成) - 5 用例
8. GET /api/agent/config (配置获取) - 2 用例
9. PUT /api/agent/config (配置更新) - 2 用例

**预计工时**: 2-3 天

#### web/tests/test_api.py (导入错误) 🔴
```python
未覆盖行：5-99 (全部)
```

**问题分析**:
- 导入路径错误：`from tests.test_api import ...`
- 应该是：`from web.api import ...`

**修复方案**:
```python
# 错误
from tests.test_api import app, client

# 正确
from web.main import create_web_app
from fastapi.testclient import TestClient
```

**预计工时**: 0.25 天

#### web/tests/test_agent_api.py (导入错误) 🔴
```python
未覆盖行：5-474 (全部)
```

**问题分析**:
- 导入路径错误
- 测试夹具 (fixtures) 未定义

**修复方案**:
- 修复导入路径
- 添加 conftest.py 提供共享 fixtures
- 配置测试数据库

**预计工时**: 0.5 天

---

### 1.2 Agent 测试模块 (0% - 高优先级)

#### agent/tests/test_document_extractor.py (0%) 🔴
```python
未覆盖行：5-534 (全部)
```

**问题分析**:
- 测试文件存在但未执行
- 可能存在导入错误
- 需要添加到 pytest 配置

**测试需求**: 35 个测试用例
- PDF 文档提取测试 - 10 用例
- Word 文档提取测试 - 10 用例
- 文本文件提取测试 - 8 用例
- Markdown 文件提取测试 - 5 用例
- 错误处理测试 - 2 用例

**预计工时**: 1.5 天

#### agent/tests/test_image_extractor.py (0%) 🔴
```python
未覆盖行：5-559 (全部)
```

**问题分析**:
- 测试文件存在但未执行
- 需要 Mock AI API 调用

**测试需求**: 38 个测试用例
- 图片题目提取测试 - 15 用例
- OCR 功能测试 - 10 用例
- 多图片批量处理测试 - 8 用例
- 错误处理测试 - 5 用例

**预计工时**: 1.5 天

#### agent/tests/test_explanation_generator.py (0%) 🔴
```python
未覆盖行：5-429 (全部)
```

**测试需求**: 22 个测试用例
- 解析生成测试 - 10 用例
- 批量生成测试 - 6 用例
- 错误处理测试 - 4 用例
- 边界条件测试 - 2 用例

**预计工时**: 1 天

#### agent/tests/test_embedding_service.py (0%) 🔴
```python
未覆盖行：5-368 (全部)
```

**测试需求**: 20 个测试用例
- 向量化测试 - 8 用例
- 批量向量化测试 - 6 用例
- 相似度计算测试 - 4 用例
- 错误处理测试 - 2 用例

**预计工时**: 1 天

#### agent/tests/test_model_client.py (0%) 🔴
```python
未覆盖行：5-357 (全部)
```

**测试需求**: 25 个测试用例
- LLM 调用测试 - 10 用例
- Vision 模型调用测试 - 8 用例
- Embedding 调用测试 - 5 用例
- 错误处理测试 - 2 用例

**预计工时**: 1 天

---

### 1.3 Agent 模块 (30% - 中优先级)

#### agent/config.py (56%) 🟡
```python
未覆盖行：41-42, 52-59, 66, 97-99, 112-125, 133-134, 
         140-141, 147-148, 156-157, 163-164, 170-171, 
         179-180, 186-187, 193-194, 202-203, 209-210, 
         216-217, 223-224, 230-231, 239-241, 247-249, 
         256-260, 265, 272, 281, 290, 299-307
```

**测试需求**: 18 个测试用例
- 配置加载测试 - 6 用例
- 配置缓存测试 - 4 用例
- 配置刷新测试 - 4 用例
- 环境变量覆盖测试 - 4 用例

**预计工时**: 0.75 天

#### agent/extractors/document_extractor.py (16%) 🔴
**测试需求**: 25 个测试用例
**预计工时**: 1 天

#### agent/extractors/image_extractor.py (16%) 🔴
**测试需求**: 25 个测试用例
**预计工时**: 1 天

#### agent/services/embedding_service.py (69%) 🟡
**测试需求**: 8 个测试用例
**预计工时**: 0.5 天

#### agent/services/model_client.py (31%) 🔴
**测试需求**: 15 个测试用例
**预计工时**: 0.75 天

---

### 1.4 Core 模块 (86% - 低优先级)

#### core/services/vector_index.py (37%) 🔴
```python
未覆盖行：57-60, 94-112, 125-138, 142-151, 173-223, 
         227-241, 257, 266, 283-317
```

**测试需求**: 20 个测试用例
- 向量相似度搜索测试 - 8 用例
- 批量向量化测试 - 6 用例
- 重建向量测试 - 4 用例
- 错误处理测试 - 2 用例

**预计工时**: 1 天

#### core/services/question_service.py (95%) ✅
```python
未覆盖行：53-55, 70, 81-85, 167
```

**测试需求**: 3 个测试用例
- Embedding 初始化测试 - 2 用例
- 边界条件测试 - 1 用例

**预计工时**: 0.25 天

#### core/database/connection.py (86%) 🟡
```python
未覆盖行：28-30, 56, 75-77, 159-164
```

**测试需求**: 5 个测试用例
- 事务回滚测试 - 2 用例
- 连接关闭测试 - 2 用例
- 错误处理测试 - 1 用例

**预计工时**: 0.25 天

---

## 二、并行执行判断

### 并行可行性分析

**✅ 支持并行**: 是

**理由**:
1. 测试文件相互独立，无共享状态
2. 使用 pytest-xdist 可并行执行测试
3. 数据库使用独立测试数据库
4. AI API 调用已 Mock，无外部依赖竞争

### 并行策略

#### 方案 1: 按模块并行 (推荐)
```
并行任务 1: web/ 模块测试 (5-7 天)
并行任务 2: agent/tests/ 测试执行 (3-4 天)
并行任务 3: agent/ 模块测试 (2-3 天)
并行任务 4: core/ 模块补充测试 (1-2 天)
```

**优点**:
- 各模块独立，无依赖冲突
- 可分配给不同开发者
- 风险隔离

**缺点**:
- 需要协调合并
- 可能需要解决冲突

#### 方案 2: 按测试类型并行
```
并行任务 1: 单元测试 (所有模块)
并行任务 2: 集成测试 (所有模块)
并行任务 3: API 测试 (所有模块)
```

**优点**:
- 测试类型清晰
- 便于管理

**缺点**:
- 模块间可能有依赖
- 协调成本较高

#### 方案 3: pytest-xdist 自动并行
```bash
pytest -n auto --cov=core --cov=web --cov=agent
```

**优点**:
- 配置简单
- 自动负载均衡
- 无需代码修改

**缺点**:
- 仅加速测试执行
- 不加速测试编写

### 推荐方案

**采用方案 1 + 方案 3 组合**:
1. 开发阶段：按模块并行开发测试
2. 执行阶段：使用 pytest-xdist 并行执行

**配置示例**:
```ini
# pytest.ini
[pytest]
addopts = -n auto --cov=core --cov=web --cov=agent --cov-report=term-missing
```

---

## 三、技术方案

### 3.1 测试框架配置

#### pytest.ini (更新)
```ini
[pytest]
testpaths = tests core/tests web/tests agent/tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    -n auto
    --cov=core
    --cov=web
    --cov=agent
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=90
    --tb=short
```

#### conftest.py (共享夹具)
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from web.main import create_web_app
from core.database.connection import DatabaseConnection

@pytest.fixture(scope="session")
def test_db():
    """测试数据库夹具"""
    db = DatabaseConnection()
    yield db
    db.close_connection()

@pytest.fixture
def client(test_db):
    """FastAPI 测试客户端"""
    app = create_web_app()
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_llm_response():
    """Mock LLM API 响应"""
    return {
        "choices": [{
            "message": {
                "content": "这是 mock 的解析内容"
            }
        }]
    }
```

### 3.2 测试工具链

#### 依赖安装
```bash
# 测试框架
uv pip install pytest pytest-cov pytest-asyncio pytest-xdist

# Mock 支持
uv pip install pytest-mock

# HTTP 测试
uv pip install httpx respx

# 数据库测试
uv pip install pytest-sqlalchemy
```

### 3.3 测试目录结构

```
tests/
├── __init__.py
├── conftest.py              # 共享 fixtures
├── unit/                    # 单元测试
│   └── ...
├── integration/             # 集成测试
│   ├── test_workflow.py
│   └── test_api_workflow.py
└── fixtures/                # 测试数据
    └── ...

web/tests/
├── __init__.py
├── conftest.py              # Web 测试 fixtures
├── test_main.py             # ✅ 新增
├── test_config.py           # ✅ 新增
└── test_api/
    ├── test_agent_api.py    # 🔧 修复导入
    ├── test_api.py          # 🔧 修复导入
    ├── test_categories.py
    ├── test_tags.py
    └── test_questions.py

agent/tests/
├── __init__.py
├── conftest.py              # Agent 测试 fixtures
├── test_config.py           # 🔧 修复导入
├── test_document_extractor.py  # 🔧 修复导入
├── test_image_extractor.py     # 🔧 修复导入
├── test_explanation_generator.py  # 🔧 修复导入
├── test_embedding_service.py    # 🔧 修复导入
└── test_model_client.py         # 🔧 修复导入
```

---

## 四、实施计划

### 阶段 1: Web 模块测试 (P0) - 5-7 天

**目标**: 8% → 90% (+82%)

#### Day 1-2: Web 基础测试
- [ ] web/tests/test_main.py (12 用例)
- [ ] web/tests/test_config.py (8 用例)
- [ ] 修复 web/tests/conftest.py

#### Day 3-5: API 测试
- [ ] web/tests/test_api/test_agent_api.py (45 用例)
- [ ] web/tests/test_api/test_api.py (修复导入，15 用例)
- [ ] web/tests/test_api/test_categories.py (12 用例)
- [ ] web/tests/test_api/test_tags.py (10 用例)
- [ ] web/tests/test_api/test_questions.py (15 用例)

**阶段验收**:
- Web 模块覆盖率 ≥ 90%
- 所有 API 端点测试通过
- 测试执行时间 < 2 分钟

### 阶段 2: Agent 测试模块 (P0) - 3-4 天

**目标**: 0% → 90% (+90%)

#### Day 6-7: 提取器测试
- [ ] agent/tests/test_document_extractor.py (修复导入，35 用例)
- [ ] agent/tests/test_image_extractor.py (修复导入，38 用例)

#### Day 8-9: 服务测试
- [ ] agent/tests/test_explanation_generator.py (修复导入，22 用例)
- [ ] agent/tests/test_embedding_service.py (修复导入，20 用例)
- [ ] agent/tests/test_model_client.py (修复导入，25 用例)

**阶段验收**:
- Agent 测试模块覆盖率 ≥ 90%
- 所有测试文件可执行
- Mock 配置正确

### 阶段 3: Agent 模块补充 (P1) - 2-3 天

**目标**: 30% → 90% (+60%)

#### Day 10-11: 配置与提取器
- [ ] agent/tests/test_config.py (18 用例)
- [ ] agent/extractors/ 补充测试 (25+25 用例)

#### Day 12: 服务层
- [ ] agent/services/ 补充测试 (8+15 用例)

**阶段验收**:
- Agent 模块覆盖率 ≥ 90%
- 配置加载测试完整
- 提取器测试完整

### 阶段 4: Core 模块补充 (P2) - 1-2 天

**目标**: 86% → 95% (+9%)

#### Day 13-14: 补充测试
- [ ] core/tests/test_vector_index.py (20 用例)
- [ ] core/tests/test_question_service.py (3 用例)
- [ ] core/tests/test_connection.py (5 用例)

**阶段验收**:
- Core 模块覆盖率 ≥ 95%
- 向量索引测试完整
- 边界条件覆盖

### 阶段 5: 整合与优化 (P1) - 1-2 天

**目标**: 确保总体覆盖率 ≥ 90%

#### Day 15-16: 整合优化
- [ ] 运行完整测试套件
- [ ] 生成覆盖率报告
- [ ] 修复失败测试
- [ ] 优化测试性能
- [ ] 配置 CI/CD 集成

**阶段验收**:
- 总体覆盖率 ≥ 90%
- 测试执行时间 < 5 分钟
- CI/CD 配置完成

---

## 五、风险与缓解

### 风险 1: 测试文件导入错误
- **影响**: 高 (1089 行测试代码无法执行)
- **概率**: 高 (已确认存在导入错误)
- **缓解**: 
  - 优先修复导入路径
  - 统一导入规范
  - 添加导入测试

### 风险 2: AI API Mock 复杂
- **影响**: 中 (测试依赖外部 API)
- **概率**: 中
- **缓解**:
  - 使用 pytest-mock
  - 创建 Mock 工具类
  - 录制真实响应作为 fixture

### 风险 3: 测试执行时间长
- **影响**: 中 (影响开发效率)
- **概率**: 中
- **缓解**:
  - 使用 pytest-xdist 并行
  - 优化慢测试
  - 分离单元测试和集成测试

### 风险 4: 覆盖率目标过高
- **影响**: 高 (90% 可能难以达到)
- **概率**: 低
- **缓解**:
  - 优先保证关键模块
  - 允许部分代码豁免 (如配置类)
  - 关注测试质量而非数量

---

## 六、质量要求

### 测试代码规范

1. **命名规范**
   - 测试文件：`test_*.py`
   - 测试类：`Test*`
   - 测试方法：`test_*`
   - 测试描述：清晰描述测试目的

2. **测试结构 (Given-When-Then)**
   ```python
   def test_extract_pdf_document():
       # Given - 准备测试数据
       extractor = DocumentExtractor()
       test_pdf = "test_data/sample.pdf"
       
       # When - 执行提取
       result = extractor.extract(test_pdf)
       
       # Then - 验证结果
       assert result is not None
       assert len(result.questions) > 0
   ```

3. **Mock 使用规范**
   ```python
   def test_llm_call_with_mock(mocker):
       # Mock LLM API
       mock_response = {"choices": [{"message": {"content": "test"}}]}
       mocker.patch('agent.services.model_client.openai.ChatCompletion.create', 
                   return_value=mock_response)
       
       # 执行测试
       result = model_client.call_llm("test prompt")
       
       # 验证
       assert result == "test"
   ```

### 覆盖率要求

| 指标 | 要求 | 检查方式 |
|------|------|----------|
| 行覆盖率 | ≥ 90% | pytest-cov |
| 分支覆盖率 | ≥ 80% | pytest-cov --cov-branch |
| 关键模块 | ≥ 95% | web/api/*, core/services/* |
| 测试通过率 | 100% | pytest 执行结果 |
| 测试执行时间 | < 5 分钟 | pytest 输出 |

---

## 七、验收标准

### 必须满足 (P0)

- [ ] 总体覆盖率 ≥ 90%
- [ ] 所有测试通过 (100%)
- [ ] web/ 模块覆盖率 ≥ 90%
- [ ] agent/tests/ 可执行且覆盖率 ≥ 90%
- [ ] 测试执行时间 < 5 分钟
- [ ] CI/CD 集成完成

### 建议满足 (P1)

- [ ] 分支覆盖率 ≥ 80%
- [ ] 集成测试覆盖核心工作流
- [ ] API 测试覆盖所有端点
- [ ] 测试文档完整
- [ ] Mock 配置完善

### 可选优化 (P2)

- [ ] 核心模块覆盖率 ≥ 95%
- [ ] 添加性能测试
- [ ] 添加安全测试
- [ ] 添加负载测试

---

## 八、交付物

### 测试代码
- 200+ 新增测试用例
- 修复 5 个导入错误的测试文件
- 完整的测试目录结构
- 共享 fixture 和工具类

### 文档
- 测试覆盖率报告 (HTML + XML)
- 测试用例清单
- 测试规范文档
- Mock 配置文档

### 配置
- pytest.ini 配置
- CI/CD 集成配置
- Pre-commit 钩子配置
- 覆盖率检查脚本

---

## 九、并行执行建议

### 推荐并行策略

**任务拆分**:
```
并行任务 A: Web 模块测试 (Tester A)
  - web/tests/test_main.py
  - web/tests/test_config.py
  - web/tests/test_api/test_agent_api.py

并行任务 B: Agent 测试修复 (Tester B)
  - agent/tests/test_document_extractor.py
  - agent/tests/test_image_extractor.py
  - agent/tests/test_explanation_generator.py

并行任务 C: Agent 服务测试 (Tester C)
  - agent/tests/test_embedding_service.py
  - agent/tests/test_model_client.py
  - agent/tests/test_config.py

并行任务 D: Core 补充测试 (Tester D)
  - core/tests/test_vector_index.py
  - core/tests/test_connection.py
```

**合并策略**:
- 每日合并到 develop 分支
- 解决冲突后运行完整测试
- 检查覆盖率变化

---

**下一步**:
- [ ] 转交 Test-Analyst 设计测试策略
- [ ] 转交 Tester 开发测试脚本
- [ ] 转交 Developer 修复代码 + 补充测试
- [ ] 转交 Reviewer 进行全面审查

---

*报告生成时间*: 2026-03-19 18:50  
*报告人*: Architect (nanobot)  
*当前覆盖率*: 46%  
*目标覆盖率*: 90%  
*预计完成时间*: 10-15 天
