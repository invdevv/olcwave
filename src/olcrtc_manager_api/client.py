"""
OlcrtcManager — async Python client for the olcrtc-manager-panel REST API.

Source of truth: cmd/olcrtc-manager/main.go
https://github.com/BigDaddy3334/olcrtc-manager-panel

Stack: Python 3.13 · httpx · pydantic v2

Quick start:
    async with OlcrtcManager("http://127.0.0.1:8888", "admin", "secret") as mgr:
        state = await mgr.get_state()
        for client in state.clients:
            print(client.client_id, client.quota.used_gb, "GB used")
"""

from __future__ import annotations

from typing import Any

import httpx

from .models import (
    AddClientRequest,
    AddLocationRequest,
    AuditResponse,
    AuthMeResponse,
    ChangePasswordRequest,
    ClientActionRequest,
    ClientState,
    CreateClientResponse,
    LocationActionRequest,
    LogsResponse,
    Metrics,
    OlcboxURI,
    LoginRequest,
    SetupRequest,
    State,
    SubscriptionMeta,
    UpdateClientRequest,
    QuotaStatus,
)


class OlcrtcManagerError(Exception):
    """Raised for non-2xx responses from the manager API."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(f"HTTP {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class OlcrtcManager:
    """
    Async client for the olcrtc-manager-panel admin API.

    All endpoints discovered from main.go:

    Auth
    ────
    GET  /api/auth/me                       → me()
    POST /api/auth/login                    → login()
    POST /api/auth/logout                   → logout()
    POST /api/auth/setup                    → setup()          [first-run]
    POST /api/auth/password                 → change_password()

    State & monitoring
    ──────────────────
    GET  /api/state                         → get_state()      [all clients + runtime]
    GET  /api/metrics                       → get_metrics()
    GET  /api/audit                         → get_audit()
    GET  /api/logs/{cid}/{room}/{transport} → get_logs()

    Client CRUD
    ───────────
    POST /api/clients                       → create_client()
    PUT  /api/clients/{id}                  → update_client()
    DELETE /api/clients/{id}               → delete_client()
    POST /api/clients/{id}/locations        → add_location()
    DELETE /api/clients/{id}/locations/{r} → delete_location()

    Actions
    ───────
    POST /api/actions/restart               → restart_location()
    POST /api/actions/regenerate-room       → regenerate_room()
    POST /api/actions/rotate-key            → rotate_key()
    POST /api/reload                        → reload()         [auth required]
    POST /-/reload                          → reload_loopback() [loopback only, no auth]

    Subscriptions (no auth)
    ───────────────────────
    GET  /{client_id}/                      → get_subscription()
                                            → get_subscription_parsed()
    """

    def __init__(
        self,
        base_url: str,
        username: str | None = None,
        password: str | None = None,
        *,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Context-manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "OlcrtcManager":
        await self._open()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    async def _open(self) -> None:
        auth = (
            httpx.BasicAuth(self._username, self._password)
            if self._username and self._password
            else None
        )
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            auth=auth,
            timeout=self._timeout,
            follow_redirects=True,
            headers={"Accept": "application/json"},
        )

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @property
    def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError(
                "Client not open. Use 'async with OlcrtcManager(...)' or call _open()."
            )
        return self._client

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        resp = await self._http.request(method, path, json=json, params=params)
        if not resp.is_success:
            try:
                detail = resp.json().get("error") or resp.text
            except Exception:
                detail = resp.text
            raise OlcrtcManagerError(resp.status_code, detail)
        return resp

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    async def me(self) -> AuthMeResponse:
        """GET /api/auth/me — check current session / setup status."""
        r = await self._request("GET", "/api/auth/me")
        return AuthMeResponse.model_validate(r.json())

    async def login(self, user: str, password: str) -> AuthMeResponse:
        """
        POST /api/auth/login — create a session cookie.

        Note: the body field is 'user', NOT 'username'.
        """
        body = LoginRequest(user=user, password=password)
        r = await self._request("POST", "/api/auth/login", json=body.model_dump())
        return AuthMeResponse.model_validate(r.json())

    async def logout(self) -> None:
        """POST /api/auth/logout — invalidate the current session."""
        await self._request("POST", "/api/auth/logout")

    async def setup(self, password: str, user: str = "admin") -> AuthMeResponse:
        """
        POST /api/auth/setup — first-run only.

        Fails with 409 if a password has already been configured.
        Password must be at least 8 characters.
        """
        body = SetupRequest(user=user, password=password)
        r = await self._request("POST", "/api/auth/setup", json=body.model_dump())
        return AuthMeResponse.model_validate(r.json())

    async def change_password(self, current_password: str, new_password: str) -> None:
        """POST /api/auth/password — change the admin password (requires auth)."""
        body = ChangePasswordRequest(
            current_password=current_password,
            new_password=new_password,
        )
        await self._request("POST", "/api/auth/password", json=body.model_dump())

    # ------------------------------------------------------------------
    # State & monitoring
    # ------------------------------------------------------------------

    async def get_state(self) -> State:
        """
        GET /api/state — returns the full manager state.

        This is the primary way to list all clients and their runtime status.
        There is no separate GET /api/clients endpoint.
        """
        r = await self._request("GET", "/api/state")
        return State.model_validate(r.json())

    async def get_metrics(self) -> Metrics:
        """GET /api/metrics — Go runtime, memory, and per-process metrics."""
        r = await self._request("GET", "/api/metrics")
        return Metrics.model_validate(r.json())

    async def get_audit(self) -> AuditResponse:
        """GET /api/audit — last 100 audit log entries."""
        r = await self._request("GET", "/api/audit")
        return AuditResponse.model_validate(r.json())

    async def get_logs(
        self, client_id: str, room_id: str, transport: str
    ) -> LogsResponse:
        """
        GET /api/logs/{client_id}/{room_id}/{transport}

        All three path segments are required.  Obtain room_id and transport
        from LocationState (via get_state()) for the desired location.
        """
        r = await self._request(
            "GET", f"/api/logs/{client_id}/{room_id}/{transport}"
        )
        return LogsResponse.model_validate(r.json())

    # ------------------------------------------------------------------
    # Client CRUD
    # ------------------------------------------------------------------

    async def create_client(self, request: AddClientRequest) -> CreateClientResponse:
        """
        POST /api/clients — create a new client.

        The server auto-generates a room ID (olcrtc -mode gen) and a 32-byte key.
        Returns 201 Created with {"client_id": "..."}.

        Key points:
        - 'transport' is a plain string ("datachannel"), NOT a JSON object.
        - Use 'payload' for transport-specific options (e.g. {"vp8-fps": "60"}).
        - Set 'from_client' to clone locations from an existing client instead
          of specifying carrier/transport/dns manually.
        """
        r = await self._request(
            "POST",
            "/api/clients",
            json=request.model_dump(exclude_none=True),
        )
        return CreateClientResponse.model_validate(r.json())

    async def update_client(
        self, client_id: str, request: UpdateClientRequest
    ) -> None:
        """
        PUT /api/clients/{client_id} — update carrier, transport, dns, quota, name.

        Updates the first location only.  carrier, transport, and dns are all
        required.  Returns 204 No Content on success.
        """
        await self._request(
            "PUT",
            f"/api/clients/{client_id}",
            json=request.model_dump(exclude_none=True),
        )

    async def delete_client(self, client_id: str) -> None:
        """
        DELETE /api/clients/{client_id}

        Stops all location processes and removes the client from config.
        Cannot delete the last remaining client.
        """
        await self._request("DELETE", f"/api/clients/{client_id}")

    async def add_location(
        self, client_id: str, request: AddLocationRequest
    ) -> None:
        """
        POST /api/clients/{client_id}/locations

        Adds a new location (with a freshly generated room ID + key) to an
        existing client.  Returns 201 No Content on success.
        """
        await self._request(
            "POST",
            f"/api/clients/{client_id}/locations",
            json=request.model_dump(exclude_none=True),
        )

    async def delete_location(self, client_id: str, room_id: str) -> None:
        """
        DELETE /api/clients/{client_id}/locations/{room_id}

        Removes one location from a client by its room ID.
        Cannot delete the last location.
        """
        await self._request("DELETE", f"/api/clients/{client_id}/locations/{room_id}")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    async def restart_location(
        self, client_id: str, room_id: str, transport: str
    ) -> None:
        """
        POST /api/actions/restart

        Restarts a specific location process identified by the three-part key
        (client_id, room_id, transport).  Obtain these from LocationState via
        get_state().
        """
        body = LocationActionRequest(
            client_id=client_id, room_id=room_id, transport=transport
        )
        await self._request(
            "POST", "/api/actions/restart", json=body.model_dump()
        )

    async def regenerate_room(self, client_id: str) -> None:
        """
        POST /api/actions/regenerate-room

        Runs 'olcrtc -mode gen' to get a new room ID for every location of
        the client, saves config, and triggers a reload.
        """
        body = ClientActionRequest(client_id=client_id)
        await self._request(
            "POST", "/api/actions/regenerate-room", json=body.model_dump()
        )

    async def rotate_key(self, client_id: str) -> None:
        """
        POST /api/actions/rotate-key

        Generates a new random 32-byte hex key for every location of the
        client, saves config, and triggers a reload.
        """
        body = ClientActionRequest(client_id=client_id)
        await self._request(
            "POST", "/api/actions/rotate-key", json=body.model_dump()
        )

    async def reload(self) -> None:
        """
        POST /api/reload (auth required)

        Hot-reloads config: restarts only clients whose config changed,
        leaves unchanged processes running.  Returns 204 No Content.
        """
        await self._request("POST", "/api/reload")

    async def reload_loopback(self) -> None:
        """
        POST /-/reload (no auth, loopback only)

        Same as reload() but requires the request to originate from 127.0.0.1.
        Useful when calling from the same host without credentials.
        """
        await self._request("POST", "/-/reload")

    # ------------------------------------------------------------------
    # Subscriptions (no auth required)
    # ------------------------------------------------------------------

    async def get_subscription(self, client_id: str) -> str:
        """
        GET /{client_id}/ — raw plain-text OlcBox subscription.

        No authentication required.  Returns the subscription text that
        clients import, including quota comment lines and OlcBox URI lines.
        """
        resp = await self._http.get(
            f"/{client_id}/", headers={"Accept": "text/plain"}
        )
        if not resp.is_success:
            raise OlcrtcManagerError(resp.status_code, resp.text)
        return resp.text

    async def get_subscription_parsed(
        self, client_id: str
    ) -> tuple[SubscriptionMeta, list[OlcboxURI]]:
        """
        Fetches and parses the plain-text subscription.

        Returns (meta, uris) where meta holds the parsed #quota-* comment
        values and uris is a list of parsed OlcboxURI objects.

        Example subscription::

            #quota-speed-mbps: 10
            #quota-traffic-gb: 100
            #quota-used-gb: 5
            #quota-used-bytes: 5368709120
            #quota-expires-at: 2026-12-31
            #quota-status: active
            olcrtc://wbstream?datachannel@room-01#key%alice$Alice
        """
        raw = await self.get_subscription(client_id)
        meta = SubscriptionMeta()
        uris: list[OlcboxURI] = []

        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("#quota-speed-mbps:"):
                meta.speed_mbps = int(line.split(":", 1)[1].strip())
            elif line.startswith("#quota-traffic-gb:"):
                meta.traffic_gb = int(line.split(":", 1)[1].strip())
            elif line.startswith("#quota-used-gb:"):
                meta.used_gb = float(line.split(":", 1)[1].strip())
            elif line.startswith("#quota-used-bytes:"):
                meta.used_bytes = int(line.split(":", 1)[1].strip())
            elif line.startswith("#quota-expires-at:"):
                meta.expires_at = line.split(":", 1)[1].strip()
            elif line.startswith("#quota-status:"):
                meta.status = QuotaStatus(line.split(":", 1)[1].strip())
            elif line.startswith("olcrtc://"):
                uris.append(OlcboxURI.from_raw(line))

        return meta, uris

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    async def is_first_run(self) -> bool:
        """Return True if the panel has no password configured yet."""
        info = await self.me()
        return info.setup_required

    async def list_clients(self) -> list[ClientState]:
        """
        Shortcut: returns state.clients (list[ClientState]).

        The server has no GET /api/clients endpoint — clients are fetched
        via GET /api/state and this helper unwraps that for convenience.
        """
        state = await self.get_state()
        return state.clients

    async def get_uri(self, client_id: str, location_index: int = 0) -> OlcboxURI | None:
        """
        Return the parsed OlcBox URI for one location of a client.

        Reads the URI from the state (LocationState.uri) and parses it.
        Returns None if the client or location does not exist.
        """
        state = await self.get_state()
        for client in state.clients:
            if client.client_id == client_id:
                if location_index < len(client.locations):
                    raw_uri = client.locations[location_index].uri
                    if raw_uri:
                        return OlcboxURI.from_raw(raw_uri)
        return None