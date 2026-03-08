# Backend Developer Memory

## 项目结构
- 项目根目录: `/Users/xiniuyiliao/Desktop/code/DeepResearchWeb`
- 后端代码: `backend/app/`

## 认证系统实现模式

### 数据库模型 (SQLAlchemy 2.0 async)
- 位置: `backend/app/models/`
- 基础: 继承 `app.db.database.Base`
- 类型标注: 使用 `Mapped[type]` 和 `mapped_column()`
- 关系: 使用 `relationship()` 而非字符串 foreign_keys

### Pydantic Schemas
- 位置: `backend/app/schemas/`
- 响应模型使用 `model_config = {"from_attributes": True}`

### 依赖注入 (deps.py)
- 数据库: `DBDep = Annotated[AsyncSession, Depends(get_db)]`
- 当前用户: `CurrentUserDep = Annotated[User, Depends(get_current_user)]`
- 超级管理员: `SuperuserDep = Annotated[User, Depends(get_current_active_superuser)]`

### JWT 认证 (security.py)
- 使用 `passlib.context.CryptContext` 进行 bcrypt 密码哈希
- 使用 `PyJWT` 进行 JWT 编解码
- Token 有效期: `settings.ACCESS_TOKEN_EXPIRE_MINUTES` (默认30分钟)

### API 端点模式
- 使用 `APIRouter` 分组路由
- 认证端点添加 `tags=["authentication"]`
- 路由前缀使用 `prefix="/auth"`

## DeepResearch Agent 核心

### 5 阶段流水线
1. **Triage**: 判断用户问题是否需要澄清 (Planner 模块)
2. **Planner**: 将复杂问题拆解为可独立检索的子问题
3. **Searcher**: 多源并行检索（Web、记忆、MCP、工具）
4. **Synthesizer**: 综合检索结果，判断信息充分性（最多 3 轮迭代）
5. **Report**: 生成带引用标记的最终报告

### Research Agent 核心文件
- `backend/app/models/research_task.py` - 研究任务数据模型
- `backend/app/schemas/research.py` - Research Schema
- `backend/app/services/research/planner.py` - Planner 模块 (问题分解)
- `backend/app/services/research/searcher.py` - Searcher 模块 (多源检索)
- `backend/app/services/research/synthesizer.py` - Synthesizer 模块 (综合分析)
- `backend/app/services/research/citation.py` - Citation 模块 (引用管理)
- `backend/app/services/research/agent.py` - Research Agent 主逻辑
- `backend/app/agents/research_agent.py` - Research Agent 实现 (继承 BaseAgent)
- `backend/app/api/v1/research.py` - DeepResearch API 端点

### API 接口列表
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/auth/register` | POST | 用户注册 |
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/auth/me` | GET | 获取当前用户 |
| `/api/v1/auth/me` | PUT | 更新当前用户 |
| `/api/v1/sessions` | POST | 创建会话 |
| `/api/v1/sessions` | GET | 获取会话列表 |
| `/api/v1/sessions/{id}` | GET | 获取会话详情 |
| `/api/v1/sessions/{id}` | PUT | 更新会话 |
| `/api/v1/sessions/{id}` | DELETE | 删除会话 |
| `/api/v1/messages` | POST | 创建消息 |
| `/api/v1/messages/by-session/{session_id}` | GET | 获取会话消息 |
| `/api/v1/messages/{id}` | GET | 获取消息详情 |
| `/api/v1/messages/{id}` | PUT | 更新消息 |
| `/api/v1/messages/{id}` | DELETE | 删除消息 |
| `/api/v1/research/tasks` | POST | 创建研究任务 (ARQ) |
| `/api/v1/research/stream` | POST | 流式深度研究 (SSE) |
| `/api/v1/research/tasks/{id}/stream` | GET | SSE 任务进度 (Pub/Sub) |
| `/api/v1/research/tasks/{id}` | GET | 获取研究任务详情 |
| `/api/v1/research/tasks` | GET | 获取研究任务列表 |
| `/api/v1/memory/search` | GET | 搜索记忆 |
| `/api/v1/memory/feedback` | POST | 提交记忆反馈 |
| `/api/v1/memory/tree` | POST | 添加树形记忆 |
| `/api/v1/memory/preference` | POST | 添加偏好记忆 |

### Research 配置
- `max_iterations`: 最大迭代次数 (默认 3, 范围 1-5)
- `search_depth`: 搜索深度 (quick/standard/deep)
- `include_memory`: 是否包含记忆检索
- `include_web`: 是否包含 Web 搜索
- `include_mcp`: 是否包含 MCP 调用

### SSE 事件流
- `plan`: 规划阶段事件
- `search`: 搜索阶段事件
- `synthesis`: 综合阶段事件
- `report`: 报告生成事件
- `complete`: 完成事件
- `error`: 错误事件

### 依赖包
- `openai>=1.12.0` - LLM 调用
- `tavily>=0.3.0` - Web 搜索
- `arq>=0.25.0` - 异步任务队列

## ARQ 任务队列实现

### 核心文件
- `backend/app/workers/research_worker.py` - ARQ Worker 配置和任务函数
- `backend/app/core/redis.py` - Redis 连接、Pub/Sub、缓存、分布式锁
- `backend/app/core/cache.py` - 搜索结果缓存和 LLM 响应缓存
- `backend/app/core/rate_limiter.py` - LLM 并发控制和通用速率限制器

### 配置 (config.py)
- `ARQ_MAX_JOBS`: 最大并发任务数 (默认 50)
- `ARQ_JOB_TIMEOUT`: 任务超时时间 (默认 600 秒)
- `ARQ_MAX_TRIES`: 最大重试次数 (默认 3)
- `ARQ_HEALTH_CHECK_INTERVAL`: 健康检查间隔 (默认 30 秒)
- `CACHE_TTL`: 缓存 TTL (默认 1800 秒)

### Redis 键规范
- `search:<hash>` - 搜索结果缓存
- `research:<task_id>` - 研究任务 Pub/Sub 频道
- `llm:rpm:count` - LLM 每分钟请求计数
- `lock:<name>` - 分布式锁
- `ratelimit:<key>` - 速率限制

### ARQ Worker 启动命令
```bash
arq app.workers.research_worker.WorkerSettings
```

## MemOS 记忆系统集成

### 核心文件
- `backend/app/services/memory_service.py` - MemOS 服务封装
- `backend/app/api/v1/memory.py` - Memory API 端点
- `backend/app/config.py` - MemOS 配置

### MemOS 配置 (config.py)
- `MEMOS_PREF_COLLECTION`: 偏好记忆集合名称 (默认 "explicit_preference")
- `MEMOS_TREE_COLLECTION`: 树形记忆集合名称 (默认 "tree_memory")
- `MEMOS_EMBEDDING_MODEL`: 嵌入模型 (默认 "BAAI/bge-large-zh-v1.5")
- `MEMOS_EMBEDDING_URL`: 嵌入 API URL (可选)

### 嵌入服务 (EmbeddingService)
- 使用 Jaro-Winkler + Jaccard 相似度替代向量嵌入
- `_jaro_similarity()`: 计算 Jaro 相似度
- `_extract_text_features()`: 提取文本特征
- `compute_similarity()`: 组合相似度计算

### 重排序服务 (RerankService)
- 使用 BM25 算法替代向量重排序
- `_bm25_score()`: 计算 BM25 分数
- `rerank()`: 对候选结果重排序

### MemoryService 方法
- `add_preference()`: 从对话提取并存储偏好记忆
- `add_tree_memory()`: 添加树形结构记忆
- `search()`: 联合检索偏好和树形记忆
- `process_feedback()`: 处理用户反馈修正

## 测试实现

### 测试配置文件
- `backend/pytest.ini` - pytest 配置
- `backend/pyproject.toml` - pytest 和 coverage 配置
- `backend/requirements-test.txt` - 测试依赖
- `backend/.env.example` - 环境变量示例

### 测试 Fixtures (conftest.py)
- `event_loop`: 异步事件循环
- `setup_database`: 测试数据库设置
- `db_session`: 数据库会话
- `client`: HTTP 测试客户端
- `mock_user_data`: 模拟用户数据
- `mock_settings`: 模拟配置
- `mock_redis`: 模拟 Redis
- `mock_openai_client`: 模拟 OpenAI 客户端

### 测试标记
- `@pytest.mark.unit`: 单元测试
- `@pytest.mark.api`: API 测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.slow`: 慢速测试

### 测试文件结构
```
backend/tests/
├── __init__.py
├── conftest.py           # pytest fixtures
├── test_auth.py          # 认证 API 测试
├── test_security.py      # 安全模块测试
├── test_chat.py          # 聊天/会话/消息测试
├── test_research.py      # 研究模块测试
├── test_memory.py        # 记忆模块测试
├── models/
│   ├── test_user.py      # User 模型测试
│   └── test_session.py   # Session/Message 模型测试
├── core/
│   └── test_cache.py     # 缓存和速率限制测试
├── api/
│   └── __init__.py
└── services/
    └── __init__.py
```

### 测试命令
```bash
# 安装测试依赖
pip install -r requirements-test.txt

# 运行所有测试
pytest

# 运行特定标记的测试
pytest -m unit
pytest -m api

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```
