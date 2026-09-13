from datetime import datetime

from settings.schemas import RuntimeSettings
from settings.repository import SettingsRepository


class SettingsService:
    _settings: RuntimeSettings | None = None

    def __init__(self, repo: SettingsRepository) -> None:
        self._repo = repo

    def get(self) -> RuntimeSettings:
        if self._settings is None:
            raise RuntimeError("Settings not loaded")
        return self._settings

    async def load(self) -> None:
        settings = await self._repo.get_settings()
        if not settings:
            data = {
                "id": 1,
                "data": RuntimeSettings().model_dump(mode="json")
            }
            await self._repo.add_settings(data)
            settings = await self._repo.get_settings()
        self._settings = RuntimeSettings(**settings.get("data", {}))

    async def set(self, settings: RuntimeSettings) -> RuntimeSettings:
        self._settings = settings
        old_settings = await self._repo.get_settings()
        data = settings.model_dump(mode="json")
        if not old_settings:
            await self._repo.add_settings(data)
        else:
            await self._repo.update_settings(data)
        return self._settings

    async def update_last_sync(self, dt: datetime) -> None:
        if self._settings is None:
            return
        self._settings.last_sync_at = dt
        settings = await self._repo.get_settings()
        if settings:
            await self._repo.update_settings(self._settings.model_dump(mode="json"))
