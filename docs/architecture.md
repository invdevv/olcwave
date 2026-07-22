# Architecture

How the pieces fit together, and what actually happens on each request.

## Components

| Component | Container | Role |
|-----------|-----------|------|
| Frontend | (none — static files served by Caddy) | React SPA, admin UI |
| Backend | `olcwave-api` | FastAPI. All logic. Talks to Postgres, Remnawave, and the Docker socket. |
| Database | `olcwave-postgres` | PostgreSQL 16. Users + profiles + traffic counters. |
| Reverse proxy | `olcwave-caddy` | Serves the SPA, proxies API, terminates HTTPS. |
| OLCRTC | `olcwave-<tag>-<uuid>` | One per (profile, user). The actual transport + a stats-writing SOCKS proxy. |

The API container mounts `/var/run/docker.sock`, so it drives the host's Docker daemon directly — that's how it builds the `olcrtc` image and starts/stops OLCRTC containers.

## Data model

Two tables, created automatically on backend startup (`create_tables`, no Alembic yet).

**users**
- `short_uuid` — the Remnawave short UUID, unique. This is the link between a subscriber and their local record.
- `created_at`, `expires_at` — expiry mirrored from Remnawave at first sight.
- `traffic_limit_bytes` — `0` means unlimited.
- `traffic_used_bytes` — accumulated by the traffic loop.

**profiles**
- `name`, `tag` (unique), `profile` (YAML template).

Note: users are created **lazily**. There's no "add user" button — a local user row appears the first time a valid subscription is requested for that UUID.

## The main flow: a subscription request

This is the heart of the system. When a client hits `GET /sub/{short_uuid}` (`Subscriptions.get`):

```
1. Ask Remnawave: is this short_uuid valid?
      └─ no  → 404, nothing happens.
      └─ yes → continue.

2. Do we have a local user row for it?
      └─ no  → create one (expiry from Remnawave, default traffic limit).

3. Check traffic:
      └─ exceeded → return a "Traffic limit Exceeded" placeholder config, HTTP 403.

4. Which of this user's containers are already running?
      └─ read their live config.yaml.

5. For every profile that has no container for this user yet:
      └─ generate a fresh config (random crypto.key, room name)
      └─ run a new container  olcwave-<tag>-<short_uuid>

6. Build an OLCBox v5 bundle from every profile's config and return it.
```

So the first time a user opens their link, their containers spin up on demand. Subsequent fetches reuse the running ones.

```
Client ──GET /sub/{uuid}──► Backend ──validate──► Remnawave
                               │
                               ├─ ensure local user row (Postgres)
                               ├─ check traffic (Postgres)
                               ├─ for each missing profile:
                               │      generate config → docker run
                               └─ return OLCBox bundle
```

### Subscription output formats

The code can render configs two ways:

- **OLCBox v5 bundle** (`olcrtc_to_olcbox_lbv4`) — a JSON object with `version: 5`, an `active_location_id`, and a `locations` array. This is what `GET /sub/{uuid}` returns. The panel's Subscriptions page renders this bundle.
- **Compact `olcrtc://` URIs** (`config_to_uri`, `config_to_olcbox_uri`) — single-line URIs, used to build human-readable subscription text with `#name` / `##icon` headers.

## Containers

### Lifecycle

The panel manages containers through the Docker SDK (`backend/src/olcrtc/sdk.py`):

| Action | What it does |
|--------|--------------|
| **build** | Builds the `olcrtc` image from `backend/olcrtc/` if it doesn't exist yet (or force-rebuild). |
| **run** | Removes any old container with the same name, then `docker run` detached with the generated config passed as the `CONFIG` env var. Named `olcwave-<tag>-<uuid>`. |
| **start** | Start an existing stopped container. |
| **stop** | Stop a running container. |
| **restart** | Restart it. |
| **remove** | Force-remove it. |
| **logs** | `docker logs` output. |
| **config** | `cat /tmp/olcwave/config.yaml` inside the container — the exact config it's running. |
| **stats** | `cat /var/lib/olcwave/stats.json` inside the container — byte counters. |

The Containers page in the UI exposes start/stop/restart, logs, config, and live per-container stats (total, up/down bytes, up/down speed, uptime), grouped by user or by config tag.

### What's inside an OLCRTC container

Built from `backend/olcrtc/Dockerfile`. Two processes, started by `entrypoint.sh`:

1. **olcrtc** — cloned and built from the upstream [openlibrecommunity/olcrtc](https://github.com/openlibrecommunity/olcrtc) repo. Runs `/tmp/olcwave/config.yaml`.
2. **proxy** — a small Go SOCKS5 proxy (`proxy.go`). OLCRTC is pointed at it via an appended `socks:` block. Every byte through the proxy is counted and flushed to `stats.json` once a second (atomic write).

The entrypoint writes the `CONFIG` env var to `config.yaml`, appends the `socks:` block, launches the proxy, then launches olcrtc, and tears down the proxy when olcrtc exits.

## Traffic system

Traffic is measured by the SOCKS proxy, aggregated by the backend.

### Inside the container: `stats.json`

`proxy.go` wraps every accepted connection in a counting reader/writer. It periodically writes `/var/lib/olcwave/stats.json`:

```json
{
  "upload_bytes": 12345,
  "download_bytes": 67890,
  "total_bytes": 80235,
  "upload_rate_bps": 1024,
  "download_rate_bps": 4096,
  "connections_open": 2,
  "connections_total": 40,
  "started_at": "...",
  "updated_at": "..."
}
```

`total_bytes` = upload + download. This resets to 0 whenever the container restarts.

### In the backend: the collection loop

`TrafficManager` runs in the FastAPI lifespan, every `TRAFFIC_COLLECT_INTERVAL` seconds:

1. For each running `olcwave-*` container, read `stats.json` and take `total_bytes`.
2. Compute the **delta** since last tick. (If the counter went down — container restarted — treat the new total as the delta, so restarts don't undercount.)
3. Add the delta to the owning user's `traffic_used_bytes` in Postgres. The owner is parsed from the container name (`olcwave-<tag>-<owner>`).
4. If the user is now over their limit, **stop all of that user's containers**.

Forgotten containers (that no longer exist) are dropped from the in-memory "last totals" map so a future container with the same name starts clean.

### Enforcement

- **Over limit** → the loop stops the user's containers. Trying to start a container for an over-limit user via `POST /containers/run` returns `403 traffic_limit_exceeded`.
- **Subscription while over limit** → `GET /sub/{uuid}` returns a placeholder config named "Traffic limit Exceeded" with HTTP 403, so the client sees the reason instead of a broken connection.

### Limit fields

Per user (see `TrafficInfoSchema`):

- `limit` — `traffic_limit_bytes`; `0` = unlimited.
- `used` — `traffic_used_bytes`.
- `remaining` — `max(0, limit - used)` (0 when unlimited).
- `unlimited` — `limit == 0`.
- `exceeded` — not unlimited **and** `used >= limit`.

### Reset

`POST /users/traffic/reset` (a button in the user edit modal) sets `traffic_used_bytes` back to 0. Combined with editing the limit or expiry, this is how you "renew" a user. Note the in-container counter isn't reset — the loop's delta logic handles that on the next tick.

## Caddy

Caddy is the only thing exposed to the internet. It does three jobs from `caddy/Caddyfile`:

```caddyfile
panel.example.org {
    handle_path /api/* {
        reverse_proxy api:8000          # API traffic → backend, /api stripped
    }
    handle {
        root * /srv/frontend/dist        # everything else → the SPA
        try_files {path} /index.html
        file_server
    }
}

sub.example.org {
    handle {
        rewrite * /sub{uri}              # sub.example.org/<uuid>
        reverse_proxy panel.example.org  #   → panel.example.org/sub/<uuid>
    }
}
```

- **reverse_proxy** — forwards to the `api` service (`api:8000`) inside the Compose network. `handle_path` strips the `/api` prefix, so the browser calls `https://panel.example.org/api/auth/login` and the backend receives `/auth/login`. That's why `VITE_API_URL` ends in `/api`. The frontend `dist` is bind-mounted read-only into the Caddy container at `/srv/frontend/dist`.
- **HTTPS / certificates / SSL** — Caddy automatically obtains and renews Let's Encrypt certificates for any real domain you configure. The Compose file publishes ports **80** and **443**, which is what it needs; the domain's DNS must point at the server.
- **SPA routing** — `try_files {path} /index.html` makes client-side routes (like `/users`) load the SPA instead of 404ing.

For a local, cert-free setup use a plain-port site block (e.g. `:80 { ... }`) instead of a domain, and Caddy serves over HTTP without certificates.
