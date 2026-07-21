#!/bin/sh
set -eu

: "${CONFIG:?CONFIG env is required}"
: "${PROXY_PORT:=1080}"
: "${PROXY_BIND_ADDR:=127.0.0.1}"
: "${STATS_FILE:=/var/lib/olcwave/stats.json}"

mkdir -p /var/lib/olcwave /tmp/olcwave

printf '%s\n' "$CONFIG" > /tmp/olcwave/config.yaml

cat >> /tmp/olcwave/config.yaml <<EOF

socks:
  proxy_addr: "localhost"
  proxy_port: ${PROXY_PORT}
EOF

export LISTEN_ADDR="${PROXY_BIND_ADDR}:${PROXY_PORT}"
export STATS_FILE

if [ -n "${UPSTREAM_SOCKS_ADDR:-}" ]; then
  export UPSTREAM_SOCKS_ADDR
fi
if [ -n "${UPSTREAM_SOCKS_HOST:-}" ]; then
  export UPSTREAM_SOCKS_HOST
fi
if [ -n "${UPSTREAM_SOCKS_PORT:-}" ]; then
  export UPSTREAM_SOCKS_PORT
fi

/app/proxy &
proxy_pid=$!

cleanup() {
  kill "$proxy_pid" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

/app/olcrtc /tmp/olcwave/config.yaml &
olcrtc_pid=$!

wait "$olcrtc_pid"
status=$?

cleanup
wait "$proxy_pid" 2>/dev/null || true

exit "$status"