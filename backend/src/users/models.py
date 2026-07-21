from sqlalchemy import String, ForeignKey, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated

from database import Base

UTC_NOW = Annotated[datetime, mapped_column(server_default = text("TIMEZONE('utc', now())"))]

class User(Base):
    __tablename__ = "users"                                      # pyright: ignore[reportUnannotatedClassAttribute]

    id: Mapped[int] = mapped_column(primary_key=True)
    short_uuid: Mapped[str] = mapped_column(String(32), unique=True)
    created_at: Mapped[UTC_NOW]  # pyright: ignore[reportUninitializedInstanceVariable]
    expires_at: Mapped[datetime]  # pyright: ignore[reportUninitializedInstanceVariable]