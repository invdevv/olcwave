from fastapi import APIRouter, Depends

from auth.dependencies import get_current_admin
from settings.schemas import RuntimeSettings
from settings.service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/")
async def get_setting(_admin: dict = Depends(get_current_admin)):
    settings = SettingsService.get()

    return settings

@router.put("/")
async def set_setting(settings: RuntimeSettings, _admin: dict = Depends(get_current_admin)):
    await SettingsService.set(settings)
    
    return SettingsService.get()
