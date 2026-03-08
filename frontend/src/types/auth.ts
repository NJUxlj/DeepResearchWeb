/** 用户注册请求 */
export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

/** 用户登录请求 */
export interface LoginRequest {
  username: string;
  password: string;
}

/** 用户信息 */
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/** 登录响应 */
export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

/** 用户信息更新请求 */
export interface UpdateUserRequest {
  email?: string;
  password?: string;
}
