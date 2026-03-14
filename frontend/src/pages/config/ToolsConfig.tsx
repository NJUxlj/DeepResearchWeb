import { useState, useEffect } from "react";
import { Wrench, Plus, Trash2, Power, PowerOff, X, Pencil } from "lucide-react";
import { toolsApi } from "@/api/tools";
import type { ToolConfig } from "@/types/citation";

export function ToolsConfig() {
  const [tools, setTools] = useState<ToolConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingTool, setEditingTool] = useState<ToolConfig | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    setIsLoading(true);
    try {
      const response = await toolsApi.list();
      setTools(response.items);
    } catch (err) {
      setError("加载工具列表失败");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (id: number, enabled: boolean) => {
    try {
      await toolsApi.toggle(id, !enabled);
      setTools((prev) =>
        prev.map((tool) =>
          tool.id === id ? { ...tool, enabled: !enabled } : tool
        )
      );
    } catch (err) {
      console.error("Failed to toggle tool:", err);
      alert("切换工具状态失败，请重试");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("确定要删除这个工具吗？")) return;
    try {
      await toolsApi.delete(id);
      setTools((prev) => prev.filter((tool) => tool.id !== id));
    } catch (err) {
      console.error("Failed to delete tool:", err);
    }
  };

  const handleCreateTool = async (data: Partial<ToolConfig>) => {
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      await toolsApi.create(data as Omit<ToolConfig, "id">);
      setIsModalOpen(false);
      loadTools();
    } catch (err: any) {
      setSubmitError(err?.response?.data?.detail || "创建工具失败");
      console.error("Failed to create tool:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (tool: ToolConfig) => {
    setEditingTool(tool);
    setIsEditModalOpen(true);
  };

  const handleUpdateTool = async (data: Partial<ToolConfig>) => {
    if (!editingTool) return;
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      await toolsApi.update(editingTool.id, data);
      setIsEditModalOpen(false);
      setEditingTool(null);
      loadTools();
    } catch (err: any) {
      setSubmitError(err?.response?.data?.detail || "更新工具失败");
      console.error("Failed to update tool:", err);
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
          <Wrench className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold">工具配置</h1>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
        >
          <Plus className="w-4 h-4" />
          添加工具
        </button>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive text-destructive rounded-lg p-3 mb-4">
          {error}
        </div>
      )}

      {tools.length === 0 ? (
        <div className="text-center text-muted-foreground py-12">
          <Wrench className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无工具配置</p>
          <p className="text-sm mt-1">点击添加按钮创建新工具</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tools.map((tool) => (
            <div
              key={tool.id}
              className={`p-4 rounded-lg border bg-card ${
                tool.enabled ? "border-primary" : "border-border"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${tool.enabled ? "bg-primary/10" : "bg-muted"}`}>
                    <Wrench className={`w-5 h-5 ${tool.enabled ? "text-primary" : "text-muted-foreground"}`} />
                  </div>
                  <div>
                    <h3 className="font-medium">{tool.name}</h3>
                    <p className="text-sm text-muted-foreground">{tool.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {tool.id !== 0 && (
                    <>
                      <button
                        onClick={() => handleEdit(tool)}
                        className="p-2 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-lg transition-colors"
                        title="编辑"
                      >
                        <Pencil className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleToggle(tool.id, tool.enabled)}
                        className={`p-2 rounded-lg transition-colors ${
                          tool.enabled
                            ? "text-primary hover:bg-primary/10"
                            : "text-muted-foreground hover:bg-muted"
                        }`}
                        title={tool.enabled ? "禁用" : "启用"}
                      >
                        {tool.enabled ? <Power className="w-5 h-5" /> : <PowerOff className="w-5 h-5" />}
                      </button>
                      <button
                        onClick={() => handleDelete(tool.id)}
                        className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
                        title="删除"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tool Form Modal */}
      {isModalOpen && (
        <ToolFormModal
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleCreateTool}
          isSubmitting={isSubmitting}
          error={submitError}
        />
      )}

      {/* Tool Edit Modal */}
      {isEditModalOpen && editingTool && (
        <ToolEditModal
          tool={editingTool}
          onClose={() => {
            setIsEditModalOpen(false);
            setEditingTool(null);
          }}
          onSubmit={handleUpdateTool}
          isSubmitting={isSubmitting}
          error={submitError}
        />
      )}
    </div>
  );
}

interface ToolFormModalProps {
  onClose: () => void;
  onSubmit: (data: Partial<ToolConfig>) => void;
  isSubmitting: boolean;
  error: string | null;
}

function ToolFormModal({ onClose, onSubmit, isSubmitting, error }: ToolFormModalProps) {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    tool_type: "custom",
    config: "{}",
    enabled: true,
  });
  const [configError, setConfigError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate JSON config
    try {
      JSON.parse(formData.config);
      setConfigError(null);
    } catch {
      setConfigError("JSON 格式不正确");
      return;
    }

    onSubmit({
      name: formData.name,
      description: formData.description,
      tool_type: formData.tool_type,
      config: JSON.parse(formData.config),
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
          <h2 className="text-lg font-semibold">添加工具</h2>
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
              placeholder="请输入工具名称"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">描述</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="请输入工具描述"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">工具类型</label>
            <select
              value={formData.tool_type}
              onChange={(e) => setFormData({ ...formData, tool_type: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="custom">自定义</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              配置 (JSON)
              {configError && <span className="text-destructive ml-2 text-xs">{configError}</span>}
            </label>
            <textarea
              value={formData.config}
              onChange={(e) => setFormData({ ...formData, config: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
              rows={4}
              placeholder='{"key": "value"}'
            />
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="enabled"
              checked={formData.enabled}
              onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            <label htmlFor="enabled" className="text-sm font-medium">
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
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
            >
              {isSubmitting ? "创建中..." : "创建"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

interface ToolEditModalProps {
  tool: ToolConfig;
  onClose: () => void;
  onSubmit: (data: Partial<ToolConfig>) => void;
  isSubmitting: boolean;
  error: string | null;
}

function ToolEditModal({ tool, onClose, onSubmit, isSubmitting, error }: ToolEditModalProps) {
  const [formData, setFormData] = useState({
    name: tool.name,
    description: tool.description || "",
    tool_type: tool.tool_type || "custom",
    config: typeof tool.config === "string" ? tool.config : JSON.stringify(tool.config, null, 2),
    enabled: tool.enabled,
  });
  const [configError, setConfigError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate JSON config
    try {
      JSON.parse(formData.config);
      setConfigError(null);
    } catch {
      setConfigError("JSON 格式不正确");
      return;
    }

    onSubmit({
      name: formData.name,
      description: formData.description,
      tool_type: formData.tool_type,
      config: JSON.parse(formData.config),
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
          <h2 className="text-lg font-semibold">编辑工具</h2>
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
              placeholder="请输入工具名称"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">描述</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="请输入工具描述"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">工具类型</label>
            <select
              value={formData.tool_type}
              onChange={(e) => setFormData({ ...formData, tool_type: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="custom">自定义</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              配置 (JSON)
              {configError && <span className="text-destructive ml-2 text-xs">{configError}</span>}
            </label>
            <textarea
              value={formData.config}
              onChange={(e) => setFormData({ ...formData, config: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
              rows={4}
              placeholder='{"key": "value"}'
            />
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="edit-enabled"
              checked={formData.enabled}
              onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            <label htmlFor="edit-enabled" className="text-sm font-medium">
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
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
            >
              {isSubmitting ? "保存中..." : "保存"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
