/** 记忆类型定义 */

/** 记忆项 */
export interface MemoryItem {
  id?: string;
  content: string;
  score?: number;
  source_type: "preference" | "tree";
  metadata?: Record<string, unknown>;
}

/** 记忆搜索响应 */
export interface MemorySearchResponse {
  query: string;
  total: number;
  results: MemoryItem[];
}

/** 记忆反馈请求 */
export interface MemoryFeedbackRequest {
  session_id: number;
  feedback: string;
  chat_history: Array<{
    role: string;
    content: string;
  }>;
}

/** 添加树形记忆请求 */
export interface AddTreeMemoryRequest {
  content: string;
  metadata?: Record<string, unknown>;
}

/** 记忆反馈响应 */
export interface MemoryFeedbackResponse {
  status: string;
  message?: string;
  correction?: {
    id: string;
    content: string;
  };
}

/** 添加偏好记忆请求 */
export interface AddPreferenceRequest {
  session_id: number;
  messages: Array<{
    role: string;
    content: string;
  }>;
  preference_type?: string;
}
