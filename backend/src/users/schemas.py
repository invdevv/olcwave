from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

from config import settings


class UserSchema(BaseModel):
    short_uuid: str = Field(max_length=255)
    created_at: datetime = Field(default = datetime.now(timezone.utc))
    expires_at: datetime = Field(default = datetime(year=1971, month=1, day=1, hour=5))
    traffic_limit_bytes: int = Field(default_factory=lambda: settings.DEFAULT_TRAFFIC_LIMIT)
    traffic_used_bytes: int = Field(default=0)

    model_config = ConfigDict(from_attributes=True)


class TrafficInfoSchema(BaseModel):
    short_uuid: str
    limit: int
    used: int
    remaining: int
    unlimited: bool
    exceeded: bool


class TrafficLimitUpdate(BaseModel):
    traffic_limit_bytes: int = Field(ge=0)  # pyright: ignore[reportUnannotatedClassAttribute]