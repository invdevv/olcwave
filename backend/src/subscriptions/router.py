from fastapi import APIRouter, HTTPException, Response, Depends

from core.config import settings
from core.factories import get_remnawave_service
from users.service import Users
from rw.service import RemnawaveService
from settings.service import SettingsService
from subscriptions.service import Subscriptions


router = APIRouter(prefix="/sub", tags=["subscriptions"])


@router.get("/{short_uuid}/check")
async def get_provider_name(
    short_uuid: str,
    remnawave_service: RemnawaveService = Depends(get_remnawave_service)
) -> Response:
    if settings.RW_ENABLED:
        if not await remnawave_service.get_subscription_info(short_uuid):
            raise HTTPException(status_code=404, detail="Not found")
    else:
        try:
            await Users.get(short_uuid)
        except HTTPException:
            raise HTTPException(status_code=404, detail="Not found")

    name = SettingsService.get().sub_name

    return Response(
        content=name,
        media_type="text/plain"
    )


@router.get("/{short_uuid}")
async def get(short_uuid: str):
    return await Subscriptions.get(short_uuid)
