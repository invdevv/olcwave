# API

The backend is a FastAPI app. Interactive docs are always available at `/docs` (Swagger) and `/redoc` on the running API.

Base URL: whatever `VITE_API_URL` points at (e.g. `http://localhost:8000` in dev). Routes below are relative to it. The backend itself serves routes with **no `/api` prefix** — in production Caddy exposes them under `/api/*` and strips the prefix before forwarding, which is why `VITE_API_URL` ends in `/api` there.

## Auth

All endpoints except `POST /auth/login` and `GET /sub/{short_uuid}` require a bearer token:

```
Authorization: Bearer <token>
```

The token is a JWT signed with `JWT_SECRET_KEY`, valid for `JWT_EXPIRE_MINUTES`. A `401` clears the token in the frontend and redirects to login.

### `POST /auth/login`

Log in as the admin. There is exactly one admin (from `ADMIN_USERNAME` / `ADMIN_PASSWORD`).

**Request**
```json
{ "username": "admin", "password": "your-password" }
```

**Response** `200`
```json
{ "access_token": "eyJhbGciOi...", "token_type": "bearer" }
```

`401` on bad credentials.

---

## Users

Local user records (traffic + expiry). `short_uuid` is the Remnawave short UUID.

### `GET /users/all?tag=`
List all users. (`tag` query param is required by the signature but unused — pass `?tag=`.)

### `GET /users/?short_uuid=<uuid>`
One user. `404` if not found.

**Response** (`UserSchema`)
```json
{
  "short_uuid": "rfWMHbDFsH_cPXRz",
  "created_at": "2026-01-01T00:00:00Z",
  "expires_at": "2026-06-01T00:00:00Z",
  "traffic_limit_bytes": 107374182400,
  "traffic_used_bytes": 1048576
}
```

### `PUT /users/?short_uuid=<uuid>&expires_at=<iso8601>`
Update a user's expiry. Parameters are query params.

### `DELETE /users/?short_uuid=<uuid>`
Delete a user.

### `GET /users/traffic?short_uuid=<uuid>`
Traffic info (`TrafficInfoSchema`).

```json
{
  "short_uuid": "rfWMHbDFsH_cPXRz",
  "limit": 107374182400,
  "used": 1048576,
  "remaining": 107373133824,
  "unlimited": false,
  "exceeded": false
}
```

### `PATCH /users/traffic?short_uuid=<uuid>`
Set the traffic limit. `0` = unlimited.

**Request**
```json
{ "traffic_limit_bytes": 214748364800 }
```

Returns the updated `TrafficInfoSchema`.

### `POST /users/traffic/reset?short_uuid=<uuid>`
Reset `used` to 0. Returns the updated `TrafficInfoSchema`.

---

## Profiles

OLCRTC YAML templates. See [profiles.md](profiles.md).

### `GET /profiles/all?tag=`
List all profiles. (`tag` param required by signature, unused.)

### `GET /profiles/?tag=<tag>`
One profile by tag. `404` if not found.

### `POST /profiles/`
Create a profile. YAML is validated (must parse).

**Request** (`ProfileSchema`)
```json
{ "name": "Germany VP8", "tag": "de-vp8", "profile": "mode: cnc\nauth:\n  provider: jitsi\n..." }
```

Returns `"ok"`.

### `PUT /profiles/?tag=<tag>&name=<name>&profile=<yaml>`
Update a profile's name and YAML. Parameters are query params. **Side effect:** stops every container whose name contains `<tag>`.

### `DELETE /profiles/?tag=<tag>`
Delete a profile. **Side effect:** stops and removes every container whose name contains `<tag>`.

---

## Containers

Docker containers named `olcwave-<config_tag>-<user_id>`.

### `GET /containers/all`
All panel containers (running and stopped).

**Response** (list of `ContainerSchema`)
```json
[
  {
    "id": "3f2a1b...",
    "name": "olcwave-de-vp8-rfWMHbDFsH_cPXRz",
    "user_id": "rfWMHbDFsH_cPXRz",
    "config_tag": "de-vp8",
    "status": "running",
    "created": "2026-01-01T00:00:00Z",
    "image": "olcrtc"
  }
]
```

### `POST /containers/run?name=<name>`
Start a container. Returns `403 traffic_limit_exceeded` if the owning user is over their limit.

### `POST /containers/stop?name=<name>`
Stop a container.

### `POST /containers/restart?name=<name>`
Restart a container.

### `DELETE /containers/?name=<name>`
Force-remove a container.

### `GET /containers/logs?name=<name>`
`{ "name": "...", "logs": "..." }` — the container's stdout/stderr.

### `GET /containers/config?name=<name>`
`{ "name": "...", "config": "..." }` — the `config.yaml` the container is running.

### `GET /containers/stats?name=<name>`
Live byte counters (`ContainerStatsSchema`).

```json
{
  "name": "olcwave-de-vp8-rfWMHbDFsH_cPXRz",
  "upload_bytes": 12345,
  "download_bytes": 67890,
  "total_bytes": 80235,
  "upload_rate_bps": 1024,
  "download_rate_bps": 4096
}
```

---

## Subscriptions (public)

### `GET /sub/{short_uuid}`
The public subscription endpoint. **No auth.** This is what a subscriber's client fetches.

Behavior (see [architecture.md](architecture.md)):

- Validates the UUID against Remnawave. `404` if unknown.
- Auto-creates a local user row on first sight.
- If the user is over their traffic limit → returns a "Traffic limit Exceeded" placeholder config with HTTP `403`.
- Otherwise launches any missing containers for the user and returns an **OLCBox v5 bundle** (JSON) of all their locations.

The response carries a `profile-update-interval` header so clients know how often to refresh.
