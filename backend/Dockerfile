FROM python:3.12-alpine

RUN apk add --no-cache \
    docker-cli \
    gcc \
    musl-dev \
    libffi-dev \
    curl

# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY backend/.env backend/.
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "python", "backend/main.py"]