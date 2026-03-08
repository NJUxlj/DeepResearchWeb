# DeepResearchWeb - Agent Lead Memory

## 待处理任务

### Phase 3: MemOS 集成优化 - 已完成

已根据 MemOS 官方 SDK 文档更新代码：

1. **MemOS 包名**: `MemoryOS` (PyPI)
2. **正确的类**:
   - `PreferenceTextMemory` + `PreferenceTextMemoryConfig`
   - `TreeTextMemory` + `TreeTextMemoryConfig`
   - `SimpleMemFeedback`
3. **配置工厂**:
   - `VectorDBConfigFactory` - 向量数据库配置
   - `EmbedderConfigFactory` - Embedding 配置
   - `LLMConfigFactory` - LLM 配置
   - `RerankerConfigFactory` - Reranker 配置

4. **关键配置参数**:
   - **Milvus**: 需要 `uri`, `collection_name` (列表), `user_name`, `password`
   - **Qdrant**: 需要 `host`, `port`, `collection_name`
   - **Embedding**: 支持 `universal_api`, `ollama`, `sentence_transformer`, `ark`
   - **Reranker**: 支持 `universal_api` 等后端

## 已完成更新

1. **memory_service.py**: 完全重写，使用正确的 MemOS SDK 配置结构
2. **requirements.txt**: 添加 `MemoryOS>=2.0.0`
3. **config.py**: 添加 `MILVUS_USER` 和 `MILVUS_PASSWORD` 配置
4. **.env**: 添加 Milvus 认证配置

## 当前状态

- 所有服务正常运行
- 前端注册/登录已修复
- MemOS SDK 集成代码已更新
- 需要在 Docker 环境中安装 MemoryOS 包后才能测试

## MemOS 配置说明

MemOS 是一个 REST API 服务器 + Python SDK:
- 可以独立运行 (`uvicorn memos.api.server_api:app`)
- 也可以作为 Python 库导入使用
- 配置使用 Pydantic 模型 (ConfigFactory 模式)
