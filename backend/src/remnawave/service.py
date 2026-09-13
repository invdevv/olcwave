from functools import wraps

from core.config import settings
from .client import RemnawaveClient
from .exceptions import RemnaWaveNotFoundError
from .schemas import (
    GetAllUsersResponseDto,
    SubscriptionInfoResponseDto,
    SubscriptionSettingsResponseDto,
    UserResponseDto,
)


def ensure_enabled(func):
    """
    Нужно отказаться от этой проверки, но пока оставим, 
    чтобы не ломать существующую логику.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not settings.RW_ENABLED:
            raise RuntimeError("Remnawave is not enabled")
        return await func(*args, **kwargs)
    return wrapper


class RemnawaveService:
    def __init__(self, client: RemnawaveClient) -> None:
        self._client = client

    @ensure_enabled
    async def get_all_users(self) -> GetAllUsersResponseDto:
        """
        Получить всех пользователей из Remnawave.
        TODO: реализовать асинхронный генератор для постраничного получения 
        пользователей, чтобы не загружать всех сразу и не тратить память 
        на хранение всех пользователей в списке.
        """
        page_size = 100
        start = 0
        users: list[UserResponseDto] = []

        while True:
            response = await self._client.get_all_users(
                start=start,
                size=page_size,
            )
            users.extend(response.users)

            if len(response.users) < page_size or len(users) >= response.total:
                break

            start += len(response.users)

        return GetAllUsersResponseDto(users=users, total=len(users))

    @staticmethod
    def is_user_in_squad(user: UserResponseDto) -> bool:
        if not settings.RW_SQUAD_NAME:
            return True

        return any(
            settings.RW_SQUAD_NAME == squad.name
            or settings.RW_SQUAD_NAME == str(squad.uuid)
            for squad in user.active_internal_squads
        )

    @ensure_enabled
    async def get_subscription_info(
        self,
        short_uuid: str,
    ) -> SubscriptionInfoResponseDto | None:
        try:
            subscription = await self._client.get_subscription_info_by_short_uuid(
                short_uuid
            )

            if not subscription.is_found:
                return None

            if settings.RW_SQUAD_NAME:
                user = await self._client.get_user_by_short_uuid(short_uuid)
                if not self.is_user_in_squad(user):
                    return None

            return subscription
        except RemnaWaveNotFoundError:
            return None

    @ensure_enabled
    async def get_subscription_settings(self) -> SubscriptionSettingsResponseDto:
        return await self._client.get_subscription_settings()
