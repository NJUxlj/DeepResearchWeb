import { useState, useEffect } from "react";
import { Server, Plus, Trash2, Power, PowerOff, Play, Loader2 } from "lucide-react";
import { mcpApi } from "@/api/mcp";
import type { MCPConfig } from "@/types/citation";

export function MCPConfig() {
  const [servers, setServers] = useState<MCPConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testingId, setTestingId] = useState<string | null>(null);

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

  const handleToggle = async (id: string, enabled: boolean) => {
    try {
      await mcpApi.toggle(id, !enabled);
      setServers((prev) =>
        prev.map((server) =>
          server.id === id ? { ...server, enabled: !enabled } : server
        )
      );
    } catch (err) {
      console.error("Failed to toggle server:", err);
    }
  };

  const handleTest = async (id: string) => {
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

  const handleDelete = async (id: string) => {
    if (!confirm("确定要删除这个 MCP 服务器吗？")) return;
    try {
      await mcpApi.delete(id);
      setServers((prev) => prev.filter((server) => server.id !== id));
    } catch (err) {
      console.error("Failed to delete server:", err);
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
        <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
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
                      类型: {server.type === "stdio" ? "标准输入输出" : "HTTP"} |
                      {server.type === "stdio"
                        ? ` 命令: ${server.config.command}`
                        : ` URL: ${server.config.url}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
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
    </div>
  );
}
