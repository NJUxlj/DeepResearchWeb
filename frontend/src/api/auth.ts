import { apiRequest } from "./client";
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  UpdateUserRequest,
  User,
} from "@/types/auth";

export const authApi = {
  /** 用户注册 */
  register: (data: RegisterRequest) =>
    apiRequest<User>({
      method: "POST",
      url: "/auth/register",
      data,
    }),

  /** 用户登录 */
  login: (data: LoginRequest) =>
    apiRequest<LoginResponse>({
      method: "POST",
      url: "/auth/login",
      data,
    }),

  /** 获取当前用户信息 */
  getMe: () =>
    apiRequest<User>({
      method: "GET",
      url: "/auth/me",
    }),

  /** 更新当前用户信息 */
  updateMe: (data: UpdateUserRequest) =>
    apiRequest<User>({
      method: "PUT",
      url: "/auth/me",
      data,
    }),
};
