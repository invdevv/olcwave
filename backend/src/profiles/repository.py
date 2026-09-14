from typing import Type, Optional, List

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from profiles.models import Profile
from db.repositories import BaseCRUDRepository


class ProfileRepository(BaseCRUDRepository[Profile]):
    def __init__(self, model: Type[Profile] = Profile) -> None:
        super().__init__(model=model)

    async def add_profile(
        self,
        profile: dict,
        session: Optional[AsyncSession] = None
    ) -> dict:
        stmt = (
            insert(self.model)
            .values(
                name=profile.get("name"),
                tag=profile.get("tag"),
                profile=profile.get("profile"),
            )
        )
        return await self.create_one(stmt, session)

    async def get_profile(
        self,
        tag: str,
        session: Optional[AsyncSession] = None,
    ) -> dict:
        stmt = (
            select(self.model)
            .where(self.model.tag == tag)
        )
        return await self.get_one(stmt, session)

    async def get_all_profiles(
        self,
        session: Optional[AsyncSession] = None,
    ) -> List[dict]:
        stmt = (
            select(self.model)
        )
        return await self.get_many(stmt, session)

    async def update_profile(
        self,
        tag: str,
        name: str,
        profile: str,
        session: Optional[AsyncSession] = None,
    ) -> dict:
        stmt = (
            update(self.model)
            .where(self.model.tag == tag)
            .values(
                name=name,
                profile=profile,
            )
        )
        return await self.update_one(stmt, session)

    async def delete_profile(
        self,
        tag: str,
        session: Optional[AsyncSession] = None,
    ) -> None:
        stmt = (
            delete(self.model)
            .where(self.model.tag == tag)
        )
        await self.delete(stmt, session)
