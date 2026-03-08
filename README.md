# DeepResearchWeb

基于 Web 的深度研究 Agent 系统，支持多阶段研究流水线、记忆系统和工具扩展。

## 系统架构

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18, TypeScript, Vite, TailwindCSS, Zustand, TanStack Query |
| 后端 | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Alembic |
| 数据库 | MySQL 8.0, Neo4j 5, Milvus, Qdrant, Redis 7, RabbitMQ |
| 任务队列 | ARQ (基于 Redis 的异步任务队列) |
| 记忆系统 | MemOS (PreferenceTextMemory + TreeTextMemory) |
| LLM | OpenAI API 兼容 |

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐   │
│  │  Login  │  │  Chat   │  │ Config  │  │  DeepResearch   │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP / SSE
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                      API Layer                              │ │
│  │  /auth, /sessions, /chat, /memory, /config, /research     │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐   │
│  │ ChatService  │ │ResearchAgent │ │   MemoryService      │   │
│  │   (SSE)      │ │  (Pipeline)  │ │   (MemOS SDK)       │   │
│  └──────────────┘ └──────────────┘ └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   MySQL       │   │    Redis      │   │   RabbitMQ    │
│  (持久数据)    │   │ (缓存/SSE)    │   │  (任务队列)    │
└───────────────┘   └───────────────┘   └───────────────┘
        │                                       │
        ▼                                       ▼
┌───────────────┐                      ┌───────────────┐
│   Neo4j       │                      │    ARQ Worker │
│  (图数据)     │                      │ (异步任务处理)  │
└───────────────┘                      └───────────────┘
        │
        ▼
┌───────────────┐   ┌───────────────┐
│   Milvus      │   │    Qdrant     │
│ (偏好记忆)     │   │  (树形记忆)    │
└───────────────┘   └───────────────┘
```

## 核心功能

### 1. 用户认证系统
- JWT 认证
- 用户注册/登录
- Session 管理

### 2. 聊天系统
- SSE 流式响应
- 多会话支持
- 消息持久化

### 3. DeepResearch Agent
5 阶段研究流水线：
1. **Triage**: 判断是否需要澄清
2. **Plan**: 将复杂问题分解为子问题
3. **Search**: 多源并行检索（Web、Memory、MCP、Tools）
4. **Synthesize**: 合并结果，最多迭代 3 次
5. **Report**: 生成带引用的最终报告

### 4. 记忆系统 (MemOS)

#### 偏好记忆 (PreferenceTextMemory)
- **向量存储**: Milvus
- **Embedding**: 支持 BAAI/bge-large-zh-v1.5 等模型
- **类型**: 显式偏好 + 隐式偏好

#### 树形记忆 (TreeTextMemory)
- **向量索引**: Qdrant
- **图存储**: Neo4j
- **结构**: 树形知识点结构

#### 记忆检索
- 向量检索 + 图检索 (Hybrid Search)
- Rerank: 支持 BAAI/bge-reranker-base 等模型
- 记忆反馈修正

### 5. 工具扩展系统
- Tools: 自定义工具
- Skills: 技能系统
- MCP: Model Context Protocol 支持

## 快速开始

### 环境要求
- Docker & Docker Compose
- Node.js 18+ (前端开发)
- Python 3.11+ (后端开发)

### 启动服务

```bash
# 克隆项目
git clone https://github.com/your-repo/DeepResearchWeb.git
cd DeepResearchWeb

# 启动所有服务
docker-compose up -d
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

### 开发模式

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 环境变量

### 核心配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | - | MySQL 连接 |
| `REDIS_URL` | - | Redis 连接 |
| `NEO4J_URI` | bolt://neo4j:7687 | Neo4j 连接 |
| `MILVUS_HOST` | milvus-standalone | Milvus 主机 |
| `QDRANT_HOST` | qdrant | Qdrant 主机 |

### LLM 配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENAI_API_KEY` | - | OpenAI API Key |
| `LLM_BASE_URL` | https://api.openai.com/v1 | API 地址 |
| `LLM_MODEL` | gpt-4o-mini | 模型名称 |

### MemOS 记忆配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MEMOS_EXPLICIT_PREF_COLLECTION` | explicit_preference | 显式偏好集合 |
| `MEMOS_IMPLICIT_PREF_COLLECTION` | implicit_preference | 隐式偏好集合 |
| `MEMOS_TREE_COLLECTION` | tree_memory | 树形记忆集合 |
| `MEMOS_EMBEDDING_MODEL` | BAAI/bge-large-zh-v1.5 | Embedding 模型 |
| `MEMOS_EMBEDDING_URL` | - | Embedding API 地址 |
| `MEMOS_EMBEDDING_API_KEY` | - | Embedding API Key |
| `MEMOS_RERANKER_MODEL` | BAAI/bge-reranker-base | Reranker 模型 |
| `MEMOS_RERANKER_URL` | - | Reranker API 地址 |
| `MEMOS_RERANKER_API_KEY` | - | Reranker API Key |

## API 端点

### 认证
- `POST /api/v1/auth/register` - 注册
- `POST /api/v1/auth/login` - 登录
- `GET /api/v1/auth/me` - 获取当前用户

### 会话
- `GET /api/v1/sessions` - 获取会话列表
- `POST /api/v1/sessions` - 创建会话
- `DELETE /api/v1/sessions/{id}` - 删除会话

### 聊天
- `GET /api/v1/chat/stream` - SSE 流式聊天

### 记忆
- `GET /api/v1/memory/search` - 搜索记忆
- `POST /api/v1/memory/tree` - 添加树形记忆
- `POST /api/v1/memory/feedback` - 记忆反馈

### 研究
- `POST /api/v1/research/start` - 开始研究
- `GET /api/v1/research/{task_id}` - 获取研究状态

## 项目结构

```
DeepResearchWeb/
├── backend/              # FastAPI 应用
│   ├── app/
│   │   ├── main.py       # 入口
│   │   ├── config.py     # 配置
│   │   ├── api/v1/      # API 路由
│   │   ├── core/         # 中间件/异常
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/     # Pydantic schema
│   │   ├── services/    # 业务逻辑
│   │   ├── agents/      # Agent 实现
│   │   ├── workers/     # ARQ worker
│   │   └── db/          # 数据库连接
│   └── requirements.txt
├── frontend/             # React 应用
│   ├── src/
│   │   ├── api/         # API 客户端
│   │   ├── components/  # UI 组件
│   │   ├── hooks/       # React hooks
│   │   ├── stores/      # Zustand store
│   │   └── types/       # TypeScript 类型
│   └── package.json
├── docker-compose.yml    # 服务编排
└── README.md
```







## 许可证

Apache License 2.0
