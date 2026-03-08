import { apiRequest } from "./client";
import type { SkillConfig } from "@/types/citation";

export interface SkillListResponse {
  items: SkillConfig[];
  total: number;
}

export const skillsApi = {
  /**
   * 获取 Skills 列表
   */
  list: async (): Promise<SkillListResponse> => {
    return apiRequest<SkillListResponse>({
      method: "GET",
      url: "/skills",
    });
  },

  /**
   * 获取单个 Skill 详情
   */
  get: async (id: string): Promise<SkillConfig> => {
    return apiRequest<SkillConfig>({
      method: "GET",
      url: `/skills/${id}`,
    });
  },

  /**
   * 创建 Skill
   */
  create: async (data: Omit<SkillConfig, "id">): Promise<SkillConfig> => {
    return apiRequest<SkillConfig>({
      method: "POST",
      url: "/skills",
      data,
    });
  },

  /**
   * 更新 Skill
   */
  update: async (id: string, data: Partial<SkillConfig>): Promise<SkillConfig> => {
    return apiRequest<SkillConfig>({
      method: "PUT",
      url: `/skills/${id}`,
      data,
    });
  },

  /**
   * 删除 Skill
   */
  delete: async (id: string): Promise<void> => {
    return apiRequest<void>({
      method: "DELETE",
      url: `/skills/${id}`,
    });
  },

  /**
   * 启用/禁用 Skill
   */
  toggle: async (id: string, enabled: boolean): Promise<SkillConfig> => {
    return apiRequest<SkillConfig>({
      method: "PATCH",
      url: `/skills/${id}/toggle`,
      data: { enabled },
    });
  },
};
