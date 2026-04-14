import { useState, useEffect } from "react";
import { Settings as SettingsIcon, User, Lock, Bell, Save, RotateCcw, Eye, EyeOff } from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { useUpdateUser } from "@/hooks/useAuth";
import { userEnvConfigApi, UserEnvConfigInitResponse } from "@/api/userEnvConfig";
import { userSettingsApi, NotificationSettings } from "@/api/userSettings";

export default function Settings() {
  const { user } = useAuthStore();
  const updateUser = useUpdateUser();
  const [activeTab, setActiveTab] = useState<"profile" | "security" | "notifications" | "env">("profile");
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [profileData, setProfileData] = useState({
    email: user?.email || "",
  });

  // ========== 环境变量配置状态 ==========
  const [envConfig, setEnvConfig] = useState<Record<string, string>>({});
  const [envLoading, setEnvLoading] = useState(false);
  const [envSaving, setEnvSaving] = useState(false);
  const [isNewConfig, setIsNewConfig] = useState(false);

  // ========== 安全设置状态 ==========
  const [passwordData, setPasswordData] = useState({
    oldPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [showPasswords, setShowPasswords] = useState({
    old: false,
    new: false,
    confirm: false,
  });
  const [passwordSaving, setPasswordSaving] = useState(false);

  // ========== 通知设置状态 ==========
  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings>({
    email_enabled: true,
    browser_enabled: false,
    notify_new_message: true,
    notify_research_complete: true,
    notify_mention: true,
  });
  const [notificationLoading, setNotificationLoading] = useState(false);
  const [notificationSaving, setNotificationSaving] = useState(false);

  // 加载环境配置
  useEffect(() => {
    if (activeTab === "env") {
      loadEnvConfig();
    }
  }, [activeTab]);

  // 加载通知设置
  useEffect(() => {
    if (activeTab === "notifications") {
      loadNotificationSettings();
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

  const loadNotificationSettings = async () => {
    setNotificationLoading(true);
    try {
      const settings = await userSettingsApi.getNotificationSettings();
      setNotificationSettings(settings);
    } catch (error) {
      console.error("Failed to load notification settings:", error);
    } finally {
      setNotificationLoading(false);
    }
  };

  const showSuccess = (message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  const showError = (message: string) => {
    setErrorMessage(message);
    setTimeout(() => setErrorMessage(null), 3000);
  };

  // ========== 个人资料提交 ==========
  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setErrorMessage(null);

    try {
      await updateUser({
        email: profileData.email,
      });
      showSuccess("个人资料更新成功");
    } catch (error) {
      console.error("Failed to update profile:", error);
      showError("更新失败");
    } finally {
      setIsSaving(false);
    }
  };

  // ========== 修改密码 ==========
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      showError("新密码与确认密码不匹配");
      return;
    }

    if (passwordData.newPassword.length < 8) {
      showError("新密码长度至少为 8 个字符");
      return;
    }

    setPasswordSaving(true);
    try {
      const response = await userSettingsApi.changePassword({
        old_password: passwordData.oldPassword,
        new_password: passwordData.newPassword,
      });
      if (response.success) {
        showSuccess("密码修改成功");
        setPasswordData({ oldPassword: "", newPassword: "", confirmPassword: "" });
      }
    } catch (error: any) {
      console.error("Failed to change password:", error);
      showError(error?.response?.data?.detail || "密码修改失败");
    } finally {
      setPasswordSaving(false);
    }
  };

  // ========== 通知设置变更 ==========
  const handleNotificationChange = async (key: keyof NotificationSettings, value: boolean) => {
    const newSettings = { ...notificationSettings, [key]: value };
    setNotificationSettings(newSettings);

    setNotificationSaving(true);
    try {
      await userSettingsApi.updateNotificationSettings({ [key]: value });
    } catch (error) {
      console.error("Failed to update notification settings:", error);
      // 回滚 - 使用函数式更新确保获取最新值
      setNotificationSettings((prev) => prev);
      showError("设置更新失败");
    } finally {
      setNotificationSaving(false);
    }
  };

  // ========== 环境配置 ==========
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
      showSuccess("环境配置保存成功");
    } catch (error) {
      console.error("Failed to save env config:", error);
      showError("保存失败");
    } finally {
      setEnvSaving(false);
    }
  };

  const handleResetEnvConfig = () => {
    // TODO: 后续应替换为自定义 Modal/Dialog 组件，以保持 UI 一致性
    if (window.confirm("确定要重置为默认值吗？当前的自定义配置将会丢失。")) {
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

        {(successMessage || errorMessage) && (
          <div className={`mb-4 p-3 rounded-lg ${successMessage ? "bg-green-50 text-green-600" : "bg-red-50 text-red-600"}`}>
            {successMessage || errorMessage}
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
            {/* ========== 个人资料 ========== */}
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

            {/* ========== 安全设置 ========== */}
            {activeTab === "security" && (
              <div className="bg-card rounded-lg border p-6">
                <h2 className="text-lg font-semibold mb-4">修改密码</h2>

                <form onSubmit={handlePasswordSubmit} className="space-y-4 max-w-md">
                  <div>
                    <label className="block text-sm font-medium mb-2">当前密码</label>
                    <div className="relative">
                      <input
                        type={showPasswords.old ? "text" : "password"}
                        value={passwordData.oldPassword}
                        onChange={(e) => setPasswordData({ ...passwordData, oldPassword: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary pr-10"
                        placeholder="请输入当前密码"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPasswords({ ...showPasswords, old: !showPasswords.old })}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                      >
                        {showPasswords.old ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">新密码</label>
                    <div className="relative">
                      <input
                        type={showPasswords.new ? "text" : "password"}
                        value={passwordData.newPassword}
                        onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary pr-10"
                        placeholder="至少 8 位，包含大小写字母和数字"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPasswords({ ...showPasswords, new: !showPasswords.new })}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                      >
                        {showPasswords.new ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">确认新密码</label>
                    <div className="relative">
                      <input
                        type={showPasswords.confirm ? "text" : "password"}
                        value={passwordData.confirmPassword}
                        onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary pr-10"
                        placeholder="请再次输入新密码"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPasswords({ ...showPasswords, confirm: !showPasswords.confirm })}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                      >
                        {showPasswords.confirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={passwordSaving || !passwordData.oldPassword || !passwordData.newPassword || !passwordData.confirmPassword}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
                  >
                    {passwordSaving ? "保存中..." : "修改密码"}
                  </button>
                </form>
              </div>
            )}

            {/* ========== 通知设置 ========== */}
            {activeTab === "notifications" && (
              <div className="bg-card rounded-lg border p-6">
                <h2 className="text-lg font-semibold mb-4">通知设置</h2>

                {notificationLoading ? (
                  <div className="text-center py-8 text-muted-foreground">加载中...</div>
                ) : (
                  <div className="space-y-6">
                    {/* 通知渠道 */}
                    <div>
                      <h3 className="text-sm font-medium mb-3">通知渠道</h3>
                      <div className="space-y-3">
                        <label className="flex items-center gap-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={notificationSettings.email_enabled}
                            onChange={(e) => handleNotificationChange("email_enabled", e.target.checked)}
                            className="w-4 h-4 rounded border-gray-300 accent-primary focus:ring-primary"
                          />
                          <span className="text-sm">邮件通知</span>
                        </label>
                        <label className="flex items-center gap-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={notificationSettings.browser_enabled}
                            onChange={(e) => handleNotificationChange("browser_enabled", e.target.checked)}
                            className="w-4 h-4 rounded border-gray-300 accent-primary focus:ring-primary"
                          />
                          <span className="text-sm">浏览器推送通知</span>
                        </label>
                      </div>
                    </div>

                    {/* 通知类型 */}
                    <div>
                      <h3 className="text-sm font-medium mb-3">通知类型</h3>
                      <div className="space-y-3">
                        <label className="flex items-center gap-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={notificationSettings.notify_new_message}
                            onChange={(e) => handleNotificationChange("notify_new_message", e.target.checked)}
                            disabled={!notificationSettings.email_enabled && !notificationSettings.browser_enabled}
                            className="w-4 h-4 rounded border-gray-300 accent-primary focus:ring-primary disabled:opacity-50"
                          />
                          <span className="text-sm">新消息通知</span>
                        </label>
                        <label className="flex items-center gap-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={notificationSettings.notify_research_complete}
                            onChange={(e) => handleNotificationChange("notify_research_complete", e.target.checked)}
                            disabled={!notificationSettings.email_enabled && !notificationSettings.browser_enabled}
                            className="w-4 h-4 rounded border-gray-300 accent-primary focus:ring-primary disabled:opacity-50"
                          />
                          <span className="text-sm">研究任务完成通知</span>
                        </label>
                        <label className="flex items-center gap-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={notificationSettings.notify_mention}
                            onChange={(e) => handleNotificationChange("notify_mention", e.target.checked)}
                            disabled={!notificationSettings.email_enabled && !notificationSettings.browser_enabled}
                            className="w-4 h-4 rounded border-gray-300 accent-primary focus:ring-primary disabled:opacity-50"
                          />
                          <span className="text-sm">被提及通知</span>
                        </label>
                      </div>
                    </div>

                    {notificationSaving && (
                      <div className="text-sm text-muted-foreground">保存中...</div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* ========== 环境变量设置 ========== */}
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
