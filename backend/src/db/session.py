from typing import AsyncIterator, Any
from functools import lru_cache, wraps
from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from fastapi.exceptions import HTTPException

from db.base import async_engine


class SessionManager:
    def __init__(self, engine: AsyncEngine = async_engine) -> None:
        self._async_engine = engine
        self._async_session_creator = async_sessionmaker(
            bind=self._async_engine,
            class_=AsyncSession,
            autoflush=True,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def manager(
        self,
        autocommit: bool = True
    ) -> AsyncIterator[AsyncSession]:
        session = self._async_session_creator()
        try:
            yield session
            if autocommit:
                await session.commit()
        except HTTPException as error:
            await session.rollback()
            raise error
        except SQLAlchemyError as error:
            await session.rollback()
            raise error
        finally:
            await session.close()


@lru_cache()
def get_session_manager() -> SessionManager:
    return SessionManager()


def with_transaction(func):
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        if kwargs.get("session") or any(isinstance(arg, AsyncSession) for arg in args):
            result = await func(*args, **kwargs)
            return result

        session_manager = get_session_manager()
        async with session_manager.manager(autocommit=False) as session:
            kwargs["session"] = session
            result = await func(*args, **kwargs)
            await session.commit()
            return result
    return wrapper
