from datetime import datetime
from fastapi import APIRouter

from users.service import Users

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def get(short_uuid: str):
    user = await Users.get(short_uuid)
    return user

@router.put("/")
async def update(short_uuid: str, expires_at: datetime):
    user = await Users.update(short_uuid, expires_at)
    return user

@router.delete("/")
async def delete(short_uuid: str):
    user = await Users.delete(short_uuid)
    return user

