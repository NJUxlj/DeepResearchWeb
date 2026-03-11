import { apiRequest } from "./client";

export interface NotificationSettings {
  email_enabled: boolean;
  browser_enabled: boolean;
  notify_new_message: boolean;
  notify_research_complete: boolean;
  notify_mention: boolean;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

export interface ChangePasswordResponse {
  success: boolean;
  message: string;
}

export const userSettingsApi = {
  /** 修改密码 */
  changePassword: (data: ChangePasswordRequest) =>
    apiRequest<ChangePasswordResponse>({
      method: "POST",
      url: "/user-settings/change-password",
      data,
    }),

  /** 获取通知设置 */
  getNotificationSettings: () =>
    apiRequest<NotificationSettings>({
      method: "GET",
      url: "/user-settings/notifications",
    }),

  /** 更新通知设置 */
  updateNotificationSettings: (data: Partial<NotificationSettings>) =>
    apiRequest<NotificationSettings>({
      method: "PUT",
      url: "/user-settings/notifications",
      data,
    }),
};
