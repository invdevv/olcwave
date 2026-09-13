from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from core.config import settings


async_engine = create_async_engine(
    settings.DB_DSN,
    echo=False,
)
Base = declarative_base()
