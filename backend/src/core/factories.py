from functools import lru_cache

from core.config import settings
from remnawave.client import RemnawaveClient
from remnawave.service import RemnawaveService
from subscriptions.service import SubscriptionsService
from users.repository import UserRepository
from users.service import UsersService
from settings.service import SettingsService
from settings.repository import SettingsRepository
from routing.service import RoutingService
from routing.repository import RoutingRepository
from profiles.service import ProfilesService
from profiles.repository import ProfileRepository
from olcrtc.service import ContainersService
from traffic import TrafficManager
from rw_sync import SyncManager
from docker_client import docker_client
from xraycore.sdk import XrayCoreClient


@lru_cache
def get_xray_core_client() -> XrayCoreClient:
    return XrayCoreClient(docker_client)


@lru_cache
def get_containers_service() -> ContainersService:
    return ContainersService(get_xray_core_client())


@lru_cache
def get_settings_service() -> SettingsService:
    return SettingsService(SettingsRepository())


@lru_cache
def get_profiles_service() -> ProfilesService:
    return ProfilesService(ProfileRepository())


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
        settings_service=get_settings_service(),
        profiles_service=get_profiles_service(),
        containers_service=get_containers_service(),
    )


@lru_cache
def get_traffic_manager() -> TrafficManager:
    return TrafficManager(
        user_service=get_users_service(),
        settings_service=get_settings_service(),
    )


@lru_cache
def get_routing_service() -> RoutingService:
    return RoutingService(
        repo=RoutingRepository(),
        xray_core=get_xray_core_client(),
    )
