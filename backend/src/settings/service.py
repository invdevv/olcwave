from datetime import datetime

from settings.models import SettingsModel
from settings.schemas import RuntimeSettings
from database import async_session_factory


class SettingsService:
    _settings: RuntimeSettings | None = None

    @staticmethod
    def get():
        if SettingsService._settings is None:
            raise RuntimeError("Settings not loaded")
        return SettingsService._settings

    @staticmethod
    async def load():
        async with async_session_factory() as db:
            obj = await db.get(SettingsModel, 1)

            if obj is None:
                obj = SettingsModel(id=1, data=RuntimeSettings().model_dump(mode="json"))
                db.add(obj)
                await db.commit()

        SettingsService._settings = RuntimeSettings.model_validate(obj.data)

    @staticmethod
    async def set(settings: RuntimeSettings):
        SettingsService._settings = settings

        async with async_session_factory() as db:
            obj = await db.get(SettingsModel, 1)

            if obj is None:
                obj = SettingsModel(id=1, data=settings.model_dump(mode="json"))
                db.add(obj)
            else:
                obj.data = settings.model_dump(mode="json")

            await db.commit()

    @staticmethod
    async def update_last_sync(dt: datetime):
        if SettingsService._settings is None:
            return
        SettingsService._settings.last_sync_at = dt

        async with async_session_factory() as db:
            obj = await db.get(SettingsModel, 1)
            if obj is not None:
                obj.data = SettingsService._settings.model_dump(mode="json")
                await db.commit()