# TERAG Fix Configuration and Restart
# Исправляет config.env и перезапускает контейнеры

param([string]$InstallPath = "E:\TERAG")

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TERAG Fix & Restart" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if install path exists
if (-not (Test-Path $InstallPath)) {
    Write-Host "  ERROR: Installation path not found: $InstallPath" -ForegroundColor Red
    Write-Host "  Run setup_terag.ps1 first!" -ForegroundColor Yellow
    exit 1
}

# Step 2: Validate and fix config.env
Write-Host "[1/4] Validating config.env..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$validateScript = "$scriptDir\validate_config.ps1"
if (Test-Path $validateScript) {
    & $validateScript -InstallPath $InstallPath -FixMissing | Out-Null
    Write-Host "  ✅ Config validated" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  validate_config.ps1 not found, using manual config update" -ForegroundColor Yellow
    
    # Fallback to manual update
    Write-Host "[1/4] Creating/Updating config.env..." -ForegroundColor Yellow
    $configPath = "$InstallPath\config.env"
    $dataPath = "$InstallPath\data"

$configContent = @"
# TERAG Local Environment Configuration
# Auto-generated configuration file

# Data Path
DATA_PATH=$dataPath

# Neo4j Configuration
NEO4J_URI=bolt://terag-neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=terag_local

# Prometheus Configuration
PROMETHEUS_PORT=9090

# Grafana Configuration
GRAFANA_PORT=3000

# FastAPI Configuration
FASTAPI_PORT=8000

# LLM Integration (optional)
# Supported providers: ollama, lm_studio, openai
LLM_PROVIDER=ollama
LLM_URL=http://host.docker.internal:11434
LLM_MODEL=llama3

# For LM Studio, use:
# LLM_PROVIDER=lm_studio
# LLM_URL=http://host.docker.internal:1234
# LLM_MODEL=local-model
"@

    # Write config file
    [System.IO.File]::WriteAllText($configPath, $configContent, [System.Text.Encoding]::UTF8)
    Write-Host "  OK config.env created/updated at: $configPath" -ForegroundColor Green
}

# Step 3: Stop existing containers
Write-Host "[2/4] Stopping existing containers..." -ForegroundColor Yellow
Set-Location $InstallPath
docker compose --env-file config.env down 2>&1 | Out-Null
Start-Sleep -Seconds 2
Write-Host "  OK Containers stopped" -ForegroundColor Green

# Step 4: Start containers with fixed config
Write-Host "[3/4] Starting containers with fixed configuration..." -ForegroundColor Yellow
docker compose --env-file config.env up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to start containers" -ForegroundColor Red
    Write-Host "  Check logs: docker compose logs" -ForegroundColor Yellow
    exit 1
}
Write-Host "  OK Containers started" -ForegroundColor Green

# Success
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TERAG Restarted Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Waiting 30 seconds for services to stabilize..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "Checking container status..." -ForegroundColor Cyan
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "terag-"

Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  TERAG API:   http://localhost:8000/health" -ForegroundColor White
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Grafana:     http://localhost:3000" -ForegroundColor White
Write-Host "  Prometheus:  http://localhost:9090" -ForegroundColor White
Write-Host "  Neo4j:       http://localhost:7474" -ForegroundColor White
Write-Host ""
Write-Host "Credentials:" -ForegroundColor Cyan
Write-Host "  Grafana: admin / terag_admin" -ForegroundColor Gray
Write-Host "  Neo4j:   neo4j / terag_local" -ForegroundColor Gray
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  docker ps                    - Check status" -ForegroundColor Gray
Write-Host "  docker compose logs -f       - View logs" -ForegroundColor Gray
Write-Host "  docker compose logs terag-neo4j - View Neo4j logs" -ForegroundColor Gray
Write-Host ""

