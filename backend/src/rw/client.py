from __future__ import annotations

from typing import Any

import httpx

from .schemas import (
    GetAllUsersResponseDto,
    GetSubscriptionInfoResponseDto,
    GetUserByShortUuidResponseDto,
    SubscriptionSettingsResponseDto,
)
from .exceptions import RemnaWaveNotFoundError


class RemnawaveClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        caddy_token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = self._build_url(base_url)
        self._timeout = timeout
        self.__headers = self._build_headers(token, caddy_token)

    def _build_headers(
        self,
        token: str,
        caddy_token: str | None
    ) -> dict[str, str]:
        headers: dict[str, str] = {}

        if token:
            headers["Authorization"] = self._build_auth_token(token)

        if caddy_token:
            headers["X-Api-Key"] = caddy_token

        return headers

    @staticmethod
    def _build_url(base_url: str) -> str:
        base_url = base_url.rstrip("/")
        if not base_url.endswith("/api"):
            base_url += "/api"
        return base_url

    @staticmethod
    def _build_auth_token(token: str) -> str:
        return token if token.startswith("Bearer ") else f"Bearer {token}"

    async def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        async with httpx.AsyncClient(
            base_url=self._base_url,
            headers=self.__headers,
            timeout=self._timeout,
        ) as client:
            response = await client.get(path, params=params)

        if response.status_code == 404:
            raise RemnaWaveNotFoundError(response.text)

        response.raise_for_status()
        payload = response.json()

        if isinstance(payload, dict) and "response" in payload:
            return payload["response"]
        return response.json()

    async def get_all_users(
        self,
        start: int | None = None,
        size: int | None = None,
    ) -> GetAllUsersResponseDto:
        response = await self._get(
            "/users",
            params={
                key: value
                for key, value in {"start": start, "size": size}.items()
                if value is not None
            },
        )
        return GetAllUsersResponseDto(**response)

    async def get_user_by_short_uuid(
        self, short_uuid: str
    ) -> GetUserByShortUuidResponseDto:
        response = await self._get(f"/users/by-short-uuid/{short_uuid}")
        return GetUserByShortUuidResponseDto(**response)

    async def get_subscription_info_by_short_uuid(
        self, short_uuid: str
    ) -> GetSubscriptionInfoResponseDto:
        response = await self._get(f"/sub/{short_uuid}/info")
        return GetSubscriptionInfoResponseDto(**response)

    async def get_subscription_settings(self) -> SubscriptionSettingsResponseDto:
        response = await self._get("/subscription-settings")
        return SubscriptionSettingsResponseDto(**response)
