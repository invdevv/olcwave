from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Core config models (mirror Go structs)
# ──────────────────────────────────────────────

class Quota(BaseModel):
    speed_mbps: int = Field(0, alias="speed_mbps")
    traffic_gb: int = Field(0, alias="traffic_gb")
    used_gb: int = Field(0, alias="used_gb")
    used_bytes: int = Field(0, alias="used_bytes")
    expires_at: str = Field("", alias="expires_at")

    model_config = {"populate_by_name": True}


class Endpoint(BaseModel):
    room_id: str = Field("", alias="room_id")
    key: str = Field("", alias="key")

    model_config = {"populate_by_name": True}


class Transport(BaseModel):
    type: str = ""
    payload: Optional[dict[str, str]] = None


class Location(BaseModel):
    name: str = ""
    client_id: str = Field("", alias="client-id")
    endpoint: Endpoint = Field(default_factory=Endpoint)  # pyright: ignore[reportArgumentType]
    carrier: str = ""
    transport: Transport = Field(default_factory=Transport)
    link: str = ""
    data: str = ""
    dns: str = ""

    model_config = {"populate_by_name": True}


class Client(BaseModel):
    client_id: str = Field("", alias="client-id")
    quota: Quota = Field(default_factory=Quota)  # pyright: ignore[reportArgumentType]
    locations: list[Location] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


# ──────────────────────────────────────────────
# State / runtime models
# ──────────────────────────────────────────────

class RuntimeState(BaseModel):
    status: str = "stopped"
    running: bool = False
    pid: Optional[int] = None
    started_at: Optional[str] = None
    exited_at: Optional[str] = None
    exit_error: Optional[str] = None
    log_count: int = 0
    restarts: int = 0


class LocationState(BaseModel):
    name: str = ""
    room_id: str = ""
    uri: str = ""
    carrier: str = ""
    transport: str = ""
    payload: Optional[dict[str, str]] = None
    link: str = ""
    dns: str = ""
    running: bool = False
    runtime: RuntimeState = Field(default_factory=RuntimeState)


class ClientState(BaseModel):
    client_id: str = ""
    quota: Quota = Field(default_factory=Quota)  # pyright: ignore[reportArgumentType]
    locations: list[LocationState] = Field(default_factory=list)


class State(BaseModel):
    name: str = ""
    port: int = 0
    client_count: int = 0
    running_count: int = 0
    clients: list[ClientState] = Field(default_factory=list)


# ──────────────────────────────────────────────
# Logs
# ──────────────────────────────────────────────

class LogLine(BaseModel):
    time: str = ""
    stream: str = ""
    line: str = ""


class LogsResponse(BaseModel):
    logs: list[LogLine] = Field(default_factory=list)


# ──────────────────────────────────────────────
# Metrics
# ──────────────────────────────────────────────

class GoMetrics(BaseModel):
    version: str = ""
    os: str = ""
    arch: str = ""
    goroutines: int = 0


class MemoryMetrics(BaseModel):
    alloc_bytes: int = 0
    sys_bytes: int = 0
    heap_alloc_bytes: int = 0
    heap_inuse_bytes: int = 0
    stack_inuse_bytes: int = 0


class ChildMetric(BaseModel):
    client_id: str = ""
    room_id: str = ""
    transport: str = ""
    name: str = ""
    runtime: RuntimeState = Field(default_factory=RuntimeState)


class Metrics(BaseModel):
    runtime: str = ""
    go: GoMetrics = Field(default_factory=GoMetrics)
    memory: MemoryMetrics = Field(default_factory=MemoryMetrics)
    manager: RuntimeState = Field(default_factory=RuntimeState)
    children: list[ChildMetric] = Field(default_factory=list)


# ──────────────────────────────────────────────
# Audit
# ──────────────────────────────────────────────

class AuditEvent(BaseModel):
    time: str = ""
    action: str = ""
    detail: str = ""


class AuditResponse(BaseModel):
    events: list[AuditEvent] = Field(default_factory=list)


# ──────────────────────────────────────────────
# Auth request / response models
# ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    user: str
    password: str


class LoginResponse(BaseModel):
    authenticated: bool = False
    user: Optional[str] = None
    setup_required: Optional[bool] = None


class SetupRequest(BaseModel):
    user: str = ""
    password: str


class SetupResponse(BaseModel):
    authenticated: bool = False
    user: Optional[str] = None
    setup_required: Optional[bool] = None


class AuthMeResponse(BaseModel):
    authenticated: bool = False
    user: Optional[str] = None
    setup_required: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    changed: bool = False


# ──────────────────────────────────────────────
# Client action request models
# ──────────────────────────────────────────────

class AddClientRequest(BaseModel):
    """
    Request body for POST /api/clients.

    Supply carrier + transport + dns for an explicit location,
    or from_client to clone locations from an existing client.
    """
    client_id: str
    from_client: str = Field("", alias="from_client")
    quota: Quota = Field(default_factory=Quota)  # pyright: ignore[reportArgumentType]
    carrier: str = ""
    room_id: str = ""
    transport: str = ""
    key: str = ""
    payload: Optional[dict[str, str]] = None
    dns: str = ""
    name: str = ""

    model_config = {"populate_by_name": True}


class AddClientResponse(BaseModel):
    client_id: str = ""


class UpdateClientRequest(BaseModel):
    """Request body for PUT /api/clients/{client_id}."""
    quota: Quota = Field(default_factory=Quota)  # pyright: ignore[reportArgumentType]
    carrier: str
    transport: str
    payload: Optional[dict[str, str]] = None
    dns: str
    name: str = ""


class AddLocationRequest(BaseModel):
    """Request body for POST /api/clients/{client_id}/locations."""
    carrier: str
    transport: str
    payload: Optional[dict[str, str]] = None
    dns: str
    name: str = ""


class LocationActionRequest(BaseModel):
    """Request body for POST /api/actions/restart."""
    client_id: str
    room_id: str
    transport: str


class ClientActionRequest(BaseModel):
    """Request body for POST /api/actions/regenerate-room and rotate-key."""
    client_id: str
