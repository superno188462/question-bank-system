# 任务 T013: 覆盖率提升审查报告

**审查任务**: T013 - 补充低覆盖率模块单元测试  
**审查时间**: 2026-03-19 23:45  
**审查人**: Code Reviewer (nanobot)  
**审查范围**: repositories.py, web/api/*, shared/config.py 测试覆盖  

---

## 📊 当前状态总览

| 指标 | 当前 | 目标 | 差距 | 状态 |
|------|------|------|------|------|
| **总覆盖率** | **85%** | 90% | **-5%** | ⚠️ |
| 通过测试 | 344 | - | - | ✅ |
| 失败测试 | 0 | 0 | 0 | ✅ |
| 跳过测试 | 2 | - | - | ⚠️ |
| 收集错误 | 6 | 0 | +6 | ❌ |

> **注**: 任务描述中 87% 与实际 85% 略有差异，以实际运行为准。

---

## 📈 模块覆盖率详情

### ❌ 低覆盖率模块 (<90%)

| 模块 | 当前 | 目标 | 差距 | 未覆盖行数 | 优先级 |
|------|------|------|------|-----------|--------|
| **web/api/agent.py** | **16%** | 90% | **-74%** | **262** | P0 |
| tests/test_approve_staging.py | 17% | 90% | -73% | 71 | P3 |
| **web/api/questions.py** | **30%** | 90% | **-60%** | **96** | P1 |
| **web/api/qa.py** | **30%** | 90% | **-60%** | **74** | P1 |
| web/api/categories.py | 48% | 90% | -42% | 63 | P2 |
| web/api/tags.py | 46% | 90% | -44% | 20 | P2 |
| **core/database/repositories.py** | **83%** | 90% | **-7%** | **66** | P0 |
| shared/config.py | 82% | 90% | -8% | 5 | P1 |
| core/database/connection.py | 86% | 90% | -4% | 10 | P1 |
| agent/extractors/image_extractor.py | 88% | 90% | -2% | 12 | P2 |

### ✅ 高覆盖率模块 (≥90%)

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| core/services/vector_index.py | 100% | ✅ |
| core/services/category_service.py | 100% | ✅ |
| core/services/tag_service.py | 100% | ✅ |
| agent/generators/explanation_generator.py | 100% | ✅ |
| agent/services/embedding_service.py | 100% | ✅ |
| core/exceptions.py | 100% | ✅ |
| 大部分测试文件 | 98-99% | ✅ |

---

## 🔍 未覆盖代码分析

### P0: core/database/repositories.py (83% → 90%)

**未覆盖代码** (66 行):

```python
# 1. Repository 基类抽象方法 (6 行) - 行 36-56
@abstractmethod
def create(self, entity: Any) -> T: ...
@abstractmethod
def get_by_id(self, entity_id: ID) -> Optional[T]: ...
# 这些是抽象方法，不需要测试

# 2. CategoryRepository 更新边界 (1 行) - 行 137
if not updates:
    return self.get_by_id(category_id)  # ❌ 未测试

# 3. QuestionRepository 复杂查询 (约 40 行) - 行 447-450, 480-481, 520-534
# 带标签筛选的分页查询
if tag_id:
    base_sql = """
    SELECT q.* FROM questions q
    INNER JOIN question_tags qt ON q.id = qt.question_id
    WHERE qt.tag_id = ?
    """
    # ... 复杂 SQL 构建逻辑 ❌ 未测试

# 更新题目时的字段构建
if update_data.content is not None:
    updates.append("content = ?")
    params.append(update_data.content)
# ... 多个字段更新逻辑 ❌ 未测试

# 4. 标签管理方法 (约 15 行) - 行 607-636
def add_tag(self, question_id: str, tag_id: str) -> bool:
    # 检查是否已存在
    check_sql = """
    SELECT COUNT(*) as count FROM question_tags 
    WHERE question_id = ? AND tag_id = ?
    """
    row = db.fetch_one(check_sql, (question_id, tag_id))
    
    if row and row['count'] > 0:
        return True  # ❌ 已存在场景未测试
    
    # 添加标签
    insert_sql = """
    INSERT INTO question_tags (question_id, tag_id)
    VALUES (?, ?)
    """
    # ... ❌ 未测试

# 5. 预备题目仓库方法 (约 60 行) - 行 645-771
def create_staging(self, staging_data: StagingQuestionCreate): ...
def get_staging_by_id(self, staging_id: int): ...
def get_all_staging(self, status: Optional[str] = None): ...
def update_staging(self, staging_id: int, update_data: StagingQuestionUpdate): ...
def delete_staging(self, staging_id: int) -> bool: ...
def approve_staging(self, staging_id: int, reviewed_by: str) -> bool: ...
# ❌ 这些方法大部分未测试

# 6. QA 日志仓库方法 (约 40 行) - 行 801-844
def log_qa(self, user_question: str, ai_answer: str, ...): ...
def get_qa_logs(self, limit: int = 100) -> List[dict]: ...
# ❌ 未测试
```

**缺失测试**:
- ❌ 带标签筛选的题目查询测试
- ❌ 题目更新边界条件测试（无更新字段）
- ❌ 标签重复添加测试
- ❌ 预备题目完整 CRUD 测试
- ❌ QA 日志记录测试

---

### P0: web/api/agent.py (16% → 90%)

**未覆盖代码** (262 行):

```python
# 1. 图片提取 API (约 80 行) - 行 50-130
@router.post("/extract/image")
async def extract_from_image(
    file: UploadFile = File(...),
    category_id: str = Form(None),
    tags: str = Form(None)
):
    # 文件验证
    # 调用提取器
    # 返回结果
    # ❌ 未测试

# 2. 文档提取 API (约 60 行) - 行 149-212
@router.post("/extract/document")
async def extract_from_document(...):
    # ❌ 未测试

# 3. 批量提取 API (约 40 行) - 行 294-340
@router.post("/extract/batch")
async def batch_extract(...):
    # ❌ 未测试

# 4. 解析生成 API (约 50 行) - 行 350-400
@router.post("/explain/generate")
async def generate_explanation(...):
    # ❌ 未测试

# 5. 智能问答 API (约 30 行) - 行 410-440
@router.post("/qa/ask")
async def qa_ask(...):
    # ❌ 未测试
```

**缺失测试**:
- ❌ 图片提取成功/失败场景
- ❌ 文档提取成功/失败场景
- ❌ 批量提取测试
- ❌ 解析生成测试
- ❌ 智能问答测试
- ❌ 文件验证测试（格式、大小）
- ❌ 错误处理测试

---

### P1: web/api/questions.py (30% → 90%)

**未覆盖代码** (96 行):

```python
# 1. 创建题目 API (约 20 行) - 行 68-88
@router.post("/", response_model=Question, status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionCreate):
    try:
        return question_service.create_question(question)
    except Exception as e:
        raise HTTPException(...)
    # ❌ 错误处理未测试

# 2. 获取题目列表 API (约 20 行) - 行 95-115
@router.get("/", response_model=QuestionListResponse)
async def get_questions(...):
    # ❌ 分页、筛选参数未测试

# 3. 更新题目 API (约 20 行) - 行 150-170
@router.put("/{question_id}", response_model=Question)
async def update_question(...):
    # ❌ 404 场景未测试

# 4. 删除题目 API (约 20 行) - 行 180-200
@router.delete("/{question_id}")
async def delete_question(...):
    # ❌ 404 场景未测试

# 5. 搜索题目 API (约 16 行) - 行 220-240
@router.get("/search/keyword")
async def search_questions(...):
    # ❌ 搜索功能未测试
```

---

### P1: web/api/qa.py (30% → 90%)

**未覆盖代码** (74 行):

```python
# 1. 智能问答 API (约 50 行) - 行 85-135
@router.post("/ask", response_model=QAAskResponse)
async def ask_question(request: QAAskRequest):
    # 向量检索
    # AI 生成回答
    # 返回相关题目
    # ❌ 未测试

# 2. 日志记录 API (约 24 行) - 行 172-246
@router.post("/log")
async def log_qa(...):
    # ❌ 未测试
```

---

### P1: shared/config.py (82% → 90%)

**未覆盖代码** (5 行):

```python
# 第 32, 37, 41, 45 行：环境变量加载
db_url = os.getenv("DATABASE_URL")
if db_url:
    self.DATABASE_URL = db_url

web_port = os.getenv("WEB_PORT")
if web_port:
    self.WEB_PORT = int(web_port)

# 第 55 行：默认数据库路径
return "data/question_bank.db"
```

---

## 🚨 web/tests/ 导入错误分析

### 错误汇总 (6 个文件)

| 文件 | 错误类型 | 原因 |
|------|----------|------|
| web/tests/test_agent_api.py | ImportError | 导入 `AgentConfigUpdate` 不存在 |
| web/tests/test_agent_api_full.py | ImportError | 同上 |
| web/tests/test_agent_functions.py | ImportError | 同上 |
| web/tests/test_api.py | 无 | ✅ 正常运行 |
| web/tests/test_config.py | ImportError | 导入 `AgentConfigUpdate` 不存在 |
| web/tests/test_main.py | ImportError | 导入问题 |

### 根本原因

**问题**: `AgentConfigUpdate` 模型未在 `core/models.py` 中定义

```python
# web/tests/test_agent_functions.py:10
from core.models import AgentConfig, AgentConfigUpdate  # ❌ AgentConfigUpdate 不存在

# core/models.py 中只有:
class AgentConfig: ...
# 没有 AgentConfigUpdate
```

### 修复方案

**方案 A**: 在 `core/models.py` 中添加 `AgentConfigUpdate`

```python
# core/models.py
class AgentConfigUpdate(BaseModel):
    """Agent 配置更新模型"""
    llm_model_id: Optional[str] = Field(None, description="LLM 模型 ID")
    llm_api_key: Optional[str] = Field(None, description="LLM API Key")
    llm_base_url: Optional[str] = Field(None, description="LLM Base URL")
    vision_model_id: Optional[str] = Field(None, description="视觉模型 ID")
    vision_api_key: Optional[str] = Field(None, description="视觉 API Key")
    vision_base_url: Optional[str] = Field(None, description="视觉 Base URL")
    embed_model_name: Optional[str] = Field(None, description="Embedding 模型")
    embed_api_key: Optional[str] = Field(None, description="Embedding API Key")
    embed_base_url: Optional[str] = Field(None, description="Embedding Base URL")
```

**方案 B**: 修改测试文件，移除不存在的导入

```python
# web/tests/test_agent_functions.py
from core.models import AgentConfig  # 移除 AgentConfigUpdate
# 或使用 dict 代替
config_update = {"llm_model_id": "qwen-plus"}
```

---

## 📋 测试补充策略

### 阶段 1: repositories.py 覆盖率提升 (83% → 90%)

**目标**: 补充 66 行未覆盖代码测试

**测试文件**: `core/tests/test_repositories_extended.py` (已存在，需补充)

**测试用例**:

```python
# core/tests/test_repositories_extended.py

class TestQuestionRepositoryWithTagFilter:
    """带标签筛选的题目查询测试"""
    
    def test_get_all_with_tag_filter(self):
        """测试按标签筛选题目"""
        # 创建分类
        # 创建题目
        # 创建标签并关联
        # 按标签筛选查询
        # 验证结果
        
    def test_get_all_with_tag_and_category_filter(self):
        """测试按标签和分类同时筛选"""
        
    def test_get_all_with_tag_no_results(self):
        """测试标签筛选无结果"""


class TestQuestionRepositoryUpdateEdgeCases:
    """题目更新边界条件测试"""
    
    def test_update_with_no_fields(self):
        """测试无更新字段时返回原题目"""
        update_data = QuestionUpdate()  # 空对象
        result = question_repo.update(question_id, update_data)
        assert result == original_question
        
    def test_update_only_content(self):
        """测试仅更新内容"""
        
    def test_update_only_category(self):
        """测试仅更新分类"""


class TestQuestionRepositoryTags:
    """题目标签管理测试"""
    
    def test_add_tag_success(self):
        """测试添加标签成功"""
        
    def test_add_tag_duplicate(self):
        """测试添加重复标签返回成功"""
        # 第一次添加
        result1 = question_repo.add_tag(question_id, tag_id)
        assert result1 is True
        
        # 第二次添加（重复）
        result2 = question_repo.add_tag(question_id, tag_id)
        assert result2 is True  # 应该返回 True
        
    def test_remove_tag_success(self):
        """测试移除标签成功"""
        
    def test_remove_tag_not_exists(self):
        """测试移除不存在的标签"""


class TestStagingRepository:
    """预备题目仓库测试"""
    
    def test_create_staging_minimal(self):
        """测试创建最小预备题目"""
        
    def test_create_staging_full(self):
        """测试创建完整预备题目"""
        
    def test_get_staging_by_id_exists(self):
        """测试获取存在的预备题目"""
        
    def test_get_staging_by_id_not_exists(self):
        """测试获取不存在的预备题目"""
        
    def test_get_all_staging_all(self):
        """测试获取所有预备题目"""
        
    def test_get_all_staging_by_status(self):
        """测试按状态筛选预备题目"""
        
    def test_update_staging_success(self):
        """测试更新预备题目成功"""
        
    def test_delete_staging_success(self):
        """测试删除预备题目成功"""
        
    def test_approve_staging_creates_question(self):
        """测试批准预备题目创建正式题目"""


class TestQALogRepository:
    """QA 日志仓库测试"""
    
    def test_log_qa_minimal(self):
        """测试记录最小 QA 日志"""
        
    def test_log_qa_full(self):
        """测试记录完整 QA 日志"""
        
    def test_get_qa_logs_limit(self):
        """测试获取限制数量的日志"""
        
    def test_get_qa_logs_empty(self):
        """测试空日志列表"""
```

**预计覆盖率提升**: +7% (83% → 90%)  
**预计工作量**: 1-2 天

---

### 阶段 2: web/api 测试补充

#### 2.1 questions.py (30% → 90%)

**测试文件**: `web/tests/test_questions_api.py` (新建)

```python
# web/tests/test_questions_api.py
import pytest
from fastapi.testclient import TestClient
from web.main import app

client = TestClient(app)


class TestQuestionsAPI:
    """题目管理 API 测试"""
    
    def test_create_question_success(self, test_category):
        """测试创建题目成功"""
        question_data = {
            "content": "测试题目",
            "options": ["A", "B", "C", "D"],
            "answer": "A",
            "explanation": "解析",
            "category_id": test_category.id
        }
        response = client.post("/api/questions/", json=question_data)
        assert response.status_code == 201
        assert response.json()["content"] == "测试题目"
        
    def test_create_question_validation_error(self):
        """测试创建题目验证错误（缺少必填字段）"""
        question_data = {"content": "测试题目"}  # 缺少 answer, explanation, category_id
        response = client.post("/api/questions/", json=question_data)
        assert response.status_code == 422
        
    def test_get_questions_list(self):
        """测试获取题目列表"""
        response = client.get("/api/questions/?page=1&limit=10")
        assert response.status_code == 200
        assert "data" in response.json()
        assert "total" in response.json()
        
    def test_get_questions_with_category_filter(self, test_category):
        """测试按分类筛选题目"""
        response = client.get(f"/api/questions/?category_id={test_category.id}")
        assert response.status_code == 200
        
    def test_get_questions_with_tag_filter(self, test_tag):
        """测试按标签筛选题目"""
        response = client.get(f"/api/questions/?tag_id={test_tag.id}")
        assert response.status_code == 200
        
    def test_get_question_success(self, test_question):
        """测试获取单个题目成功"""
        response = client.get(f"/api/questions/{test_question.id}")
        assert response.status_code == 200
        assert response.json()["id"] == test_question.id
        
    def test_get_question_not_found(self):
        """测试获取不存在的题目"""
        response = client.get("/api/questions/non-existent-id")
        assert response.status_code == 404
        
    def test_update_question_success(self, test_question):
        """测试更新题目成功"""
        update_data = {"content": "更新后的内容"}
        response = client.put(f"/api/questions/{test_question.id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["content"] == "更新后的内容"
        
    def test_update_question_not_found(self):
        """测试更新不存在的题目"""
        response = client.put("/api/questions/non-existent-id", json={"content": "更新"})
        assert response.status_code == 404
        
    def test_delete_question_success(self, test_question):
        """测试删除题目成功"""
        response = client.delete(f"/api/questions/{test_question.id}")
        assert response.status_code == 200
        
    def test_delete_question_not_found(self):
        """测试删除不存在的题目"""
        response = client.delete("/api/questions/non-existent-id")
        assert response.status_code == 404
        
    def test_search_questions(self, test_question):
        """测试搜索题目"""
        response = client.get(f"/api/questions/search/keyword?keyword={test_question.content[:10]}")
        assert response.status_code == 200
        assert len(response.json()["data"]) > 0
```

**预计覆盖率提升**: +60% (30% → 90%)  
**预计工作量**: 1 天

---

#### 2.2 qa.py (30% → 90%)

**测试文件**: `web/tests/test_qa_api.py` (新建)

```python
# web/tests/test_qa_api.py
import pytest
from fastapi.testclient import TestClient
from web.main import app

client = TestClient(app)


class TestQAAPI:
    """智能问答 API 测试"""
    
    @patch('web.api.qa.VectorIndex')
    @patch('web.api.qa.AgentConfig')
    def test_ask_question_success(self, mock_config, mock_vector_index):
        """测试智能问答成功"""
        # Mock 向量检索
        mock_vector_index.return_value.search_similar.return_value = [
            {"question_id": "q1", "content": "相关题目", "similarity": 0.9}
        ]
        
        request_data = {
            "question": "Python 中列表如何创建？",
            "top_k": 5
        }
        response = client.post("/api/qa/ask", json=request_data)
        assert response.status_code == 200
        assert "answer" in response.json()
        assert "related_questions" in response.json()
        
    def test_ask_question_empty_keyword(self):
        """测试空问题"""
        request_data = {"question": ""}
        response = client.post("/api/qa/ask", json=request_data)
        assert response.status_code == 422
        
    @patch('web.api.qa.VectorIndex')
    def test_ask_question_no_results(self, mock_vector_index):
        """测试无相关题目"""
        mock_vector_index.return_value.search_similar.return_value = []
        
        request_data = {"question": "不存在的题目"}
        response = client.post("/api/qa/ask", json=request_data)
        assert response.status_code == 200
        assert response.json()["related_questions"] == []
```

**预计覆盖率提升**: +60% (30% → 90%)  
**预计工作量**: 0.5 天

---

#### 2.3 agent.py (16% → 90%)

**测试文件**: `web/tests/test_agent_api.py` (修复并补充)

```python
# web/tests/test_agent_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from web.main import app

client = TestClient(app)


class TestAgentExtractImageAPI:
    """图片提取 API 测试"""
    
    @patch('web.api.agent.ImageExtractor')
    def test_extract_image_success(self, mock_extractor_class):
        """测试图片提取成功"""
        # Mock 提取器
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            "questions": [],
            "total_count": 0,
            "confidence": 0.9
        }
        mock_extractor_class.return_value = mock_extractor
        
        # 准备测试文件
        file_data = BytesIO(b"fake image data")
        files = {"file": ("test.jpg", file_data, "image/jpeg")}
        
        response = client.post("/api/agent/extract/image", files=files)
        assert response.status_code == 200
        
    @patch('web.api.agent.ImageExtractor')
    def test_extract_image_invalid_format(self, mock_extractor_class):
        """测试不支持的图片格式"""
        file_data = BytesIO(b"fake data")
        files = {"file": ("test.txt", file_data, "text/plain")}
        
        response = client.post("/api/agent/extract/image", files=files)
        assert response.status_code == 400
        
    @patch('web.api.agent.ImageExtractor')
    def test_extract_image_file_too_large(self, mock_extractor_class):
        """测试文件过大"""
        # Mock 大文件
        file_data = BytesIO(b"x" * (51 * 1024 * 1024))  # 51MB
        files = {"file": ("large.jpg", file_data, "image/jpeg")}
        
        response = client.post("/api/agent/extract/image", files=files)
        assert response.status_code == 400


class TestAgentExtractDocumentAPI:
    """文档提取 API 测试"""
    
    @patch('web.api.agent.DocumentExtractor')
    def test_extract_document_pdf(self, mock_extractor_class):
        """测试 PDF 文档提取"""
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            "questions": [],
            "total_count": 0
        }
        mock_extractor_class.return_value = mock_extractor
        
        file_data = BytesIO(b"%PDF fake pdf")
        files = {"file": ("test.pdf", file_data, "application/pdf")}
        
        response = client.post("/api/agent/extract/document", files=files)
        assert response.status_code == 200
        
    @patch('web.api.agent.DocumentExtractor')
    def test_extract_document_word(self, mock_extractor_class):
        """测试 Word 文档提取"""
        # 类似 PDF 测试


class TestAgentBatchExtractAPI:
    """批量提取 API 测试"""
    
    def test_batch_extract_success(self):
        """测试批量提取成功"""
        # 实现批量提取测试


class TestAgentExplainAPI:
    """解析生成 API 测试"""
    
    @patch('web.api.agent.ExplanationGenerator')
    def test_generate_explanation_success(self, mock_generator_class):
        """测试解析生成成功"""
        mock_generator = Mock()
        mock_generator.generate.return_value = "这是解析"
        mock_generator_class.return_value = mock_generator
        
        request_data = {
            "question_id": "test-id",
            "content": "题目内容",
            "answer": "答案"
        }
        response = client.post("/api/agent/explain/generate", json=request_data)
        assert response.status_code == 200
        assert response.json()["explanation"] == "这是解析"


class TestAgentQAAPI:
    """智能问答 API 测试"""
    
    @patch('web.api.agent.VectorIndex')
    def test_qa_ask_success(self, mock_vector_index):
        """测试智能问答成功"""
        mock_vector_index.return_value.search_similar.return_value = [
            {"question_id": "q1", "content": "相关题目"}
        ]
        
        request_data = {"question": "测试问题"}
        response = client.post("/api/agent/qa/ask", json=request_data)
        assert response.status_code == 200
```

**预计覆盖率提升**: +74% (16% → 90%)  
**预计工作量**: 2 天

---

### 阶段 3: shared/config.py 补充 (82% → 90%)

**测试文件**: `shared/tests/test_config.py` (补充)

```python
# shared/tests/test_config.py
import pytest
from unittest.mock import patch
from shared.config import SharedConfig


class TestSharedConfigEnvironmentVariables:
    """环境变量加载测试"""
    
    @patch('os.getenv')
    def test_database_url_from_env(self, mock_getenv):
        """测试从环境变量加载数据库 URL"""
        mock_getenv.return_value = "sqlite:///./test.db"
        config = SharedConfig()
        assert config.DATABASE_URL == "sqlite:///./test.db"
        
    @patch('os.getenv')
    def test_database_url_not_set(self, mock_getenv):
        """测试环境变量未设置时使用默认值"""
        mock_getenv.return_value = None
        config = SharedConfig()
        assert config.DATABASE_URL == "sqlite:///./data/question_bank.db"
        
    @patch('os.getenv')
    def test_web_port_from_env(self, mock_getenv):
        """测试从环境变量加载 Web 端口"""
        mock_getenv.side_effect = lambda key, default=None: "9000" if key == "WEB_PORT" else default
        config = SharedConfig()
        assert config.WEB_PORT == 9000
        
    @patch('os.getenv')
    def test_mcp_port_from_env(self, mock_getenv):
        """测试从环境变量加载 MCP 端口"""
        mock_getenv.side_effect = lambda key, default=None: "9001" if key == "MCP_PORT" else default
        config = SharedConfig()
        assert config.MCP_PORT == 9001
        
    @patch('os.getenv')
    def test_wechat_port_from_env(self, mock_getenv):
        """测试从环境变量加载微信端口"""
        mock_getenv.side_effect = lambda key, default=None: "9002" if key == "WECHAT_PORT" else default
        config = SharedConfig()
        assert config.WECHAT_PORT == 9002


class TestSharedConfigGetDatabasePath:
    """数据库路径获取测试"""
    
    def test_get_database_path_sqlite(self):
        """测试 SQLite 数据库路径"""
        config = SharedConfig()
        config.DATABASE_URL = "sqlite:///./data/test.db"
        assert config.get_database_path() == "./data/test.db"
        
    def test_get_database_path_default(self):
        """测试默认数据库路径"""
        config = SharedConfig()
        config.DATABASE_URL = "postgresql://user:pass@localhost/db"
        assert config.get_database_path() == "data/question_bank.db"
```

**预计覆盖率提升**: +8% (82% → 90%)  
**预计工作量**: 0.5 天

---

## 📊 预期覆盖率提升

| 阶段 | 任务 | 当前 | 目标 | 提升 | 工作量 |
|------|------|------|------|------|--------|
| 当前 | - | 85% | - | - | - |
| 阶段 1 | repositories.py 测试 | 83% | 90% | +7% | 1-2 天 |
| 阶段 2.1 | questions.py API 测试 | 30% | 90% | +60% | 1 天 |
| 阶段 2.2 | qa.py API 测试 | 30% | 90% | +60% | 0.5 天 |
| 阶段 2.3 | agent.py API 测试 | 16% | 90% | +74% | 2 天 |
| 阶段 3 | config.py 测试 | 82% | 90% | +8% | 0.5 天 |
| **总计** | **全部完成** | **85%** | **92%+** | **+7%+** | **5-6 天** |

---

## 🚨 关键问题修复

### P0: 修复 web/tests/ 导入错误

**问题**: `AgentConfigUpdate` 未定义

**修复方案**:

```python
# core/models.py (添加)
class AgentConfigUpdate(BaseModel):
    """Agent 配置更新模型"""
    llm_model_id: Optional[str] = Field(None, description="LLM 模型 ID")
    llm_api_key: Optional[str] = Field(None, description="LLM API Key")
    llm_base_url: Optional[str] = Field(None, description="LLM Base URL")
    vision_model_id: Optional[str] = Field(None, description="视觉模型 ID")
    vision_api_key: Optional[str] = Field(None, description="视觉 API Key")
    vision_base_url: Optional[str] = Field(None, description="视觉 Base URL")
    embed_model_name: Optional[str] = Field(None, description="Embedding 模型")
    embed_api_key: Optional[str] = Field(None, description="Embedding API Key")
    embed_base_url: Optional[str] = Field(None, description="Embedding Base URL")
```

---

## 📋 行动项清单

### P0 (立即执行)

- [ ] **修复 `core/models.py`**: 添加 `AgentConfigUpdate` 类
- [ ] **修复 web/tests/ 导入**: 更新所有导入语句
- [ ] **补充 `test_repositories_extended.py`**: 添加 66 行未覆盖代码测试

### P1 (本周完成)

- [ ] **创建 `web/tests/test_questions_api.py`**: 题目 API 测试
- [ ] **创建 `web/tests/test_qa_api.py`**: QA API 测试
- [ ] **补充 `shared/tests/test_config.py`**: 配置测试

### P2 (下周完成)

- [ ] **修复 `web/tests/test_agent_api.py`**: Agent API 测试
- [ ] **创建 `web/tests/test_agent_extract.py`**: 提取 API 测试
- [ ] **运行完整测试套件验证**: 确保覆盖率 >90%

---

## ⚠️ 风险提示

### 技术风险
1. **web/tests/ 依赖**: 需要数据库环境和 Mock 配置
2. **异步测试**: Agent API 多为异步函数，需要正确配置
3. **文件上传测试**: 需要 Mock 文件上传

### 时间风险
1. **工作量估算**: 5-6 天可能不足
2. **测试稳定性**: 新增测试可能不稳定

### 建议
1. **优先 P0**: 先修复导入错误和 repositories.py
2. **增量提交**: 每个测试文件单独提交
3. **使用 Fixture**: 确保测试独立性

---

## 📝 审查结论

### 当前状态 ✅ 良好

- **测试通过率**: 100% (344 passed, 0 failed)
- **覆盖率**: 85% (距离目标 -5%)
- **主要差距**: web/api/ 模块测试缺失

### 可行性评估

- **90% 目标**: ✅ 可行 (5-6 天工作量)
- **测试质量**: ⚠️ 需要注意 Mock 配置和测试隔离
- **维护成本**: ⚠️ web API 测试可能随代码变更频繁更新

### 建议优先级

```
P0: 修复导入错误 + repositories.py 测试
  ↓
P1: questions.py + qa.py API 测试
  ↓
P2: agent.py API 测试 + config.py 测试
```

---

**审查人**: Code Reviewer  
**审查时间**: 2026-03-19 23:45  
**建议复审**: 阶段 1 完成后

**下一步**: 请 Developer 立即修复 `core/models.py` 导入错误，然后补充 repositories.py 测试。
