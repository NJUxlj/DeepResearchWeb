/** 会话 */
export interface Session {
  id: number;
  user_id: number;
  title: string;
  mode: "chat" | "research";
  created_at: string;
  updated_at: string;
  message_count: number;
}

/** 会话详情 */
export interface SessionDetail extends Session {
  messages: Message[];
}

/** 创建会话请求 */
export interface CreateSessionRequest {
  title: string;
  mode?: "chat" | "research";
}

/** 更新会话请求 */
export interface UpdateSessionRequest {
  title?: string;
}

/** 会话列表响应 */
export interface SessionListResponse {
  items: Session[];
  total: number;
  page: number;
  page_size: number;
}

/** 消息 */
export interface Message {
  id: number;
  session_id: number;
  role: "user" | "assistant" | "system";
  content: string;
  citations?: Citation[];
  meta_info?: Record<string, unknown>;
  created_at: string;
}

/** 引用 */
export interface Citation {
  id: string;
  index: number;
  url: string;
  title: string;
  snippet: string;
  source_type: "web" | "mcp" | "memory" | "document";
  favicon?: string;
}

/** 聊天请求 */
export interface ChatRequest {
  session_id?: number;
  message: string;
  stream?: boolean;
}

/** 聊天响应 */
export interface ChatResponse {
  message_id: number;
  content: string;
  citations?: Citation[];
  session_id: number;
}

/** SSE 事件类型 */
export interface ChatStreamEvent {
  event: "message" | "chunk" | "citations" | "error" | "done";
  data: Record<string, unknown>;
}
