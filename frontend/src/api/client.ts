import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api/v1";

// 验证 API URL 必须以 /api/v1 开头
if (!API_BASE_URL.endsWith('/api/v1')) {
  console.warn('API_BASE_URL should end with /api/v1');
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token 并添加到请求头
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // 获取请求 URL
    const url = error.config?.url || '';

    // 如果是 /auth/me 请求（auth 验证），不自动重定向
    // 这样可以避免 auth 初始化时的无限循环
    if (error.response?.status === 401 && url.includes('/auth/me')) {
      // 只清除 token，不重定向
      localStorage.removeItem("token");
      return Promise.reject(error);
    }

    // 其他 401 错误才重定向到登录页
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

/**
 * 通用 API 请求函数
 * @param config Axios 请求配置
 * @returns 响应数据
 */
export async function apiRequest<T>(
  config: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.request<T>(config);
  return response.data;
}
