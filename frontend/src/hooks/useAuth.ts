import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/stores/authStore";
import type { LoginRequest, RegisterRequest, UpdateUserRequest, User } from "@/types/auth";

/** 登录 hook */
export function useLogin() {
  const navigate = useNavigate();
  const { setAuth, setUser } = useAuthStore();

  const login = useCallback(
    async (data: LoginRequest): Promise<{ success: boolean; error?: string }> => {
      try {
        const response = await authApi.login(data);
        setAuth(response);
        localStorage.setItem("token", response.access_token);

        // 获取用户信息
        const user = await authApi.getMe();
        setUser(user);

        navigate("/");
        return { success: true };
      } catch (error) {
        const message = error instanceof Error ? error.message : "Login failed";
        return { success: false, error: message };
      }
    },
    [navigate, setAuth, setUser]
  );

  return login;
}

/** 注册 hook */
export function useRegister() {
  const navigate = useNavigate();

  const register = useCallback(
    async (data: RegisterRequest): Promise<{ success: boolean; error?: string }> => {
      try {
        await authApi.register(data);
        navigate("/login");
        return { success: true };
      } catch (error) {
        const message = error instanceof Error ? error.message : "Registration failed";
        return { success: false, error: message };
      }
    },
    [navigate]
  );

  return register;
}

/** 登出 hook */
export function useLogout() {
  const navigate = useNavigate();
  const { logout } = useAuthStore();

  const handleLogout = useCallback(() => {
    logout();
    localStorage.removeItem("token");
    navigate("/login");
  }, [navigate, logout]);

  return handleLogout;
}

/** 获取当前用户 hook */
export function useCurrentUser() {
  const { user, isAuthenticated } = useAuthStore();

  const fetchUser = useCallback(async (): Promise<User | null> => {
    if (!isAuthenticated) return null;

    try {
      const userData = await authApi.getMe();
      useAuthStore.getState().setUser(userData);
      return userData;
    } catch {
      return null;
    }
  }, [isAuthenticated]);

  return { user, isAuthenticated, fetchUser };
}

/** 更新用户信息 hook */
export function useUpdateUser() {
  const { setUser } = useAuthStore();

  const updateUser = useCallback(
    async (data: UpdateUserRequest): Promise<{ success: boolean; error?: string; user?: User }> => {
      try {
        const user = await authApi.updateMe(data);
        setUser(user);
        return { success: true, user };
      } catch (error) {
        const message = error instanceof Error ? error.message : "Update failed";
        return { success: false, error: message };
      }
    },
    [setUser]
  );

  return updateUser;
}
