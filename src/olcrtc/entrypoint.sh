#!/bin/sh

echo "=== OlcRTC Container Starting ===" >&2
echo "SOCKS_PORT: $SOCKS_PORT" >&2
echo "RX_LIMIT: $RX_LIMIT" >&2
echo "TX_LIMIT: $TX_LIMIT" >&2

# Start SOCKS5 proxy if enabled (for srv mode)
if [ ! -z "$SOCKS_PORT" ]; then
    echo "Starting SOCKS5 proxy on port $SOCKS_PORT..." >&2

    STATS_FILE="/tmp/socks.stats"
    RX_LIMIT="${RX_LIMIT:-0}"
    TX_LIMIT="${TX_LIMIT:-0}"

    # Start proxy and capture output
    /app/socks5proxy -port "$SOCKS_PORT" -stats "$STATS_FILE" -rx-limit "$RX_LIMIT" -tx-limit "$TX_LIMIT" 2>&1 &
    PROXY_PID=$!
    echo "SOCKS5 proxy PID: $PROXY_PID" >&2

    # Wait for proxy to start and verify it's listening
    for i in 1 2 3 4 5; do
        sleep 1
        if netstat -tuln 2>/dev/null | grep -q ":$SOCKS_PORT " || ss -tuln 2>/dev/null | grep -q ":$SOCKS_PORT "; then
            echo "SOCKS5 proxy started successfully on port $SOCKS_PORT" >&2
            break
        fi
        echo "Waiting for SOCKS5 proxy to start... ($i/5)" >&2
        if [ $i -eq 5 ]; then
            echo "ERROR: SOCKS5 proxy did not start!" >&2
            echo "Checking if process is running:" >&2
            ps aux | grep socks5proxy >&2
        fi
    done
else
    echo "SOCKS_PORT not set, skipping SOCKS5 proxy" >&2
fi

echo "Starting OlcRTC..." >&2
# Start olcrtc with all arguments
exec /app/olcrtc "$@"
