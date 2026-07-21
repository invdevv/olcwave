from datetime import datetime
from fastapi import APIRouter, Depends

from auth.dependencies import get_current_admin
from users.service import Users

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def get(short_uuid: str, _admin: dict = Depends(get_current_admin)):
    user = await Users.get(short_uuid)
    return user

@router.put("/")
async def update(short_uuid: str, expires_at: datetime, _admin: dict = Depends(get_current_admin)):
    user = await Users.update(short_uuid, expires_at)
    return user

@router.delete("/")
async def delete(short_uuid: str, _admin: dict = Depends(get_current_admin)):
    user = await Users.delete(short_uuid)
    return user

@router.get("/all")
async def get_all(tag: str, _admin: dict = Depends(get_current_admin)):
    users = await Users.get_all()

    return users