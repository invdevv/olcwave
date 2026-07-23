from datetime import datetime

from database import async_session_factory
from users.db import UserDB
from users.schemas import UserSchema, TrafficInfoSchema

class Users:
    @staticmethod
    async def add(user: UserSchema):
        async with async_session_factory() as db:
            return await UserDB.add(db, user)

    @staticmethod
    async def exists(short_uuid: str) -> bool:
        async with async_session_factory() as db:
            return await UserDB.exists(db, short_uuid)

    @staticmethod
    async def get(short_uuid: str) -> UserSchema:
        async with async_session_factory() as db:
            user = await UserDB.get(db, short_uuid)
        return user

    @staticmethod
    async def update(short_uuid: str, expires_at: datetime):
        async with async_session_factory() as db:
            _ = await UserDB.update(db, short_uuid, expires_at)

    @staticmethod
    async def delete(short_uuid: str):
        async with async_session_factory() as db:
            _ = await UserDB.delete(db, short_uuid)

    @staticmethod
    async def get_all() -> list[UserSchema]:
        async with async_session_factory() as db:
            users: list[UserSchema] = await UserDB.get_all(db)
        return users

    @staticmethod
    async def get_traffic(short_uuid: str) -> TrafficInfoSchema:
        user = await Users.get(short_uuid)
        unlimited = user.traffic_limit_bytes == 0
        remaining = 0 if unlimited else max(0, user.traffic_limit_bytes - user.traffic_used_bytes)
        exceeded = (not unlimited) and user.traffic_used_bytes >= user.traffic_limit_bytes
        return TrafficInfoSchema(
            short_uuid=short_uuid,
            limit=user.traffic_limit_bytes,
            used=user.traffic_used_bytes,
            remaining=remaining,
            unlimited=unlimited,
            exceeded=exceeded,
        )

    @staticmethod
    async def set_traffic_limit(short_uuid: str, limit: int):
        async with async_session_factory() as db:
            await UserDB.set_traffic_limit(db, short_uuid, limit)

    @staticmethod
    async def reset_traffic(short_uuid: str):
        async with async_session_factory() as db:
            await UserDB.reset_traffic(db, short_uuid)

    @staticmethod
    async def add_traffic_used(short_uuid: str, delta: int):
        if delta <= 0:
            return
        async with async_session_factory() as db:
            await UserDB.update_traffic_used(db, short_uuid, delta)
