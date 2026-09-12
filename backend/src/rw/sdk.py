from uuid import UUID
from functools import lru_cache
from typing import Callable, Any

from remnawave.models.users import GetAllUsersResponseDto, UserResponseDto
from remnawave.models.users import GetUserByShortUuidResponseDto
from remnawave.models.subscription import GetSubscriptionInfoResponseDto
from remnawave import RemnawaveSDK
from remnawave.exceptions.general import NotFoundError
from remnawave.models import (
    SubscriptionInfoResponseDto,
    SubscriptionSettingsResponseDto
)

from config import settings


def make_uuid_optional(model) -> None:
    field = model.model_fields.get("uuid")

    if field is None:
        return

    field.annotation = UUID | None
    field.default = None

    model.model_rebuild(force=True)


def patch_remnawave_users() -> None:
    """
    Patch the Remnawave SDK models to make the `uuid` 
    field optional in certain user-related response DTOs.
    """
    make_uuid_optional(UserResponseDto)
    make_uuid_optional(GetUserByShortUuidResponseDto)
    GetAllUsersResponseDto.model_rebuild(force=True)


@lru_cache
def _get_sdk() -> RemnawaveSDK:
    patch_remnawave_users()
    return RemnawaveSDK(
        base_url=settings.RW_API_URL,
        token=settings.RW_API_TOKEN,
        caddy_token=settings.RW_CADDY_TOKEN or None,
    )


def ensure_enabled(func) -> Callable[..., Any]:
    def wrapper(*args, **kwargs) -> Any:
        if not settings.RW_ENABLED:
            raise RuntimeError("Remnawave is not enabled")
        return func(*args, **kwargs)
    return wrapper


@ensure_enabled
async def get_all_users() -> GetAllUsersResponseDto:
    sdk = _get_sdk()
    PAGE_SIZE = 100

    start = 0
    users: list[UserResponseDto] = []

    while True:
        response = await sdk.users.get_all_users(
            start=start,
            size=PAGE_SIZE,
        )

        users.extend(response.users)

        if len(response.users) < PAGE_SIZE or len(users) >= response.total:
            break

        start += len(response.users)

    return GetAllUsersResponseDto(
        users=users,
        total=len(users),
    )


def is_user_in_squad(user: UserResponseDto) -> bool:
    if not settings.RW_SQUAD_NAME:
        return True

    return any(
        settings.RW_SQUAD_NAME == squad.name or settings.RW_SQUAD_NAME == str(
            squad.uuid)
        for squad in user.active_internal_squads
    )


@ensure_enabled
async def get_subscription_info(
    short_uuid: str
) -> SubscriptionInfoResponseDto | None:
    sdk = _get_sdk()

    try:
        # pyright: ignore[reportAssignmentType]
        sub: GetSubscriptionInfoResponseDto = await sdk.subscription.get_subscription_info_by_short_uuid(short_uuid)

        if not sub.is_found:
            return None

        if settings.RW_SQUAD_NAME:
            # pyright: ignore[reportAssignmentType]
            user: GetUserByShortUuidResponseDto = await sdk.users.get_user_by_short_uuid(short_uuid)

            if not is_user_in_squad(user):
                return None

        return sub

    except NotFoundError:
        return None


@ensure_enabled
async def get_subscription_settings() -> SubscriptionSettingsResponseDto:
    sdk = _get_sdk()
    return await sdk.subscriptions_settings.get_settings()
