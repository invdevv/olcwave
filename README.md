# OLcWave

Web control panel for [OLCRTC](https://github.com/openlibrecommunity/olcrtc) instances, integrated with [Remnawave](https://docs.rw/).

You store OLCRTC config templates ("profiles") in the panel. When a user opens their subscription link, the panel checks the user against Remnawave, generates a fresh OLCRTC config from each profile, launches it in its own Docker container, and returns a ready-to-import subscription. It also meters per-user traffic and stops containers when a user runs out of quota.

The panel is admin-only. End users never log in - they just hit their subscription URL.

## Features

- **Remnawave integration** - user validity and expiry come from your Remnawave instance. No separate user database to maintain.
- **Profiles** - reusable OLCRTC YAML templates. One profile → one container per user.
- **Automatic config generation** - the panel fills in the parts that must be unique per user (encryption key, Jitsi room) so you never hand-edit them.
- **Container lifecycle** - start / stop / restart / remove OLCRTC containers, view their live logs and the exact `config.yaml` they run.
- **Traffic accounting** - a SOCKS proxy inside each container counts bytes; the backend sums them per user, enforces limits, and can reset them.
- **Subscriptions** - one stable URL per user that returns an OLCBox-compatible bundle of all their locations.

## Architecture overview

```
Browser (admin)                Subscriber's client
      │                              │
      ▼                              ▼
   Frontend (React SPA)          /sub/{uuid}
      │                              │
      └──────────────┬──────────────┘
                     ▼
              Backend (FastAPI)
                     │
        ┌────────────┼─────────────────────┐
        ▼            ▼                      ▼
   PostgreSQL   Remnawave API        Docker daemon
   (users,      (validate user,      (runs OLCRTC
    profiles,    expiry)              containers)
    traffic)                              │
                                          ▼
                                  OLCRTC container(s)
                                  olcwave-<tag>-<uuid>
```

- **Frontend** - React + Vite single-page app. Talks to the backend over HTTP with a JWT. Built to static files and served by Caddy in production.
- **Backend** - FastAPI. Owns all logic: auth, profiles, Remnawave calls, container management (via the Docker socket), subscription generation, and the background traffic loop.
- **PostgreSQL** - stores local user records (traffic + expiry) and profile templates.
- **Docker** - the backend builds the `olcrtc` image and runs one container per (profile, user) pair on the host's Docker daemon.
- **OLCRTC** - the actual transport. Each container also runs a small SOCKS proxy that writes byte counters to `stats.json`, which the backend reads.

See [docs/architecture.md](docs/architecture.md) for the full flow.

## Quick start

Requires Docker + Docker Compose and a running Remnawave instance.

```bash
git clone https://github.com/invdevv/olcwave.git
cd olcwave

chmod +x install.sh
./install.sh
```

Then open the panel and log in with `ADMIN_USERNAME` / `ADMIN_PASSWORD` from `backend/.env`.

Or install manualy
[docs/installation.md](docs/installation.md) 


## Documentation

| Doc | What's in it |
|-----|--------------|
| [installation.md](docs/installation.md) | Full install on a clean Linux server |
| [configuration.md](docs/configuration.md) | Every environment variable, explained |
| [profiles.md](docs/profiles.md) | How profiles work, config generation, example YAML |
| [architecture.md](docs/architecture.md) | Components, request flow, traffic system, Caddy |
| [development.md](docs/development.md) | Running locally + AI usage rules for contributors |
| [api.md](docs/api.md) | HTTP endpoints |
| [troubleshooting.md](docs/troubleshooting.md) | Common problems and fixes |

## License

GNU GPL v3. See [LICENSE](LICENSE).
