from fastapi import APIRouter, Response
from subscriptions.service import Subscriptions

router = APIRouter(prefix="/sub", tags=["subscriptions"])

@router.get("/{short_uuid}")
async def get(short_uuid: str):
    sub = await Subscriptions.get(short_uuid)
    
    return Response(content=sub, headers={"profile-update-interval": "1"}, media_type="text/plain")