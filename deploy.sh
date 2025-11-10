#!/usr/bin/env bash
set -euo pipefail

# Script to SSH into another server and deploy

# 1. Build the Docker image
# 2. tag the image with the latest version
# 3. Push the Docker image to the registry docker.io/ethannjw/ktmb-scraper
# 4. SSH into the server
# 5. Pull and run  the Docker image using docker compose up -d --pull always

# read the .env file
source .env

# Configuration (override via env vars)
REGISTRY_HOST=${REGISTRY_HOST:-docker.io/ethannjw}
IMAGE_NAME=${IMAGE_NAME:-ktmb-scraper}
IMAGE="${REGISTRY_HOST}/${IMAGE_NAME}"

# Remote deployment config
SSH_USER=${SSH_USER}
SSH_HOST=${SSH_HOST}
SSH_PORT=${SSH_PORT:-22}
REMOTE_DIR=${REMOTE_DIR:-/opt/ktmb-scraper/compose}
COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.yml}
ENV_FILE_LOCAL=${ENV_FILE_LOCAL:-.env}
ENV_FILE_REMOTE=${ENV_FILE_REMOTE:-.env}
REMOTE_COMPOSE_PATH="${REMOTE_DIR}/${COMPOSE_FILE}"

# Determine a version tag (defaults to git short SHA or "local")
GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "local")
TAG=${TAG:-${GIT_SHA}}
LATEST_TAG=${LATEST_TAG:-latest}

echo "Using image: ${IMAGE}"
echo "Version tag: ${TAG}"
echo "Latest tag: ${LATEST_TAG}"

# Optional registry login if credentials provided
if [[ -n "${DOCKER_USERNAME:-}" && -n "${DOCKER_PASSWORD:-}" ]]; then
  echo "Logging into registry ${REGISTRY_HOST}..."
  echo "${DOCKER_PASSWORD}" | docker login "${REGISTRY_HOST}" --username "${DOCKER_USERNAME}" --password-stdin
fi

echo "[1/3] Building Docker image ${IMAGE}:${TAG}..."
docker build -t "${IMAGE}:${TAG}" .

echo "[2/3] Tagging image as ${IMAGE}:${LATEST_TAG}..."
docker tag "${IMAGE}:${TAG}" "${IMAGE}:${LATEST_TAG}"

echo "[3/3] Pushing images to ${REGISTRY_HOST}..."
# docker push "${IMAGE}:${TAG}"
docker push "${IMAGE}:${LATEST_TAG}"

echo "✅ Done. Pushed: ${IMAGE}:${TAG} and ${IMAGE}:${LATEST_TAG}"

echo "[4/5] Syncing compose and env files to ${SSH_USER}@${SSH_HOST}:${REMOTE_DIR}..."
ssh -p "${SSH_PORT}" "${SSH_USER}@${SSH_HOST}" "mkdir -p '${REMOTE_DIR}'"
scp -P "${SSH_PORT}" "${COMPOSE_FILE}" "${SSH_USER}@${SSH_HOST}":"${REMOTE_COMPOSE_PATH}"
if [[ -f "${ENV_FILE_LOCAL}" ]]; then
  echo "Uploading env file ${ENV_FILE_LOCAL} -> ${ENV_FILE_REMOTE}"
  scp -P "${SSH_PORT}" "${ENV_FILE_LOCAL}" "${SSH_USER}@${SSH_HOST}":"${REMOTE_DIR}/${ENV_FILE_REMOTE}"
else
  echo "No local env file at ${ENV_FILE_LOCAL}; skipping upload."
fi

echo "[5/5] Deploying on remote host with docker compose..."
ssh -p "${SSH_PORT}" "${SSH_USER}@${SSH_HOST}" \
  "cd '${REMOTE_DIR}' && docker compose -f '${REMOTE_COMPOSE_PATH}' pull && docker compose -f '${REMOTE_COMPOSE_PATH}' up -d --remove-orphans"

echo "Cleaning up unused Docker images on remote host..."
ssh -p "${SSH_PORT}" "${SSH_USER}@${SSH_HOST}" "docker image prune -af"

echo "✅ Deployment triggered on ${SSH_USER}@${SSH_HOST}."
