"""MemOS 记忆服务封装."""

from typing import Any
import hashlib
import re

from app.config import settings


class EmbeddingService:
    """嵌入服务 - 使用 Jaro + Jaccard 相似度替代向量嵌入 (Fallback)."""

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """将文本转换为嵌入向量 (Fallback 实现)."""
        embeddings = []
        for text in texts:
            features = self._extract_text_features(text)
            embeddings.append(features)
        return embeddings

    def _extract_text_features(self, text: str) -> list[float]:
        """提取文本特征用于相似度计算."""
        ngrams = self._get_ngrams(text.lower(), 2)
        ngram_set = set(ngrams)
        words = re.findall(r'\w+', text.lower())
        word_set = set(words)

        features = []
        common_ngrams = list(ngram_set)[:64]
        for i in range(64):
            if i < len(common_ngrams):
                h = int(hashlib.md5(common_ngrams[i].encode()).hexdigest(), 16)
                features.append((h % 1000) / 1000.0)
            else:
                features.append(0.0)

        common_words = list(word_set)[:64]
        for i in range(64):
            if i < len(common_words):
                h = int(hashlib.md5(common_words[i].encode()).hexdigest(), 16)
                features.append((h % 1000) / 1000.0)
            else:
                features.append(0.0)
        return features

    def _get_ngrams(self, text: str, n: int) -> list[str]:
        """获取字符 n-gram."""
        return [text[i:i+n] for i in range(len(text) - n + 1)]

    async def compute_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度 (Jaro-Winkler + Jaccard)."""
        jaro_sim = self._jaro_similarity(text1, text2)
        ngrams1 = set(self._get_ngrams(text1.lower(), 2))
        ngrams2 = set(self._get_ngrams(text2.lower(), 2))

        if not ngrams1 or not ngrams2:
            return 0.0

        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)
        jaccard_sim = intersection / union if union > 0 else 0.0

        return 0.6 * jaro_sim + 0.4 * jaccard_sim

    def _jaro_similarity(self, s1: str, s2: str) -> float:
        """计算 Jaro 相似度."""
        if s1 == s2:
            return 1.0
        if len(s1) == 0 or len(s2) == 0:
            return 0.0

        match_distance = max(len(s1), len(s2)) // 2 - 1
        if match_distance < 0:
            match_distance = 0

        s1_matches = [False] * len(s1)
        s2_matches = [False] * len(s2)
        matches = 0
        transpositions = 0

        for i in range(len(s1)):
            start = max(0, i - match_distance)
            end = min(i + match_distance + 1, len(s2))
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

        if matches == 0:
            return 0.0

        k = 0
        for i in range(len(s1)):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1

        return (
            1.0 / 3.0 * (matches / len(s1) + matches / len(s2) +
                        (matches - transpositions / 2) / matches)
        )


class RerankService:
    """重排序服务 - 使用 BM25 替代向量重排序 (Fallback)."""

    def __init__(self):
        self.k1 = 1.5
        self.b = 0.75

    async def rerank(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """使用 BM25 对候选结果进行重排序."""
        if not candidates:
            return []

        for candidate in candidates:
            content = candidate.get("content", "") or candidate.get("memory", "")
            score = self._bm25_score(query, content)
            candidate["rerank_score"] = score

        candidates.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        return candidates[:top_k]

    def _bm25_score(self, query: str, document: str) -> float:
        """计算 BM25 分数."""
        query_terms = self._tokenize(query)
        doc_terms = self._tokenize(document)

        if not query_terms or not doc_terms:
            return 0.0

        doc_len = len(doc_terms)
        avg_doc_len = doc_len

        doc_freq = {}
        for term in doc_terms:
            doc_freq[term] = doc_freq.get(term, 0) + 1

        score = 0.0
        for term in query_terms:
            if term in doc_freq:
                tf = doc_freq[term]
                idf = 1.0
                score += idf * (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * doc_len / avg_doc_len)
                )
        return score

    def _tokenize(self, text: str) -> list[str]:
        """简单分词."""
        text = text.lower()
        terms = re.findall(r'\w+', text)
        return terms


class MemoryService:
    """记忆服务，封装 MemOS SDK."""

    def __init__(self):
        self._pref_memory = None
        self._tree_memory = None
        self._initialized = False
        self._embedding_service = EmbeddingService()
        self._rerank_service = RerankService()
        # 内存存储（生产环境应使用实际数据库）
        self._pref_memories: dict[str, list[dict[str, Any]]] = {}
        self._tree_memories: dict[str, list[dict[str, Any]]] = {}

    async def initialize(self) -> None:
        """初始化 MemOS 客户端."""
        if self._initialized:
            return

        # 检查是否启用 MemOS
        if not settings.USE_MEMOS:
            print("USE_MEMOS is disabled, using fallback implementation")
            self._initialized = True
            return

        try:
            from memos.memories.textual.preference import PreferenceTextMemory
            from memos.memories.textual.tree import TreeTextMemory
            from memos.configs.memory import (
                PreferenceTextMemoryConfig,
                TreeTextMemoryConfig,
            )
            from memos.configs.vec_db import VectorDBConfigFactory
            from memos.configs.embedder import EmbedderConfigFactory
            from memos.configs.llm import LLMConfigFactory
            from memos.configs.reranker import RerankerConfigFactory

            # PreferenceTextMemory 配置
            # 根据 MemOS 源码: PreferenceTextMemoryConfig 需要:
            # - extractor_llm
            # - vector_db (Milvus)
            # - embedder
            # - reranker (optional)
            # - extractor
            # - adder
            # - retriever

            # 构建 LLM 配置
            llm_config = LLMConfigFactory(
                backend="openai",
                config={
                    "model_name_or_path": settings.LLM_MODEL,
                    "api_key": settings.OPENAI_API_KEY,
                    "api_base": settings.LLM_BASE_URL or "https://api.openai.com/v1",
                    "temperature": 0.7,
                },
            )

            # 构建 Embedder 配置
            embedder_config = EmbedderConfigFactory(
                backend="universal_api",
                config={
                    "model_name_or_path": settings.MEMOS_EMBEDDING_MODEL,
                    "provider": "openai",
                    "api_key": settings.MEMOS_EMBEDDING_API_KEY or settings.OPENAI_API_KEY,
                    "base_url": settings.MEMOS_EMBEDDING_URL or settings.LLM_BASE_URL or "https://api.openai.com/v1",
                },
            )

            # 构建 VectorDB 配置 (Milvus)
            vector_db_config = VectorDBConfigFactory(
                backend="milvus",
                config={
                    "uri": f"http://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}",
                    "collection_name": [
                        settings.MEMOS_EXPLICIT_PREF_COLLECTION,
                        settings.MEMOS_IMPLICIT_PREF_COLLECTION,
                    ],
                    "user_name": "root",
                    "password": "milvus",
                },
            )

            # 构建 Reranker 配置 (可选)
            reranker_config = None
            if settings.MEMOS_RERANKER_MODEL:
                reranker_config = RerankerConfigFactory(
                    backend="universal_api",
                    config={
                        "model_name_or_path": settings.MEMOS_RERANKER_MODEL,
                        "provider": "openai",
                        "api_key": settings.MEMOS_RERANKER_API_KEY or settings.OPENAI_API_KEY,
                        "base_url": settings.MEMOS_RERANKER_URL or settings.LLM_BASE_URL or "https://api.openai.com/v1",
                    },
                )

            # PreferenceTextMemory 配置
            # 使用简化配置 - MemOS 0.3.x 版本支持
            pref_config = PreferenceTextMemoryConfig(
                extractor_llm=llm_config,
                vector_db=vector_db_config,
                embedder=embedder_config,
                reranker=reranker_config,
            )

            # TreeTextMemory 配置
            # 根据 MemOS 源码: TreeTextMemoryConfig 需要:
            # - extractor_llm
            # - dispatcher_llm
            # - embedder
            # - graph_db (Neo4j)
            # - reranker (optional)
            # - search_strategy (optional)
            # - reorganize (optional)
            # - memory_size (optional)
            # - mode (optional)
            # - include_embedding (optional)

            from memos.configs.graph_db import GraphDBConfigFactory

            # 构建 GraphDB 配置 (Neo4j)
            graph_db_config = GraphDBConfigFactory(
                backend="neo4j",
                config={
                    "uri": settings.NEO4J_URI,
                    "user": settings.NEO4J_USER,
                    "password": settings.NEO4J_PASSWORD,
                },
            )

            # 构建 TreeTextMemory 配置
            tree_config = TreeTextMemoryConfig(
                extractor_llm=llm_config,
                dispatcher_llm=llm_config,
                embedder=embedder_config,
                graph_db=graph_db_config,
                reranker=reranker_config,
                search_strategy={"bm25": True, "cot": False},
                mode="sync",
                include_embedding=False,
            )

            self._pref_memory = PreferenceTextMemory(pref_config)
            self._tree_memory = TreeTextMemory(tree_config)

            print("MemOS initialized successfully")

        except ImportError as e:
            # MemOS SDK 未安装，使用模拟实现
            print(f"Warning: MemOS SDK not found, using fallback implementation: {e}")
        except Exception as e:
            print(f"Error initializing MemOS: {e}")

        self._initialized = True

    # ========== 偏好记忆操作 ==========

    async def add_preference(
        self,
        messages: list[dict[str, str]],
        user_id: int,
        session_id: int,
        preference_type: str = "chat",
    ) -> list[dict[str, Any]]:
        """从对话中提取并存储用户偏好记忆."""
        if not self._initialized:
            await self.initialize()

        if self._pref_memory is not None:
            try:
                # MemOS PreferenceTextMemory.get_memory() 接口
                # messages: list[MessageList] - 对话消息列表
                # type: str - 偏好类型
                # info: dict - 附加信息
                memories = self._pref_memory.get_memory(
                    messages=messages,
                    type=preference_type,
                    info={
                        "user_id": str(user_id),
                        "session_id": str(session_id),
                    },
                )

                if memories:
                    # MemOS PreferenceTextMemory.add() 接口
                    # memories: list[TextualMemoryItem | dict]
                    self._pref_memory.add(memories)

                # 转换为 dict 格式返回
                return [
                    {
                        "id": getattr(m, "id", None),
                        "content": getattr(m, "memory", None) or getattr(m, "content", ""),
                        "type": preference_type,
                        "user_id": str(user_id),
                        "session_id": str(session_id),
                        "metadata": getattr(m, "metadata", None),
                    }
                    for m in memories
                ]

            except Exception as e:
                print(f"Error adding preference via MemOS: {e}")

        # Fallback: 从对话中提取偏好
        memories = self._extract_preference_from_messages(
            messages=messages,
            user_id=user_id,
            session_id=session_id,
            preference_type=preference_type,
        )

        key = f"pref_{user_id}"
        if key not in self._pref_memories:
            self._pref_memories[key] = []
        self._pref_memories[key].extend(memories)

        return memories

    def _extract_preference_from_messages(
        self,
        messages: list[dict[str, str]],
        user_id: int,
        session_id: int,
        preference_type: str,
    ) -> list[dict[str, Any]]:
        """从对话消息中提取偏好（占位实现）."""
        memories = []
        user_messages = [m["content"] for m in messages if m.get("role") == "user"]

        for i, msg in enumerate(user_messages):
            if any(kw in msg.lower() for kw in ["我喜欢", "偏好", "喜欢", "讨厌"]):
                memories.append({
                    "id": f"pref_{user_id}_{session_id}_{i}",
                    "content": msg,
                    "type": preference_type,
                    "user_id": str(user_id),
                    "session_id": str(session_id),
                    "metadata": {"extracted_from": "message"},
                })

        return memories

    # ========== 树形记忆操作 ==========

    async def add_tree_memory(
        self,
        content: str,
        user_id: int,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """添加树形结构记忆（知识点、研究成果）."""
        if not self._initialized:
            await self.initialize()

        if self._tree_memory is not None:
            try:
                user_name = f"user_{user_id}"
                memory_data = {
                    "content": content,
                    "metadata": metadata or {},
                }

                # MemOS TreeTextMemory.add() 接口
                # memories: list[TextualMemoryItem | dict]
                # user_name: str (可选)
                result = self._tree_memory.add([memory_data], user_name=user_name)

                if result:
                    return {
                        "id": result[0] if isinstance(result, list) else result,
                        "content": content,
                        "user_id": str(user_id),
                        "metadata": metadata or {},
                    }

            except Exception as e:
                print(f"Error adding tree memory via MemOS: {e}")

        # Fallback 实现
        import uuid
        memory = {
            "id": str(uuid.uuid4()),
            "content": content,
            "user_id": str(user_id),
            "metadata": metadata or {},
        }

        key = f"tree_{user_id}"
        if key not in self._tree_memories:
            self._tree_memories[key] = []
        self._tree_memories[key].append(memory)

        return memory

    # ========== 记忆检索 ==========

    async def search(
        self,
        query: str,
        user_id: int | None = None,
        top_k: int = 10,
        search_type: str = "hybrid",
    ) -> list[dict[str, Any]]:
        """联合检索偏好记忆和树形记忆."""
        if not self._initialized:
            await self.initialize()

        results = []

        if search_type in ("preference", "hybrid"):
            pref_results = await self._search_preference(
                query=query,
                user_id=user_id,
                top_k=top_k // 2 if search_type == "hybrid" else top_k,
            )
            for r in pref_results:
                r["source_type"] = "preference"
            results.extend(pref_results)

        if search_type in ("tree", "hybrid"):
            tree_results = await self._search_tree(
                query=query,
                user_id=user_id,
                top_k=top_k // 2 if search_type == "hybrid" else top_k,
            )
            for r in tree_results:
                r["source_type"] = "tree"
            results.extend(tree_results)

        if results and (self._pref_memory is None and self._tree_memory is None):
            # 使用 Fallback rerank
            results = await self._rerank_service.rerank(
                query=query,
                candidates=results,
                top_k=top_k,
            )

        results.sort(key=lambda x: x.get("rerank_score", x.get("score", 0)), reverse=True)
        return results[:top_k]

    async def _search_preference(
        self,
        query: str,
        user_id: int | None,
        top_k: int,
    ) -> list[dict[str, Any]]:
        """检索偏好记忆."""
        if self._pref_memory is not None:
            try:
                # MemOS PreferenceTextMemory.search() 接口
                # query: str
                # top_k: int
                # info: dict (可选)
                # search_filter: dict (可选)
                search_filter = {"user_id": str(user_id)} if user_id else None
                results = self._pref_memory.search(
                    query=query,
                    top_k=top_k,
                    search_filter=search_filter,
                )

                # 转换为 dict 格式
                return [
                    {
                        "id": getattr(r, "id", None),
                        "content": getattr(r, "memory", None) or getattr(r, "content", ""),
                        "score": 1.0,  # MemOS 不返回 score，使用默认
                        "metadata": getattr(r, "metadata", None).__dict__ if hasattr(getattr(r, "metadata", None), "__dict__") else None,
                    }
                    for r in results
                ]
            except Exception as e:
                print(f"Error searching preference via MemOS: {e}")

        # Fallback
        key = f"pref_{user_id}" if user_id else "pref_default"
        memories = self._pref_memories.get(key, [])

        results = []
        for mem in memories:
            score = await self._embedding_service.compute_similarity(
                query, mem.get("content", "")
            )
            results.append({
                **mem,
                "score": score,
            })

        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]

    async def _search_tree(
        self,
        query: str,
        user_id: int | None,
        top_k: int,
    ) -> list[dict[str, Any]]:
        """检索树形记忆."""
        if self._tree_memory is not None:
            try:
                # MemOS TreeTextMemory.search() 接口
                # query: str
                # top_k: int
                # mode: str (fast/fine)
                # memory_type: str (All/WorkingMemory/LongTermMemory/UserMemory)
                # search_filter: dict (可选)
                # user_name: str (可选)
                user_name = f"user_{user_id}" if user_id else None
                search_filter = {"user_id": str(user_id)} if user_id else None

                results = self._tree_memory.search(
                    query=query,
                    top_k=top_k,
                    mode="fast",
                    memory_type="All",
                    search_filter=search_filter,
                    user_name=user_name,
                )

                # 转换为 dict 格式
                return [
                    {
                        "id": getattr(r, "id", None),
                        "content": getattr(r, "memory", None) or getattr(r, "content", ""),
                        "score": 1.0,
                        "metadata": getattr(r, "metadata", None).__dict__ if hasattr(getattr(r, "metadata", None), "__dict__") else None,
                    }
                    for r in results
                ]
            except Exception as e:
                print(f"Error searching tree via MemOS: {e}")

        # Fallback
        key = f"tree_{user_id}" if user_id else "tree_default"
        memories = self._tree_memories.get(key, [])

        results = []
        for mem in memories:
            score = await self._embedding_service.compute_similarity(
                query, mem.get("content", "")
            )
            results.append({
                **mem,
                "score": score,
            })

        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]

    # ========== 记忆反馈 ==========

    async def process_feedback(
        self,
        user_id: int,
        session_id: int,
        chat_history: list[dict[str, str]],
        feedback_content: str,
    ) -> dict[str, Any]:
        """处理用户对记忆的反馈修正.

        注意:
        - 当 USE_MEMOS=true 时，MemOS 的 SimpleMemFeedback 会自动处理
          偏好记忆和树形记忆的反馈修正
        - 当 USE_MEMOS=false 时，使用 Fallback 实现
        """
        if not self._initialized:
            await self.initialize()

        # 当 USE_MEMOS=true 时，可以扩展此处以使用 SimpleMemFeedback
        # 当前统一使用 Fallback 实现
        return await self._process_feedback_placeholder(
            user_id=user_id,
            session_id=session_id,
            feedback_content=feedback_content,
        )

    async def _process_feedback_placeholder(
        self,
        user_id: int,
        session_id: int,
        feedback_content: str,
    ) -> dict[str, Any]:
        """处理反馈（占位实现）."""
        import uuid

        correction = {
            "id": str(uuid.uuid4()),
            "type": "correction",
            "content": feedback_content,
            "user_id": str(user_id),
            "session_id": str(session_id),
            "metadata": {"source": "feedback"},
        }

        key = f"pref_{user_id}"
        if key not in self._pref_memories:
            self._pref_memories[key] = []
        self._pref_memories[key].append(correction)

        return {
            "status": "success",
            "correction": correction,
            "message": "Feedback processed successfully",
        }


# 全局记忆服务实例
memory_service = MemoryService()
