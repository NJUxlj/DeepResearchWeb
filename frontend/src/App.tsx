import { useEffect, useState, useRef } from "react";
import { BrowserRouter, Routes, Route, Navigate, Link } from "react-router-dom";
import { useAuthStore } from "./stores/authStore";
import { authApi } from "@/api/auth";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Chat from "./pages/Chat";
import Settings from "./pages/Settings";
import { ToolsConfig } from "./pages/config/ToolsConfig";
import { SkillsConfig } from "./pages/config/SkillsConfig";
import { MCPConfig } from "@/pages/config/MCPConfig";

function HomePage() {
  const { user, isAuthenticated } = useAuthStore();

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">
          DeepResearchWeb
        </h1>
        {isAuthenticated ? (
          <div className="space-y-2">
            <p className="text-green-600">Welcome, {user?.username || "User"}!</p>
            <p className="text-gray-600">Email: {user?.email}</p>
            <Link
              to="/chat"
              className="inline-block mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              进入聊天
            </Link>
          </div>
        ) : (
          <p className="text-gray-500">Please login to continue</p>
        )}
      </div>
    </div>
  );
}

/** 私有路由组件 - 需要登录才能访问 */
function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isLoading = useAuthStore((state) => state.isLoading);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  // 认证初始化中，显示加载状态
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function App() {
  const [initialized, setInitialized] = useState(false);
  const setUser = useAuthStore((state) => state.setUser);
  const setAuth = useAuthStore((state) => state.setAuth);
  const setLoading = useAuthStore((state) => state.setLoading);
  const initRef = useRef(false);

  // 初始化时检查 token 并获取用户信息
  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;

    const initAuth = async () => {
      try {
        const stored = localStorage.getItem("auth-storage");
        if (stored) {
          const parsed = JSON.parse(stored);
          const storedToken = parsed?.state?.token;
          if (storedToken) {
            // 有 token，先设置 auth 状态为已认证
            setAuth({
              access_token: storedToken,
              token_type: 'bearer',
              expires_in: 1800
            });

            // 然后尝试获取用户信息
            try {
              const user = await authApi.getMe();
              setUser(user);
            } catch (e) {
              // token 无效，清除 auth 状态
              setAuth({
                access_token: '',
                token_type: 'bearer',
                expires_in: 0
              });
            }
          }
        }
      } catch (e) {
        console.error("Auth init error:", e);
      } finally {
        setLoading(false);
        setInitialized(true);
      }
    };

    // 延迟执行确保 zustand 加载完成
    setTimeout(initAuth, 100);
  }, [setUser, setAuth, setLoading]);

  // 在认证初始化完成前显示加载状态
  if (!initialized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/chat"
          element={
            <PrivateRoute>
              <Chat />
            </PrivateRoute>
          }
        />
        <Route
          path="/chat/:sessionId"
          element={
            <PrivateRoute>
              <Chat />
            </PrivateRoute>
          }
        />
        <Route
          path="/config/tools"
          element={
            <PrivateRoute>
              <ToolsConfig />
            </PrivateRoute>
          }
        />
        <Route
          path="/config/skills"
          element={
            <PrivateRoute>
              <SkillsConfig />
            </PrivateRoute>
          }
        />
        <Route
          path="/config/mcp"
          element={
            <PrivateRoute>
              <MCPConfig />
            </PrivateRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <PrivateRoute>
              <Settings />
            </PrivateRoute>
          }
        />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <HomePage />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
