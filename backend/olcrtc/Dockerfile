FROM golang:1.26 AS builder

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

RUN go install github.com/magefile/mage@latest
ENV PATH="/go/bin:${PATH}"

WORKDIR /build

RUN git clone --depth=1 https://github.com/openlibrecommunity/olcrtc.git olcrtc

WORKDIR /build/olcrtc

RUN mage build


WORKDIR /build/proxy

COPY proxy.go go.mod go.sum ./

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build \
    -trimpath \
    -ldflags="-s -w" \
    -o /proxy \
    proxy.go


# =======================================================
# Runtime
# =======================================================

FROM alpine:3.20

RUN apk add --no-cache \
    ca-certificates \
    bash

WORKDIR /app

COPY --from=builder /build/olcrtc/build/olcrtc-linux-amd64 ./olcrtc
COPY --from=builder /proxy ./proxy

COPY entrypoint.sh .

RUN chmod +x \
    /app/olcrtc \
    /app/proxy \
    /app/entrypoint.sh

RUN mkdir -p \
    /var/lib/olcwave \
    /tmp/olcwave

ENV PROXY_BIND_ADDR=127.0.0.1
ENV PROXY_PORT=1080
ENV STATS_FILE=/var/lib/olcwave/stats.json

ENTRYPOINT ["/app/entrypoint.sh"]