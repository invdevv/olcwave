from fastapi import APIRouter, HTTPException, Response
from config import settings
from settings.service import SettingsService
from subscriptions.service import Subscriptions
from users.service import Users

router = APIRouter(prefix="/sub", tags=["subscriptions"])


@router.get("/{short_uuid}/check")
async def get_provider_name(short_uuid: str):
    if settings.RW_ENABLED:
        from rw.sdk import get_subscription_info
        if not await get_subscription_info(short_uuid):
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
    sub = await Subscriptions.get(short_uuid)

    return sub
