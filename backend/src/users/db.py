from typing import Sequence


from backend.src.users.models import User


from fastapi import HTTPException, status
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from users.schemas import UserSchema

class UserDB:
    @staticmethod
    async def add(db: AsyncSession, data: UserSchema) -> User:
        user = User(
            short_uuid = data.short_uuid,
            expires_at = data.expires_at
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
    async def get_all(db: AsyncSession, short_uuid: str) -> UserSchema:
        result = await db.execute(select(User))
        users: Sequence[User] = result.scalars().all()
        if users is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Users not found",
            )
        
        return [UserSchema.model_validate(user) for user in users]