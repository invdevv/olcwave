from fastapi import APIRouter, Depends

from auth.dependencies import get_current_admin
from core.config import settings
from settings.schemas import RuntimeSettings
from settings.service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/")
async def get_settings(_admin: dict = Depends(get_current_admin)):
    settings = SettingsService.get()

    return settings

@router.put("/")
async def set_setting(settings: RuntimeSettings, _admin: dict = Depends(get_current_admin)):
    await SettingsService.set(settings)
    
    return SettingsService.get()

@router.get("/rw_enabled")
async def get_rw_enabled(_admin: dict = Depends(get_current_admin)) -> bool:
    return settings.RW_ENABLED
