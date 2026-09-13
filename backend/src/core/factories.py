from functools import lru_cache

from core.config import settings
from rw.client import RemnawaveClient
from rw.service import RemnawaveService
from subscriptions.service import SubscriptionsService
from users.repository import UserRepository
from users.service import UsersService
from settings.service import SettingsService
from settings.repository import SettingsRepository
from traffic import TrafficManager
from rw_sync import SyncManager


@lru_cache
def get_settings_service() -> SettingsService:
    return SettingsService(SettingsRepository())


@lru_cache
def get_remnawave_service() -> RemnawaveService:
    return RemnawaveService(
        RemnawaveClient(
            base_url=settings.RW_API_URL,
            token=settings.RW_API_TOKEN,
            caddy_token=settings.RW_CADDY_TOKEN or None,
        )
    )


@lru_cache
def get_users_service() -> UsersService:
    return UsersService(
        repo=UserRepository(),
        settings_service=get_settings_service(),
        remnawave_service=get_remnawave_service(),
    )


@lru_cache
def get_sync_manager() -> SyncManager:
    return SyncManager(
        users_service=get_users_service(),
        settings_service=get_settings_service(),
    )


@lru_cache
def get_subscription_service() -> SubscriptionsService:
    return SubscriptionsService(
        remnawave_service=get_remnawave_service(),
        users_service=get_users_service(),
    )


@lru_cache
def get_traffic_manager() -> TrafficManager:
    return TrafficManager(
        user_service=get_users_service(),
        settings_service=get_settings_service(),
    )
