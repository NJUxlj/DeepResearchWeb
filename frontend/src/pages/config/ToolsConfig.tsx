import { useState, useEffect } from "react";
import { Wrench, Plus, Trash2, Power, PowerOff } from "lucide-react";
import { toolsApi } from "@/api/tools";
import type { ToolConfig } from "@/types/citation";

export function ToolsConfig() {
  const [tools, setTools] = useState<ToolConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  const handleToggle = async (id: string, enabled: boolean) => {
    try {
      await toolsApi.toggle(id, !enabled);
      setTools((prev) =>
        prev.map((tool) =>
          tool.id === id ? { ...tool, enabled: !enabled } : tool
        )
      );
    } catch (err) {
      console.error("Failed to toggle tool:", err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("确定要删除这个工具吗？")) return;
    try {
      await toolsApi.delete(id);
      setTools((prev) => prev.filter((tool) => tool.id !== id));
    } catch (err) {
      console.error("Failed to delete tool:", err);
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
        <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
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
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
