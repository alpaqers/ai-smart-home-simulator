#!/usr/bin/env bash
set -euo pipefail

echo "Setting up Python environment..."

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "Regenerating protobuf files..."
.venv/bin/python -m grpc_tools.protoc \
  -I src \
  --python_out=src \
  src/smart_home/proto/v1/message.proto

echo "Running tests..."
.venv/bin/python -m pytest

echo "Checking Docker..."
until docker info >/dev/null 2>&1; do
  echo "Docker is not running or is not reachable."
  echo "Start Docker Desktop or the Docker daemon, then keep this terminal open."
  echo "Retrying in 5 seconds..."
  sleep 5
done

echo "Docker is available."

echo "Building Docker image..."
docker compose build

echo "Starting server container..."
docker compose up -d server

echo "Opening Docker client."
echo "Type 'exit' or 'quit' to close the client."

docker compose run --rm client

echo "Stopping Docker services..."
docker compose down

echo "Setup and Docker completed."
