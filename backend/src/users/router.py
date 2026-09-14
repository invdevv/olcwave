from fastapi import APIRouter, Depends, HTTPException, Depends

from auth.dependencies import get_current_admin
from core.config import settings
from core.factories import get_users_service
from users.service import UsersService
from users.schemas import UserSchema, TrafficInfoSchema, TrafficLimitUpdate


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get(
    short_uuid: str,
    _admin: dict = Depends(get_current_admin),
    users_service: UsersService = Depends(get_users_service),
) -> UserSchema:
    return await users_service.get(short_uuid)


@router.post("/")
async def create(
    body: UserSchema,
    _admin: dict = Depends(get_current_admin),
    users_service: UsersService = Depends(get_users_service),
) -> UserSchema:
    return await users_service.add(body)


@router.put("/")
async def update(
    body: UserSchema,
    _admin: dict = Depends(get_current_admin),
    users_service: UsersService = Depends(get_users_service),
) -> None:
    return await users_service.update(body)


@router.delete("/")
async def delete(
    short_uuid: str,
    _admin: dict = Depends(get_current_admin),
    users_service: UsersService = Depends(get_users_service)
) -> None:
    return await users_service.delete(short_uuid)


@router.get("/all")
async def get_all(
    _admin: dict = Depends(get_current_admin),
    users_service: UsersService = Depends(get_users_service)
) -> list[UserSchema]:
    return await users_service.get_all()


@router.get("/traffic")
async def get_traffic(
    short_uuid: str,
    _admin: dict = Depends(get_current_admin),
    users_service: UsersService = Depends(get_users_service)
) -> TrafficInfoSchema:
    return await users_service.get_traffic(short_uuid)


@router.patch("/traffic")
async def update_traffic(
    short_uuid: str,
    body: TrafficLimitUpdate,
    _admin: dict = Depends(get_current_admin),
    users_service: UsersService = Depends(get_users_service)
) -> TrafficInfoSchema:
    await users_service.set_traffic_limit(short_uuid, body.traffic_limit_bytes)
    return await users_service.get_traffic(short_uuid)


@router.post("/traffic/reset")
async def reset_traffic(
    short_uuid: str,
    _admin: dict = Depends(get_current_admin),
    users_service: UsersService = Depends(get_users_service)
) -> TrafficInfoSchema:
    await users_service.reset_traffic(short_uuid)
    return await users_service.get_traffic(short_uuid)


@router.post("/sync")
async def sync_from_remnawave(
    _admin: dict = Depends(get_current_admin),
    users_service: UsersService = Depends(get_users_service)
) -> dict[str, int]:
    if not settings.RW_ENABLED:
        raise HTTPException(status_code=400, detail="Remnawave is not enabled")
    res = await users_service.sync_with_remnawave()
    return res
