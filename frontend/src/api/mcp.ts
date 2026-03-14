import { apiRequest } from "./client";
import type { MCPConfig } from "@/types/citation";

export interface MCPListResponse {
  items: MCPConfig[];
  total: number;
}

export const mcpApi = {
  /**
   * 获取 MCP 服务器列表
   */
  list: async (): Promise<MCPListResponse> => {
    return apiRequest<MCPListResponse>({
      method: "GET",
      url: "/mcp/servers",
    });
  },

  /**
   * 获取单个 MCP 服务器详情
   */
  get: async (id: number): Promise<MCPConfig> => {
    return apiRequest<MCPConfig>({
      method: "GET",
      url: `/mcp/servers/${id}`,
    });
  },

  /**
   * 创建 MCP 服务器
   */
  create: async (data: Omit<MCPConfig, "id">): Promise<MCPConfig> => {
    return apiRequest<MCPConfig>({
      method: "POST",
      url: "/mcp/servers",
      data,
    });
  },

  /**
   * 更新 MCP 服务器
   */
  update: async (id: number, data: Partial<MCPConfig>): Promise<MCPConfig> => {
    return apiRequest<MCPConfig>({
      method: "PUT",
      url: `/mcp/servers/${id}`,
      data,
    });
  },

  /**
   * 删除 MCP 服务器
   */
  delete: async (id: number): Promise<void> => {
    return apiRequest<void>({
      method: "DELETE",
      url: `/mcp/servers/${id}`,
    });
  },

  /**
   * 启用/禁用 MCP 服务器
   */
  toggle: async (id: number, enabled: boolean): Promise<MCPConfig> => {
    return apiRequest<MCPConfig>({
      method: "PATCH",
      url: `/mcp/servers/${id}/toggle`,
      data: { enabled },
    });
  },

  /**
   * 测试 MCP 服务器连接
   */
  test: async (id: number): Promise<{ success: boolean; message: string }> => {
    return apiRequest<{ success: boolean; message: string }>({
      method: "POST",
      url: `/mcp/servers/${id}/test`,
    });
  },
};
