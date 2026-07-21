FROM golang:1.26 AS builder

RUN apt-get update && apt-get install -y git

RUN go install github.com/magefile/mage@latest
ENV PATH="/go/bin:${PATH}"

WORKDIR /src

RUN git clone --depth=1 https://github.com/openlibrecommunity/olcrtc.git .

RUN mage build


FROM alpine:3.20

RUN apk add --no-cache ca-certificates

WORKDIR /app

COPY --from=builder /src/build/olcrtc-linux-amd64 ./olcrtc

ENTRYPOINT ["sh", "-c", "echo \"$CONFIG\" > /app/config.yaml && exec ./olcrtc /app/config.yaml"]