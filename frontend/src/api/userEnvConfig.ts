import { apiRequest } from "./client";

export interface UserEnvConfigInitResponse {
  env_config: Record<string, string>;
  is_new: boolean;
}

export interface UserEnvConfigResponse {
  id: number;
  user_id: number;
  config_name: string;
  env_config: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export const userEnvConfigApi = {
  /** 获取用户环境配置 */
  get: (configName: string = "default") =>
    apiRequest<UserEnvConfigInitResponse>({
      method: "GET",
      url: `/user-env-config?config_name=${configName}`,
    }),

  /** 创建用户环境配置 */
  create: (configName: string = "default", envConfig: Record<string, string>) =>
    apiRequest<UserEnvConfigResponse>({
      method: "POST",
      url: `/user-env-config?config_name=${configName}`,
      data: {
        config_name: configName,
        env_config: envConfig,
      },
    }),

  /** 更新用户环境配置 */
  update: (configName: string = "default", envConfig: Record<string, string>) =>
    apiRequest<UserEnvConfigResponse>({
      method: "PUT",
      url: `/user-env-config?config_name=${configName}`,
      data: {
        config_name: configName,
        env_config: envConfig,
      },
    }),

  /** 删除用户环境配置 */
  delete: (configName: string = "default") =>
    apiRequest<void>({
      method: "DELETE",
      url: `/user-env-config?config_name=${configName}`,
    }),
};
