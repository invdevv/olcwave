from typing import Literal

from fastapi import APIRouter, Depends

from auth.dependencies import get_current_admin
from profiles.schemas import ProfileSchema
from profiles.service import ProfilesService
from core.factories import get_profiles_service

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/")
async def add(
    profile: ProfileSchema,
    _admin: dict = Depends(get_current_admin),
    profiles_service: ProfilesService = Depends(get_profiles_service)
) -> Literal['ok']:
    await profiles_service.add(profile)
    return "ok"


@router.get("/")
async def get(
    tag: str,
    _admin: dict = Depends(get_current_admin),
    profiles_service: ProfilesService = Depends(get_profiles_service)
) -> ProfileSchema:
    return await profiles_service.get(tag)


@router.put("/")
async def update(
    tag: str,
    name: str,
    profile: str,
    _admin: dict = Depends(get_current_admin),
    profiles_service: ProfilesService = Depends(get_profiles_service)
) -> None:
    await profiles_service.update(tag, name, profile)


@router.delete("/")
async def delete(
    tag: str,
    _admin: dict = Depends(get_current_admin),
    profiles_service: ProfilesService = Depends(get_profiles_service)
) -> None:
    await profiles_service.delete(tag)


@router.get("/all")
async def get_all(
    _admin: dict = Depends(get_current_admin),
    profiles_service: ProfilesService = Depends(get_profiles_service)
) -> list[ProfileSchema]:
    return await profiles_service.get_all()
