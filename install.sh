#!/usr/bin/env bash
#
# install.sh - production install helper for OLcWave.
#
# It checks prerequisites, makes sure the three env files exist, builds the
# frontend, and starts the Docker Compose stack. It does NOT invent values for
# you: if an env file is missing it copies the example and stops so you can
# edit it. Read docs/installation.md for what each variable means.
#
# Usage:
#   chmod +x install.sh
#   ./install.sh

set -euo pipefail

# Always run from the repo root (the directory this script lives in).
cd "$(dirname "$0")"

# --- tiny logging helpers -------------------------------------------------
info()  { printf '\033[0;34m[*]\033[0m %s\n' "$1"; }
ok()    { printf '\033[0;32m[+]\033[0m %s\n' "$1"; }
warn()  { printf '\033[0;33m[!]\033[0m %s\n' "$1"; }
err()   { printf '\033[0;31m[x]\033[0m %s\n' "$1" >&2; }

# --- 1. check prerequisites ----------------------------------------------
info "Checking prerequisites..."

if ! command -v docker >/dev/null 2>&1; then
  err "docker is not installed. See docs/installation.md (step 1)."
  exit 1
fi

# The Compose v2 plugin is invoked as 'docker compose' (two words).
if ! docker compose version >/dev/null 2>&1; then
  err "'docker compose' is not available. Install the Docker Compose plugin."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  err "npm is not installed. The frontend is built on the host. See docs/installation.md (step 2)."
  exit 1
fi

ok "docker, docker compose and npm are present."

# --- 2. env files ---------------------------------------------------------
# We never guess secrets. If a file is missing we create it from the example
# (or a template) and ask the user to fill it in, then stop.
missing_env=0

ensure_env_from_example() {
  # $1 = target file, $2 = example file
  local target="$1" example="$2"
  if [ -f "$target" ]; then
    ok "$target exists."
    return
  fi
  if [ -f "$example" ]; then
    cp "$example" "$target"
    warn "Created $target from $example - edit it before continuing."
  else
    warn "$target is missing and no example found at $example."
  fi
  missing_env=1
}

info "Checking environment files..."

missing_env=0

ensure_env_from_example() {
    local target="$1"
    local example="$2"

    if [ -f "$target" ]; then
        ok "$target exists."
        return
    fi

    cp "$example" "$target"
    warn "Created $target from $example."
    missing_env=1
}

ensure_env_from_example "backend/.env" "backend/.env.example"
ensure_env_from_example "frontend/.env" "frontend/.env.example"

if [ "$missing_env" -eq 1 ]; then
    err "Configuration files were created."
    err "Edit backend/.env and frontend/.env, then run ./install.sh again."
    exit 1
fi

# --- 3. sanity check: obvious placeholder values --------------------------
# Cheap guard against starting with defaults that are clearly not production.
if grep -q "^JWT_SECRET_KEY=change_me$" backend/.env; then
  warn "JWT_SECRET_KEY is still 'change_me' in backend/.env - set a real random value."
fi
if grep -q "^RW_API_URL=https://CHANGE_WITH_RAMNAWAVE.url$" backend/.env; then
  err "RW_API_URL is still the placeholder in backend/.env. Set your Remnawave URL."
  exit 1
fi

# --- 4. build the frontend ------------------------------------------------
# Caddy serves the static files from frontend/dist, so we build them here.
info "Building the frontend (npm ci && npm run build)..."
(
  cd frontend
  npm ci
  npm run build
)
ok "Frontend built into frontend/dist."

# --- 5. start the stack ---------------------------------------------------
info "Building the API image and starting the stack..."
docker compose up -d --build

# --- 6. status ------------------------------------------------------------
info "Current container status:"
docker compose ps

ok "Done. Follow the API logs with:  docker compose logs -f api"
ok "Then open the panel and log in with ADMIN_USERNAME / ADMIN_PASSWORD from backend/.env."
