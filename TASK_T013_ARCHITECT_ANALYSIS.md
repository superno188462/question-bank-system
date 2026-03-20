# 任务 T013 - 低覆盖率模块单元测试补充方案 (82% → 90%)

**任务编号**: T013  
**任务名称**: 补充低覆盖率模块单元测试，完成 90% 覆盖率目标  
**执行时间**: 2026-03-19 23:20  
**执行人**: Architect (nanobot)  
**当前覆盖率**: 82%  
**目标覆盖率**: 90%  
**差距**: +8%  
**失败测试**: 0 个 ✅ (317 passed)

---

## 执行摘要

### T012 完成情况

✅ **所有测试通过**: 317 passed, 2 skipped  
✅ **覆盖率提升**: 80% → 82% (+2%)  
✅ **失败测试修复**: 8 个失败 + 1 个错误 → 0 个

### 当前覆盖率状态

| 模块 | 语句数 | 未覆盖 | 覆盖率 | 状态 | 优先级 |
|------|--------|--------|--------|------|--------|
| **总体** | 5042 | 915 | **82%** | 🟡 需改进 | P0 |
| **core/database/repositories.py** | 380 | 193 | **49%** | 🔴 严重不足 | P0 |
| **web/api/agent.py** | 312 | 262 | **16%** | 🔴 严重不足 | P0 |
| **shared/config.py** | 28 | 5 | **82%** | 🟡 需改进 | P1 |
| **core/database/connection.py** | 71 | 10 | **86%** | 🟡 需改进 | P1 |
| **agent/config.py** | 162 | 31 | **81%** | 🟡 需改进 | P2 |
| **agent/extractors/image_extractor.py** | 102 | 12 | **88%** | 🟡 需改进 | P2 |

### 覆盖率目标分解

| 模块 | 当前 | 目标 | 需提升 | 测试用例 | 预计工时 |
|------|------|------|--------|----------|----------|
| **总体** | 82% | 90% | +8% | 80 个 | 4-5 天 |
| **repositories.py** | 49% | 90% | +41% | 45 个 | 2-3 天 |
| **web/api/agent.py** | 16% | 90% | +74% | 30 个 | 2 天 |
| **shared/config.py** | 82% | 90% | +8% | 4 个 | 0.25 天 |
| **connection.py** | 86% | 90% | +4% | 5 个 | 0.25 天 |
| **agent/config.py** | 81% | 90% | +9% | 5 个 | 0.5 天 |

---

## 一、低覆盖率模块详细分析

### 1.1 core/database/repositories.py (49% → 90%)

**未覆盖代码**: 193 行 (50%)

#### 未覆盖区域分析

| 类/方法 | 未覆盖行数 | 复杂度 | 测试需求 |
|---------|------------|--------|----------|
| **CategoryRepository** | 30 | 中 | 8 个测试 |
| - get_by_name() | 8 | 低 | 2 个测试 |
| - get_by_path() | 8 | 低 | 2 个测试 |
| - search() | 14 | 中 | 4 个测试 |
| **TagRepository** | 25 | 中 | 6 个测试 |
| - get_by_names() | 10 | 低 | 2 个测试 |
| - search() | 15 | 中 | 4 个测试 |
| **QuestionRepository** | 80 | 高 | 20 个测试 |
| - search() | 30 | 高 | 8 个测试 |
| - get_by_category() | 15 | 中 | 4 个测试 |
| - get_by_tag() | 15 | 中 | 4 个测试 |
| - batch_create() | 20 | 高 | 4 个测试 |
| **StagingQuestionRepository** | 58 | 中 | 14 个测试 |
| - get_pending() | 15 | 低 | 4 个测试 |
| - get_approved() | 15 | 低 | 4 个测试 |
| - approve() | 14 | 中 | 3 个测试 |
| - reject() | 14 | 中 | 3 个测试 |

**测试策略**:
- 边界条件测试：空值、最大值、特殊字符
- 错误处理测试：外键约束、唯一约束
- 复杂查询测试：多条件组合、排序、分页

**预计工时**: 2-3 天

---

### 1.2 web/api/agent.py (16% → 90%)

**未覆盖代码**: 262 行 (84%)

#### 未覆盖区域分析

| API 端点 | 未覆盖行数 | 复杂度 | 测试需求 |
|----------|------------|--------|----------|
| **POST /api/agent/extract/image** | 80 | 高 | 10 个测试 |
| - 图片上传 | 20 | 中 | 3 个测试 |
| - 提取逻辑 | 40 | 高 | 5 个测试 |
| - 错误处理 | 20 | 中 | 2 个测试 |
| **POST /api/agent/extract/document** | 60 | 高 | 8 个测试 |
| - 文档上传 | 15 | 中 | 2 个测试 |
| - 提取逻辑 | 35 | 高 | 5 个测试 |
| - 错误处理 | 10 | 中 | 1 个测试 |
| **POST /api/agent/staging/approve** | 40 | 中 | 6 个测试 |
| - 审核通过 | 20 | 中 | 3 个测试 |
| - 审核失败 | 20 | 中 | 3 个测试 |
| **GET /api/agent/staging/list** | 30 | 低 | 4 个测试 |
| - 列表查询 | 20 | 低 | 3 个测试 |
| - 分页 | 10 | 低 | 1 个测试 |
| **其他端点** | 52 | 中 | 6 个测试 |

**测试策略**:
- API 端点测试：使用 TestClient
- 请求验证：参数校验、文件类型校验
- 响应验证：状态码、返回数据结构
- Mock AI 服务：避免真实 API 调用

**预计工时**: 2 天

---

### 1.3 shared/config.py (82% → 90%)

**未覆盖代码**: 5 行 (18%)

#### 未覆盖区域

```python
# 行 32, 37, 41, 45, 55
def validate(self):
    """验证配置"""
    if not self.llm_api_key:  # 行 32
        raise ValueError("LLM API key is required")
    if not self.vision_api_key:  # 行 37
        raise ValueError("Vision API key is required")
    # ... 更多验证
```

**测试需求**: 4 个测试用例
- test_validate_missing_llm_key
- test_validate_missing_vision_key
- test_validate_success
- test_validate_partial_config

**预计工时**: 0.25 天

---

### 1.4 core/database/connection.py (86% → 90%)

**未覆盖代码**: 10 行 (14%)

#### 未覆盖区域

```python
# 行 28-30, 56, 75-77, 159-164
def rollback_transaction(self):
    """回滚事务"""
    # ...

def close_connection(self):
    """关闭连接"""
    # ...

# 错误处理逻辑
```

**测试需求**: 5 个测试用例
- test_rollback_transaction
- test_rollback_without_transaction
- test_close_connection
- test_close_already_closed
- test_connection_error_handling

**预计工时**: 0.25 天

---

### 1.5 agent/config.py (81% → 90%)

**未覆盖代码**: 31 行 (19%)

#### 未覆盖区域

| 方法 | 未覆盖行数 | 测试需求 |
|------|------------|----------|
| load_config() | 14 | 3 个测试 |
| refresh() | 8 | 2 个测试 |
| get_embedding_config() | 9 | 2 个测试 |

**测试需求**: 7 个测试用例

**预计工时**: 0.5 天

---

## 二、技术方案

### 2.1 Repository 层测试方案

#### 测试模板

```python
# core/tests/test_category_repository.py
class TestCategoryRepositoryGetByName:
    """测试 CategoryRepository.get_by_name() 方法"""
    
    @pytest.fixture
    def repo(self, db_connection):
        return CategoryRepository(db_connection)
    
    def test_get_by_name_exists(self, repo):
        """测试获取存在的分类"""
        # Given
        category = repo.create(name="测试分类", path="/test")
        
        # When
        result = repo.get_by_name("测试分类")
        
        # Then
        assert result is not None
        assert result.name == "测试分类"
        assert result.id == category.id
    
    def test_get_by_name_not_exists(self, repo):
        """测试获取不存在的分类"""
        # When
        result = repo.get_by_name("不存在的分类")
        
        # Then
        assert result is None
    
    def test_get_by_name_case_sensitive(self, repo):
        """测试大小写敏感"""
        # Given
        repo.create(name="Test", path="/test")
        
        # When
        result = repo.get_by_name("test")  # 小写
        
        # Then
        assert result is None  # 应该区分大小写
```

#### 边界条件测试

```python
def test_search_with_empty_query(self, repo):
    """测试空查询"""
    results = repo.search("")
    assert len(results) == 0

def test_search_with_special_characters(self, repo):
    """测试特殊字符"""
    results = repo.search("@#$%")
    assert isinstance(results, list)

def test_search_with_very_long_query(self, repo):
    """测试超长查询"""
    long_query = "a" * 1000
    results = repo.search(long_query)
    assert isinstance(results, list)
```

---

### 2.2 Web API 测试方案

#### 测试模板

```python
# web/tests/test_agent_api.py
class TestAgentExtractImageAPI:
    """测试图片提取 API"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from web.main import create_web_app
        app = create_web_app()
        with TestClient(app) as client:
            yield client
    
    def test_extract_image_success(self, client, mocker):
        """测试图片提取成功"""
        # Given
        mock_result = {"questions": [...], "success": True}
        mocker.patch('web.api.agent.extract_from_image', return_value=mock_result)
        
        # When
        with open("test_data/test_image.png", "rb") as f:
            response = client.post("/api/agent/extract/image", files={"file": f})
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "questions" in data
    
    def test_extract_image_unsupported_format(self, client):
        """测试不支持的图片格式"""
        # Given
        test_file = io.BytesIO(b"not an image")
        test_file.name = "test.xyz"
        
        # When
        response = client.post("/api/agent/extract/image", files={"file": test_file})
        
        # Then
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
```

#### Mock AI 服务

```python
@pytest.fixture
def mock_llm_response(mocker):
    """Mock LLM API 响应"""
    mock_response = {
        "choices": [{
            "message": {
                "content": '{"questions": [...]}'
            }
        }]
    }
    mocker.patch('agent.services.model_client.openai.ChatCompletion.create',
                return_value=mock_response)
    return mock_response
```

---

### 2.3 配置和连接测试方案

#### Config 测试

```python
# core/tests/test_shared_config.py
class TestSharedConfigValidate:
    """测试配置验证"""
    
    def test_validate_missing_llm_key(self):
        """测试缺少 LLM API key"""
        config = SharedConfig(
            llm_api_key="",
            vision_api_key="test_key"
        )
        with pytest.raises(ValueError, match="LLM API key is required"):
            config.validate()
    
    def test_validate_missing_vision_key(self):
        """测试缺少 Vision API key"""
        config = SharedConfig(
            llm_api_key="test_key",
            vision_api_key=""
        )
        with pytest.raises(ValueError, match="Vision API key is required"):
            config.validate()
    
    def test_validate_success(self):
        """测试验证成功"""
        config = SharedConfig(
            llm_api_key="test_key",
            vision_api_key="test_key"
        )
        # 应该不抛出异常
        config.validate()
```

#### Connection 测试

```python
# core/tests/test_connection.py
class TestConnectionRollback:
    """测试事务回滚"""
    
    def test_rollback_transaction(self, db_connection):
        """测试正常回滚"""
        # Given
        db_connection.begin_transaction()
        
        # When
        db_connection.rollback_transaction()
        
        # Then
        # 应该不抛出异常
    
    def test_rollback_without_transaction(self, db_connection):
        """测试无事务时回滚"""
        # When & Then
        with pytest.raises(Exception):
            db_connection.rollback_transaction()
```

---

## 三、实施计划

### 阶段 1: Repository 层测试 (P0) - 2-3 天

**目标**: 49% → 90% (+41%)

#### Day 1: Category + Tag Repository
- [ ] test_category_repository.py (8 用例)
  - get_by_name (2)
  - get_by_path (2)
  - search (4)
- [ ] test_tag_repository.py (6 用例)
  - get_by_names (2)
  - search (4)

**预计覆盖率**: 60%

#### Day 2: Question Repository
- [ ] test_question_repository.py (20 用例)
  - search (8)
  - get_by_category (4)
  - get_by_tag (4)
  - batch_create (4)

**预计覆盖率**: 80%

#### Day 3: StagingQuestion Repository
- [ ] test_staging_repository.py (14 用例)
  - get_pending (4)
  - get_approved (4)
  - approve (3)
  - reject (3)

**预计覆盖率**: 90%

**阶段验收**:
- Repository 覆盖率 ≥ 90%
- 总体覆盖率 ≥ 85%

---

### 阶段 2: Web API 测试 (P0) - 2 天

**目标**: 16% → 90% (+74%)

#### Day 4: Extract API
- [ ] test_agent_extract_api.py (18 用例)
  - extract/image (10)
  - extract/document (8)

#### Day 5: Staging API
- [ ] test_agent_staging_api.py (12 用例)
  - staging/approve (6)
  - staging/list (4)
  - staging/delete (2)

**阶段验收**:
- web/api/agent.py 覆盖率 ≥ 90%
- 总体覆盖率 ≥ 88%

---

### 阶段 3: Config 和 Connection (P1) - 0.5-1 天

**目标**: 82%/86% → 90%

#### Half Day 1: Shared Config
- [ ] test_shared_config.py (4 用例)

#### Half Day 2: Connection
- [ ] test_connection.py (5 用例)

#### Half Day 3: Agent Config
- [ ] test_agent_config.py (5 用例)

**阶段验收**:
- shared/config.py 覆盖率 ≥ 90%
- connection.py 覆盖率 ≥ 90%
- agent/config.py 覆盖率 ≥ 90%
- 总体覆盖率 ≥ 90%

---

### 阶段 4: 整合与验证 (P1) - 0.5 天

**目标**: 确保覆盖率稳定在 90%+

- [ ] 运行完整测试套件
- [ ] 生成覆盖率报告
- [ ] 修复失败测试
- [ ] 验证覆盖率达标

**阶段验收**:
- 总体覆盖率 ≥ 90%
- 测试执行时间 < 5 分钟
- 所有测试通过 (100%)

---

## 四、职责分工

### Tester 职责

**核心**: Web API 测试

- [ ] web/api/agent.py 测试 (30 用例)
- [ ] API 端点测试
- [ ] 请求/响应验证
- [ ] Mock AI 服务

**交付物**:
- web/tests/test_agent_extract_api.py
- web/tests/test_agent_staging_api.py
- Mock 配置指南

### Developer 职责

**核心**: Repository 层 + 基础模块测试

- [ ] repositories.py 测试 (48 用例)
- [ ] shared/config.py 测试 (4 用例)
- [ ] connection.py 测试 (5 用例)
- [ ] agent/config.py 测试 (5 用例)

**交付物**:
- core/tests/test_*_repository.py
- core/tests/test_shared_config.py
- core/tests/test_connection.py
- agent/tests/test_config.py

---

## 五、风险与缓解

### 风险 1: Repository 测试复杂
- **影响**: 中 (进度延迟)
- **概率**: 中
- **缓解**: 
  - 使用测试模板
  - 分阶段实施
  - 每日检查进度

### 风险 2: Web API 测试依赖
- **影响**: 中 (测试失败)
- **概率**: 中
- **缓解**:
  - Mock 所有外部依赖
  - 使用 TestClient
  - 隔离测试环境

### 风险 3: 覆盖率目标过高
- **影响**: 高 (难以达到 90%)
- **概率**: 低
- **缓解**:
  - 优先保证关键模块
  - 允许部分代码豁免
  - 关注测试质量

---

## 六、验收标准

### Tester 验收标准

- [ ] web/api/agent.py 覆盖率 ≥ 90%
- [ ] 所有 API 端点测试通过
- [ ] Mock 配置正确
- [ ] 测试文档完整

### Developer 验收标准

- [ ] repositories.py 覆盖率 ≥ 90%
- [ ] shared/config.py 覆盖率 ≥ 90%
- [ ] connection.py 覆盖率 ≥ 90%
- [ ] agent/config.py 覆盖率 ≥ 90%

### 总体验收标准

- [ ] 总体覆盖率 ≥ 90%
- [ ] 所有测试通过 (100%)
- [ ] 测试执行时间 < 5 分钟
- [ ] 测试文档完整

---

## 七、交付物

### Tester 交付
- Web API 测试文件 (2 个)
- 30 个测试用例
- Mock 配置指南

### Developer 交付
- Repository 测试文件 (4 个)
- Config/Connection 测试文件 (3 个)
- 62 个测试用例

### 共同交付
- 覆盖率报告 (HTML + XML)
- 测试文档

---

**下一步**:
- [ ] 转交 Test-Analyst 设计测试策略
- [ ] 转交 Tester 开发 Web API 测试
- [ ] 转交 Developer 补充 Repository 测试
- [ ] 转交 Reviewer 审查 + 验证

---

*报告生成时间*: 2026-03-19 23:25  
*报告人*: Architect (nanobot)  
*当前覆盖率*: 82%  
*目标覆盖率*: 90%  
*预计完成时间*: 4-5 天
