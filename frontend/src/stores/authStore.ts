import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, LoginResponse } from "@/types/auth";

interface AuthState {
  // 状态
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean; // 认证初始化中

  // 方法
  setAuth: (response: LoginResponse) => void;
  setUser: (user: User) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      isLoading: true, // 初始为 true，等待初始化完成

      setAuth: (response) =>
        set({
          token: response.access_token,
          isAuthenticated: true,
          // 注意: LoginResponse 不包含 user 字段，用户信息需通过单独的 API 获取
        }),

      setUser: (user) => set({ user }),

      logout: () =>
        set({
          token: null,
          user: null,
          isAuthenticated: false,
        }),

      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({ token: state.token }),
    }
  )
);
