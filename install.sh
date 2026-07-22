#!/usr/bin/env bash
#
# install.sh - interactive installer for OLCWave.
#
# Asks you a handful of questions, then generates backend/.env
# (for Docker Compose) and frontend/.env for you, builds the frontend, and
# brings the Docker Compose stack up. No manual file editing required.
#
# Usage:
#   chmod +x install.sh
#   ./install.sh

set -euo pipefail

# Always operate from the repo root (the directory this script lives in).
cd "$(dirname "$0")"

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
if [ -t 1 ]; then
  C_RESET=$'\033[0m'; C_BLUE=$'\033[0;34m'; C_GREEN=$'\033[0;32m'
  C_YELLOW=$'\033[0;33m'; C_RED=$'\033[0;31m'; C_BOLD=$'\033[1m'
else
  C_RESET=''; C_BLUE=''; C_GREEN=''; C_YELLOW=''; C_RED=''; C_BOLD=''
fi

info()    { printf '%s[*]%s %s\n' "$C_BLUE"   "$C_RESET" "$1"; }
warn()    { printf '%s[!]%s %s\n' "$C_YELLOW" "$C_RESET" "$1"; }
success() { printf '%s[+]%s %s\n' "$C_GREEN"  "$C_RESET" "$1"; }
error()   { printf '%s[x]%s %s\n' "$C_RED"    "$C_RESET" "$1" >&2; }

# Fatal error: print and exit.
die() { error "$1"; exit 1; }

# ---------------------------------------------------------------------------
# Input helpers  (all read from /dev/tty so the script also works when piped)
# ---------------------------------------------------------------------------

# ask VAR "Prompt" ["default"]
# Reads a line into VAR. Falls back to the default when the input is empty.
ask() {
  local __var="$1" __msg="$2" __def="${3:-}" __in
  if [ -n "$__def" ]; then
    printf '%s%s%s [%s]: ' "$C_BOLD" "$__msg" "$C_RESET" "$__def" > /dev/tty
  else
    printf '%s%s%s: ' "$C_BOLD" "$__msg" "$C_RESET" > /dev/tty
  fi
  read -r __in < /dev/tty || true
  printf -v "$__var" '%s' "${__in:-$__def}"
}

# ask_required VAR "Prompt" - like ask, but keeps asking until non-empty.
ask_required() {
  local __var="$1" __msg="$2"
  while :; do
    ask "$__var" "$__msg"
    [ -n "${!__var}" ] && break
    warn "This value is required."
  done
}

# ask_secret VAR "Prompt" - hidden input, keeps asking until non-empty.
ask_secret() {
  local __var="$1" __msg="$2" __in
  while :; do
    printf '%s%s%s: ' "$C_BOLD" "$__msg" "$C_RESET" > /dev/tty
    read -rs __in < /dev/tty || true
    printf '\n' > /dev/tty
    if [ -n "$__in" ]; then
      printf -v "$__var" '%s' "$__in"
      break
    fi
    warn "This value is required."
  done
}

# confirm "Question" - returns 0 for yes (default), 1 for no.
confirm() {
  local __ans
  printf '%s%s%s [Y/n]: ' "$C_BOLD" "$1" "$C_RESET" > /dev/tty
  read -r __ans < /dev/tty || true
  case "$__ans" in
    [nN] | [nN][oO]) return 1 ;;
    *) return 0 ;;
  esac
}

# Generate a cryptographically random hex secret (32 bytes → 64 hex chars).
generate_secret() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32
  elif [ -r /dev/urandom ]; then
    head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n'
  else
    python3 -c 'import secrets; print(secrets.token_hex(32))'
  fi
}

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    die "Please run this script as root."
  fi
}

install_base_packages() {
    info "Installing base packages..."

    apt-get update
    apt-get install -y curl ca-certificates openssl git

    success "Base packages installed."
}

# ---------------------------------------------------------------------------
# 1. Dependency checks and installs
# ---------------------------------------------------------------------------
install_docker() {
  info "Installing Docker..."

  if command -v docker >/dev/null 2>&1; then
    success "Docker already installed."
    return
  fi

  info "Downloading Docker installer..."

  curl -fsSL https://get.docker.com | sh

  systemctl enable --now docker

  success "Docker installed."
}


install_nodejs() {
  info "Installing Node.js..."

  if command -v npm >/dev/null 2>&1; then
    success "npm already installed."
    return
  fi

  info "Installing Node.js 20..."

  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -

  apt-get install -y nodejs

  success "Node.js installed."
}


check_dependencies() {
  info "Checking prerequisites..."

  if ! command -v docker >/dev/null 2>&1; then
    install_docker
  fi

  if ! docker compose version >/dev/null 2>&1; then
    die "'docker compose' is not available after Docker installation."
  fi

  if ! command -v npm >/dev/null 2>&1; then
    install_nodejs
  fi

  success "docker, docker compose and npm are present."

  docker --version
  docker compose version
  node --version
  npm --version
}

# ---------------------------------------------------------------------------
# 2. Collect configuration from the user
# ---------------------------------------------------------------------------
collect_input() {
  info "Configuration - answer the prompts below. Defaults are shown in [brackets]."
  printf '\n' > /dev/tty

  ask          SUB_NAME  "Subscription name"            "OLCWave"
  ask_required RW_API_URL    "Remnawave URL (e.g. https://rw.example.com)"
  ask_secret   RW_API_TOKEN  "Remnawave API token (hidden)"

  ask          ADMIN_USERNAME "Admin username"          "admin"

  JWT_SECRET_KEY="$(generate_secret)"
  ADMIN_PASSWORD="$(generate_secret)"

  # Traffic limit is asked in GB and converted to bytes. 0 = unlimited.
  while :; do
    ask TRAFFIC_GB "Default traffic limit in GB (0 = unlimited)" "100"
    case "$TRAFFIC_GB" in
      *[!0-9]* | '') warn "Enter a whole number of gigabytes (e.g. 100)." ;;
      *) break ;;
    esac
  done
  DEFAULT_TRAFFIC_LIMIT=$(( TRAFFIC_GB * 1024 * 1024 * 1024 ))

  ask TRAFFIC_COLLECT_INTERVAL "Traffic collection interval (seconds)" "10"

  # Panel URL drives the frontend. Caddy strips /api, so VITE_API_URL = <panel>/api.
  ask_required PANEL_URL "OLCWave Panel URL (e.g. https://panel.example.com)"
  PANEL_URL="${PANEL_URL%/}"                       # drop trailing slash
  VITE_API_URL="${PANEL_URL}/api"

  # Subscription template shown/copied in the UI. {uuid} is substituted per user.
  info "Subscription URL template - {uuid} is replaced with each user's short UUID."
  info "  examples: https://sub.example.com/{uuid}   or   ${PANEL_URL}/sub/{uuid}"
  ask SUB_URL_TEMPLATE "Subscription URL template" "${PANEL_URL}/sub/{uuid}"

  # Postgres credentials are generated, not asked. They are written identically
  POSTGRES_USER="olcwave"
  POSTGRES_DB="main"
  POSTGRES_PASSWORD="$(generate_secret)"
}

# ---------------------------------------------------------------------------
# 3. Generate env files
# ---------------------------------------------------------------------------

# Warn + confirm before clobbering an existing file. Returns 1 to skip.
may_overwrite() {
  local target="$1"
  [ -f "$target" ] || return 0
  confirm "$target already exists. Overwrite it?" || { warn "Kept existing $target."; return 1; }
  return 0
}

write_backend_env() {
  may_overwrite "backend/.env" || return 0
  # printf '%s' keeps values verbatim (safe for passwords with special chars).
  {
    printf 'NAME=%s\n\n'                     "$SUB_NAME"
    printf 'RW_API_URL=%s\n'                 "$RW_API_URL"
    printf 'RW_API_TOKEN=%s\n\n'             "$RW_API_TOKEN"
    printf 'DB_HOST=postgres\n'
    printf 'DB_PORT=5432\n'
    printf 'POSTGRES_USER=%s\n'              "$POSTGRES_USER"
    printf 'POSTGRES_PASSWORD=%s\n'          "$POSTGRES_PASSWORD"
    printf 'POSTGRES_DB=%s\n\n'              "$POSTGRES_DB"
    printf 'ADMIN_USERNAME=%s\n'             "$ADMIN_USERNAME"
    printf 'ADMIN_PASSWORD=%s\n\n'           "$ADMIN_PASSWORD"
    printf 'JWT_SECRET_KEY=%s\n'             "$JWT_SECRET_KEY"
    printf 'JWT_EXPIRE_MINUTES=1440\n\n'
    printf '# %s GB in bytes (0 = unlimited)\n' "$TRAFFIC_GB"
    printf 'DEFAULT_TRAFFIC_LIMIT=%s\n'      "$DEFAULT_TRAFFIC_LIMIT"
    printf 'TRAFFIC_COLLECT_INTERVAL=%s\n'   "$TRAFFIC_COLLECT_INTERVAL"
  } > backend/.env
  success "Wrote backend/.env"
}

write_frontend_env() {
  may_overwrite "frontend/.env" || return 0
  {
    printf 'VITE_API_URL=%s\n'          "$VITE_API_URL"
    printf 'VITE_SUB_URL_TEMPLATE=%s\n' "$SUB_URL_TEMPLATE"
  } > frontend/.env
  success "Wrote frontend/.env"
}

# ---------------------------------------------------------------------------
# 4. Build the frontend  (Caddy serves frontend/dist)
# ---------------------------------------------------------------------------
build_frontend() {
  info "Building the frontend..."
  (
    cd frontend
    if [ -d node_modules ]; then
      info "node_modules present - skipping dependency install."
    else
      info "Installing dependencies (npm ci)..."
      if [ -f package-lock.json ]; then
        npm ci
      else
        npm install
      fi
    fi
    npm run build
  )
  success "Frontend built into frontend/dist."
}

# ---------------------------------------------------------------------------
# 5. Start the Docker Compose stack
# ---------------------------------------------------------------------------
start_stack() {
  info "Building images and starting the stack (docker compose up -d --build)..."
  docker compose up -d --build
}

# ---------------------------------------------------------------------------
# 6. Verify the API container came up
# ---------------------------------------------------------------------------
verify_stack() {
  info "Waiting for the API container to start..."
  local running="" i
  # The API waits for Postgres to become healthy, so give it a little time.
  for i in $(seq 1 20); do
    running="$(docker inspect -f '{{.State.Running}}' olcwave-api 2>/dev/null || echo false)"
    [ "$running" = "true" ] && break
    sleep 3
  done

  if [ "$running" != "true" ]; then
    error "The API container (olcwave-api) is not running."
    error "Inspect the logs with:  docker compose logs api"
    docker compose ps || true
    exit 1
  fi

  success "API container is running."
  docker compose ps
}

# ---------------------------------------------------------------------------
# 7. Final summary
# ---------------------------------------------------------------------------
print_summary() {
  local line="========================================"
  printf '\n%s%s%s\n\n' "$C_GREEN" "$line" "$C_RESET"
  printf '  %s%s installed successfully%s\n\n' "$C_BOLD" "$SUB_NAME" "$C_RESET"
  printf '  Panel\n    %s\n\n'                 "$PANEL_URL"
  printf '  Admin username\n    %s\n\n'        "$ADMIN_USERNAME"
  printf '  Subscription template\n    %s\n\n' "$SUB_URL_TEMPLATE"
  printf '  Containers\n    docker compose ps\n\n'
  printf '  API logs\n    docker compose logs -f api\n\n'
  printf '%s%s%s\n\n' "$C_GREEN" "$line" "$C_RESET"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  require_root
  install_base_packages
  check_dependencies
  collect_input
  write_backend_env
  write_frontend_env
  build_frontend
  start_stack
  verify_stack
  print_summary
}

main "$@"
