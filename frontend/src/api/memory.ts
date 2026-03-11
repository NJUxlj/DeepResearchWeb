import { apiRequest } from "./client";
import type {
  AddTreeMemoryRequest,
  MemoryFeedbackRequest,
  MemorySearchResponse,
  MemoryFeedbackResponse,
  AddPreferenceRequest,
} from "@/types/memory";

export const memoryApi = {
  /**
   * 搜索记忆
   */
  search: (query: string, topK?: number, searchType?: string) =>
    apiRequest<MemorySearchResponse>({
      method: "GET",
      url: "/memory/search",
      params: {
        query,
        top_k: topK ?? 10,
        search_type: searchType ?? "hybrid",
      },
    }),

  /**
   * 提交记忆反馈
   */
  submitFeedback: (data: MemoryFeedbackRequest) =>
    apiRequest<MemoryFeedbackResponse>({
      method: "POST",
      url: "/memory/feedback",
      data,
    }),

  /**
   * 添加树形记忆
   */
  addTreeMemory: (data: AddTreeMemoryRequest) =>
    apiRequest<{ status: string; memory?: unknown }>({
      method: "POST",
      url: "/memory/tree",
      data,
    }),

  /**
   * 添加偏好记忆
   */
  addPreference: (data: AddPreferenceRequest) =>
    apiRequest<{ status: string; memories?: unknown }>({
      method: "POST",
      url: "/memory/preference",
      data,
    }),
};
