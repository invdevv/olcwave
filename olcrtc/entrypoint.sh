#!/bin/sh

echo "=== OlcRTC Container Ready ===" >&2

if [ "$1" = "olcrtc" ]; then
    shift
    exec /app/olcrtc "$@"
fi

echo "No command provided. Container is idle." >&2
tail -f /dev/null