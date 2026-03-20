# 题库管理系统 - 架构分析报告

**报告日期**: 2026-03-17  
**项目名称**: question-bank-system  
**GitHub**: https://github.com/superno188462/question-bank-system  
**代码规模**: 8,321 行 (45 个 Python 文件)  
**分析范围**: 模块划分、依赖关系、设计模式、架构质量评估

---

## 执行摘要

### 系统概述

题库管理系统是一个多入口、分层架构的在线题库管理平台，采用 FastAPI + SQLite 技术栈，支持 Web 管理界面、MCP 协议接入、微信小程序三端访问。

### 架构评分总览

| 评估维度 | 评分 | 等级 | 说明 |
|---------|------|------|------|
| 模块划分 | 4.0/5.0 | 良好 | 分层清晰，职责分离良好 |
| 依赖管理 | 3.0/5.0 | 中等 | 存在循环依赖风险，全局状态过多 |
| 设计模式 | 4.0/5.0 | 良好 | 使用了多种经典模式，实现质量高 |
| 可扩展性 | 3.0/5.0 | 中等 | 多入口设计好，但数据库选型限制扩展 |
| 可维护性 | 4.0/5.0 | 良好 | 代码结构清晰，文档完善 |
| 测试性 | 2.0/5.0 | 较差 | 全局状态导致测试困难，覆盖率低 |

**综合评分**: 3.3/5.0

---

## 一、系统架构概览

### 1.1 整体架构图

```
+-----------------------------------------------------------------------------+
|                           客户端层 (Client Layer)                            |
+----------------------+----------------------+-------------------------------+
|   Web 管理界面        |   MCP Server         |   微信小程序后端               |
|   (FastAPI + Jinja2) |   (FastAPI)          |   (FastAPI)                   |
|   Port: 8000         |   Port: 8002         |   Port: 8001                  |
+----------+-----------+----------+-----------+--------------+----------------+
           |                      |                          |
           +----------------------+--------------------------+
                                  |
                          +-------v-------+
                          |   API 路由层   |
                          |  (web/api/)   |
                          +-------+-------+
                                  |
                          +-------v-------+
                          |   业务服务层   |
                          |  (services)   |
                          +-------+-------+
                                  |
                          +-------v-------+
                          |   数据仓库层   |
                          | (repositories)|
                          +-------+-------+
                                  |
                          +-------v-------+
                          |   数据访问层   |
                          | (connection)  |
                          +-------+-------+
                                  |
                          +-------v-------+
                          | SQLite 数据库  |
                          | (data/*.db)   |
                          +---------------+

+-----------------------------------------------------------------------------+
|                           AI 能力层 (AI Capability Layer)                    |
+----------------------+----------------------+-------------------------------+
|   文档提取器          |   图像提取器          |   Embedding 服务               |
|   (DocumentExtractor)|   (ImageExtractor)   |   (EmbeddingService)          |
+----------------------+----------------------+-------------------------------+
                                  |
                          +-------v-------+
                          |  向量索引服务  |
                          | (VectorIndex) |
                          +---------------+
```

### 1.2 技术栈

| 层级 | 技术选型 | 评估 |
|------|---------|------|
| Web 框架 | FastAPI | 优秀 - 异步支持、自动文档 |
| 数据库 | SQLite | 受限 - 开发友好，并发有限 |
| 数据验证 | Pydantic | 优秀 - 类型安全 |
| AI 接入 | OpenAI 兼容 API | 优秀 - 支持多提供商 |
| 向量计算 | numpy | 合适 - 轻量级 |
| 模板引擎 | Jinja2 | 标准 - 成熟稳定 |

---

## 二、模块划分分析

### 2.1 模块结构

```
question-bank-system/
├── core/              # 核心业务模块 (1,500 行)
│   ├── models.py      # 数据模型 (450 行)
│   ├── services.py    # 业务服务层 (280 行)
│   └── database/      # 数据访问层
│       ├── connection.py    # 数据库连接 (120 行)
│       ├── repositories.py  # 数据仓库 (520 行)
│       └── migrations.py    # 数据库迁移 (150 行)
│
├── web/               # Web 入口模块 (800 行)
│   ├── main.py        # Web 应用入口
│   └── api/           # API 路由 (5 个文件)
│
├── agent/             # AI Agent 模块 (1,000 行)
│   ├── config.py      # Agent 配置 (热更新)
│   ├── services/      # AI 服务
│   ├── extractors/    # 提取器
│   └── generators/    # 生成器
│
├── mcp_server/        # MCP 入口模块 (100 行)
├── wechat/            # 微信入口模块 (150 行)
├── shared/            # 共享模块 (100 行)
├── scripts/           # 脚本工具
├── tests/             # 测试模块 (覆盖率~20%)
└── config/            # 配置文件
```

### 2.2 模块职责分析

| 模块 | 职责 | 内聚度 | 耦合度 | 评价 |
|------|------|--------|--------|------|
| core/ | 核心业务逻辑、数据访问 | 高 | 中 | 职责清晰，分层合理 |
| web/ | Web 入口、API 路由 | 高 | 中 | 结构标准 |
| agent/ | AI 能力、题目提取 | 高 | 高 | 与 core 耦合较紧 |
| mcp_server/ | MCP 协议接入 | 中 | 低 | 独立性好 |
| wechat/ | 微信小程序 API | 中 | 低 | 独立性好 |
| shared/ | 共享配置和工具 | 高 | 低 | 设计合理 |
| tests/ | 测试代码 | 低 | - | 覆盖不足 |

---

## 三、依赖关系分析

### 3.1 模块依赖图

```
                    shared/ (配置)
                        |
                        v
                    core/ (核心)
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
      web/        mcp_server/       wechat/
        |               |               |
        +---------------+---------------+
                        |
                        v
                    agent/ (AI)
```

### 3.2 依赖矩阵

| 依赖模块 | shared | core | web | agent | mcp | wechat |
|---------|--------|------|-----|-------|-----|--------|
| shared  | -      |      |     |       |     |        |
| core    | Y      | -    |     | ~     |     |        |
| web     | Y      | Y    | -   | ~     |     |        |
| agent   | Y      | Y    |     | -     |     |        |
| mcp     | Y      | Y    |     |       | -   |        |
| wechat  | Y      | Y    |     |       |     | -      |

图例: Y=直接依赖，~=间接依赖

### 3.3 依赖问题分析

#### 问题 1: 循环依赖风险 (高优先级)

core/services.py 依赖 agent/config.py 和 agent/services/embedding_service.py

**风险**: 核心业务逻辑与 AI 能力耦合，违反依赖倒置原则

**建议**: 引入接口抽象，通过依赖注入解耦

#### 问题 2: 全局状态过多 (高优先级)

- db = DatabaseConnection() (全局单例)
- category_repo/tag_repo/question_repo (全局实例)
- question_service (全局实例)

**风险**: 测试时难以 mock，状态难以隔离

**建议**: 使用依赖注入容器管理实例

#### 问题 3: 路径硬编码 (中优先级)

sys.path.insert(0, os.path.dirname(...)) 在多个入口重复

**建议**: 使用项目根目录配置统一管理

---

## 四、设计模式使用分析

### 4.1 已实现的设计模式

| 模式 | 位置 | 质量 | 说明 |
|------|------|------|------|
| 单例模式 | DatabaseConnection | 优秀 | 线程安全，实现规范 |
| 工厂模式 | create_web_app() | 良好 | 应用创建封装 |
| 仓库模式 | repositories.py | 良好 | 接口统一 |
| 服务层模式 | services.py | 良好 | 职责清晰 |
| 延迟初始化 | QuestionService | 良好 | 性能优化 |
| 配置热更新 | AgentConfig | 优秀 | 文件修改时间检测 |
| 上下文管理器 | transaction() | 良好 | 事务管理规范 |
| 策略模式 | DocumentExtractor | 中等 | 隐式使用 |

### 4.2 核心模式详解

#### 单例模式 (DatabaseConnection)

```python
class DatabaseConnection:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_connection()
        return cls._instance
```

评价: 双重检查锁定，线程安全，使用 threading.local() 实现线程隔离

#### 配置热更新 (AgentConfig)

```python
class AgentConfig:
    _config_cache = None
    _cache_mtime = 0
    
    @classmethod
    def _load_config(cls, force_refresh=False):
        if not force_refresh and cls._config_cache is not None:
            current_mtime = cls.CONFIG_FILE.stat().st_mtime
            if current_mtime == cls._cache_mtime:
                return cls._config_cache
        # 加载配置...
```

评价: 文件修改时间检测，自动刷新，缓存机制，这是项目中实现最优秀的模式

#### 仓库模式 (Repository)

```python
class Repository(Generic[T, ID], ABC):
    @abstractmethod
    def create(self, entity: Any) -> T: ...
    @abstractmethod
    def get_by_id(self, entity_id: ID) -> Optional[T]: ...
    @abstractmethod
    def update(self, entity_id: ID, update_data: Any) -> Optional[T]: ...
    @abstractmethod
    def delete(self, entity_id: ID) -> bool: ...
    @abstractmethod
    def search(self, keyword: str) -> List[T]: ...
```

评价: 使用泛型抽象，类型安全，但部分 Repository 未继承基类

---

## 五、SOLID 原则评估

| 原则 | 评分 | 问题 |
|------|------|------|
| SRP 单一职责 | 3/5 | QuestionService 职责过多 |
| OCP 开闭原则 | 3/5 | 文档读取器扩展性差 |
| LSP 里氏替换 | 4/5 | 继承规范 |
| ISP 接口隔离 | 3/5 | Repository 接口过大 |
| DIP 依赖倒置 | 2/5 | 依赖具体类而非抽象 |

---

## 六、架构度量指标

### 6.1 代码复杂度

| 模块 | 平均函数行数 | 最大函数行数 | 复杂度 |
|------|-------------|-------------|--------|
| core/models.py | 15 | 40 | 低 |
| core/services.py | 25 | 60 | 中 |
| core/database/repositories.py | 30 | 80 | 中 |
| web/api/*.py | 15 | 30 | 低 |
| agent/extractors/*.py | 25 | 50 | 中 |

### 6.2 测试覆盖度

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| core/ | ~30% | 不足 |
| web/ | ~20% | 不足 |
| agent/ | ~10% | 严重不足 |
| mcp_server/ | 0% | 无测试 |
| wechat/ | 0% | 无测试 |

**整体覆盖率**: ~20% (远低于推荐的 80%)

---

## 七、架构风险识别

### 高风险问题

| ID | 风险 | 影响 | 优先级 |
|----|------|------|--------|
| R-001 | SQLite 并发限制 | 多用户写入冲突 | 高 |
| R-002 | 全局状态过多 | 测试困难，难以维护 | 高 |
| R-003 | 同步 AI 调用阻塞 | 请求超时 | 高 |
| R-004 | 循环依赖风险 | 重构困难 | 高 |

### 中风险问题

| ID | 风险 | 影响 | 优先级 |
|----|------|------|--------|
| R-005 | 测试覆盖不足 | 回归风险 | 中 |
| R-006 | 向量检索 O(n) | 大数据量性能差 | 中 |
| R-007 | Pydantic v1/v2 混合 | 升级困难 | 中 |

---

## 八、优化建议

### 短期优化 (1-2 周)

| 建议 | 优先级 | 工作量 | 收益 |
|------|--------|--------|------|
| 统一 Pydantic v2 API | 高 | 2-3 天 | 减少技术债务 |
| 引入全局异常处理器 | 高 | 1 天 | 减少重复代码 |
| 补充核心单元测试 | 高 | 3-5 天 | 提高测试覆盖 |

### 中期优化 (1-2 月)

| 建议 | 优先级 | 工作量 | 收益 |
|------|--------|--------|------|
| 引入依赖注入容器 | 高 | 2-3 天 | 解耦模块，便于测试 |
| 引入 Celery 异步任务 | 高 | 3-5 天 | 解决 AI 调用阻塞 |
| 拆分 QuestionService | 中 | 2-3 天 | 提高内聚性 |

### 长期优化 (3-6 月)

| 建议 | 优先级 | 工作量 | 收益 |
|------|--------|--------|------|
| PostgreSQL 迁移评估 | 中 | 2-3 天 | 提高并发能力 |
| 向量数据库引入 | 中 | 3-5 天 | 提高检索性能 |
| 引入 Redis 缓存 | 低 | 2-3 天 | 提高响应速度 |

---

## 九、总结

### 架构优势

1. 分层清晰: 路由层 - 服务层 - 仓库层 - 数据访问层
2. 模块化好: Web、MCP、微信三入口独立
3. 配置灵活: 支持热更新，环境变量配置
4. AI 集成完善: Embedding、题目提取、解析生成
5. 设计模式应用: 单例、工厂、仓库、延迟初始化等

### 主要风险

1. 数据库扩展性: SQLite 限制并发和分布式
2. 同步 AI 调用: 可能阻塞请求
3. 全局状态: 测试困难
4. 测试覆盖: 回归风险

### 核心建议

| 时间 | 重点任务 |
|------|---------|
| 短期 (1-2 周) | Pydantic v2 迁移、统一错误处理、补充测试 |
| 中期 (1-2 月) | 引入异步任务队列、依赖注入容器 |
| 长期 (3-6 月) | 向量检索优化、缓存层引入、CI/CD 完善 |

---

**报告生成时间**: 2026-03-17 20:40
**分析师**: Code Architect Agent
