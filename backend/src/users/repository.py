from typing import Dict, Type, Optional

from sqlalchemy import insert, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from db.repositories import BaseCRUDRepository


class UserRepository(BaseCRUDRepository[User]):
    def __init__(self, model: Type[User] = User) -> None:
        super().__init__(model=model)

    async def add_user(
        self,
        user: dict,
        session: Optional[AsyncSession] = None
    ) -> dict:
        stmt = (
            insert(self.model)
            .values(user)
        )
        return await self.create_one(stmt, session)

    async def get_user(
        self,
        short_uuid: str,
        session: Optional[AsyncSession] = None,
    ) -> dict:
        stmt = (
            select(User)
            .where(User.short_uuid == short_uuid)
        )
        return await self.get_one(stmt, session)

    async def update_user(
        self,
        user: dict,
        session: Optional[AsyncSession] = None
    ) -> bool:
        stmt = (
            update(User)
            .where(User.short_uuid == user.get("short_uuid"))
            .values(**user)
        )
        await self.update_one(stmt, session)
        return True

    async def delete_user(
        self,
        short_uuid: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ) -> bool:
        stmt = (
            delete(User)
            .where(User.short_uuid == short_uuid)
        )
        await self.delete(stmt, session)
        return True

    async def get_all_users(
        self,
        session: Optional[AsyncSession] = None,
    ) -> list[Dict]:
        stmt = select(User)
        return await self.get_many(stmt, session)

    async def is_user_exists(
        self,
        short_uuid: str,
        session: Optional[AsyncSession] = None,
    ) -> bool:
        stmt = (
            select(User)
            .where(
                User.short_uuid == short_uuid
            )
        )
        return bool(await self.get_one(stmt, session))

    async def update_traffic_used(
        self,
        short_uuid: str,
        delta: int,
        session: Optional[AsyncSession] = None,
    ) -> None:
        stmt = (
            update(User)
            .where(User.short_uuid == short_uuid)
            .values(traffic_used_bytes=User.traffic_used_bytes + delta)
        )
        await self.update_one(stmt, session)

    async def set_traffic_limit(
        self,
        short_uuid: str,
        limit: int,
        session: Optional[AsyncSession] = None,
    ) -> None:
        stmt = (
            update(User)
            .where(User.short_uuid == short_uuid)
            .values(traffic_limit_bytes=limit)
        )
        await self.update_one(stmt, session)

    async def reset_traffic(
        self,
        short_uuid: str,
        session: Optional[AsyncSession] = None,
    ) -> None:
        stmt = (
            update(User)
            .where(User.short_uuid == short_uuid)
            .values(traffic_used_bytes=0)
        )
        await self.update_one(stmt, session)
