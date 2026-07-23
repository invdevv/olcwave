from remnawave import RemnawaveSDK  # pyright: ignore[reportMissingTypeStubs]
from remnawave.exceptions.general import NotFoundError  # pyright: ignore[reportMissingTypeStubs]
from remnawave.models import (  # pyright: ignore[reportMissingTypeStubs]
    SubscriptionInfoResponseDto,
    SubscriptionSettingsResponseDto
)

from config import settings


remnawave = RemnawaveSDK(base_url=settings.RW_API_URL, token=settings.RW_API_TOKEN)


async def getAllUsers():
    users_coroutine = remnawave.users.get_all_users()
    users = await users_coroutine # what the f are this syntax

    return users

async def isUserValid(short_uuid: str) -> SubscriptionInfoResponseDto | None:
    try:
        sub = await remnawave.subscription.get_subscription_info_by_short_uuid(short_uuid)  # pyright: ignore[reportUnknownVariableType]
    except NotFoundError:
        return None
        
    return sub  # pyright: ignore[reportReturnType, reportUnknownVariableType]


async def getSubscriptionSettings():
    sub: SubscriptionSettingsResponseDto = await remnawave.subscriptions_settings.get_settings()  # pyright: ignore[reportAssignmentType, reportUnknownVariableType]

    return sub