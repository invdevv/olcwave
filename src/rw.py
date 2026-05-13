from remnawave import RemnawaveSDK
from remnawave.exceptions.general import NotFoundError
from remnawave.models import (
    SubscriptionInfoResponseDto,
    SubscriptionSettingsResponseDto
)

from config import settings


remnawave = RemnawaveSDK(base_url=settings.RW_API_URL, token=settings.RW_API_TOKEN)


async def isUserValid(short_uuid: str) -> SubscriptionInfoResponseDto | None:
    try:
        sub = await remnawave.subscription.get_subscription_info_by_short_uuid(short_uuid)
    except NotFoundError:
        return None
        
    return sub  # pyright: ignore[reportReturnType]


async def getSubscriptionSettings():
    sub: SubscriptionSettingsResponseDto = await remnawave.subscriptions_settings.get_settings()  # pyright: ignore[reportAssignmentType]

    return sub