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
