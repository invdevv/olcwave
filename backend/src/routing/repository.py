from typing import Type, Optional

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from routing.models import Routing
from db.repositories import BaseCRUDRepository


class RoutingRepository(BaseCRUDRepository[Routing]):
    def __init__(self, model: Type[Routing] = Routing) -> None:
        super().__init__(model=model)

    async def add_routing(
        self,
        xray_json: str,
        session: Optional[AsyncSession] = None
    ) -> dict:
        stmt = (
            insert(self.model)
            .values(
                id=1,
                xray_json=xray_json
            )
        )
        return await self.create_one(stmt, session)

    async def get_routing(
        self,
        session: Optional[AsyncSession] = None,
    ) -> dict:
        stmt = (
            select(self.model)
            .where(self.model.id == 1)
        )
        return await self.get_one(stmt, session)

    async def update_routing(
        self,
        xray_json: str,
        session: Optional[AsyncSession] = None,
    ) -> dict:
        stmt = (
            update(self.model)
            .where(self.model.id == 1)
            .values(xray_json=xray_json)
        )
        return await self.update_one(stmt, session)

    async def delete_routing(
        self,
        session: Optional[AsyncSession] = None,
    ) -> None:
        stmt = (
            delete(self.model)
            .where(self.model.id == 1)
        )
        await self.delete(stmt, session)
