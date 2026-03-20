# 任务 T010 覆盖率分析报告

**任务**: 将代码覆盖率从 46% 提升至 90%  
**分析时间**: 2026-03-19 20:45  
**执行人**: Tester (nanobot)  

---

## 一、当前覆盖率状态

### 1.1 总体覆盖率

| 模块 | 当前覆盖率 | 目标覆盖率 | 差距 | 状态 |
|------|-----------|-----------|------|------|
| **总计** | **79%** | 90% | +11% | 🔄 进行中 |
| core/ | 85% | 90% | +5% | 🟡 接近 |
| web/ | 65% | 90% | +25% | 🔴 需改进 |
| agent/ | 82% | 90% | +8% | 🟡 接近 |
| mcp_server/ | 0% | 90% | +90% | 🔴 未测试 |
| wechat/ | 0% | 90% | +90% | 🔴 未测试 |
| shared/ | 82% | 90% | +8% | 🟡 接近 |

### 1.2 详细模块覆盖率

#### Core 模块 (85%)

| 文件 | 覆盖率 | 未覆盖行数 | 优先级 |
|------|--------|-----------|--------|
| core/database/connection.py | 90% | 7 | 低 |
| core/database/migrations.py | 41% | 94 | 中 |
| core/database/repositories.py | 63% | 142 | 中 |
| core/exceptions.py | 100% | 0 | ✅ |
| core/models.py | 97% | 4 | ✅ |
| core/services.py | 47% | 10 | 中 |
| core/services/category_service.py | 100% | 0 | ✅ |
| core/services/question_service.py | 95% | 7 | 低 |
| core/services/tag_service.py | 100% | 0 | ✅ |
| core/services/vector_index.py | 37% | 72 | 高 |

#### Web 模块 (65%)

| 文件 | 覆盖率 | 未覆盖行数 | 优先级 |
|------|--------|-----------|--------|
| web/api/agent.py | 50% | 156 | 高 |
| web/api/categories.py | 48% | 63 | 中 |
| web/api/qa.py | 30% | 74 | 高 |
| web/api/questions.py | 30% | 96 | 高 |
| web/api/tags.py | 46% | 20 | 中 |
| web/config.py | 88% | 2 | 低 |
| web/main.py | 80% | 10 | 低 |
| web/tests/test_agent_api.py | 94% | 14 | ✅ |
| web/tests/test_api.py | 98% | 1 | ✅ |

#### Agent 模块 (82%)

| 文件 | 覆盖率 | 未覆盖行数 | 优先级 |
|------|--------|-----------|--------|
| agent/config.py | 59% | 66 | 中 |
| agent/extractors/document_extractor.py | 66% | 36 | 中 |
| agent/extractors/image_extractor.py | 88% | 12 | 低 |
| agent/generators/explanation_generator.py | 100% | 0 | ✅ |
| agent/services/embedding_service.py | 100% | 0 | ✅ |
| agent/services/model_client.py | 98% | 1 | ✅ |

#### MCP Server (0%)

| 文件 | 覆盖率 | 未覆盖行数 | 优先级 |
|------|--------|-----------|--------|
| mcp_server/config.py | 0% | 16 | 高 |
| mcp_server/server.py | 0% | 15 | 高 |

#### WeChat 模块 (0%)

| 文件 | 覆盖率 | 未覆盖行数 | 优先级 |
|------|--------|-----------|--------|
| wechat/config.py | 0% | 16 | 高 |
| wechat/server.py | 0% | 23 | 高 |

---

## 二、覆盖率差距分析

### 2.1 高优先级模块 (覆盖率 < 50%)

| 模块 | 覆盖率 | 未覆盖原因 | 测试需求 |
|------|--------|-----------|----------|
| mcp_server/ | 0% | 无测试文件 | 需要创建 MCP 协议测试 |
| wechat/ | 0% | 无测试文件 | 需要创建微信 API 测试 |
| core/services/vector_index.py | 37% | 向量索引复杂 | 需要 Mock 向量数据库 |
| web/api/qa.py | 30% | QA 接口复杂 | 需要完整 API 测试 |
| web/api/questions.py | 30% | 题目 API 复杂 | 需要完整 API 测试 |
| core/database/migrations.py | 41% | 迁移脚本复杂 | 需要迁移测试 |
| web/api/categories.py | 48% | 分类 API 部分覆盖 | 需要补充边界测试 |
| web/api/tags.py | 46% | 标签 API 部分覆盖 | 需要补充边界测试 |

### 2.2 中优先级模块 (覆盖率 50-80%)

| 模块 | 覆盖率 | 未覆盖原因 | 测试需求 |
|------|--------|-----------|----------|
| core/services.py | 47% | 服务层包装 | 需要集成测试 |
| agent/config.py | 59% | 配置管理复杂 | 需要配置测试 |
| agent/extractors/document_extractor.py | 66% | PDF/Word 依赖 | 需要 Mock 测试 |
| core/database/repositories.py | 63% | Repository 层大 | 需要补充测试 |

### 2.3 低优先级模块 (覆盖率 > 80%)

| 模块 | 覆盖率 | 未覆盖原因 | 测试需求 |
|------|--------|-----------|----------|
| core/database/connection.py | 90% | 连接管理 | 少量边界测试 |
| core/services/question_service.py | 95% | 业务逻辑 | 少量边界测试 |
| web/main.py | 80% | 主入口 | 补充启动测试 |

---

## 三、测试提升计划

### 3.1 第一阶段：创建缺失测试文件 (预计提升至 85%)

#### 3.1.1 MCP Server 测试

**文件**: `mcp_server/tests/test_server.py`

需要测试:
- [ ] MCP 协议握手
- [ ] 工具调用接口
- [ ] 资源查询接口
- [ ] 错误处理

**预计工作量**: 2 小时  
**预计覆盖率提升**: +5%

#### 3.1.2 WeChat Server 测试

**文件**: `wechat/tests/test_server.py`

需要测试:
- [ ] 微信消息处理
- [ ] 答题接口
- [ ] 分类查询接口
- [ ] 错误处理

**预计工作量**: 2 小时  
**预计覆盖率提升**: +5%

### 3.2 第二阶段：补充 Web API 测试 (预计提升至 88%)

#### 3.2.1 Questions API 测试

**文件**: `web/tests/test_questions_api.py` (新建)

需要测试:
- [ ] 题目列表 API (分页、筛选)
- [ ] 题目详情 API
- [ ] 题目创建 API (各种题型)
- [ ] 题目更新 API
- [ ] 题目删除 API
- [ ] 题目搜索 API
- [ ] 批量导入 API
- [ ] 错误处理

**预计工作量**: 3 小时  
**预计覆盖率提升**: +8%

#### 3.2.2 QA API 测试

**文件**: `web/tests/test_qa_api.py` (新建)

需要测试:
- [ ] 问答接口
- [ ] 相似度搜索
- [ ] 推荐题目
- [ ] 错误处理

**预计工作量**: 2 小时  
**预计覆盖率提升**: +5%

#### 3.2.3 Categories/Tags API 补充测试

**文件**: `web/tests/test_categories_api.py`, `web/tests/test_tags_api.py`

需要测试:
- [ ] 边界条件
- [ ] 异常场景
- [ ] 级联操作

**预计工作量**: 1 小时  
**预计覆盖率提升**: +3%

### 3.3 第三阶段：补充 Core 模块测试 (预计提升至 90%)

#### 3.3.1 Vector Index 测试

**文件**: `core/tests/test_vector_index.py` (已有，需补充)

需要测试:
- [ ] 向量创建
- [ ] 相似度搜索
- [ ] 向量更新
- [ ] 向量删除
- [ ] Mock 向量数据库

**预计工作量**: 2 小时  
**预计覆盖率提升**: +5%

#### 3.3.2 Repository 层补充测试

**文件**: `core/tests/test_question_repository.py` (新建)

需要测试:
- [ ] 题目 CRUD 操作
- [ ] 题目搜索
- [ ] 题目关联查询

**预计工作量**: 2 小时  
**预计覆盖率提升**: +5%

#### 3.3.3 Migration 测试

**文件**: `core/tests/test_migrations.py` (新建)

需要测试:
- [ ] 迁移应用
- [ ] 迁移回滚
- [ ] 迁移状态查询

**预计工作量**: 2 小时  
**预计覆盖率提升**: +3%

### 3.4 第四阶段：补充 Agent 模块测试 (预计提升至 92%)

#### 3.4.1 Config 测试

**文件**: `agent/tests/test_config.py` (已有，需补充)

需要测试:
- [ ] 配置加载
- [ ] 配置验证
- [ ] 配置更新
- [ ] 配置热更新

**预计工作量**: 1 小时  
**预计覆盖率提升**: +3%

#### 3.4.2 Document Extractor 补充测试

**文件**: `agent/tests/test_document_extractor.py` (已有，需补充)

需要测试:
- [ ] Mock PDF 提取
- [ ] Mock Word 提取
- [ ] 错误处理

**预计工作量**: 1 小时  
**预计覆盖率提升**: +2%

---

## 四、测试开发优先级

### P0 紧急 (立即执行)

1. **创建 MCP Server 测试** - 覆盖率 0% → 90%
2. **创建 WeChat Server 测试** - 覆盖率 0% → 90%
3. **补充 Questions API 测试** - 覆盖率 30% → 90%

### P1 高优先级 (本周完成)

4. **补充 QA API 测试** - 覆盖率 30% → 90%
5. **补充 Vector Index 测试** - 覆盖率 37% → 90%
6. **补充 Repository 层测试** - 覆盖率 63% → 90%

### P2 中优先级 (本月完成)

7. **补充 Migration 测试** - 覆盖率 41% → 90%
8. **补充 Categories/Tags API 测试** - 覆盖率 48% → 90%
9. **补充 Agent Config 测试** - 覆盖率 59% → 90%

### P3 低优先级 (可选)

10. **补充 Document Extractor 测试** - 覆盖率 66% → 90%
11. **补充连接管理测试** - 覆盖率 90% → 95%

---

## 五、测试开发指南

### 5.1 测试框架

- **测试框架**: pytest 9.0.2
- **Mock 库**: unittest.mock
- **HTTP 测试**: FastAPI TestClient
- **覆盖率工具**: pytest-cov

### 5.2 测试规范

```python
"""
测试文件命名：test_<module>.py
测试类命名：Test<Module><Functionality>
测试方法命名：test_<action>_<condition>_<expected>
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

class TestQuestionAPI:
    """题目 API 测试"""
    
    def test_create_question_success(self, client, mock_db):
        """测试题目创建成功"""
        # Arrange
        question_data = {...}
        
        # Act
        response = client.post("/api/questions/", json=question_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["success"] is True
    
    def test_create_question_missing_fields(self, client):
        """测试题目创建缺少必填字段"""
        # Arrange
        question_data = {"content": "测试题目"}  # 缺少 answer, explanation
        
        # Act
        response = client.post("/api/questions/", json=question_data)
        
        # Assert
        assert response.status_code == 422
```

### 5.3 Mock 使用指南

```python
# Mock 数据库
@patch('core.database.repositories.QuestionRepository')
def test_question_service(mock_repo):
    mock_repo_instance = Mock()
    mock_repo.return_value = mock_repo_instance
    mock_repo_instance.create.return_value = 1
    
    # 测试逻辑

# Mock 外部 API
@patch('agent.services.model_client.requests.post')
def test_model_client(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {"choices": [...]}
    mock_post.return_value = mock_response
    
    # 测试逻辑
```

---

## 六、执行时间表

| 阶段 | 任务 | 预计时间 | 目标覆盖率 |
|------|------|----------|-----------|
| 第一阶段 | MCP/WeChat 测试 | 4 小时 | 85% |
| 第二阶段 | Web API 测试 | 6 小时 | 88% |
| 第三阶段 | Core 模块测试 | 6 小时 | 90% |
| 第四阶段 | Agent 模块测试 | 2 小时 | 92% |
| **总计** | | **18 小时** | **92%** |

---

## 七、风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| MCP 协议复杂 | 高 | 中 | 使用 Mock，先测试接口 |
| 微信依赖外部 API | 中 | 中 | 完全 Mock 微信 API |
| 向量数据库依赖 | 中 | 中 | 使用 Mock 向量 |
| 测试维护成本 | 中 | 高 | 编写可维护的测试 |

---

## 八、下一步行动

1. ✅ 完成覆盖率分析
2. ✅ 制定测试提升计划
3. ⏳ 创建 MCP Server 测试
4. ⏳ 创建 WeChat Server 测试
5. ⏳ 补充 Web API 测试
6. ⏳ 补充 Core 模块测试
7. ⏳ 验证最终覆盖率

---

*创建时间*: 2026-03-19 20:45  
*执行人*: Tester (nanobot)  
*当前覆盖率*: 79%  
*目标覆盖率*: 90%
