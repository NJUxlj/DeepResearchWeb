import { useState, useEffect } from "react";
import { Settings as SettingsIcon, User, Lock, Bell, Save, RotateCcw } from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { useUpdateUser } from "@/hooks/useAuth";
import { userEnvConfigApi, UserEnvConfigInitResponse } from "@/api/userEnvConfig";

export default function Settings() {
  const { user } = useAuthStore();
  const updateUser = useUpdateUser();
  const [activeTab, setActiveTab] = useState<"profile" | "security" | "notifications" | "env">("profile");
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [profileData, setProfileData] = useState({
    email: user?.email || "",
  });

  // 环境变量配置状态
  const [envConfig, setEnvConfig] = useState<Record<string, string>>({});
  const [envLoading, setEnvLoading] = useState(false);
  const [envSaving, setEnvSaving] = useState(false);
  const [isNewConfig, setIsNewConfig] = useState(false);

  // 加载环境配置
  useEffect(() => {
    if (activeTab === "env") {
      loadEnvConfig();
    }
  }, [activeTab]);

  const loadEnvConfig = async () => {
    setEnvLoading(true);
    try {
      const response: UserEnvConfigInitResponse = await userEnvConfigApi.get();
      setEnvConfig(response.env_config);
      setIsNewConfig(response.is_new);
    } catch (error) {
      console.error("Failed to load env config:", error);
    } finally {
      setEnvLoading(false);
    }
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSuccessMessage(null);

    try {
      await updateUser({
        email: profileData.email,
      });
      setSuccessMessage("Profile updated successfully");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (error) {
      console.error("Failed to update profile:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleEnvConfigChange = (key: string, value: string) => {
    setEnvConfig((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSaveEnvConfig = async () => {
    setEnvSaving(true);
    try {
      if (isNewConfig) {
        await userEnvConfigApi.create("default", envConfig);
      } else {
        await userEnvConfigApi.update("default", envConfig);
      }
      setIsNewConfig(false);
      setSuccessMessage("环境配置保存成功");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (error) {
      console.error("Failed to save env config:", error);
      setSuccessMessage("保存失败");
      setTimeout(() => setSuccessMessage(null), 3000);
    } finally {
      setEnvSaving(false);
    }
  };

  const handleResetEnvConfig = () => {
    if (confirm("确定要重置为默认值吗？当前的自定义配置将会丢失。")) {
      loadEnvConfig();
    }
  };

  // 按类别分组环境变量
  const envCategories: Record<string, string[]> = {
    "数据库配置": ["MYSQL_ROOT_PASSWORD", "MYSQL_USER", "MYSQL_PASSWORD", "DATABASE_URL", "DB_POOL_SIZE", "DB_MAX_OVERFLOW", "DB_POOL_RECYCLE"],
    "Neo4j 配置": ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "NEO4J_MAX_CONNECTIONS"],
    "Redis 配置": ["REDIS_URL", "REDIS_MAX_CONNECTIONS", "CACHE_TTL"],
    "RabbitMQ 配置": ["RABBITMQ_URL", "RABBITMQ_USER", "RABBITMQ_PASSWORD"],
    "Milvus 配置": ["MILVUS_HOST", "MILVUS_PORT", "MILVUS_USER", "MILVUS_PASSWORD", "MILVUS_MAX_CONNECTIONS"],
    "Qdrant 配置": ["QDRANT_HOST", "QDRANT_PORT", "QDRANT_GRPC_PORT"],
    "JWT 配置": ["SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"],
    "LLM 配置": ["OPENAI_API_KEY", "LLM_BASE_URL", "LLM_MODEL", "LLM_MAX_CONCURRENT"],
    "搜索配置": ["TAVILY_API_KEY", "SERPAPI_KEY"],
    "ARQ 配置": ["ARQ_MAX_JOBS", "ARQ_JOB_TIMEOUT", "ARQ_MAX_TRIES", "ARQ_HEALTH_CHECK_INTERVAL"],
    "MemOS 配置": ["USE_MEMOS", "MEMOS_EXPLICIT_PREF_COLLECTION", "MEMOS_IMPLICIT_PREF_COLLECTION", "MEMOS_TREE_COLLECTION", "MEMOS_EMBEDDING_MODEL", "MEMOS_EMBEDDING_URL", "MEMOS_EMBEDDING_API_KEY", "MEMOS_RERANKER_MODEL", "MEMOS_RERANKER_URL", "MEMOS_RERANKER_API_KEY"],
    "应用配置": ["DEBUG", "ENV", "APP_NAME", "APP_VERSION", "CORS_ORIGINS"],
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <SettingsIcon className="w-8 h-8 text-primary" />
          <h1 className="text-2xl font-bold">设置</h1>
        </div>

        {successMessage && (
          <div className="mb-4 p-3 bg-green-50 text-green-600 rounded-lg">
            {successMessage}
          </div>
        )}

        <div className="flex gap-6">
          {/* Sidebar */}
          <div className="w-48 flex-shrink-0">
            <nav className="space-y-1">
              <button
                onClick={() => setActiveTab("profile")}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  activeTab === "profile"
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                <User className="w-4 h-4" />
                个人资料
              </button>
              <button
                onClick={() => setActiveTab("security")}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  activeTab === "security"
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                <Lock className="w-4 h-4" />
                安全设置
              </button>
              <button
                onClick={() => setActiveTab("notifications")}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  activeTab === "notifications"
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                <Bell className="w-4 h-4" />
                通知设置
              </button>
              <button
                onClick={() => setActiveTab("env")}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  activeTab === "env"
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                <SettingsIcon className="w-4 h-4" />
                环境变量设置
              </button>
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1">
            {activeTab === "profile" && (
              <div className="bg-card rounded-lg border p-6">
                <h2 className="text-lg font-semibold mb-4">个人资料</h2>

                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">用户名</label>
                  <input
                    type="text"
                    value={user?.username || ""}
                    disabled
                    className="w-full px-3 py-2 border rounded-lg bg-muted text-muted-foreground"
                  />
                  <p className="text-xs text-muted-foreground mt-1">用户名不可更改</p>
                </div>

                <form onSubmit={handleProfileSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">邮箱</label>
                    <input
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isSaving}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
                  >
                    {isSaving ? "保存中..." : "保存"}
                  </button>
                </form>
              </div>
            )}

            {activeTab === "security" && (
              <div className="bg-card rounded-lg border p-6">
                <h2 className="text-lg font-semibold mb-4">安全设置</h2>
                <p className="text-muted-foreground">安全设置功能开发中...</p>
              </div>
            )}

            {activeTab === "notifications" && (
              <div className="bg-card rounded-lg border p-6">
                <h2 className="text-lg font-semibold mb-4">通知设置</h2>
                <p className="text-muted-foreground">通知设置功能开发中...</p>
              </div>
            )}

            {activeTab === "env" && (
              <div className="bg-card rounded-lg border p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">环境变量设置</h2>
                  <div className="flex gap-2">
                    <button
                      onClick={handleResetEnvConfig}
                      className="flex items-center gap-2 px-3 py-1.5 text-sm border rounded-lg hover:bg-accent"
                    >
                      <RotateCcw className="w-4 h-4" />
                      重置
                    </button>
                    <button
                      onClick={handleSaveEnvConfig}
                      disabled={envSaving}
                      className="flex items-center gap-2 px-3 py-1.5 text-sm bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
                    >
                      <Save className="w-4 h-4" />
                      {envSaving ? "保存中..." : "保存配置"}
                    </button>
                  </div>
                </div>

                {envLoading ? (
                  <div className="text-center py-8 text-muted-foreground">加载中...</div>
                ) : (
                  <div className="space-y-6 max-h-[calc(100vh-300px)] overflow-y-auto">
                    {Object.entries(envCategories).map(([category, keys]) => {
                      // 过滤出实际存在的环境变量
                      const existingKeys = keys.filter((key) => key in envConfig);
                      if (existingKeys.length === 0) return null;

                      return (
                        <div key={category}>
                          <h3 className="text-sm font-medium text-muted-foreground mb-2">{category}</h3>
                          <div className="space-y-3">
                            {existingKeys.map((key) => (
                              <div key={key} className="grid grid-cols-[200px_1fr] gap-4 items-center">
                                <label className="text-sm font-mono text-foreground">{key}</label>
                                <input
                                  type="text"
                                  value={envConfig[key] || ""}
                                  onChange={(e) => handleEnvConfigChange(key, e.target.value)}
                                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
                                />
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {isNewConfig && (
                  <div className="mt-4 p-3 bg-blue-50 text-blue-600 rounded-lg text-sm">
                    您还没有保存过环境配置。当前显示的是系统默认值。点击"保存配置"保存您的自定义配置。
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
