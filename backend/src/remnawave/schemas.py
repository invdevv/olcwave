from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RemnawaveModel(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        from_attributes=True,
        populate_by_name=True,
    )


class ActiveInternalSquadSchema(RemnawaveModel):
    uuid: UUID
    name: str


class UserResponseDto(RemnawaveModel):
    uuid: UUID | None = None
    short_uuid: str = Field(alias="shortUuid")
    username: str
    expire_at: datetime = Field(alias="expireAt")
    active_internal_squads: list[ActiveInternalSquadSchema] = Field(
        alias="activeInternalSquads"
    )


GetUserByShortUuidResponseDto = UserResponseDto


class GetAllUsersResponseDto(RemnawaveModel):
    users: list[UserResponseDto]
    total: int


class SubscriptionInfoResponseDto(RemnawaveModel):
    is_found: bool = Field(alias="isFound")
    user: Any
    links: list[str]
    ss_conf_links: dict[str, str] = Field(alias="ssConfLinks")
    subscription_url: str = Field(alias="subscriptionUrl")


GetSubscriptionInfoResponseDto = SubscriptionInfoResponseDto


class SubscriptionSettingsResponseDto(RemnawaveModel):
    uuid: UUID
    profile_title: str = Field(alias="profileTitle")
    support_link: str = Field(alias="supportLink")
    profile_update_interval: int = Field(alias="profileUpdateInterval")
    is_profile_webpage_url_enabled: bool = Field(
        alias="isProfileWebpageUrlEnabled")
    serve_json_at_base_subscription: bool = Field(
        alias="serveJsonAtBaseSubscription")
    show_custom_remarks: bool = Field(alias="isShowCustomRemarks")
    custom_remarks: Any = Field(alias="customRemarks")
    happ_announce: str | None = Field(default=None, alias="happAnnounce")
    happ_routing: str | None = Field(default=None, alias="happRouting")
    custom_response_headers: dict[str, str] | None = Field(
        default=None, alias="customResponseHeaders"
    )
    randomize_hosts: bool = Field(alias="randomizeHosts")
    response_rules: Any | None = Field(default=None, alias="responseRules")
    hwid_settings: Any | None = Field(default=None, alias="hwidSettings")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
