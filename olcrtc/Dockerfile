FROM golang:1.26-alpine AS builder

WORKDIR /build

RUN apk add --no-cache git

RUN git clone --depth 1 --recurse-submodules https://github.com/openlibrecommunity/olcrtc.git .

RUN go mod download && go build -o olcrtc ./cmd/olcrtc


FROM alpine:latest

RUN apk add --no-cache ca-certificates net-tools

WORKDIR /app

COPY --from=builder /build/olcrtc /app/olcrtc
RUN chmod +x /app/olcrtc

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]