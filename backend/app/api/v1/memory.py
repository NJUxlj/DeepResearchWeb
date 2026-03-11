"""记忆管理 API 端点."""

from typing import Any

from fastapi import APIRouter, Body, Query
from pydantic import BaseModel

from app.api.deps import CurrentUserDep
from app.services.memory_service import memory_service

router = APIRouter(prefix="/memory", tags=["memory"])


class SearchQuery(BaseModel):
    """搜索请求"""
    query: str
    top_k: int = 10
    search_type: str = "hybrid"


class FeedbackRequest(BaseModel):
    """记忆反馈请求"""
    session_id: int
    feedback: str
    chat_history: list[dict[str, str]]


class TreeMemoryRequest(BaseModel):
    """添加树形记忆请求"""
    content: str
    metadata: dict[str, Any] | None = None


class PreferenceRequest(BaseModel):
    """添加偏好记忆请求"""
    session_id: int
    messages: list[dict[str, str]]
    preference_type: str = "chat"


@router.get("/search")
async def search_memory(
    current_user: CurrentUserDep,
    query: str = Query(..., description="搜索查询"),
    top_k: int = Query(10, ge=1, le=50, description="返回结果数量"),
    search_type: str = Query("hybrid", regex="^(preference|tree|hybrid)$", description="搜索类型"),
):
    """
    搜索用户记忆.

    - preference: 只搜索偏好记忆
    - tree: 只搜索树形记忆
    - hybrid: 同时搜索两种记忆并合并排序
    """
    results = await memory_service.search(
        query=query,
        user_id=current_user.id,
        top_k=top_k,
        search_type=search_type,
    )

    return {
        "query": query,
        "total": len(results),
        "results": results,
    }


@router.post("/feedback")
async def memory_feedback(
    current_user: CurrentUserDep,
    request: FeedbackRequest,
):
    """
    提交记忆反馈.

    用户可以对记忆中的信息进行修正或补充.
    """
    result = await memory_service.process_feedback(
        user_id=current_user.id,
        session_id=request.session_id,
        chat_history=request.chat_history,
        feedback_content=request.feedback,
    )

    return result


@router.post("/tree")
async def add_tree_memory(
    current_user: CurrentUserDep,
    request: TreeMemoryRequest,
):
    """
    手动添加树形记忆.

    用户可以直接添加知识点到记忆树中.
    """
    result = await memory_service.add_tree_memory(
        content=request.content,
        user_id=current_user.id,
        metadata=request.metadata,
    )

    return {
        "status": "success" if result else "failed",
        "memory": result,
    }


@router.post("/preference")
async def add_preference_memory(
    current_user: CurrentUserDep,
    request: PreferenceRequest,
):
    """
    手动添加偏好记忆.

    从对话消息中提取并存储用户偏好.
    """
    result = await memory_service.add_preference(
        messages=request.messages,
        user_id=current_user.id,
        session_id=request.session_id,
        preference_type=request.preference_type,
    )

    return {
        "status": "success" if result else "failed",
        "memories": result,
    }
