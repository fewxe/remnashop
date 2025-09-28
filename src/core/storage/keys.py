from src.core.storage.key_builder import StorageKey


class WebhookLockKey(StorageKey, prefix="webhook_lock"):
    bot_id: int
    webhook_hash: str


class AccessModeKey(StorageKey, prefix="access_mode"): ...


class AccessWaitListKey(StorageKey, prefix="access_wait_list"): ...


class DefaultCurrencyKey(StorageKey, prefix="default_currency"): ...


class SystemNotificationSettingsKey(StorageKey, prefix="system_notification_settings"): ...


class UserNotificationSettingsKey(StorageKey, prefix="user_notification_settings"): ...


class RecentRegisteredUsersKey(StorageKey, prefix="recent_registered_users"): ...


class RecentActivityUsersKey(StorageKey, prefix="recent_activity_users"): ...
