from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base

class Profile(Base):
    __tablename__ = "profiles"                                   # pyright: ignore[reportUnannotatedClassAttribute]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    tag: Mapped[str] = mapped_column(String(255), unique=True)
    profile: Mapped[str]                                         # pyright: ignore[reportUninitializedInstanceVariable]

