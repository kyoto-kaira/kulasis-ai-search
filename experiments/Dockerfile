FROM python:3.11-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.5.5 /uv /uvx /bin/

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN uv pip install -r requirements.txt --system

ENV PYTHONPATH=/app/src:/app
