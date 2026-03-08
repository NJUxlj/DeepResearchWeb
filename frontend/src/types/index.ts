/** 基础 API 响应类型 */
export interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
}

/** API 错误响应 */
export interface ApiError {
  error: string;
  message: string;
  details?: unknown;
}

/** 健康检查响应 */
export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
}
