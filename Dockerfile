FROM python:3.12-alpine

# system deps
RUN apk add --no-cache \
    ca-certificates \
    net-tools \
    bash

# install uv
RUN apk add --no-cache curl gcc musl-dev libffi-dev
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# backend deps
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "python", "src/main.py"]