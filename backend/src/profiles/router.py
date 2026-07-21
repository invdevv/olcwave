from fastapi import APIRouter, Depends

from auth.dependencies import get_current_admin
from profiles.schemas import ProfileSchema
from profiles.service import Profiles

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("/")
async def add(profile: ProfileSchema, _admin: dict = Depends(get_current_admin)):
    await Profiles.add(profile)

    return "ok"

@router.get("/")
async def get(tag: str, _admin: dict = Depends(get_current_admin)):
    profile = await Profiles.get(tag)

    return profile
    
@router.put("/")
async def update(tag: str, name: str, profile: str, _admin: dict = Depends(get_current_admin)):
    await Profiles.update(tag, name, profile)

@router.delete("/")
async def delete(tag: str, _admin: dict = Depends(get_current_admin)):
    await Profiles.delete(tag)
