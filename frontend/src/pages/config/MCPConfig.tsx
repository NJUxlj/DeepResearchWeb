import { useState, useEffect } from "react";
import { Server, Plus, Trash2, Power, PowerOff, Play, Loader2, X, Pencil } from "lucide-react";
import { mcpApi } from "@/api/mcp";
import type { MCPConfig } from "@/types/citation";

export function MCPConfig() {
  const [servers, setServers] = useState<MCPConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testingId, setTestingId] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingServer, setEditingServer] = useState<MCPConfig | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    loadServers();
  }, []);

  const loadServers = async () => {
    setIsLoading(true);
    try {
      const response = await mcpApi.list();
      setServers(response.items);
    } catch (err) {
      setError("加载 MCP 服务器列表失败");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (id: number, enabled: boolean) => {
    try {
      await mcpApi.toggle(id, !enabled);
      setServers((prev) =>
        prev.map((server) =>
          server.id === id ? { ...server, enabled: !enabled } : server
        )
      );
    } catch (err) {
      console.error("Failed to toggle server:", err);
      alert("切换 MCP 服务器状态失败，请重试");
    }
  };

  const handleTest = async (id: number) => {
    setTestingId(id);
    try {
      const result = await mcpApi.test(id);
      alert(result.success ? "连接成功！" : `连接失败：${result.message}`);
    } catch (err) {
      alert("测试连接失败");
      console.error(err);
    } finally {
      setTestingId(null);
    }
  };

  const handleDelete = async (id: number) => {
    // TODO: 后续应替换为自定义 Modal/Dialog 组件，以保持 UI 一致性
    if (!window.confirm("确定要删除这个 MCP 服务器吗？")) return;
    try {
      await mcpApi.delete(id);
      setServers((prev) => prev.filter((server) => server.id !== id));
    } catch (err) {
      console.error("Failed to delete server:", err);
      alert("删除 MCP 服务器失败，请重试");
    }
  };

  const handleCreateServer = async (data: Partial<MCPConfig>) => {
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const newServer = await mcpApi.create(data as Omit<MCPConfig, "id">);
      setServers((prev) => [...prev, newServer]);
      setIsModalOpen(false);
    } catch (err: any) {
      setSubmitError(err?.response?.data?.detail || "创建 MCP 服务器失败");
      console.error("Failed to create server:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (server: MCPConfig) => {
    setEditingServer(server);
    setIsEditModalOpen(true);
  };

  const handleUpdateServer = async (data: Partial<MCPConfig>) => {
    if (!editingServer) return;
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const updatedServer = await mcpApi.update(editingServer.id, data);
      setServers((prev) =>
        prev.map((server) => (server.id === editingServer.id ? updatedServer : server))
      );
      setIsEditModalOpen(false);
      setEditingServer(null);
    } catch (err: any) {
      setSubmitError(err?.response?.data?.detail || "更新 MCP 服务器失败");
      console.error("Failed to update server:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">加载中...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Server className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold">MCP 配置</h1>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
        >
          <Plus className="w-4 h-4" />
          添加服务器
        </button>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive text-destructive rounded-lg p-3 mb-4">
          {error}
        </div>
      )}

      {servers.length === 0 ? (
        <div className="text-center text-muted-foreground py-12">
          <Server className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无 MCP 服务器配置</p>
          <p className="text-sm mt-1">点击添加按钮创建新 MCP 服务器</p>
        </div>
      ) : (
        <div className="space-y-3">
          {servers.map((server) => (
            <div
              key={server.id}
              className={`p-4 rounded-lg border bg-card ${
                server.enabled ? "border-primary" : "border-border"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${server.enabled ? "bg-primary/10" : "bg-muted"}`}>
                    <Server className={`w-5 h-5 ${server.enabled ? "text-primary" : "text-muted-foreground"}`} />
                  </div>
                  <div>
                    <h3 className="font-medium">{server.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      类型: {server.transport === "stdio" ? "标准输入输出" : "HTTP"} |
                      {server.transport === "stdio"
                        ? ` 命令: ${server.command}`
                        : ` URL: ${server.url}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleEdit(server)}
                    className="p-2 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-lg transition-colors"
                    title="编辑"
                  >
                    <Pencil className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleTest(server.id)}
                    disabled={testingId === server.id}
                    className="p-2 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-lg transition-colors disabled:opacity-50"
                    title="测试连接"
                  >
                    {testingId === server.id ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Play className="w-5 h-5" />
                    )}
                  </button>
                  <button
                    onClick={() => handleToggle(server.id, server.enabled)}
                    className={`p-2 rounded-lg transition-colors ${
                      server.enabled
                        ? "text-primary hover:bg-primary/10"
                        : "text-muted-foreground hover:bg-muted"
                    }`}
                    title={server.enabled ? "禁用" : "启用"}
                  >
                    {server.enabled ? <Power className="w-5 h-5" /> : <PowerOff className="w-5 h-5" />}
                  </button>
                  <button
                    onClick={() => handleDelete(server.id)}
                    className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
                    title="删除"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* MCP Form Modal */}
      {isModalOpen && (
        <MCPFormModal
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleCreateServer}
          isSubmitting={isSubmitting}
          error={submitError}
        />
      )}

      {/* MCP Edit Modal */}
      {isEditModalOpen && editingServer && (
        <MCPEditModal
          server={editingServer}
          onClose={() => {
            setIsEditModalOpen(false);
            setEditingServer(null);
          }}
          onSubmit={handleUpdateServer}
          isSubmitting={isSubmitting}
          error={submitError}
        />
      )}
    </div>
  );
}

interface MCPFormModalProps {
  onClose: () => void;
  onSubmit: (data: Partial<MCPConfig>) => void;
  isSubmitting: boolean;
  error: string | null;
}

function MCPFormModal({ onClose, onSubmit, isSubmitting, error }: MCPFormModalProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    transport: "stdio" as "stdio" | "http",
    command: "",
    args: "",
    env: "",
    url: "",
    enabled: true,
  });
  const [envError, setEnvError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Parse env if provided (key=value format, one per line)
    const env: Record<string, string> = {};
    if (formData.transport === "stdio" && formData.env.trim()) {
      try {
        const envLines = formData.env.trim().split("\n");
        for (const line of envLines) {
          const [key, ...valueParts] = line.split("=");
          if (key && valueParts.length > 0) {
            env[key.trim()] = valueParts.join("=").trim();
          }
        }
      } catch {
        setEnvError("环境变量格式错误，应为 key=value 格式，每行一个");
        return;
      }
    }

    // Parse args if provided (comma-separated)
    const args: string[] = formData.transport === "stdio" && formData.args.trim()
      ? formData.args.split(",").map((a) => a.trim()).filter((a) => a.length > 0)
      : [];

    // 直接发送顶层字段，与后端 MCPServerConfigBase 保持一致
    onSubmit({
      name: formData.name,
      description: formData.description,
      transport: formData.transport,
      command: formData.transport === "stdio" ? formData.command : null,
      args: formData.transport === "stdio" && args.length > 0 ? args : [],
      env: formData.transport === "stdio" && Object.keys(env).length > 0 ? env : {},
      url: formData.transport === "http" ? formData.url : null,
      enabled: formData.enabled,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-background rounded-lg shadow-lg w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">添加 MCP 服务器</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-accent"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive text-destructive rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">
              名称 <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="请输入服务器名称"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">描述</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="请输入服务器描述"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">传输方式</label>
            <select
              value={formData.transport}
              onChange={(e) => setFormData({ ...formData, transport: e.target.value as "stdio" | "http" })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="stdio">标准输入输出 (stdio)</option>
              <option value="http">HTTP</option>
            </select>
          </div>

          {formData.transport === "stdio" && (
            <>
              <div>
                <label className="block text-sm font-medium mb-2">
                  命令 <span className="text-destructive">*</span>
                </label>
                <input
                  type="text"
                  value={formData.command}
                  onChange={(e) => setFormData({ ...formData, command: e.target.value })}
                  required={formData.transport === "stdio"}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="例如: npx, python"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  参数 <span className="text-muted-foreground">(逗号分隔)</span>
                </label>
                <input
                  type="text"
                  value={formData.args}
                  onChange={(e) => setFormData({ ...formData, args: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="例如: -y, @modelcontextprotocol/server-filesystem"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  环境变量 <span className="text-muted-foreground">(每行一个 key=value)</span>
                  {envError && <span className="text-destructive ml-2 text-xs">{envError}</span>}
                </label>
                <textarea
                  value={formData.env}
                  onChange={(e) => {
                    setFormData({ ...formData, env: e.target.value });
                    setEnvError(null);
                  }}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
                  rows={3}
                  placeholder="KEY=value
ANOTHER_KEY=value2"
                />
              </div>
            </>
          )}

          {formData.transport === "http" && (
            <div>
              <label className="block text-sm font-medium mb-2">
                URL <span className="text-destructive">*</span>
              </label>
              <input
                type="url"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                required={formData.transport === "http"}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="例如: http://localhost:3000/mcp"
              />
            </div>
          )}

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="mcp-enabled"
              checked={formData.enabled}
              onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300 accent-primary focus:ring-primary"
            />
            <label htmlFor="mcp-enabled" className="text-sm font-medium">
              启用
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border rounded-lg hover:bg-accent"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 flex items-center gap-2"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              {isSubmitting ? "创建中..." : "创建"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

interface MCPEditModalProps {
  server: MCPConfig;
  onClose: () => void;
  onSubmit: (data: Partial<MCPConfig>) => void;
  isSubmitting: boolean;
  error: string | null;
}

function MCPEditModal({ server, onClose, onSubmit, isSubmitting, error }: MCPEditModalProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  // Convert env object to string format for editing
  const convertEnvToString = (env: Record<string, string> | undefined | null): string => {
    if (!env) return "";
    return Object.entries(env)
      .map(([key, value]) => `${key}=${value}`)
      .join("\n");
  };

  const [formData, setFormData] = useState({
    name: server.name,
    description: server.description || "",
    transport: (server.transport || "stdio") as "stdio" | "http",
    command: server.command || "",
    args: server.args?.join(", ") || "",
    env: convertEnvToString(server.env),
    url: server.url || "",
    enabled: server.enabled,
  });
  const [envError, setEnvError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Parse env if provided (key=value format, one per line)
    const env: Record<string, string> = {};
    if (formData.transport === "stdio" && formData.env.trim()) {
      try {
        const envLines = formData.env.trim().split("\n");
        for (const line of envLines) {
          const [key, ...valueParts] = line.split("=");
          if (key && valueParts.length > 0) {
            env[key.trim()] = valueParts.join("=").trim();
          }
        }
      } catch {
        setEnvError("环境变量格式错误，应为 key=value 格式，每行一个");
        return;
      }
    }

    // Parse args if provided (comma-separated)
    const args: string[] = formData.transport === "stdio" && formData.args.trim()
      ? formData.args.split(",").map((a) => a.trim()).filter((a) => a.length > 0)
      : [];

    // 直接发送顶层字段，与后端 MCPServerConfigBase 保持一致
    onSubmit({
      name: formData.name,
      description: formData.description,
      transport: formData.transport,
      command: formData.transport === "stdio" ? formData.command : null,
      args: formData.transport === "stdio" && args.length > 0 ? args : [],
      env: formData.transport === "stdio" && Object.keys(env).length > 0 ? env : {},
      url: formData.transport === "http" ? formData.url : null,
      enabled: formData.enabled,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-background rounded-lg shadow-lg w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">编辑 MCP 服务器</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-accent"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive text-destructive rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">
              名称 <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="请输入服务器名称"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">描述</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="请输入服务器描述"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">传输方式</label>
            <select
              value={formData.transport}
              onChange={(e) => setFormData({ ...formData, transport: e.target.value as "stdio" | "http" })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="stdio">标准输入输出 (stdio)</option>
              <option value="http">HTTP</option>
            </select>
          </div>

          {formData.transport === "stdio" && (
            <>
              <div>
                <label className="block text-sm font-medium mb-2">
                  命令 <span className="text-destructive">*</span>
                </label>
                <input
                  type="text"
                  value={formData.command}
                  onChange={(e) => setFormData({ ...formData, command: e.target.value })}
                  required={formData.transport === "stdio"}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="例如: npx, python"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  参数 <span className="text-muted-foreground">(逗号分隔)</span>
                </label>
                <input
                  type="text"
                  value={formData.args}
                  onChange={(e) => setFormData({ ...formData, args: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="例如: -y, @modelcontextprotocol/server-filesystem"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  环境变量 <span className="text-muted-foreground">(每行一个 key=value)</span>
                  {envError && <span className="text-destructive ml-2 text-xs">{envError}</span>}
                </label>
                <textarea
                  value={formData.env}
                  onChange={(e) => {
                    setFormData({ ...formData, env: e.target.value });
                    setEnvError(null);
                  }}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
                  rows={3}
                  placeholder="KEY=value
ANOTHER_KEY=value2"
                />
              </div>
            </>
          )}

          {formData.transport === "http" && (
            <div>
              <label className="block text-sm font-medium mb-2">
                URL <span className="text-destructive">*</span>
              </label>
              <input
                type="url"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                required={formData.transport === "http"}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="例如: http://localhost:3000/mcp"
              />
            </div>
          )}

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="edit-mcp-enabled"
              checked={formData.enabled}
              onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300 accent-primary focus:ring-primary"
            />
            <label htmlFor="edit-mcp-enabled" className="text-sm font-medium">
              启用
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border rounded-lg hover:bg-accent"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 flex items-center gap-2"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              {isSubmitting ? "保存中..." : "保存"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
