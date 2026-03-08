import { apiRequest } from "./client";
import type { HealthResponse } from "@/types";

export const healthApi = {
  /** 基础健康检查 */
  check: () =>
    apiRequest<HealthResponse>({
      method: "GET",
      url: "/health",
    }),

  /** 详细健康检查 */
  checkDetail: () =>
    apiRequest<HealthResponse & { database: string; redis: string }>({
      method: "GET",
      url: "/health/detail",
    }),
};
