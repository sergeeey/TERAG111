# TERAG Local Installer - Simple Version
# Minimal, guaranteed working setup script

param(
    [string]$InstallPath = "E:\TERAG"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TERAG Local Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
Write-Host "[1/6] Checking Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    docker compose version | Out-Null
    Write-Host "  OK Docker found" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Docker not found!" -ForegroundColor Red
    Write-Host "  Install Docker Desktop first" -ForegroundColor Yellow
    exit 1
}

# Step 2: Create directories
Write-Host "[2/6] Creating directories..." -ForegroundColor Yellow
$dirs = @(
    "$InstallPath",
    "$InstallPath\app",
    "$InstallPath\app\modules",
    "$InstallPath\data",
    "$InstallPath\data\neo4j\data",
    "$InstallPath\data\neo4j\logs",
    "$InstallPath\data\neo4j\import",
    "$InstallPath\data\neo4j\plugins",
    "$InstallPath\data\cache",
    "$InstallPath\data\logs",
    "$InstallPath\data\prometheus",
    "$InstallPath\data\grafana",
    "$InstallPath\prometheus",
    "$InstallPath\grafana\provisioning\datasources",
    "$InstallPath\grafana\dashboards"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

# Step 3: Get installer directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path $scriptPath)) {
    Write-Host "  ERROR: Installer directory not found" -ForegroundColor Red
    exit 1
}

# Step 4: Copy files
Write-Host "[3/6] Copying files..." -ForegroundColor Yellow
Copy-Item "$scriptPath\docker-compose.yml" "$InstallPath\docker-compose.yml" -Force
Copy-Item "$scriptPath\config.env" "$InstallPath\config.env" -Force

if (Test-Path "$scriptPath\app") {
    Copy-Item "$scriptPath\app\*" "$InstallPath\app\" -Recurse -Force
    Write-Host "  OK App files copied" -ForegroundColor Green
}

if (Test-Path "$scriptPath\prometheus") {
    Copy-Item "$scriptPath\prometheus\*" "$InstallPath\prometheus\" -Recurse -Force
}

if (Test-Path "$scriptPath\grafana") {
    Copy-Item "$scriptPath\grafana\*" "$InstallPath\grafana\" -Recurse -Force
}

# Step 5: Update config.env
Write-Host "[4/6] Updating configuration..." -ForegroundColor Yellow
$configFile = "$InstallPath\config.env"
$config = Get-Content $configFile -Raw
$config = $config -replace "DATA_PATH=E:\\TERAG\\data", "DATA_PATH=$InstallPath\data"
[System.IO.File]::WriteAllText($configFile, $config, [System.Text.Encoding]::UTF8)
Write-Host "  OK Configuration updated" -ForegroundColor Green

# Step 6: Start Docker
Write-Host "[5/6] Starting Docker containers..." -ForegroundColor Yellow
Set-Location $InstallPath
docker compose --env-file config.env up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Containers started" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Failed to start containers" -ForegroundColor Red
    exit 1
}

# Success message
Write-Host ""
Write-Host "[6/6] Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Services are starting. Wait 30-60 seconds." -ForegroundColor Yellow
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  TERAG API:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Grafana:     http://localhost:3000" -ForegroundColor White
Write-Host "  Prometheus:  http://localhost:9090" -ForegroundColor White
Write-Host "  Neo4j:       http://localhost:7474" -ForegroundColor White
Write-Host ""
Write-Host "Grafana: admin / terag_admin" -ForegroundColor Gray
Write-Host "Neo4j:   neo4j / terag_local" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop:  cd $InstallPath; docker compose down" -ForegroundColor Gray
Write-Host "To logs:   cd $InstallPath; docker compose logs -f" -ForegroundColor Gray
Write-Host ""

