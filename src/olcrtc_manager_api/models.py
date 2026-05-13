"""
Pydantic models for olcrtc-manager-panel API.

Source of truth: cmd/olcrtc-manager/main.go
https://github.com/BigDaddy3334/olcrtc-manager-panel

Stack: Python 3.13 · pydantic v2
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Carrier(StrEnum):
    WBSTREAM = "wbstream"
    JAZZ = "jazz"
    TELEMOST = "telemost"


class TransportType(StrEnum):
    """
    Actual transport string values used by the Go server (from isSupported matrix).
    Note: it is "vp8channel", "seichannel", "videochannel" — NOT "vp8" / "sei".
    """
    DATACHANNEL = "datachannel"
    VP8CHANNEL = "vp8channel"
    SEICHANNEL = "seichannel"
    VIDEOCHANNEL = "videochannel"


class QuotaStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TRAFFIC_EXCEEDED = "traffic_exceeded"


# ---------------------------------------------------------------------------
# Config-level sub-models (used inside state / config responses)
# ---------------------------------------------------------------------------


class Endpoint(BaseModel):
    room_id: str
    key: str


class TransportConfig(BaseModel):
    """
    Transport as stored in config.json and returned inside Location objects.
    Serialised as {"type": "datachannel", "payload": {...}}.
    """
    type: TransportType
    payload: dict[str, str] | None = None


class Quota(BaseModel):
    """
    Traffic and speed quota.
    All numeric fields default to 0 (= unlimited / not set), matching Go's zero values.
    expires_at is an empty string when absent.
    """
    speed_mbps: int = Field(0, ge=0)
    traffic_gb: int = Field(0, ge=0)
    used_gb: int = Field(0, ge=0)
    used_bytes: int = Field(0, ge=0)
    expires_at: str = Field("", description="YYYY-MM-DD or empty string")

    @field_validator("expires_at")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        if v:
            from datetime import date
            date.fromisoformat(v)
        return v


class Location(BaseModel):
    """
    A single olcrtc server location as stored in config.json.
    Returned embedded inside ClientState.locations in the /api/state response.
    """
    name: str
    client_id: str = Field("", alias="client-id")
    endpoint: Endpoint
    carrier: str
    transport: TransportConfig
    link: str = "direct"
    data: str = "data"
    dns: str = "1.1.1.1:53"

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Runtime state (returned by GET /api/state)
# ---------------------------------------------------------------------------


class RuntimeState(BaseModel):
    status: str           # "running" | "exited" | "stopped"
    running: bool
    pid: int | None = None
    started_at: str | None = None
    exited_at: str | None = None
    exit_error: str | None = None
    log_count: int = 0
    restarts: int = 0


class LocationState(BaseModel):
    """Location with runtime state, as returned inside ClientState."""
    name: str
    room_id: str
    uri: str              # OlcBox URI string for this location
    carrier: str
    transport: str        # transport type string
    payload: dict[str, str] | None = None
    link: str
    dns: str
    running: bool
    runtime: RuntimeState


class ClientState(BaseModel):
    client_id: str
    quota: Quota
    locations: list[LocationState] = Field(default_factory=list)


class State(BaseModel):
    """Full response body for GET /api/state."""
    name: str
    port: int
    client_count: int
    running_count: int
    clients: list[ClientState] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Metrics (GET /api/metrics)
# ---------------------------------------------------------------------------


class GoMetrics(BaseModel):
    version: str
    os: str
    arch: str
    goroutines: int


class MemoryMetrics(BaseModel):
    alloc_bytes: int
    sys_bytes: int
    heap_alloc_bytes: int
    heap_inuse_bytes: int
    stack_inuse_bytes: int


class ChildMetric(BaseModel):
    client_id: str
    room_id: str
    transport: str
    name: str
    runtime: RuntimeState


class Metrics(BaseModel):
    """Full response body for GET /api/metrics."""
    runtime: str          # RFC3339 collection timestamp
    go: GoMetrics
    memory: MemoryMetrics
    manager: RuntimeState
    children: list[ChildMetric] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Logs (GET /api/logs/{client_id}/{room_id}/{transport})
# ---------------------------------------------------------------------------


class LogLine(BaseModel):
    time: str             # RFC3339
    stream: str           # "stdout" | "stderr"
    line: str


class LogsResponse(BaseModel):
    logs: list[LogLine] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Audit (GET /api/audit)
# ---------------------------------------------------------------------------


class AuditEvent(BaseModel):
    time: str
    action: str
    detail: str = ""


class AuditResponse(BaseModel):
    events: list[AuditEvent] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    """POST /api/auth/login.  Field name is 'user', not 'username'."""
    user: str
    password: str


class SetupRequest(BaseModel):
    """POST /api/auth/setup — first-run, only works when no password is set yet."""
    user: str = "admin"
    password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """POST /api/auth/password — requires active session / basic auth."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class AuthMeResponse(BaseModel):
    authenticated: bool
    user: str | None = None
    setup_required: bool = False


# ---------------------------------------------------------------------------
# Client / location mutation requests
# ---------------------------------------------------------------------------


class AddClientRequest(BaseModel):
    """
    POST /api/clients

    'transport' is a plain string (e.g. "datachannel"), NOT a JSON object.
    Separate 'payload' carries transport-specific options.
    Leave 'carrier'/'transport'/'dns' empty and set 'from_client' to clone
    all locations from an existing client.
    """
    client_id: str
    carrier: str = "wbstream"
    transport: str = "datachannel"
    payload: dict[str, str] | None = None
    dns: str = "1.1.1.1:53"
    name: str = ""
    from_client: str = ""
    quota: Quota = Field(default_factory=Quota)  # pyright: ignore[reportArgumentType]


class UpdateClientRequest(BaseModel):
    """
    PUT /api/clients/{client_id}

    Updates the first location of a client.
    carrier, transport, and dns are all required by the server.
    'transport' is a plain string, not a JSON object.
    """
    carrier: str
    transport: str
    dns: str
    payload: dict[str, str] | None = None
    name: str = ""
    quota: Quota = Field(default_factory=Quota)  # pyright: ignore[reportArgumentType]


class AddLocationRequest(BaseModel):
    """POST /api/clients/{client_id}/locations"""
    carrier: str = "wbstream"
    transport: str = "datachannel"
    payload: dict[str, str] | None = None
    dns: str = "1.1.1.1:53"
    name: str = ""


class CreateClientResponse(BaseModel):
    """201 Created response from POST /api/clients."""
    client_id: str


# ---------------------------------------------------------------------------
# Action requests
# ---------------------------------------------------------------------------


class LocationActionRequest(BaseModel):
    """POST /api/actions/restart — targets one specific location process."""
    client_id: str
    room_id: str
    transport: str


class ClientActionRequest(BaseModel):
    """POST /api/actions/regenerate-room and POST /api/actions/rotate-key."""
    client_id: str


# ---------------------------------------------------------------------------
# Subscription helpers
# ---------------------------------------------------------------------------


class SubscriptionMeta(BaseModel):
    """Quota metadata parsed from '#quota-*' comment lines in the subscription."""
    speed_mbps: int | None = None
    traffic_gb: int | None = None
    used_gb: float | None = None
    used_bytes: int | None = None
    expires_at: str | None = None
    status: QuotaStatus | None = None


class OlcboxURI(BaseModel):
    """
    Parsed OlcBox URI.
    Format: olcrtc://<carrier>?<transport>@<room_id>#<key>%<client_id>$<display_name>
    """
    carrier: str
    transport: str
    room_id: str
    key: str
    client_id: str | None = None
    display_name: str | None = None
    raw: str

    @classmethod
    def from_raw(cls, uri: str) -> "OlcboxURI":
        if not uri.startswith("olcrtc://"):
            raise ValueError(f"Not a valid OlcBox URI: {uri!r}")
        body = uri.removeprefix("olcrtc://")
        carrier, rest = body.split("?", 1)
        transport, rest = rest.split("@", 1)
        room_id, key, client_id, display_name = rest, "", None, None
        if "#" in room_id:
            room_id, rest = room_id.split("#", 1)
            if "%" in rest:
                key, rest = rest.split("%", 1)
                client_id, display_name = (rest.split("$", 1) + [None])[:2]
            else:
                key = rest
        return cls(
            carrier=carrier,
            transport=transport,
            room_id=room_id,
            key=key,
            client_id=client_id,
            display_name=display_name,
            raw=uri,
        )