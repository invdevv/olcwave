from fastapi import APIRouter, Depends

from auth.dependencies import get_current_admin
from core.config import settings
from core.factories import get_settings_service
from settings.schemas import RuntimeSettings
from settings.service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/")
async def get_settings(
    _admin: dict = Depends(get_current_admin),
    settings_service: SettingsService = Depends(get_settings_service),
) -> RuntimeSettings:
    return settings_service.get()


@router.put("/")
async def set_setting(
    settings: RuntimeSettings,
    _admin: dict = Depends(get_current_admin),
    settings_service: SettingsService = Depends(get_settings_service),
) -> RuntimeSettings:
    return await settings_service.set(settings)


@router.get("/rw_enabled")
async def get_rw_enabled(_admin: dict = Depends(get_current_admin)) -> bool:
    return settings.RW_ENABLED
