import { apiRequest } from "./client";
import type {
  ChatRequest,
  ChatResponse,
  CreateSessionRequest,
  Session,
  SessionDetail,
  SessionListResponse,
  UpdateSessionRequest,
} from "@/types/session";

export const sessionApi = {
  /** 获取会话列表 */
  list: (params?: { page?: number; page_size?: number; mode?: string }) =>
    apiRequest<SessionListResponse>({
      method: "GET",
      url: "/sessions",
      params,
    }),

  /** 创建会话 */
  create: (data: CreateSessionRequest) =>
    apiRequest<Session>({
      method: "POST",
      url: "/sessions",
      data,
    }),

  /** 获取会话详情 */
  get: (sessionId: number) =>
    apiRequest<SessionDetail>({
      method: "GET",
      url: `/sessions/${sessionId}`,
    }),

  /** 更新会话 */
  update: (sessionId: number, data: UpdateSessionRequest) =>
    apiRequest<Session>({
      method: "PUT",
      url: `/sessions/${sessionId}`,
      data,
    }),

  /** 删除会话 */
  delete: (sessionId: number) =>
    apiRequest<void>({
      method: "DELETE",
      url: `/sessions/${sessionId}`,
    }),
};

export const chatApi = {
  /** 发送消息（非流式） */
  sendMessage: (data: ChatRequest) =>
    apiRequest<ChatResponse>({
      method: "POST",
      url: "/chat/message",
      data,
    }),
};
