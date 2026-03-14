# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DeepResearchWeb is a web-based deep research agent system with:
- Chatbot interaction interface
- DeepResearch capability using multi-stage pipeline (Triage → Plan → Search → Synthesize → Report)
- Tool calling and Skills/MCP extension support
- MemOS memory system integration (preference + tree memory)

**Status**: Project in early development phase (P0 scaffold phase).



## Sub-Agent Workflow

1. **deepresearchweb_lead** - Receives task, invokes plan_decomposer first to break down the master plan
2. **plan_decomposer** - Breaks down master plan into executable sub-plans
3. **architect** - Designs system architecture, data models, and API contracts
4. **backend_dev** - Implements backend logic, API endpoints, database models
5. **frontend_dev** - Builds user interface and integrates with backend APIs
6. **devops** - Manages Docker configuration, deployment, and environment

### Sub-Agents Table

| Agent Name | Description | Capabilities | Use Case Examples |
|------------|-------------|--------------|-------------------|
| **deepresearchweb-lead** | 项目主协调 Agent，负责统筹整个项目的开发工作 | 任务分析与分解、智能委派给其他 Agent、结果整合、质量控制 | 协调全栈开发任务、设置 Docker 环境、构建多阶段工作流 |
| **plan-decomposer** | 方案分解专家，负责将总开发方案拆分为可执行的子方案 | 阅读总方案、分析模块依赖、拆分方案、输出子方案 | 将 P0-P6 开发方案拆分为独立可执行的子计划 |
| **system-architect** | 系统架构师，负责技术选型和架构设计 | 系统架构设计、技术选型决策、数据库模型设计、API 接口定义 | 设计认证架构、设计 MemOS 存储层、定义 DeepResearch API 契约 |
| **backend-developer** | 后端开发专家，专注于 FastAPI + SQLAlchemy | FastAPI 路由实现、SQLAlchemy 模型编写、服务层逻辑、ARQ Workers、API 端点开发 | 创建 API 端点、编写数据库模型、实现业务逻辑服务、调试后端问题 |
| **frontend-dev** | 前端开发专家，专注于 React + TypeScript | React 组件开发、UI 元素实现、状态管理、数据获取、响应式布局 | 开发 ChatUI、实现引用面板、构建表单组件、设置 TanStack Query |
| **devops-engineer** | DevOps 工程师，专注于 Docker 和部署 | Docker 配置、Docker Compose 编排、环境变量管理、服务依赖配置、CI/CD | 编写 Dockerfile、配置 docker-compose.yml、管理环境变量、故障排查 |

### Agent Delegation Strategy

| Task Type | Delegate To | Example |
|-----------|-------------|---------|
| 分解总方案 | `plan-decomposer` | 将开发方案拆分为子计划 |
| 技术选型/架构设计 | `system-architect` | 设计 DeepResearch 工作流、设计数据库模型 |
| API/后端逻辑 | `backend-developer` | 实现 FastAPI 端点、编写 SQLAlchemy 模型 |
| UI/前端交互 | `frontend-dev` | 开发 ChatUI、引用面板、配置页面 |
| Docker/部署 | `devops-engineer` | 编写 Dockerfile、docker-compose.yml |


## Master Plan

**Overall Development Plan**: `/Users/xiniuyiliao/Desktop/code/DeepResearchWeb/plans/DeepResearchWeb_开发方案.md`

**IMPORTANT**: Before executing any development task, `deepresearchweb_lead` MUST first invoke `plan_decomposer` to break down the master plan into executable sub-plans.


## Architecture


### Tech Stack
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Alembic
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS, Zustand, TanStack Query
- **Data Stores**: MySQL 8.0, Neo4j 5, Milvus, Qdrant, Redis 7, RabbitMQ
- **Task Queue**: ARQ (async task queue based on Redis)

### Project Structure
```
DeepResearchWeb/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py       # FastAPI entry point
│   │   ├── config.py    # Pydantic Settings
│   │   ├── api/v1/      # API routes
│   │   ├── core/        # Middleware, exceptions
│   │   ├── models/      # SQLAlchemy ORM models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── agents/      # Agent implementations
│   │   ├── workers/     # ARQ workers
│   │   ├── utils/       # Utilities (logger, etc.)
│   │   └── db/          # Database connection & migrations
│   └── requirements.txt
├── frontend/             # React application
│   ├── src/
│   │   ├── api/         # API client layer
│   │   ├── components/  # UI components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── stores/      # Zustand stores
│   │   └── types/       # TypeScript types
│   └── package.json
├── docker-compose.yml    # All services orchestration
└── subplans/            # Development phase documentation
```

## Common Commands

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Backend
```bash
cd backend

# Setup virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database migration
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --port 8000

# Run ARQ worker (separate terminal)
arq app.workers.research_worker.WorkerSettings

# Run tests
pytest
pytest tests/test_module.py
pytest --cov=app --cov-report=html
```

### Frontend
```bash
cd frontend
npm install
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```


## Notice about Embedding and Reranker model
- Embedding model: we currently do not have api, so you temporarily need to use string-matching algorithm (jaro + jaccard similarity) to replace it, although you still need to complete the coding for the Embedding API
- Reranker model: we currently do not have api, so you temporarily need to use BM25 to replace it, although you still need to complete the coding for the Reranker API



## Code Standards

### Python Backend
- Follow PEP 8
- Use `black` for formatting, `isort` for imports
- Use `mypy` for type checking
- Async functions use `async/await`
- SQLAlchemy 2.0 async style
- **Logging**: All Python scripts that need to print logs must import `Logger` from `app.utils.logger` in the import section, then initialize a logger with a name representing the current script below the imports

### TypeScript Frontend
- ESLint + Prettier for linting
- Functional components with Hooks
- Use `interface` over `type` for type definitions
- API calls unified in `api/` directory
- Zustand for state management

## Development Workflow

This project uses subplans for phased development (see `subplans/` directory):
- P0: Scaffold + Docker environment + User system + Basic Chat UI
- P1: DeepResearch Agent core
- P2: ARQ task queue + Redis Pub/Sub SSE + concurrency
- P3: MemOS integration
- P4: Tools + Skills + MCP system
- P5: Citation panel + research progress UI
- P6: Performance testing + deployment


### Notice about MemOS
- in phase3 (MemOS integration), you have to first investigate the memos docuements: [MemOS](https://memos-docs.openmem.net/cn/open_source/getting_started/installation), and the MemOS github: [MemOS Github](https://github.com/MemTensor/MemOS)


### DeepResearch Workflow
The system uses a 5-stage pipeline:
1. **Triage**: Determine if user query needs clarification
2. **Plan**: Break complex questions into independent sub-questions
3. **Search**: Parallel multi-source retrieval (Web, Memory, MCP, Tools)
4. **Synthesize**: Combine results, iterate up to 3 times if needed
5. final report with citations

## **Report**: Generate Environment Variables

Key environment variables (see `.env`):
- `DATABASE_URL`: MySQL connection
- `REDIS_URL`: Redis connection
- `NEO4J_URI`, `NEO4J_PASSWORD`: Neo4j
- `MILVUS_HOST`, `MILVUS_PORT`: Milvus vector store
- `QDRANT_HOST`, `QDRANT_PORT`: Qdrant vector index
- `RABBITMQ_URL`: RabbitMQ connection
- `OPENAI_API_KEY`, `LLM_BASE_URL`: LLM configuration
- `TAVILY_API_KEY`, `SERPAPI_KEY`: Search APIs

## Key Files

- `DeepResearchWeb_开发方案.md`: Full project documentation
- `subplans/*.md`: Detailed development plans for each phase


### Logger Utility

The project includes a Logger utility at `backend/app/utils/logger.py`:

```python
from app.utils.logger import get_logger

logger = get_logger("my_module")
logger.log("This is an info message")
logger.log("This is a warning", mode="warning")
logger.log("This is an error", mode="error")
```

Logs are written to `logs/{name}.log` relative to the project root.



## Acceptance Criteria

After code is built, you MUST follow the acceptance criteria to verify the system:

**Acceptance Criteria Document**: `/Users/xiniuyiliao/Desktop/code/DeepResearchWeb/plans/验收标准.md`

### Acceptance Steps

1. **Check Docker containers**: All containers must be running
   ```bash
   docker ps
   ```

2. **Run unit tests**: All tests must pass
   ```bash
   cd backend && pytest
   ```

3. **Run API tests**: All API endpoints must work correctly
   ```bash
   bash scripts/test_all_apis.sh
   ```
   - Test script: `/Users/xiniuyiliao/Desktop/code/DeepResearchWeb/scripts/test_all_apis.sh`
   - Output: `/Users/xiniuyiliao/Desktop/code/DeepResearchWeb/output/`

4. **Check logs**: No errors in logs
   ```bash
   tail -n 200 logs/*.log
   grep -i "error\|exception\|failed" logs/*.log
   ```

If any step fails, fix the issue and re-run the acceptance process until all steps pass.

## Files

- `CLAUDE.md` - This file
- `plans/DeepResearchWeb_开发方案.md` - Master development plan
- `plans/验收标准.md` - Acceptance criteria (CRITICAL - must follow after building code)
- `scripts/test_all_apis.sh` - API test script
- `output/` - Test output directory
