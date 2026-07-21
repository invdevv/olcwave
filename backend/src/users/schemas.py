from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class UserSchema(BaseModel):
    short_uuid: str = Field(max_length=255)
    created_at: datetime = Field(default = datetime.now(timezone.utc))
    expires_at: datetime = Field(default = datetime(year=1971, month=1, day=1, hour=5))

    model_config = ConfigDict(from_attributes=True)  # pyright: ignore[reportUnannotatedClassAttribute]