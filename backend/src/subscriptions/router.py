from fastapi import APIRouter, HTTPException, Response, Depends

from core.config import settings
from core.factories import (
    get_remnawave_service,
    get_users_service,
    get_subscription_service,
    get_settings_service,
)
from users.service import UsersService
from rw.service import RemnawaveService
from settings.service import SettingsService
from subscriptions.service import SubscriptionsService


router = APIRouter(prefix="/sub", tags=["subscriptions"])


@router.get("/{short_uuid}/check")
async def get_provider_name(
    short_uuid: str,
    remnawave_service: RemnawaveService = Depends(get_remnawave_service),
    users_service: UsersService = Depends(get_users_service),
    settings_service: SettingsService = Depends(get_settings_service)
) -> Response:
    if settings.RW_ENABLED:
        if not await remnawave_service.get_subscription_info(short_uuid):
            raise HTTPException(status_code=404, detail="Not found")
    else:
        try:
            await users_service.get(short_uuid)
        except HTTPException:
            raise HTTPException(status_code=404, detail="Not found")

    name = settings_service.get().sub_name

    return Response(
        content=name,
        media_type="text/plain"
    )


@router.get("/{short_uuid}")
async def get(
    short_uuid: str,
    subscription_service: SubscriptionsService = Depends(
        get_subscription_service)
) -> Response:
    return await subscription_service.get(short_uuid)
