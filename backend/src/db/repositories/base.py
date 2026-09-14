from typing import Type, TypeVar, Generic, Any, List, Protocol, Optional

from sqlalchemy import Select, Update, Delete, Insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import SessionManager, get_session_manager
from db.base import Base


T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(
        self,
        model: Type[T],
        session_manager: SessionManager = get_session_manager(),
    ) -> None:
        self._model = model
        self._session_manager = session_manager

    @property
    def session_manager(self) -> SessionManager:
        # Read only
        return self._session_manager

    @property
    def model(self) -> Type[T]:
        # Read only
        return self._model


class CRUDRepositoryProtocol(Protocol):
    @property
    def session_manager(self) -> SessionManager: ...

    @property
    def model(self) -> Type[Any]: ...


class ReadRepositoryMixin(CRUDRepositoryProtocol):
    """
    Handling SELECT queries
    """

    async def get_one(
        self,
        stmt: Select,
        session: Optional[AsyncSession] = None
    ) -> dict:
        if session is None:
            async with self.session_manager.manager() as session:
                result = (await session.execute(stmt)).scalar_one_or_none()
        else:
            result = (await session.execute(stmt)).scalar_one_or_none()
        return result.__dict__ if result else {}

    async def get_many(
        self,
        stmt: Select,
        session: Optional[AsyncSession] = None
    ) -> List[dict]:
        if session is None:
            async with self.session_manager.manager() as session:
                results = (await session.execute(stmt)).scalars().all()
        else:
            results = (await session.execute(stmt)).scalars().all()
        return [result.__dict__ for result in results]


class CreateRepositoryMixin(ReadRepositoryMixin, CRUDRepositoryProtocol):
    """
    Handling INSERT queries
    """

    async def create_one(
        self,
        stmt: Insert,
        session: Optional[AsyncSession] = None
    ) -> dict:
        stmt = stmt.returning(stmt.table)
        if session is None:
            async with self.session_manager.manager() as session:
                result = (await session.execute(stmt)).scalar_one_or_none()
        else:
            result = (await session.execute(stmt)).scalar_one_or_none()
        return result.__dict__ if result else {}

    async def create_many(
        self,
        stmt: Insert,
        session: Optional[AsyncSession] = None
    ) -> List[dict]:
        stmt = stmt.returning(stmt.table)
        if session is None:
            async with self.session_manager.manager() as session:
                results = (await session.execute(stmt)).scalars().all()
        else:
            results = (await session.execute(stmt)).scalars().all()
        return [result.__dict__ for result in results]


class UpdateRepositoryMixin(ReadRepositoryMixin, CRUDRepositoryProtocol):
    """
    Handling UPDATE queries
    """

    async def update_one(
        self,
        stmt: Update,
        session: Optional[AsyncSession] = None
    ) -> dict:
        stmt = stmt.returning(stmt.table)
        if session is None:
            async with self.session_manager.manager() as session:
                result = (await session.execute(stmt)).scalar_one_or_none()
        else:
            result = (await session.execute(stmt)).scalar_one_or_none()
        return result.__dict__ if result else {}

    async def update_many(
        self,
        stmt: Update,
        session: Optional[AsyncSession] = None
    ) -> List[dict]:
        stmt = stmt.returning(stmt.table)
        if session is None:
            async with self.session_manager.manager() as session:
                results = (await session.execute(stmt)).scalars().all()
        else:
            results = (await session.execute(stmt)).scalars().all()
        return [result.__dict__ for result in results]


class DeleteRepositoryMixin(ReadRepositoryMixin, CRUDRepositoryProtocol):
    """
    Handling DELETE queries
    """

    async def delete(
        self,
        stmt: Delete,
        session: Optional[AsyncSession] = None
    ) -> None:
        if session is None:
            async with self.session_manager.manager() as session:
                await session.execute(stmt)
        else:
            await session.execute(stmt)


class BaseCRUDRepository(
    BaseRepository[T],
    CreateRepositoryMixin,
    UpdateRepositoryMixin,
    DeleteRepositoryMixin,
):
    pass
