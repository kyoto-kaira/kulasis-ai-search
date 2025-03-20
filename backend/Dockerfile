# VARIABLES
ARG PYTHON_VERSION=3.11-slim
ARG APP_DIR=app/backend

FROM python:3.11-slim

WORKDIR /${APP_DIR}

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
