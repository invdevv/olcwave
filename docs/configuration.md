# Configuration

All configuration is done through environment files. There are **three** of them, and they serve different purposes:

| File | Read by | When |
|------|---------|------|
| `backend/.env` | The FastAPI backend (`pydantic-settings`) | Passed into the API container via `env_file` at runtime |
| `.env` (repo root) | Docker Compose | At `docker compose up`, to fill `${...}` in `docker-compose.yaml` |
| `frontend/.env` | Vite | At `npm run build` — baked into the static JS |

The Postgres credentials appear in both `backend/.env` and the root `.env`. **They must match.**

---

## backend/.env

Defined and validated in `backend/src/config.py`. If a required variable is missing, the backend won't start.

### `NAME`

```ini
NAME=moi-krutoi-vpnchik
```

Display name of your service. It's used as the subscription title (`#name:` header) returned to clients. Purely cosmetic — change it freely.

### `RW_API_URL`

```ini
RW_API_URL=https://remnawave.example.org
```

Base URL of your Remnawave API. The backend calls it to check whether a subscriber's UUID is valid and to read their expiry. **Must be reachable from inside the API container.** If it's wrong or unreachable, every subscription request fails.

### `RW_API_TOKEN`

```ini
RW_API_TOKEN=ey...
```

API token for Remnawave. Generate it in your Remnawave admin panel. Without it (or with a bad token), Remnawave calls fail and no subscriptions are issued. Keep it secret.

### `DB_HOST` / `DB_PORT`

```ini
DB_HOST=postgres
DB_PORT=5432
```

Where the database lives. In the Compose setup, `postgres` is the service name, so leave `DB_HOST=postgres`. For local development against a Postgres on your machine, use `localhost`.

### `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`

```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=strong_password_here
POSTGRES_DB=main
```

Database credentials. The backend builds its connection string from these:

```
postgresql+asyncpg://<user>:<password>@<host>:<port>/<db>
```

**These three must be identical to the ones in the root `.env`**, because that's what actually initializes the Postgres container. If they differ, the API can't authenticate to its own database.

### `ADMIN_USERNAME` / `ADMIN_PASSWORD`

```ini
ADMIN_USERNAME=admin
ADMIN_PASSWORD=strong_password_also_here
```

The single admin login for the panel. There is no user registration and no second account — this is it. Login checks these values directly (plain comparison), then issues a JWT. Use a strong password; change it and restart the API to rotate.

### `JWT_SECRET_KEY`

```ini
JWT_SECRET_KEY=change_me
```

Secret used to sign admin JWTs (HS256). **Change it to a long random string.** Anyone who knows it can forge admin tokens. Rotating it invalidates all existing sessions.

Generate one:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

### `JWT_EXPIRE_MINUTES`

```ini
JWT_EXPIRE_MINUTES=1440
```

How long an admin token stays valid, in minutes. Default `1440` = 24 hours. After it expires the panel redirects you to login. Lower = more secure, more frequent logins.

### `DEFAULT_TRAFFIC_LIMIT`

```ini
# 100 GB
DEFAULT_TRAFFIC_LIMIT=107374182400
```

Traffic quota (in **bytes**) assigned to a user the first time they're auto-created from a subscription request. Set `0` for unlimited. You can override any individual user's limit later in the UI.

Convert GB → bytes:

```bash
python3 -c "print(int(input())*(1024**3))"
```

### `TRAFFIC_COLLECT_INTERVAL`

```ini
# seconds
TRAFFIC_COLLECT_INTERVAL=10
```

How often (seconds) the background traffic loop reads each running container's counters, adds the delta to the owning user, and stops the user's containers if they're over the limit. Lower = tighter enforcement and more Docker exec calls; higher = less overhead but coarser accounting.

### `CORS_ORIGINS` (optional)

Not in `.env.example`; has a default in `config.py`:

```python
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
```

Browser origins allowed to call the API. The defaults cover local dev. For production you generally serve the SPA and API from the same origin through Caddy, so CORS isn't hit — but if you call the API cross-origin, add your panel domain here (as a Python-style list in the env value).

---

## Root `.env` (for Docker Compose)

Only three variables, only used to initialize the Postgres container:

```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=strong_password_here
POSTGRES_DB=main
```

Compose reads this file automatically because it sits next to `docker-compose.yaml`. Again: keep these equal to the same-named values in `backend/.env`.

---

## frontend/.env

Read by Vite at build time. Both values end up hard-coded in the compiled JS, so **rebuild the frontend after changing them** (`npm run build`).

### `VITE_API_URL`

```ini
VITE_API_URL=http://localhost:8000
```

Base URL the browser uses to reach the backend. For local dev, `http://localhost:8000`. For production behind Caddy, your panel domain **with the `/api` suffix** (e.g. `https://panel.example.org/api`) — Caddy strips `/api` before forwarding, so the backend still sees its real routes (see [installation.md](installation.md)).

### `VITE_SUB_URL_TEMPLATE`

```ini
VITE_SUB_URL_TEMPLATE=https://sub.example.org/{uuid}
```

Template for the per-user subscription link shown and copied in the UI. Every `{uuid}` is replaced with the user's short UUID:

```
https://sub.example.org/{uuid}  →  https://sub.example.org/rfWMHbDFsH_cPXRz
```

If left empty, the UI falls back to `<current-origin>/sub/<uuid>`.
