FROM ghcr.io/astral-sh/uv:alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app"

WORKDIR /app

# Install system dependencies (Rust, build tools, headers)
RUN apk add --no-cache \
    build-base \
    rust \
    cargo \
    python3-dev \
    linux-headers

# Copy and install Python deps
COPY pyproject.toml uv.lock ./
RUN uv sync

# Copy your source code
COPY . .

EXPOSE 7860

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
