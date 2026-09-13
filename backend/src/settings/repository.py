from typing import Type, Optional

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from settings.models import SettingsModel
from db.repositories import BaseCRUDRepository


class SettingsRepository(BaseCRUDRepository[SettingsModel]):
    def __init__(self, model: Type[SettingsModel] = SettingsModel) -> None:
        super().__init__(model=model)

    async def add_settings(
        self,
        settings: dict,
        session: Optional[AsyncSession] = None
    ) -> dict:
        stmt = (
            insert(self.model)
            .values(settings)
        )
        return await self.create_one(stmt, session)

    async def get_settings(
        self,
        session: Optional[AsyncSession] = None,
    ) -> dict:
        stmt = (
            select(SettingsModel)
            .where(SettingsModel.id == 1)
        )
        return await self.get_one(stmt, session)

    async def update_settings(
        self,
        settings: dict,
        session: Optional[AsyncSession] = None,
    ) -> dict:
        stmt = (
            update(SettingsModel)
            .where(SettingsModel.id == 1)
            .values(data=settings)
        )
        return await self.update_one(stmt, session)
