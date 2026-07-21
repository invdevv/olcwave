from fastapi import HTTPException, status

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from profiles.models import Profile
from profiles.schemas import ProfileSchema

class ProfilesDB:
    @staticmethod
    async def add(db: AsyncSession, data: ProfileSchema) -> Profile:
        profile = Profile(
            name=data.name,
            tag=data.tag,
            profile=data.profile,
        )

        db.add(profile)
        await db.commit()
        await db.refresh(profile)

        return profile

    @staticmethod
    async def get(db: AsyncSession, tag: str) -> ProfileSchema:
        result = await db.execute(select(Profile).where(Profile.tag == tag))
        profile = result.scalar_one_or_none()
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )
        
        return ProfileSchema.model_validate(profile)

    @staticmethod
    async def update(db: AsyncSession, tag: str, name: str, profile: str) -> bool:
        _ = await db.execute(update(Profile).where(Profile.tag == tag).values(profile=profile, name=name))
        await db.commit()
    
        return True
    
    @staticmethod
    async def delete(db: AsyncSession, tag: str) -> bool:
        _= await db.execute(delete(Profile).where(Profile.tag == tag))
        await db.commit()

        return True

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(Profile))
        profiles = result.scalars().all()
        if profiles is None:  # pyright: ignore[reportUnnecessaryComparison]
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profiles not found",
            )
        
        return [ProfileSchema.model_validate(profile) for profile in profiles]