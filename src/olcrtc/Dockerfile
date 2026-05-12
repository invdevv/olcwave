FROM golang:1.26-alpine AS builder

WORKDIR /build

RUN apk add --no-cache git

RUN git clone --depth 1 --recurse-submodules https://github.com/openlibrecommunity/olcrtc.git .

RUN go mod download && go build -o olcrtc ./cmd/olcrtc

# Build SOCKS5 proxy
WORKDIR /socks5proxy
COPY socks5proxy/ .
RUN go mod download
RUN go build -o socks5proxy .

FROM alpine:latest

RUN apk add --no-cache ca-certificates net-tools

WORKDIR /app

COPY --from=builder /build/olcrtc /app/olcrtc
COPY --from=builder /socks5proxy/socks5proxy /app/socks5proxy

RUN chmod +x /app/olcrtc /app/socks5proxy

# Create entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
