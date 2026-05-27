"""
Async API client for olcrtc-manager.

Usage example::

    async with OlcrtcManager("http://127.0.0.1:8080") as mgr:
        login = await mgr.login("admin", "secret")
        state = await mgr.get_state()
        print(state.clients)
"""
from __future__ import annotations

from typing import Optional

import httpx

from .models import (
    AddClientRequest,
    AddClientResponse,
    AddLocationRequest,
    AuditResponse,
    AuthMeResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    ClientActionRequest,
    LocationActionRequest,
    LogsResponse,
    LoginRequest,
    LoginResponse,
    Metrics,
    SetupRequest,
    SetupResponse,
    State,
    UpdateClientRequest,
)


class OlcrtcManagerError(Exception):
    """Raised when the API returns a non-2xx status code."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class OlcrtcManager:
    """
    Async client for the olcrtc-manager HTTP API.

    Parameters
    ----------
    base_url:
        Root URL of the running manager, e.g. ``"http://127.0.0.1:8080"``.
    username / password:
        Optional Basic-Auth credentials.  When supplied, every request uses
        HTTP Basic Auth in addition to any session cookie that was obtained
        via :meth:`login`.
    timeout:
        httpx timeout in seconds (default 30).
    """

    def __init__(
        self,
        base_url: str,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._auth = (username, password) if username and password else None
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    # ── context-manager support ───────────────────────────────────────────

    async def __aenter__(self) -> "OlcrtcManager":
        await self._ensure_client()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying httpx client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ── internal helpers ──────────────────────────────────────────────────

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                # Persist cookies so the session cookie from login() is reused
                cookies=httpx.Cookies(),
                follow_redirects=True,
            )
        return self._client

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: object = None,
        params: Optional[dict] = None,
    ) -> httpx.Response:
        client = await self._ensure_client()
        kwargs: dict = {"method": method, "url": path}
        if json is not None:
            kwargs["json"] = json
        if params:
            kwargs["params"] = params
        if self._auth:
            kwargs["auth"] = self._auth
        response = await client.request(**kwargs)
        if not response.is_success:
            raise OlcrtcManagerError(response.status_code, response.text.strip())
        return response

    async def _get(self, path: str, **kw: object) -> httpx.Response:
        return await self._request("GET", path, **kw)  # pyright: ignore[reportArgumentType]

    async def _post(self, path: str, **kw: object) -> httpx.Response:
        return await self._request("POST", path, **kw)  # pyright: ignore[reportArgumentType]

    async def _put(self, path: str, **kw: object) -> httpx.Response:
        return await self._request("PUT", path, **kw)  # pyright: ignore[reportArgumentType]

    async def _delete(self, path: str, **kw: object) -> httpx.Response:
        return await self._request("DELETE", path, **kw)  # pyright: ignore[reportArgumentType]

    # ── Auth ──────────────────────────────────────────────────────────────

    async def auth_me(self) -> AuthMeResponse:
        """GET /api/auth/me — return current authentication status."""
        r = await self._get("/api/auth/me")
        return AuthMeResponse.model_validate(r.json())

    async def login(self, user: str, password: str) -> LoginResponse:
        """
        POST /api/auth/login — authenticate and store the session cookie.

        After a successful login the cookie is kept inside the httpx client
        and sent automatically with subsequent requests.
        """
        body = LoginRequest(user=user, password=password)
        r = await self._post("/api/auth/login", json=body.model_dump())
        return LoginResponse.model_validate(r.json())

    async def setup(self, password: str, user: str = "") -> SetupResponse:
        """POST /api/auth/setup — create initial admin credentials."""
        body = SetupRequest(user=user, password=password)
        r = await self._post("/api/auth/setup", json=body.model_dump(exclude_none=True))
        return SetupResponse.model_validate(r.json())

    async def logout(self) -> None:
        """POST /api/auth/logout — invalidate the current session."""
        await self._post("/api/auth/logout")

    async def change_password(
        self, current_password: str, new_password: str
    ) -> ChangePasswordResponse:
        """POST /api/auth/password — change the admin password."""
        body = ChangePasswordRequest(
            current_password=current_password,
            new_password=new_password,
        )
        r = await self._post("/api/auth/password", json=body.model_dump())
        return ChangePasswordResponse.model_validate(r.json())

    # ── State & metrics ───────────────────────────────────────────────────

    async def get_state(self) -> State:
        """GET /api/state — return the full supervisor state."""
        r = await self._get("/api/state")
        return State.model_validate(r.json())

    async def get_metrics(self) -> Metrics:
        """GET /api/metrics — return runtime/memory/process metrics."""
        r = await self._get("/api/metrics")
        return Metrics.model_validate(r.json())

    async def get_audit(self) -> AuditResponse:
        """GET /api/audit — return the last 100 audit log events."""
        r = await self._get("/api/audit")
        return AuditResponse.model_validate(r.json())

    async def get_logs(
        self, client_id: str, room_id: str, transport: str
    ) -> LogsResponse:
        """GET /api/logs/{client_id}/{room_id}/{transport} — fetch process logs."""
        path = f"/api/logs/{client_id}/{room_id}/{transport}"
        r = await self._get(path)
        return LogsResponse.model_validate(r.json())

    # ── Config reload ─────────────────────────────────────────────────────

    async def reload(self) -> None:
        """POST /api/reload — reload the config file on the server."""
        await self._post("/api/reload")

    # ── Clients ───────────────────────────────────────────────────────────

    async def add_client(self, request: AddClientRequest) -> AddClientResponse:
        """
        POST /api/clients — create a new client.

        Pass an :class:`AddClientRequest` with at minimum ``client_id`` and
        either ``carrier``/``transport``/``dns`` or ``from_client``.
        """
        r = await self._post(
            "/api/clients",
            json=request.model_dump(exclude_none=True, by_alias=True),
        )
        return AddClientResponse.model_validate(r.json())

    async def update_client(
        self, client_id: str, request: UpdateClientRequest
    ) -> None:
        """PUT /api/clients/{client_id} — update an existing client."""
        await self._put(
            f"/api/clients/{client_id}",
            json=request.model_dump(exclude_none=True),
        )

    async def delete_client(self, client_id: str) -> None:
        """DELETE /api/clients/{client_id} — remove a client."""
        await self._delete(f"/api/clients/{client_id}")

    # ── Locations ─────────────────────────────────────────────────────────

    async def add_location(
        self, client_id: str, request: AddLocationRequest
    ) -> None:
        """POST /api/clients/{client_id}/locations — add a location to a client."""
        await self._post(
            f"/api/clients/{client_id}/locations",
            json=request.model_dump(exclude_none=True),
        )

    async def delete_location(self, client_id: str, room_id: str) -> None:
        """DELETE /api/clients/{client_id}/locations/{room_id} — remove a location."""
        await self._delete(f"/api/clients/{client_id}/locations/{room_id}")

    # ── Actions ───────────────────────────────────────────────────────────

    async def restart(
        self, client_id: str, room_id: str, transport: str
    ) -> None:
        """POST /api/actions/restart — restart a specific location process."""
        body = LocationActionRequest(
            client_id=client_id,
            room_id=room_id,
            transport=transport,
        )
        await self._post("/api/actions/restart", json=body.model_dump())

    async def regenerate_room(self, client_id: str) -> None:
        """
        POST /api/actions/regenerate-room — generate a new room ID for
        all locations of a client.
        """
        body = ClientActionRequest(client_id=client_id)
        await self._post("/api/actions/regenerate-room", json=body.model_dump())

    async def rotate_key(self, client_id: str) -> None:
        """
        POST /api/actions/rotate-key — rotate the encryption key for all
        locations of a client.
        """
        body = ClientActionRequest(client_id=client_id)
        await self._post("/api/actions/rotate-key", json=body.model_dump())

    # ── Subscription ──────────────────────────────────────────────────────

    async def get_subscription(self, subscriptionPath: str, client_id: str) -> str:
        """
        GET /{client_id} — fetch the plain-text subscription config for a
        client (no auth required).
        """
        r = await self._get(f"/{subscriptionPath}/{client_id}")
        return r.text
