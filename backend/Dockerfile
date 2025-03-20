FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app/backend

COPY requirements.txt .

RUN uv pip install --no-cache-dir -r requirements.txt --system

COPY . .
