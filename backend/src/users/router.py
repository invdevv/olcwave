from datetime import datetime
from fastapi import APIRouter, Depends

from auth.dependencies import get_current_admin
from users.service import Users
from users.schemas import UserSchema, TrafficInfoSchema, TrafficLimitUpdate
from rw.sdk import getAllUsers

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def get(short_uuid: str, _admin: dict = Depends(get_current_admin)):
    user = await Users.get(short_uuid)
    return user

@router.post("/")
async def create(body: UserSchema, _admin: dict = Depends(get_current_admin)):
    user = await Users.add(body)
    return user

@router.put("/")
async def update(body: UserSchema, _admin: dict = Depends(get_current_admin)):
    user = await Users.update(body)
    return user

@router.delete("/")
async def delete(short_uuid: str, _admin: dict = Depends(get_current_admin)):
    user = await Users.delete(short_uuid)
    return user

@router.get("/all")
async def get_all(_admin: dict = Depends(get_current_admin)):
    users = await Users.get_all()

    return users

@router.get("/traffic")
async def get_traffic(short_uuid: str, _admin: dict = Depends(get_current_admin)) -> TrafficInfoSchema:
    return await Users.get_traffic(short_uuid)

@router.patch("/traffic")
async def update_traffic(short_uuid: str, body: TrafficLimitUpdate, _admin: dict = Depends(get_current_admin)) -> TrafficInfoSchema:
    await Users.set_traffic_limit(short_uuid, body.traffic_limit_bytes)
    return await Users.get_traffic(short_uuid)

@router.post("/traffic/reset")
async def reset_traffic(short_uuid: str, _admin: dict = Depends(get_current_admin)) -> TrafficInfoSchema:
    await Users.reset_traffic(short_uuid)
    return await Users.get_traffic(short_uuid)

@router.post("/sync")
async def sync_from_remnawave(_admin: dict = Depends(get_current_admin)):
    res = await Users.sync_with_remnawave()

    return res