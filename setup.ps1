$ErrorActionPreference = "Stop"

Write-Host "Setting up Python environment..."

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host "Regenerating protobuf files..."
& ".\.venv\Scripts\python.exe" -m grpc_tools.protoc `
    -I src `
    --python_out=src `
    src/smart_home/proto/v1/message.proto

Write-Host "Running tests..."
& ".\.venv\Scripts\python.exe" -m pytest

Write-Host "Checking Docker..."
while ($true) {
    docker info *> $null
    if ($LASTEXITCODE -eq 0) {
        break
    }

    Write-Host "Docker is not running or is not reachable."
    Write-Host "Start Docker Desktop or the Docker daemon, then keep this terminal open."
    Write-Host "Retrying in 5 seconds..."
    Start-Sleep -Seconds 5
}

Write-Host "Docker is available."

Write-Host "Building Docker image..."
docker compose build

Write-Host "Starting server container..."
docker compose up -d server

Write-Host "Opening Docker client."
Write-Host "Type 'exit' or 'quit' to close the client."

docker compose run --rm client

Write-Host "Stopping Docker services..."
docker compose down

Write-Host "Setup and Docker completed."
