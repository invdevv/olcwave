# Installation

This walks through a full deployment on a fresh Linux server. By the end you'll have the panel running behind Caddy with your own domains.

## What you need

- A Linux server (any modern distro). Examples below use Debian/Ubuntu `apt`.
- **Docker** and the **Docker Compose plugin**.
- **Node.js 20+ / npm** — the frontend is built on the host, not in Docker.
- A running **Remnawave** instance and an API token for it.
- For production: a **domain** (two names, e.g. `panel.example.org` and `sub.example.org`) pointing at the server. Caddy gets HTTPS certificates for them automatically.

The API container talks to the host's Docker daemon through `/var/run/docker.sock` — that's how it launches OLCRTC containers. This means the panel effectively has root on the host. Only run it on a server you control.

## 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl enable --now docker
```

Verify:

```bash
docker --version
docker compose version
```

If you want to run `docker` without `sudo`, add your user to the `docker` group and re-log:

```bash
sudo usermod -aG docker "$USER"
```

## 2. Install Node.js

```bash
# Debian/Ubuntu — NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version   # v20+
```

## 3. Clone the repo

```bash
git clone https://github.com/invdevv/olcwave.git
cd olcwave
```

## 4. Configure the backend

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Every variable is explained in [configuration.md](configuration.md). The ones you **must** change before first start:

```ini
RW_API_URL=https://your-remnawave-host        # your Remnawave API base URL
RW_API_TOKEN=...                               # Remnawave API token
POSTGRES_PASSWORD=<something strong>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<something strong>
JWT_SECRET_KEY=<random string>
```

> Note: `backend/.env` is passed into the API container at runtime via `env_file` in `docker-compose.yaml` (it is **not** baked into the image — it's in `.dockerignore`). If you change it later, just restart the API: `docker compose up -d api`.

## 5. Configure Compose (root `.env`)

Docker Compose substitutes `${POSTGRES_USER}`, `${POSTGRES_PASSWORD}` and `${POSTGRES_DB}` in `docker-compose.yaml` from a `.env` file **in the repo root**. This is a separate file from `backend/.env`, and the three Postgres values **must match** what you put in `backend/.env` — otherwise the API and the database won't agree on credentials.

Create `./.env`:

```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<same strong password as backend/.env>
POSTGRES_DB=main
```

## 6. Configure the frontend

```bash
cp frontend/.env.example frontend/.env
$EDITOR frontend/.env
```

```ini
# Where the browser reaches the backend API.
# Caddy serves the SPA and the API under one domain and strips the /api prefix,
# so point this at <panel-domain>/api:
VITE_API_URL=https://panel.example.org/api

# Subscription link shown/copied in the UI. {uuid} is replaced per user.
VITE_SUB_URL_TEMPLATE=https://sub.example.org/{uuid}
```

These values are baked into the built JavaScript at build time (step 7). Change them → rebuild the frontend.

## 7. Build the frontend

Caddy serves the static files from `frontend/dist`, so you build them once on the host:

```bash
cd frontend
npm ci
npm run build      # outputs frontend/dist
cd ..
```

## 8. Set up your domains in Caddy

Edit `caddy/Caddyfile` and replace the example domains with yours:

```caddyfile
panel.example.org {
    # /api/* is stripped before proxying: /api/auth/login -> /auth/login on the backend.
    handle_path /api/* {
        reverse_proxy api:8000
    }

    handle {
        root * /srv/frontend/dist
        try_files {path} /index.html
        file_server
    }
}

sub.example.org {
    handle {
        rewrite * /sub{uri}
        reverse_proxy panel.example.org
    }
}
```

- `panel.example.org` serves the SPA and proxies `/api/*` to the backend, stripping the `/api` prefix (so `VITE_API_URL` ends in `/api` and the backend still sees its real routes like `/auth/login`).
- `sub.example.org/<uuid>` rewrites to `panel.example.org/sub/<uuid>` — that's the public subscription URL.

The Compose file publishes ports **80** and **443**, which is what Caddy needs for automatic HTTPS on the real domains above. If you only want plain HTTP for a quick test, replace the `panel.example.org { ... }` block with a plain-port site (Caddy then serves over HTTP, no certificates):

```caddyfile
:80 {
    handle_path /api/* {
        reverse_proxy api:8000
    }
    handle {
        root * /srv/frontend/dist
        try_files {path} /index.html
        file_server
    }
}
```

## 9. Start everything

```bash
docker compose up -d
```

This starts three containers:

- `olcwave-postgres` — the database
- `olcwave-api` — the FastAPI backend (waits for Postgres to be healthy)
- `olcwave-caddy` — reverse proxy + static file server

The backend creates its database tables automatically on first start (no migration step needed yet).

## 10. Verify

```bash
docker ps
```

You should see `olcwave-postgres`, `olcwave-api`, `olcwave-caddy` all `Up`.

Check the API logs:

```bash
docker compose logs -f api
```

Then open `https://panel.example.org` (or your host) and log in with the `ADMIN_USERNAME` / `ADMIN_PASSWORD` from `backend/.env`.

## Local / HTTP-only variant

There is a `docker-compose-dev.yaml` that runs only Postgres + the API (no Caddy). For local development it's usually easier to run the backend and frontend directly on the host — see [development.md](development.md).

## Updating

```bash
git pull
cd frontend && npm ci && npm run build && cd ..   # rebuild SPA if it changed
docker compose up -d --build                        # rebuild API image, restart
```

If you only changed `backend/.env`, no rebuild is needed — it's read at container start, so `docker compose up -d api` picks it up.
