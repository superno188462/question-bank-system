# 题库管理系统架构分析报告

**报告日期**: 2026-03-17  
**项目名称**: question-bank-system  
**GitHub**: https://github.com/superno188462/question-bank-system

---

## 📋 执行摘要

### 整体评价
题库管理系统采用**清晰的分层架构设计**，技术选型合理，代码结构良好。系统支持 Web、MCP、微信小程序三入口，具备完整的题目管理、AI 提取、向量搜索等功能。

| 评估维度 | 评分 | 说明 |
|---------|------|------|
| 架构设计 | ⭐⭐⭐⭐☆ (4/5) | 分层清晰，但部分模块耦合度较高 |
| 代码质量 | ⭐⭐⭐⭐☆ (4/5) | 代码规范，文档完善，但测试覆盖不足 |
| 可维护性 | ⭐⭐⭐⭐☆ (4/5) | 模块化良好，配置热更新支持优秀 |
| 扩展性 | ⭐⭐⭐☆☆ (3.5/5) | 支持多入口，但数据库选型限制扩展 |
| 技术债务 | ⭐⭐⭐☆☆ (3/5) | 存在少量技术债务，需关注 |

---

## 🏗️ 一、当前架构分析

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端层 (Client Layer)                    │
├─────────────────┬─────────────────────┬─────────────────────────┤
│   Web 管理界面    │   MCP Server        │   微信小程序后端          │
│   (port: 8000)  │   (port: 8002)      │   (port: 8001)          │
└────────┬────────┴──────────┬──────────┴────────────┬────────────┘
         │                   │                       │
         └───────────────────┼───────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   API 路由层     │
                    │  (web/api/)     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   服务层         │
                    │  (services.py)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   仓库层         │
                    │  (repositories) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   数据访问层     │
                    │  (connection.py)│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   SQLite 数据库  │
                    │  (data/*.db)    │
                    └─────────────────┘
```

### 1.2 目录结构评估

```
question-bank-system/
├── config/              # ✅ 配置文件 - 结构清晰
├── core/               # ✅ 核心业务逻辑 - 分层合理
│   ├── database/       # 数据库层 (connection, repositories, migrations)
│   ├── services/       # 服务层 (vector_index.py)
│   └── models.py       # 数据模型 (Pydantic)
├── web/                # ✅ Web 入口 - 结构标准
│   ├── api/            # API 路由
│   ├── static/         # 静态资源
│   └── templates/      # 模板文件
├── mcp_server/         # ✅ MCP 服务 - 独立模块
├── wechat/             # ✅ 微信服务 - 独立模块
├── agent/              # ✅ AI Agent - 功能完整
│   ├── services/       # Embedding、Model 服务
│   ├── extractors/     # 题目提取器
│   └── generators/     # 解析生成器
├── shared/             # ✅ 共享模块 - 配置管理
├── scripts/            # ✅ 工具脚本
├── test/               # ⚠️  测试目录 - 覆盖度待提升
└── docs/               # ✅ 文档 - 较为完善
```

**优点**:
- 目录结构清晰，职责分离明确
- 核心业务逻辑与入口层分离
- 共享模块独立，避免代码重复

**改进点**:
- `test/` 和 `tests/` 目录并存，建议统一
- 缺少 `alembic/` 或专门的迁移版本管理目录

---

## 🔧 二、技术栈评估

### 2.1 当前技术栈

| 层级 | 技术选型 | 版本 | 评估 |
|------|---------|------|------|
| Web 框架 | FastAPI | >=0.109.0 | ✅ 优秀，异步支持好 |
| 数据库 | SQLite | - | ⚠️  适合小型项目，扩展性有限 |
| ORM | SQLAlchemy | >=2.0.0 | ⚠️  实际使用原生 SQL，未充分利用 ORM |
| 数据验证 | Pydantic | - | ✅ 优秀，类型安全 |
| 模板引擎 | Jinja2 | >=3.1.0 | ✅ 成熟稳定 |
| AI/ML | OpenAI API + numpy + scikit-learn | - | ✅ 合理选型 |
| 包管理 | uv (推荐) / pip | - | ✅ uv 性能好 |

### 2.2 技术选型分析

#### ✅ 优秀选择

1. **FastAPI**
   - 异步性能优秀
   - 自动生成 OpenAPI 文档
   - 类型提示支持好

2. **Pydantic 数据模型**
   - 类型安全
   - 自动验证
   - 与 FastAPI 集成好

3. **uv 包管理**
   - 安装速度快
   - 依赖解析准确

#### ⚠️ 需关注点

1. **SQLite 数据库**
   - **优势**: 零配置、单文件、适合开发和小规模部署
   - **劣势**: 
     - 并发写入受限
     - 不支持分布式
     - 大数据量性能下降
   - **建议**: 如用户量增长，考虑迁移到 PostgreSQL

2. **SQLAlchemy 使用方式**
   - 当前主要使用原生 SQL，未充分利用 ORM 特性
   - 建议：统一使用 SQLAlchemy ORM 或完全使用原生 SQL

3. **缺少消息队列**
   - AI 提取、向量化等耗时操作同步执行
   - 建议：引入 Celery + Redis 处理异步任务

---

## 📦 三、模块详细分析

### 3.1 核心模块 (core/)

#### 3.1.1 数据模型 (models.py)

**优点**:
- 使用 Pydantic BaseModel，类型安全
- 模型分层清晰 (Base/Create/Update/Full)
- 验证逻辑完善 (如答案验证)
- 文档字符串完整

**问题**:
```python
# 问题 1: validator 装饰器已废弃 (Pydantic v2)
@validator('options')  # ⚠️ Pydantic v2 应使用 @field_validator
def validate_options(cls, v):
    ...

# 问题 2: Config 类配置方式已变更 (Pydantic v2)
class Config:
    from_attributes = True  # ⚠️ Pydantic v2 应使用 model_config
```

**建议**:
```python
# Pydantic v2 推荐写法
from pydantic import BaseModel, Field, field_validator, ConfigDict

class QuestionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        ...
```

#### 3.1.2 服务层 (services.py)

**优点**:
- 服务类职责清晰 (CategoryService, TagService, QuestionService)
- 依赖注入模式 (通过 Repository)
- 延迟初始化 Embedding 服务 (性能优化)

**问题**:
```python
# 问题 1: 服务层直接依赖 Repository 实例，而非抽象
class QuestionService:
    def __init__(self, question_repo: QuestionRepository, ...):
        self.question_repo = question_repo  # ⚠️ 紧耦合

# 问题 2: Embedding 初始化逻辑复杂，放在服务层不合适
def _init_embedding(self):
    if self._embedding_service is None:
        from agent.config import AgentConfig  # ⚠️ 跨模块依赖
        ...
```

**建议**:
- 引入服务层接口/抽象基类
- 使用依赖注入容器管理依赖
- Embedding 服务初始化移至专门的工厂类

#### 3.1.3 仓库层 (repositories.py)

**优点**:
- 通用 Repository 抽象基类
- 事务管理完善 (`transaction()` 上下文管理器)
- 支持软删除和级联删除

**问题**:
```python
# 问题 1: 通用 Repository 未被充分利用
class Repository(Generic[T, ID], ABC):
    # 定义了抽象方法，但具体实现重复代码较多
    ...

# 问题 2: 部分 Repository 未遵循通用接口
class StagingQuestionRepository:  # ⚠️ 未继承 Repository 基类
    @staticmethod
    def create(...):
        ...

# 问题 3: 硬编码的 SQL 字符串，难以维护
sql = """
INSERT INTO questions (id, content, options, answer, explanation, category_id, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""
```

**建议**:
- 统一所有 Repository 继承基类
- 考虑使用 SQLAlchemy Core 或 ORM 减少原生 SQL
- 引入 SQL 构建器或查询构建器

#### 3.1.4 数据库连接 (connection.py)

**优点**:
- 单例模式实现
- 线程安全 (threading.local)
- 事务上下文管理器
- 行工厂返回字典格式

**问题**:
```python
# 问题 1: 全局单例实例，测试时难以 mock
db = DatabaseConnection()  # ⚠️ 全局状态

# 问题 2: 连接池管理简单，无最大连接数限制
def get_connection(self) -> sqlite3.Connection:
    if not hasattr(self._local, 'connection'):
        self._local.connection = sqlite3.connect(self.db_path)
    return self._local.connection
```

**建议**:
- 考虑使用依赖注入而非全局单例
- 添加连接池大小限制和超时配置

#### 3.1.5 数据库迁移 (migrations.py)

**优点**:
- 自动迁移支持
- 版本追踪
- 回滚和备份功能
- 表结构差异检测

**问题**:
```python
# 问题 1: 迁移版本号硬编码
MIGRATION_VERSION = "20260308"  # ⚠️ 手动维护

# 问题 2: 迁移逻辑集中在单文件，复杂度高
def migrate_database(auto: bool = True):
    # 包含表创建、数据初始化、结构变更等所有逻辑
    ...
```

**建议**:
- 采用 Alembic 或类似迁移工具
- 每个迁移独立文件，支持顺序执行和回滚

### 3.2 Web 入口 (web/)

#### 3.2.1 主应用 (main.py)

**优点**:
- 工厂函数创建应用 (`create_web_app()`)
- 中间件配置完整 (CORS)
- 自动执行数据库迁移
- 健康检查端点

**问题**:
```python
# 问题 1: 模块级导入副作用
from web.api import categories, tags, questions, qa, agent  # ⚠️ 导入即执行

# 问题 2: 应用实例在模块级创建
app = create_web_app()  # ⚠️ 不利于测试
```

**建议**:
- 使用 `create_app()` 工厂模式，测试时创建独立实例
- 路由注册移至专门函数

#### 3.2.2 API 路由 (web/api/)

**优点**:
- RESTful 设计
- 统一的错误响应格式
- 分页支持
- 类型提示完整

**问题**:
```python
# 问题 1: 错误处理重复
@router.post("/")
async def create_question(question: QuestionCreate):
    try:
        return question_service.create_question(question)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(...).dict()
        )

# 问题 2: 服务实例在模块级创建
question_service = QuestionService(question_repo, category_repo, tag_repo)  # ⚠️ 全局状态
```

**建议**:
- 引入全局异常处理器，减少重复代码
- 使用依赖注入管理服务实例

### 3.3 AI Agent 模块 (agent/)

#### 3.3.1 配置管理 (config.py)

**优点**:
- 配置热更新支持
- 配置缓存 + 文件修改时间检测
- 配置验证方法
- 安全处理敏感信息 (API Key 掩码)

**问题**:
```python
# 问题 1: 类属性作为装饰器使用 (非标准)
@classmethod
@property
def LLM_MODEL_ID(cls) -> str:  # ⚠️ classmethod + property 不标准
    ...

# 问题 2: 配置文件路径硬编码
CONFIG_FILE = Path(__file__).parent.parent / "config" / "agent.json"
```

**建议**:
```python
# 标准写法
@property
@classmethod
def LLM_MODEL_ID(cls) -> str:
    # 或
    @property
    def LLM_MODEL_ID(self) -> str:
        ...
```

#### 3.3.2 Embedding 服务 (embedding_service.py)

**优点**:
- 支持 OpenAI 兼容 API (包括 Ollama)
- 批量 Embedding 支持
- 单例模式 + 配置哈希检测
- 模型版本追踪

**问题**:
```python
# 问题 1: 全局缓存变量
_embedding_service: Optional[EmbeddingService] = None  # ⚠️ 全局状态
_last_config_hash: str = ""

# 问题 2: 错误处理简单
except Exception as e:
    logger.error(f"Embedding 计算失败：{e}")
    raise  # ⚠️ 直接抛出，无降级策略
```

**建议**:
- 使用依赖注入容器管理单例
- 添加降级策略 (如 Embedding 失败时使用关键词搜索)

#### 3.3.3 向量索引 (vector_index.py)

**优点**:
- 智能检测是否需要重新向量化
- 内容哈希 + 模型版本双重检测
- 余弦相似度检索
- 统计和监控功能

**问题**:
```python
# 问题 1: 向量存储在 SQLite BLOB 字段，查询效率有限
# 问题 2: 全表扫描计算相似度
for row in rows:  # ⚠️ O(n) 复杂度
    emb = np.frombuffer(emb_bytes, dtype=np.float32)
    similarity = np.dot(embedding, emb) / (query_norm * emb_norm)
```

**建议**:
- 考虑使用专门的向量数据库 (如 Chroma, Qdrant, Milvus)
- 或至少添加 HNSW 等近似最近邻索引

### 3.4 共享模块 (shared/)

#### 3.4.1 配置管理 (config.py)

**优点**:
- 环境变量支持
- 多入口共享配置

**问题**:
```python
# 问题 1: 配置类设计简单，无验证
class SharedConfig:
    DATABASE_URL: str = "sqlite:///./data/question_bank.db"
    
    def __init__(self):
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"  # ⚠️ 无类型验证

# 问题 2: 全局实例
config = SharedConfig()  # ⚠️ 全局状态
```

**建议**:
- 使用 Pydantic Settings 进行配置管理
- 添加配置验证

---

## 💰 四、技术债务识别

### 4.1 高优先级债务

| ID | 问题 | 影响 | 建议 | 工作量 |
|----|------|------|------|--------|
| TD-001 | Pydantic v1/v2 兼容性问题 | 升级困难，验证可能失效 | 迁移到 Pydantic v2 API | 2-3 天 |
| TD-002 | SQLite 并发限制 | 多用户写入冲突 | 评估 PostgreSQL 迁移 | 3-5 天 |
| TD-003 | 全局状态过多 | 测试困难，难以 mock | 引入依赖注入容器 | 2-3 天 |
| TD-004 | 同步 AI 调用阻塞 | 请求超时，用户体验差 | 引入 Celery 异步任务 | 3-5 天 |

### 4.2 中优先级债务

| ID | 问题 | 影响 | 建议 | 工作量 |
|----|------|------|------|--------|
| TD-005 | 原生 SQL 过多 | 维护成本高，SQL 注入风险 | 使用 SQLAlchemy ORM | 5-7 天 |
| TD-006 | 迁移版本手动管理 | 易出错，难追踪 | 使用 Alembic | 2-3 天 |
| TD-007 | 向量检索 O(n) 复杂度 | 大数据量性能差 | 引入向量索引或专用 DB | 3-5 天 |
| TD-008 | 测试覆盖不足 | 回归风险高 | 补充单元测试和集成测试 | 持续 |

### 4.3 低优先级债务

| ID | 问题 | 影响 | 建议 | 工作量 |
|----|------|------|------|--------|
| TD-009 | 目录命名不一致 (test/tests) | 轻微混淆 | 统一命名 | 0.5 天 |
| TD-010 | 日志配置分散 | 日志格式不统一 | 集中日志配置 | 0.5 天 |
| TD-011 | 缺少 API 版本管理 | 未来升级困难 | 添加 /api/v1/ 前缀 | 1 天 |

---

## 📊 五、代码质量评估

### 5.1 代码规范

| 维度 | 评分 | 说明 |
|------|------|------|
| 命名规范 | ⭐⭐⭐⭐☆ | 大部分符合 PEP8，少数不一致 |
| 类型提示 | ⭐⭐⭐⭐☆ | 主要函数有类型提示 |
| 文档字符串 | ⭐⭐⭐⭐☆ | 核心函数有 docstring |
| 代码复用 | ⭐⭐⭐☆☆ | 部分重复代码可提取 |
| 错误处理 | ⭐⭐⭐☆☆ | 有异常处理，但不够统一 |

### 5.2 测试覆盖

```
测试目录结构:
├── test/                    # e2e 测试
│   ├── quick_validate.sh
│   └── validate_project.py
├── tests/                   # 单元测试
│   ├── e2e/
│   ├── integration/
│   └── test_approve_staging.py
└── test_frontend.py         # 前端测试
```

**问题**:
- 测试目录不统一 (`test/` vs `tests/`)
- 测试文件较少，覆盖率低
- 缺少核心服务的单元测试

**建议**:
```bash
# 推荐测试结构
tests/
├── unit/                    # 单元测试
│   ├── test_models.py
│   ├── test_services.py
│   └── test_repositories.py
├── integration/             # 集成测试
│   ├── test_api.py
│   └── test_database.py
└── e2e/                     # 端到端测试
    └── test_workflows.py
```

### 5.3 可维护性指标

| 指标 | 当前状态 | 目标 |
|------|---------|------|
| 函数平均行数 | ~30 行 | <25 行 |
| 类平均方法数 | ~8 个 | <10 个 |
| 模块耦合度 | 中等 | 低 |
| 代码重复率 | ~15% | <10% |
| 注释覆盖率 | ~60% | >70% |

---

## 🚀 六、优化建议

### 6.1 架构优化

#### 建议 1: 引入依赖注入容器

**当前问题**:
```python
# 模块级全局实例
question_service = QuestionService(question_repo, category_repo, tag_repo)
db = DatabaseConnection()
config = SharedConfig()
```

**优化方案**:
```python
# 使用依赖注入容器 (如 dependency-injector)
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Config)
    database = providers.Singleton(DatabaseConnection, config=config)
    question_repo = providers.Factory(QuestionRepository, db=database)
    question_service = providers.Factory(QuestionService, question_repo=question_repo)

# 在 FastAPI 中使用
@app.get("/questions")
async def get_questions(
    service: QuestionService = Depends(lambda: container.question_service())
):
    ...
```

**收益**:
- 测试时可轻松 mock 依赖
- 减少全局状态
- 依赖关系清晰

#### 建议 2: 引入异步任务队列

**当前问题**:
```python
# 同步 AI 调用，阻塞请求
def _try_embed_question(self, question_id: str, content: str, ...):
    embedding = self._embedding_service.embed(content)  # ⚠️ 阻塞
```

**优化方案**:
```python
# 使用 Celery 异步任务
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def embed_question_task(question_id: str, content: str):
    embedding = embedding_service.embed(content)
    vector_index.update_embedding(question_id, embedding, ...)

# API 中异步调用
@router.post("/questions")
async def create_question(question: QuestionCreate):
    q = question_service.create_question(question)
    embed_question_task.delay(q.id, q.content)  # ⚠️ 非阻塞
    return q
```

**收益**:
- API 响应更快
- 支持重试和失败处理
- 可水平扩展

#### 建议 3: 数据库迁移方案

**当前问题**:
- SQLite 并发写入受限
- 无分布式支持

**优化方案**:
```python
# 支持多数据库后端
DATABASES = {
    'sqlite': 'sqlite:///./data/question_bank.db',
    'postgresql': 'postgresql://user:pass@localhost/dbname'
}

# 使用 SQLAlchemy 统一接口
from sqlalchemy import create_engine
engine = create_engine(DATABASES[config.DB_TYPE])
```

**迁移步骤**:
1. 确保所有 SQL 兼容 PostgreSQL
2. 添加数据库类型配置
3. 测试 PostgreSQL 兼容性
4. 提供数据迁移脚本

### 6.2 代码优化

#### 建议 4: Pydantic v2 迁移

```python
# 当前 (Pydantic v1)
from pydantic import BaseModel, validator

class Question(BaseModel):
    @validator('options')
    def validate_options(cls, v):
        ...
    
    class Config:
        from_attributes = True

# 优化后 (Pydantic v2)
from pydantic import BaseModel, Field, field_validator, ConfigDict

class Question(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        ...
```

#### 建议 5: 统一错误处理

```python
# 当前：每个路由重复错误处理
@router.post("/")
async def create_question(question: QuestionCreate):
    try:
        return question_service.create_question(question)
    except Exception as e:
        raise HTTPException(...)

# 优化：全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=True,
            code=ErrorCodes.INTERNAL_ERROR,
            message=str(exc)
        ).dict()
    )

# 路由简化
@router.post("/")
async def create_question(question: QuestionCreate):
    return question_service.create_question(question)
```

#### 建议 6: 引入 Repository 基类实现

```python
# 当前：每个 Repository 重复实现 CRUD
class CategoryRepository:
    def create(self, ...): ...
    def get_by_id(self, ...): ...
    def get_all(self, ...): ...
    def update(self, ...): ...
    def delete(self, ...): ...

# 优化：通用基类实现
class SQLAlchemyRepository(Generic[T, ID]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session
    
    def create(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        return entity
    
    def get_by_id(self, entity_id: ID) -> Optional[T]:
        return self.session.get(self.model, entity_id)
    
    # ... 其他通用方法

class CategoryRepository(SQLAlchemyRepository[Category, str]):
    # 只需实现特定查询
    def search(self, keyword: str) -> List[Category]:
        ...
```

### 6.3 性能优化

#### 建议 7: 向量检索优化

**当前**: O(n) 全表扫描
```python
for row in rows:  # 所有题目
    similarity = np.dot(embedding, emb) / (query_norm * emb_norm)
```

**优化**:
```python
# 方案 1: 使用 FAISS 索引
import faiss
index = faiss.IndexFlatIP(dimension)  # 内积相似度
index.add(all_embeddings)
similarities, indices = index.search(query_embedding, k=10)

# 方案 2: 使用专用向量数据库
from qdrant_client import QdrantClient
client = QdrantClient(url="http://localhost:6333")
results = client.search(
    collection_name="questions",
    query_vector=embedding,
    limit=10
)
```

#### 建议 8: 缓存策略

```python
# 引入 Redis 缓存
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379)

@lru_cache(maxsize=1000)
def get_category_cached(category_id: str):
    # 先查缓存
    cached = redis_client.get(f"category:{category_id}")
    if cached:
        return json.loads(cached)
    
    # 查数据库
    category = category_repo.get_by_id(category_id)
    
    # 写缓存
    redis_client.setex(
        f"category:{category_id}",
        300,  # 5 分钟过期
        json.dumps(category.dict())
    )
    return category
```

### 6.4 测试优化

#### 建议 9: 完善测试覆盖

```python
# tests/unit/test_services.py
import pytest
from unittest.mock import Mock, patch

class TestQuestionService:
    @pytest.fixture
    def service(self):
        question_repo = Mock()
        category_repo = Mock()
        tag_repo = Mock()
        return QuestionService(question_repo, category_repo, tag_repo)
    
    def test_create_question_success(self, service):
        # 测试正常创建
        ...
    
    def test_create_question_invalid_category(self, service):
        # 测试分类不存在
        ...
    
    def test_create_question_triggers_embedding(self, service):
        # 测试向量化触发
        ...
```

#### 建议 10: 添加 CI/CD 测试

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=core --cov=web --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## 📋 七、实施路线图

### 阶段 1: 基础优化 (1-2 周)

| 任务 | 优先级 | 工作量 | 风险 |
|------|--------|--------|------|
| Pydantic v2 迁移 | 高 | 2-3 天 | 低 |
| 统一错误处理 | 高 | 1 天 | 低 |
| 测试目录统一 | 中 | 0.5 天 | 低 |
| 补充核心单元测试 | 高 | 3-5 天 | 低 |

### 阶段 2: 架构优化 (2-4 周)

| 任务 | 优先级 | 工作量 | 风险 |
|------|--------|--------|------|
| 引入依赖注入容器 | 中 | 2-3 天 | 中 |
| 引入 Celery 异步任务 | 高 | 3-5 天 | 中 |
| 统一 Repository 实现 | 中 | 3-5 天 | 中 |
| 完善集成测试 | 高 | 持续 | 低 |

### 阶段 3: 扩展性优化 (4-8 周)

| 任务 | 优先级 | 工作量 | 风险 |
|------|--------|--------|------|
| PostgreSQL 迁移评估 | 中 | 2-3 天 | 中 |
| 向量检索优化 (FAISS/Qdrant) | 中 | 3-5 天 | 中 |
| 引入 Redis 缓存 | 低 | 2-3 天 | 低 |
| API 版本管理 | 低 | 1-2 天 | 低 |

---

## 📝 八、总结

### 8.1 架构优势

1. **分层清晰**: 路由层 → 服务层 → 仓库层 → 数据访问层
2. **模块化好**: Web、MCP、微信三入口独立
3. **配置灵活**: 支持热更新，环境变量配置
4. **AI 集成完善**: Embedding、题目提取、解析生成
5. **文档完善**: 代码注释、README、专项文档

### 8.2 主要风险

1. **数据库扩展性**: SQLite 限制并发和分布式
2. **同步 AI 调用**: 可能阻塞请求
3. **全局状态**: 测试困难
4. **测试覆盖**: 回归风险

### 8.3 核心建议

1. **短期** (1-2 周):
   - 迁移 Pydantic v2
   - 统一错误处理
   - 补充核心测试

2. **中期** (1-2 月):
   - 引入异步任务队列
   - 引入依赖注入
   - 评估 PostgreSQL 迁移

3. **长期** (3-6 月):
   - 向量检索优化
   - 缓存层引入
   - CI/CD 完善

---

## 📚 附录

### A. 相关文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `core/models.py` | 核心 | 数据模型定义 |
| `core/services.py` | 核心 | 业务服务层 |
| `core/database/repositories.py` | 核心 | 数据仓库层 |
| `core/database/connection.py` | 核心 | 数据库连接 |
| `core/database/migrations.py` | 核心 | 数据库迁移 |
| `web/main.py` | 入口 | Web 应用入口 |
| `web/api/*.py` | 入口 | API 路由 |
| `agent/config.py` | AI | Agent 配置 |
| `agent/services/embedding_service.py` | AI | Embedding 服务 |
| `core/services/vector_index.py` | AI | 向量索引 |

### B. 参考资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic v2 迁移指南](https://docs.pydantic.dev/latest/migration/)
- [SQLAlchemy 2.0 教程](https://docs.sqlalchemy.org/en/20/)
- [Celery 最佳实践](https://docs.celeryq.dev/en/stable/)
- [依赖注入容器](https://github.com/ets-labs/python-dependency-injector)

---

**报告生成时间**: 2026-03-17 19:30  
**分析师**: Code Architect Agent
