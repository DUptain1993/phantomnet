Param(
  [string]$Domain = "localhost",
  [int]$Port = 8443
)

function Write-Info    { Write-Host "[INFO] $($args[0])" -ForegroundColor Green }
function Write-Warn    { Write-Host "[WARN] $($args[0])" -ForegroundColor Yellow }
function Write-ErrorEx { Write-Host "[ERROR] $($args[0])" -ForegroundColor Red }

# Prerequisite checks
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-ErrorEx "Docker Desktop is not installed."
  exit 1
}

# Compose plugin check
if (-not ((docker compose version) 2>$null)) {
  Write-ErrorEx "Docker Compose v2 plugin missing."
  exit 1
}

# Generate files (Dockerfile, compose, nginx.conf, .env) – exactly the
# same content as the bash script but with PowerShell heredocs (shown
# abbreviated here to save space) …

Write-Info "Writing Dockerfile / docker-compose.yml / nginx.conf"

@"
FROM python:3.11-slim
# ... identical to Linux Dockerfile ...
"@ | Out-File Dockerfile -Encoding utf8

@"
services:
  phantomnet:
    build: .
    container_name: phantomnet-app
    ports:
      - "$Port:8443"
# ...
"@ | Out-File docker-compose.yml -Encoding utf8

# .env, nginx.conf, backup.ps1, monitor.ps1 follow exactly the same
# patterns as the bash version.

Write-Info "Building & starting containers…"
docker compose up --build -d
Write-Info "Stack is running →  https://$Domain/  (port $Port)"
