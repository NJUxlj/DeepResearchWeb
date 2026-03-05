# DeepResearchWeb 项目指南

## 项目概述

DeepResearchWeb 是一个网页端的深度研究 Agent 系统，具备 Chatbot 交互、深度研究（DeepResearch）、工具调用、Skills/MCP 扩展能力，并集成 MemOS 记忆系统实现用户偏好和知识树记忆。

**当前状态**: 项目处于规划设计阶段，尚未开始实际开发。

---

## Agent Team 配置

本项目配置了专业的 Agent Team 来协同开发，采用 **Multi-Subagent** 架构：

### 团队结构

```
deepresearchweb-lead (主协调 Agent)
├── architect (架构师)
├── backend-dev (后端开发专家)
├── frontend-dev (前端开发专家)
└── devops (DevOps 工程师)
```

### 启动 Agent Team

```bash
# 启动主协调 Agent
kimi --agent-file .claude/agents/deepresearchweb-lead/agent.yaml
```

### 各 Agent 职责

| Agent | 职责 | 适用任务 |
|-------|------|---------|
| **deepresearchweb-lead** | 任务分析、智能委派、结果整合 | 任何开发需求，自动分发给专业 Agent |
| **architect** | 技术选型、架构设计、接口定义 | 数据库设计、API 设计、技术方案 |
| **backend-dev** | FastAPI 后端开发 | API 实现、ORM 模型、业务逻辑 |
| **frontend-dev** | React 前端开发 | UI 组件、页面布局、交互实现 |
| **devops** | Docker 部署配置 | docker-compose、Dockerfile、环境配置 |

### 使用示例

**场景 1: 实现一个新功能**
```
用户: 我需要实现用户认证系统，包括注册、登录、JWT 验证

lead → 分析任务
    ├── architect: 设计数据库模型和 API 接口
    ├── backend-dev: 实现 FastAPI 认证端点
    └── frontend-dev: 开发登录/注册页面
```

**场景 2: 添加 DeepResearch 功能**
```
用户: 实现 DeepResearch Agent 的核心流程

lead → 委派给 architect 设计工作流
    → 委派给 backend-dev 实现 Agent 逻辑
    → 委派给 frontend-dev 实现进度展示 UI
```

**场景 3: 部署配置**
```
用户: 配置 Docker Compose 部署环境

lead → 委派给 devops 编写配置
    → 协调 backend-dev 提供依赖信息
    → 协调 frontend-dev 确认构建配置
```

---

## 技术栈

### 后端
- **语言**: Python 3.11+
- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **迁移**: Alembic
- **认证**: JWT + passlib

### 前端
- **语言**: TypeScript
- **框架**: React 18
- **构建工具**: Vite
- **样式**: TailwindCSS + shadcn/ui
- **状态管理**: Zustand
- **数据请求**: TanStack Query (React Query)

### 数据存储
| 服务 | 用途 | 部署方式 |
|------|------|----------|
| MySQL 8.0 | 用户信息、会话、配置 | Docker |
| Milvus | 偏好记忆向量存储 | Docker |
| Qdrant v1.15+ | 树形记忆向量索引 | Docker |
| Neo4j 5 | 树形记忆图存储 | Docker |
| Redis 7 | 缓存、队列、SSE 状态、限流 | Docker |
| RabbitMQ | MemOS Scheduler 异步调度 | Docker |

### 外部服务
- **LLM**: OpenAI / vLLM
- **搜索**: Tavily / SerpAPI / Brave Search MCP / Firecrawl MCP
- **记忆系统**: MemOS SDK (PreferenceTextMemory + TreeTextMemory)

### 任务队列
- **ARQ**: 异步任务队列（基于 Redis）

---

## 项目结构

```
DeepResearchWeb/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py             # FastAPI 入口
│   │   ├── config.py           # 配置管理
│   │   ├── api/v1/             # API 路由
│   │   ├── core/               # 核心组件
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── schemas/            # Pydantic 模型
│   │   ├── services/           # 业务服务层
│   │   ├── agents/             # Agent 实现
│   │   ├── workers/            # ARQ Worker
│   │   └── db/                 # 数据库连接 & 迁移
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
│
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api/                # API 调用层
│   │   ├── components/         # UI 组件
│   │   ├── hooks/              # 自定义 Hooks
│   │   ├── stores/             # Zustand 状态管理
│   │   └── types/              # TypeScript 类型定义
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── docker-compose.yml          # Docker 编排配置
├── .env                        # 环境变量
├── plans/                      # 开发方案文档
│   └── deepresearchweb_开发方案_0943c7a0.plan.md
└── .claude/agents/             # Agent Team 配置
    ├── deepresearchweb-lead/
    ├── architect/
    ├── backend-dev/
    ├── frontend-dev/
    └── devops/
```

---

## 构建和运行

### 前置要求
- Docker & Docker Compose
- Python 3.11+ (本地开发)
- Node.js 18+ (本地开发)

### 快速启动（使用 Docker）

```bash
# 1. 启动所有服务（数据库 + 后端 + 前端）
docker-compose up -d

# 2. 查看服务状态
docker-compose ps

# 3. 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 本地开发

**后端开发:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --port 8000

# 启动 ARQ Worker（另一个终端）
arq app.workers.research_worker.WorkerSettings
```

**前端开发:**
```bash
cd frontend
npm install
npm run dev
```

---

## 代码规范

### Python 后端
- 遵循 PEP 8 规范
- 使用 `black` 进行代码格式化
- 使用 `isort` 管理 import
- 使用 `mypy` 进行类型检查
- 异步函数使用 `async/await` 语法
- 数据库模型使用 SQLAlchemy 2.0 风格

### TypeScript 前端
- 使用 ESLint + Prettier 进行代码检查
- 组件使用函数式组件 + Hooks
- 类型定义优先使用 `interface` 而非 `type`
- API 调用统一封装在 `api/` 目录
- 状态管理使用 Zustand，避免过度使用

---

## 测试

### 后端测试
```bash
# 运行单元测试
pytest

# 运行特定模块测试
pytest tests/test_research_agent.py

# 覆盖率报告
pytest --cov=app --cov-report=html
```

### 前端测试
```bash
# 运行测试
npm test

# 运行 e2e 测试
npm run test:e2e
```

---

## DeepResearch 工作流

系统采用四阶段流水线设计：

1. **Triage（分流）**: 判断用户问题是否需要澄清
2. **Plan（规划）**: 将复杂问题拆解为可独立检索的子问题
3. **Search（检索）**: 并行执行多源检索（Web、记忆、MCP、工具）
4. **Synthesize（综合）**: 综合所有结果，判断信息是否充分（最多 3 轮迭代）
5. **Report（报告）**: 生成带引用标记的最终报告

### 引用系统
- 引用格式: `[n]` 上标样式
- 支持来源类型: web | mcp | memory | document
- 前端点击引用可展开右侧引用面板，高亮对应数据卡片

---

## 并发与性能

### 并发参数配置
| 组件 | 配置 |
|------|------|
| API Workers | gunicorn + 4 uvicorn workers |
| ARQ Workers | 8 workers，最大并发研究任务 50 |
| MySQL 连接池 | pool_size=20, max_overflow=30 |
| Neo4j 连接池 | max_connection_pool_size=50 |
| Redis 连接池 | max_connections=100 |
| LLM 并发 | 全局信号量限制 20 |
| MCP 进程池 | 最大 20 进程，空闲 5min 回收 |

### 缓存策略
- 搜索结果缓存: Redis，key=hash(query+params)，TTL=30min
- 目标缓存命中率: > 30%

---

## 环境变量

创建 `.env` 文件，包含以下配置：

```env
# 数据库
MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=deepresearch

# Neo4j
NEO4J_PASSWORD=your_password

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM
OPENAI_API_KEY=sk-...
LLM_BASE_URL=https://api.openai.com/v1

# 搜索
TAVILY_API_KEY=tvly-...
SERPAPI_KEY=...

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 开发阶段

| 阶段 | 内容 | 状态 |
|------|------|------|
| P0 | 项目脚手架 + Docker 环境 + 用户系统 + 基础 Chat UI | 🔴 待开始 |
| P1 | DeepResearch Agent 核心流程 | 🔴 待开始 |
| P2 | ARQ 任务队列 + Redis Pub/Sub SSE + 并发控制 | 🔴 待开始 |
| P3 | MemOS 集成 | 🔴 待开始 |
| P4 | 工具调用 + Skills + MCP 系统 | 🔴 待开始 |
| P5 | 引用面板交互 + 研究进度展示 | 🔴 待开始 |
| P6 | 并发压测 + 部署文档完善 | 🔴 待开始 |

---

## 关键依赖

### 后端
```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
gunicorn>=21.2.0
sqlalchemy>=2.0.0
alembic>=1.13.0
pymysql>=1.1.0
pyjwt>=2.8.0
passlib[bcrypt]>=1.7.4
redis[hiredis]>=5.0.0
arq>=0.25.0
mcp>=0.4.0
httpx>=0.26.0
openai>=1.12.0
tavily-python>=0.3.0
```

### 前端
```
react@^18.2.0
react-dom@^18.2.0
react-router-dom@^6.22.0
@tanstack/react-query@^5.20.0
zustand@^4.5.0
tailwindcss@^3.4.0
axios@^1.6.0
react-markdown@^9.0.0
remark-gfm@^4.0.0
lucide-react@^0.330.0
```

---

## 安全注意事项

1. **API 密钥**: 永远不要将 API 密钥提交到代码仓库
2. **JWT 密钥**: 生产环境使用强随机密钥
3. **CORS**: 生产环境限制允许的源
4. **速率限制**: 已集成基于 Redis 的限流，防止滥用
5. **SQL 注入**: 使用 SQLAlchemy ORM，避免裸 SQL
6. **XSS**: 前端对用户输入进行适当的转义和过滤

---

## 参考文档

- [DeepResearchWeb 开发方案](./plans/deepresearchweb_开发方案_0943c7a0.plan.md)
- FastAPI 文档: https://fastapi.tiangolo.com/
- MemOS SDK 文档: 本地路径 `/Users/xiniuyiliao/Desktop/code/MemOS`
- MCP 协议文档: https://modelcontextprotocol.io/
