"""用户设置 API 端点 (安全设置和通知设置)."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from app.api.deps import CurrentUserDep, DBDep
from app.core.security import get_password_hash, verify_password
from app.models.user_notification_settings import UserNotificationSettings

router = APIRouter(prefix="/user-settings", tags=["user-settings"])

# 默认通知设置
DEFAULT_NOTIFICATION_SETTINGS = {
    "email_enabled": True,
    "browser_enabled": False,
    "notify_new_message": True,
    "notify_research_complete": True,
    "notify_mention": True,
}


# ========== 安全设置 Schema ==========

class ChangePasswordRequest(BaseModel):
    """修改密码请求."""
    old_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    """修改密码响应."""
    success: bool
    message: str


# ========== 通知设置 Schema ==========

class NotificationSettingsResponse(BaseModel):
    """通知设置响应."""
    email_enabled: bool
    browser_enabled: bool
    notify_new_message: bool
    notify_research_complete: bool
    notify_mention: bool


class NotificationSettingsUpdate(BaseModel):
    """通知设置更新请求."""
    email_enabled: bool | None = None
    browser_enabled: bool | None = None
    notify_new_message: bool | None = None
    notify_research_complete: bool | None = None
    notify_mention: bool | None = None


# ========== 安全设置 API ==========

@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    summary="修改密码",
)
async def change_password(
    db: DBDep,
    current_user: CurrentUserDep,
    data: ChangePasswordRequest,
) -> ChangePasswordResponse:
    """修改用户密码."""
    # 验证旧密码
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码不正确",
        )

    # 验证新密码复杂度
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度至少为 8 个字符",
        )
    if not any(c.isupper() for c in data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码必须包含大写字母",
        )
    if not any(c.islower() for c in data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码必须包含小写字母",
        )
    if not any(c.isdigit() for c in data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码必须包含数字",
        )

    # 更新密码
    current_user.hashed_password = get_password_hash(data.new_password)
    await db.commit()

    return ChangePasswordResponse(
        success=True,
        message="密码修改成功",
    )


# ========== 通知设置 API ==========

@router.get(
    "/notifications",
    response_model=NotificationSettingsResponse,
    summary="获取通知设置",
)
async def get_notification_settings(
    db: DBDep,
    current_user: CurrentUserDep,
) -> NotificationSettingsResponse:
    """获取用户的通知设置."""
    result = await db.execute(
        select(UserNotificationSettings).where(
            UserNotificationSettings.user_id == current_user.id
        )
    )
    settings = result.scalar_one_or_none()

    if settings:
        return NotificationSettingsResponse(**settings.settings)

    # 返回默认设置
    return NotificationSettingsResponse(**DEFAULT_NOTIFICATION_SETTINGS)


@router.put(
    "/notifications",
    response_model=NotificationSettingsResponse,
    summary="更新通知设置",
)
async def update_notification_settings(
    db: DBDep,
    current_user: CurrentUserDep,
    data: NotificationSettingsUpdate,
) -> NotificationSettingsResponse:
    """更新用户的通知设置."""
    result = await db.execute(
        select(UserNotificationSettings).where(
            UserNotificationSettings.user_id == current_user.id
        )
    )
    settings = result.scalar_one_or_none()

    if settings:
        # 更新现有设置
        current_settings = settings.settings
        if data.email_enabled is not None:
            current_settings["email_enabled"] = data.email_enabled
        if data.browser_enabled is not None:
            current_settings["browser_enabled"] = data.browser_enabled
        if data.notify_new_message is not None:
            current_settings["notify_new_message"] = data.notify_new_message
        if data.notify_research_complete is not None:
            current_settings["notify_research_complete"] = data.notify_research_complete
        if data.notify_mention is not None:
            current_settings["notify_mention"] = data.notify_mention
        settings.settings = current_settings
    else:
        # 创建新设置
        new_settings = DEFAULT_NOTIFICATION_SETTINGS.copy()
        if data.email_enabled is not None:
            new_settings["email_enabled"] = data.email_enabled
        if data.browser_enabled is not None:
            new_settings["browser_enabled"] = data.browser_enabled
        if data.notify_new_message is not None:
            new_settings["notify_new_message"] = data.notify_new_message
        if data.notify_research_complete is not None:
            new_settings["notify_research_complete"] = data.notify_research_complete
        if data.notify_mention is not None:
            new_settings["notify_mention"] = data.notify_mention

        settings = UserNotificationSettings(
            user_id=current_user.id,
            settings=new_settings,
        )
        db.add(settings)

    await db.commit()
    await db.refresh(settings)

    return NotificationSettingsResponse(**settings.settings)
