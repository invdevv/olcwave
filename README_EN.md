# OlcWave

[🇷🇺 Русский](README_RU.md)

> Subscription bridge between [RemnaWave](https://github.com/remnawave) and [olcrtc-manager-panel](https://github.com/BigDaddy3334/olcrtc-manager-panel)

OlcWave acts as a middleware layer: when a user requests their subscription via a `short_uuid`, OlcWave validates their account in RemnaWave, then automatically provisions or retrieves their client in olcrtc-manager and returns a ready-to-use OlcBox subscription.

---

## How it works

```
User → olcwave.example.com/{short_uuid}
         │
         ├─ 1. Validate subscription in RemnaWave
         │       └─ 404 if not found / expired
         │
         ├─ 2. Look up client in olcrtc-manager
         │       └─ Auto-create if missing (quota synced from RemnaWave expiry)
         │
         └─ 3. Return OlcBox subscription text
```

The `short_uuid` is the same one used in your RemnaWave subscription link, so users just swap the domain — no extra configuration on their end.

---

## Requirements

- Docker & Docker Compose
- A running [RemnaWave](https://github.com/remnawave) instance
- A running [olcrtc-manager-panel](https://github.com/BigDaddy3334/olcrtc-manager-panel) instance
- Caddy/Nginx

---

## Installation

First install and configure [OlcrtcManagerPanel](https://github.com/BigDaddy3334/olcrtc-manager-panel)
```bash
curl -fsSL https://raw.githubusercontent.com/BigDaddy3334/olcrtc-manager-panel/main/scripts/install.sh | sudo bash
```

Then install and configure OlcWave
```bash
git clone https://github.com/invdevv/olcwave.git --depth=1
cd olcwave
cp .env.example .env   # fill in your values
nano .env
docker compose up -d
```

The service listens on port `8000` by default.

---

## Настройка Reverse proxy:

Caddy:
```Caddyfile
olcwave.example.com {
    reverse_proxy 127.0.0.1:8000
}
olcmanager.example.com {
    reverse_proxy 127.0.0.1:8888
}
```

Nginx:
```nginx
server {
    listen 80;
    server_name olcwave.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name olcmanager.example.com;

    location / {
        proxy_pass http://127.0.0.1:8888;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Configuration

All settings are loaded from a `.env` file:

| Variable | Description |
|---|---|
| `BASE_HOST` | Host to bind the server to |
| `BASE_PORT` | Port to bind the server to |
| `RW_API_URL` | RemnaWave API base URL |
| `RW_API_TOKEN` | RemnaWave API token |
| `OLCRTC_MANAGER_URL` | olcrtc-manager-panel base URL |
| `OLCRTC_MANAGER_LOGIN` | olcrtc-manager admin username |
| `OLCRTC_MANAGER_PASSWORD` | olcrtc-manager admin password |
| `OLCRTC_CARRIER` | Default carrier for new clients (e.g. `wbstream`) |
| `OLCRTC_TRANSPORT` | Default transport (e.g. `datachannel`) |
| `OLCRTC_SERVER_NAME` | Display name for the server location |
| `OLCRTC_DNS` | DNS server for new clients (e.g. `1.1.1.1:53`) |

---

## Project structure

```
src/
├── main.py                  # FastAPI app, single GET /{short_uuid} endpoint
├── config.py                # Pydantic settings (loaded from .env)
├── rw.py                    # RemnaWave SDK wrapper — subscription validation
├── olcmanager.py            # olcrtc-manager logic — create/get client & subscription
└── olcrtc_manager_api/
    ├── client.py            # Async HTTP client for olcrtc-manager-panel REST API
    └── models.py            # Pydantic models (State, ClientState, Quota, OlcboxURI, …)
```

---

## API

### `GET /{short_uuid}`

Returns an OlcBox subscription for the given user.

| Status | Meaning |
|---|---|
| `200` | Subscription text returned |
| `404` | User not found in RemnaWave |

---

## Stack

- **Python 3.13**
- **FastAPI** — HTTP framework
- **httpx** — async HTTP client
- **Pydantic v2** — data validation & settings
- **remnawave** — RemnaWave Python SDK
- **uv** — package management

---

## License

[GPL-3.0](LICENSE)