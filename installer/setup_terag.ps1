# TERAG Local Installer for Windows
param([string]$InstallPath = "E:\TERAG", [switch]$SkipDockerCheck = $false)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TERAG Local Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
if (-not $SkipDockerCheck) {
    Write-Host "[1/6] Checking Docker..." -ForegroundColor Yellow
    docker --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Docker not found!" -ForegroundColor Red
        Write-Host "  Install Docker Desktop first" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "  OK Docker found" -ForegroundColor Green
}

# Step 2: Create directories
Write-Host "[2/6] Creating directories..." -ForegroundColor Yellow
$dirs = @("$InstallPath", "$InstallPath\app", "$InstallPath\app\modules", "$InstallPath\data", "$InstallPath\data\neo4j\data", "$InstallPath\data\neo4j\logs", "$InstallPath\data\neo4j\import", "$InstallPath\data\neo4j\plugins", "$InstallPath\data\cache", "$InstallPath\data\logs", "$InstallPath\data\prometheus", "$InstallPath\data\grafana", "$InstallPath\prometheus", "$InstallPath\grafana\provisioning\datasources", "$InstallPath\grafana\dashboards")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

# Step 3: Get installer directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path $scriptDir)) {
    Write-Host "  ERROR: Installer directory not found" -ForegroundColor Red
    exit 1
}

# Step 4: Copy files
Write-Host "[3/6] Copying files..." -ForegroundColor Yellow
Copy-Item "$scriptDir\docker-compose.yml" "$InstallPath\docker-compose.yml" -Force
Copy-Item "$scriptDir\config.env" "$InstallPath\config.env" -Force
if (Test-Path "$scriptDir\app") {
    Copy-Item "$scriptDir\app\*" "$InstallPath\app\" -Recurse -Force
    Write-Host "  OK App files copied" -ForegroundColor Green
}
if (Test-Path "$scriptDir\prometheus") {
    Copy-Item "$scriptDir\prometheus\*" "$InstallPath\prometheus\" -Recurse -Force
}
if (Test-Path "$scriptDir\grafana") {
    Copy-Item "$scriptDir\grafana\*" "$InstallPath\grafana\" -Recurse -Force
}

# Step 5: Update config.env
Write-Host "[4/6] Updating configuration..." -ForegroundColor Yellow
$configPath = "$InstallPath\config.env"
$configContent = Get-Content $configPath -Raw
$configContent = $configContent -replace "DATA_PATH=E:\\TERAG\\data", "DATA_PATH=$InstallPath\data"
[System.IO.File]::WriteAllText($configPath, $configContent, [System.Text.Encoding]::UTF8)
Write-Host "  OK Configuration updated" -ForegroundColor Green

# Step 6: Load environment variables
Write-Host "[5/6] Loading environment variables..." -ForegroundColor Yellow
Get-Content $configPath | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

# Step 7: Start Docker
Write-Host "[6/6] Starting Docker containers..." -ForegroundColor Yellow
Set-Location $InstallPath
docker compose --env-file config.env up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to start containers" -ForegroundColor Red
    exit 1
}
Write-Host "  OK Containers started" -ForegroundColor Green

# Success
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TERAG Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services starting. Wait 30-60 seconds." -ForegroundColor Yellow
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
