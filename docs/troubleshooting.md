# Troubleshooting

Real problems you'll actually hit, and how to fix them. Start by looking at logs:

```bash
docker compose logs -f api        # backend
docker compose logs -f caddy      # reverse proxy
docker compose logs -f postgres   # database
docker logs olcwave-<tag>-<uuid>  # a specific OLCRTC container
```

---

## Docker: permission denied

**Symptom:** the API logs show something like `PermissionError: /var/run/docker.sock` or the panel can't list/run containers.

**Cause:** the API container can't access the host Docker socket.

**Fix:**
- Confirm the socket is mounted — `docker-compose.yaml` maps `/var/run/docker.sock:/var/run/docker.sock`.
- On the host, the socket must be accessible. If you run Compose as a non-root user, that user needs to be in the `docker` group:
  ```bash
  sudo usermod -aG docker "$USER"   # then log out and back in
  ```
- On SELinux systems, a `:z`/`:Z` on the mount or an SELinux policy adjustment may be needed.

---

## Container won't start

**Symptom:** `POST /containers/run` fails, or a container immediately exits.

**Check, in order:**

1. **Traffic limit** — if the response is `403 traffic_limit_exceeded`, the owning user is over quota. Reset or raise their limit (Users page → edit → Reset traffic / change limit).
2. **Image build** — the first run builds the `olcrtc` image, which clones and compiles OLCRTC from GitHub. This needs internet access and takes a while. Watch `docker compose logs -f api` during the first subscription/run.
3. **Bad config** — a profile that parses as YAML but isn't a valid OLCRTC config will start a container that exits. Check its logs and its config:
   ```bash
   docker logs olcwave-<tag>-<uuid>
   ```
   The entrypoint requires the `CONFIG` env var; the panel always sets it, so if you see `CONFIG env is required`, the container was started outside the panel.
4. **Name collision** — container names must be `olcwave-<tag>-<uuid>` with exactly two dashes' worth of parts. A `-` inside a profile tag breaks ownership parsing. Rename the profile tag.

---

## Database connection failed

**Symptom:** API logs show `asyncpg` connection/authentication errors, or the API keeps restarting.

**Causes and fixes:**

- **Credentials mismatch** — `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` in `backend/.env` must equal the same three in the **root `.env`**. If they differ, the DB is initialized with one set and the API connects with another. Make them identical, then:
  ```bash
  docker compose down
  # if the DB was already initialized with the wrong password, wipe its volume:
  docker volume rm olcwave_postgres_data   # destroys all data
  docker compose up -d
  ```
- **Wrong host** — inside Compose, `DB_HOST` must be `postgres` (the service name). For a host-side dev run it should be `localhost`.
- **Postgres not ready** — the API `depends_on` a healthcheck, so this is rare, but if you started the API by itself, give Postgres a moment.

---

## Remnawave connection failed

**Symptom:** every subscription request returns `404`, or the API logs show connection/timeout errors when hitting Remnawave.

**Fix:**
- `RW_API_URL` must be the correct Remnawave **API base URL** and reachable from inside the API container (the API image is Python-based, so test with Python, which is guaranteed present):
  ```bash
  docker compose exec api python -c "import os,urllib.request; print(urllib.request.urlopen(os.environ['RW_API_URL']).status)"
  ```
- `RW_API_TOKEN` must be valid. A revoked or wrong token means Remnawave rejects the calls and no user validates.
- Remember: a `404` from `/sub/{uuid}` is also the normal response for a UUID Remnawave doesn't know. Test with a UUID you know is valid.

---

## Subscription doesn't generate

**Symptom:** `GET /sub/{uuid}` returns nothing useful, or no containers appear.

**Walk the flow (see [architecture.md](architecture.md)):**

1. **UUID valid in Remnawave?** If not → `404`. This is the most common cause.
2. **Traffic exceeded?** Then you get the "Traffic limit Exceeded" placeholder and HTTP `403`, not real configs. Reset traffic.
3. **Any profiles defined?** With zero profiles there's nothing to launch — the bundle will have no locations. Create at least one profile.
4. **Docker healthy?** Container creation needs the Docker socket working (see the permission-denied section).
5. Watch the API logs while you fetch the URL — errors during config generation or `docker run` show up there.

---

## Traffic not updating

**Symptom:** `traffic_used_bytes` stays at 0 even though a container is passing traffic.

**Checks:**

- Traffic is only counted for **running** `olcwave-*` containers. A stopped container reports nothing.
- Traffic flows through the container's SOCKS proxy — only bytes through that proxy are counted. If the client isn't actually using it, there's nothing to count.
- Read the raw stats from inside the container:
  ```bash
  docker exec olcwave-<tag>-<uuid> cat /var/lib/olcwave/stats.json
  ```
  If `total_bytes` is growing here but the user's `used` isn't, the collection loop isn't seeing it — check API logs.
- The loop runs every `TRAFFIC_COLLECT_INTERVAL` seconds. If it's set very high, updates are slow. Lower it and restart the API.
- Container name must parse to an owner (`olcwave-<tag>-<uuid>`). A malformed name means the delta is discarded.

---

## Caddy / SSL problems

**Symptom:** browser shows a certificate error, or the site is unreachable over HTTPS.

**Checks:**

- **Port 443** — the `docker-compose.yaml` publishes both `80` and `443`, which automatic HTTPS needs. If you customized Compose and dropped `443`, add it back to the `caddy` service:
  ```yaml
      ports:
        - "80:80"
        - "443:443"
  ```
- **DNS** — the domains in `caddy/Caddyfile` must resolve to this server's public IP. Caddy can't get a certificate for a name that doesn't point at it.
- **Firewall** — ports 80 and 443 must be open. Let's Encrypt validates over port 80.
- **Watch Caddy logs** — `docker compose logs -f caddy` shows certificate issuance errors clearly (rate limits, DNS failures, etc.).
- **Frontend can't reach the API** — if the SPA loads but every request fails, `VITE_API_URL` and your Caddy proxy don't line up. Caddy strips `/api`, so `VITE_API_URL` must end in `/api` (e.g. `https://panel.example.org/api`). See [installation.md](installation.md) step 8.

---

## Changes to `.env` don't take effect

- **`backend/.env`** is passed to the API container via `env_file` and read at container start. Restart to apply:
  ```bash
  docker compose up -d api
  ```
- **`frontend/.env`** (`VITE_*`) is baked into the built JS. Rebuild the frontend:
  ```bash
  cd frontend && npm run build && cd ..
  docker compose restart caddy
  ```
- **Root `.env`** (Postgres creds) only applies when the Postgres volume is first created. Changing it later needs a volume reset (see the database section).
