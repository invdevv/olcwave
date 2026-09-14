from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings


async_engine = create_async_engine(
    settings.DB_DSN,
    echo=False,
)


class Base(DeclarativeBase):
    pass


async def create_tables(reload: bool = False) -> None:
    async with async_engine.begin() as conn:
        if reload:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
