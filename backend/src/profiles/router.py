from fastapi import APIRouter

from profiles.schemas import ProfileSchema
from profiles.service import Profiles

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("/")
async def add(profile: ProfileSchema):
    await Profiles.add(profile)

    return "ok"

@router.get("/")
async def get(tag: str):
    profile = await Profiles.get(tag)

    return profile
    
@router.put("/")
async def update(tag: str, name: str, profile: str):
    await Profiles.update(tag, name, profile)

@router.delete("/")
async def delete(tag: str):
    await Profiles.delete(tag)