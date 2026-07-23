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
        global _settings

        async with async_session_factory() as db:
            obj = await db.get(SettingsModel, 1)

            if obj is None:
                obj = SettingsModel(id=1, data=RuntimeSettings().model_dump())
                db.add(obj)
                await db.commit()

        _settings = RuntimeSettings.model_validate(obj.data)

    @staticmethod
    async def set(settings: RuntimeSettings):
        global _settings

        _settings = settings

        async with async_session_factory() as db:
            obj = await db.get(SettingsModel, 1)

            if obj is None:
                obj = SettingsModel(id=1, data=settings.model_dump())
                db.add(obj)
            else:
                obj.data = settings.model_dump()

            await db.commit()