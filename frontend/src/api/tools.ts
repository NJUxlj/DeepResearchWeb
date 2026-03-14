import { apiRequest } from "./client";
import type { ToolConfig } from "@/types/citation";

export interface ToolListResponse {
  items: ToolConfig[];
  total: number;
}

export const toolsApi = {
  /**
   * 获取工具列表
   */
  list: async (): Promise<ToolListResponse> => {
    return apiRequest<ToolListResponse>({
      method: "GET",
      url: "/tools",
    });
  },

  /**
   * 获取单个工具详情
   */
  get: async (id: number): Promise<ToolConfig> => {
    return apiRequest<ToolConfig>({
      method: "GET",
      url: `/tools/${id}`,
    });
  },

  /**
   * 创建工具
   */
  create: async (data: Omit<ToolConfig, "id">): Promise<ToolConfig> => {
    return apiRequest<ToolConfig>({
      method: "POST",
      url: "/tools",
      data,
    });
  },

  /**
   * 更新工具
   */
  update: async (id: number, data: Partial<ToolConfig>): Promise<ToolConfig> => {
    return apiRequest<ToolConfig>({
      method: "PUT",
      url: `/tools/${id}`,
      data,
    });
  },

  /**
   * 删除工具
   */
  delete: async (id: number): Promise<void> => {
    return apiRequest<void>({
      method: "DELETE",
      url: `/tools/${id}`,
    });
  },

  /**
   * 启用/禁用工具
   */
  toggle: async (id: number, enabled: boolean): Promise<ToolConfig> => {
    return apiRequest<ToolConfig>({
      method: "PATCH",
      url: `/tools/${id}/toggle`,
      data: { enabled },
    });
  },
};
