from typing import Sequence

from fastapi import HTTPException, status
from datetime import datetime

from sqlalchemy import delete, select, update, exists as sa_exists
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from users.schemas import UserSchema

class UserDB:
    @staticmethod
    async def add(db: AsyncSession, data: UserSchema) -> User:
        user = User(
            short_uuid = data.short_uuid,
            name = data.name,
            expires_at = data.expires_at,
            traffic_limit_bytes = data.traffic_limit_bytes,
            traffic_used_bytes = data.traffic_used_bytes,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def get(db: AsyncSession, short_uuid: str) -> UserSchema:
        result = await db.execute(select(User).where(User.short_uuid == short_uuid))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        return UserSchema.model_validate(user)

    @staticmethod
    async def update(db: AsyncSession, short_uuid: str, expires_at: datetime) -> bool:
        _ = await db.execute(update(User).where(User.short_uuid == short_uuid).values(expires_at=expires_at))
        await db.commit()
    
        return True
    
    @staticmethod
    async def delete(db: AsyncSession, short_uuid: str) -> bool:
        _= await db.execute(delete(User).where(User.short_uuid == short_uuid))
        await db.commit()

        return True

    @staticmethod
    async def get_all(db: AsyncSession) -> list[UserSchema]:
        result = await db.execute(select(User))
        users: Sequence[User] = result.scalars().all()
        if users is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Users not found",
            )

        return [UserSchema.model_validate(user) for user in users]

    @staticmethod
    async def exists(db: AsyncSession, short_uuid: str) -> bool:
        result = await db.execute(
            sa_exists(select(User).where(User.short_uuid == short_uuid)).select()
        )
        return result.scalar_one()

    @staticmethod
    async def update_traffic_used(db: AsyncSession, short_uuid: str, delta: int) -> None:
        await db.execute(
            update(User)
            .where(User.short_uuid == short_uuid)
            .values(traffic_used_bytes=User.traffic_used_bytes + delta)
        )
        await db.commit()

    @staticmethod
    async def set_traffic_limit(db: AsyncSession, short_uuid: str, limit: int) -> None:
        await db.execute(
            update(User).where(User.short_uuid == short_uuid).values(traffic_limit_bytes=limit)
        )
        await db.commit()

    @staticmethod
    async def reset_traffic(db: AsyncSession, short_uuid: str) -> None:
        await db.execute(
            update(User).where(User.short_uuid == short_uuid).values(traffic_used_bytes=0)
        )
        await db.commit()