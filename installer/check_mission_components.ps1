# TERAG Mission Components Check
# Проверка всех компонентов перед запуском миссии

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TERAG Mission Components Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allOk = $true

# 1. Проверка Brave API Key
Write-Host "[1/5] Checking Brave API Key..." -ForegroundColor Yellow
$braveKey = $env:BRAVE_API_KEY
if ($braveKey) {
    Write-Host "  [OK] BRAVE_API_KEY is set" -ForegroundColor Green
    Write-Host "  [INFO] Key length: $($braveKey.Length) characters" -ForegroundColor Gray
    
    # Опциональная проверка доступности API
    try {
        $testUrl = "https://api.search.brave.com/res/v1/web/search?q=test&count=1"
        $headers = @{
            "Accept" = "application/json"
            "X-Subscription-Token" = $braveKey
        }
        $response = Invoke-WebRequest -Uri $testUrl -Headers $headers -Method Get -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  [OK] Brave API is accessible" -ForegroundColor Green
    } catch {
        Write-Host "  [WARNING] Could not verify Brave API (might be network issue)" -ForegroundColor Yellow
        Write-Host "  [INFO] Error: $($_.Exception.Message)" -ForegroundColor Gray
    }
} else {
    Write-Host "  [ERROR] BRAVE_API_KEY is not set!" -ForegroundColor Red
    Write-Host "  [INFO] Set it with: setx BRAVE_API_KEY `"your-key-here`"" -ForegroundColor Yellow
    Write-Host "  [INFO] Then restart PowerShell" -ForegroundColor Yellow
    $allOk = $false
}
Write-Host ""

# 2. Проверка Python
Write-Host "[2/5] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Python is available: $pythonVersion" -ForegroundColor Green
        
        # Проверка необходимых модулей
        Write-Host "  [INFO] Checking Python modules..." -ForegroundColor Gray
        $modules = @("yaml", "requests", "neo4j")
        foreach ($module in $modules) {
            $check = python -c "import $module; print('OK')" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "    [OK] $module module available" -ForegroundColor Green
            } else {
                Write-Host "    [WARNING] $module module not found" -ForegroundColor Yellow
                Write-Host "    [INFO] Install with: pip install $module" -ForegroundColor Gray
            }
        }
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "  [ERROR] Python is not available!" -ForegroundColor Red
    Write-Host "  [INFO] Install Python from python.org" -ForegroundColor Yellow
    $allOk = $false
}
Write-Host ""

# 3. Проверка Ollama
Write-Host "[3/5] Checking Ollama..." -ForegroundColor Yellow
try {
    $ollamaResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 3 -ErrorAction Stop
    if ($ollamaResponse.models) {
        $modelCount = $ollamaResponse.models.Count
        Write-Host "  [OK] Ollama is running" -ForegroundColor Green
        Write-Host "  [INFO] Available models: $modelCount" -ForegroundColor Gray
        
        # Показать первые 3 модели
        $models = $ollamaResponse.models | Select-Object -First 3
        foreach ($model in $models) {
            Write-Host "    - $($model.name)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  [WARNING] Ollama is running but no models found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] Ollama is not running or not accessible!" -ForegroundColor Red
    Write-Host "  [INFO] Start Ollama with: ollama serve" -ForegroundColor Yellow
    Write-Host "  [INFO] Or check if it's running on port 11434" -ForegroundColor Gray
    $allOk = $false
}
Write-Host ""

# 4. Проверка Neo4j
Write-Host "[4/5] Checking Neo4j..." -ForegroundColor Yellow
try {
    # Проверка через Docker
    $neo4jContainer = docker ps --format "{{.Names}}" | Select-String "neo4j"
    if ($neo4jContainer) {
        Write-Host "  [OK] Neo4j container is running: $neo4jContainer" -ForegroundColor Green
        
        # Проверка подключения
        $neo4jUri = $env:NEO4J_URI
        $neo4jUser = $env:NEO4J_USER
        $neo4jPassword = $env:NEO4J_PASSWORD
        
        if ($neo4jUri -and $neo4jUser -and $neo4jPassword) {
            Write-Host "  [INFO] Neo4j URI: $neo4jUri" -ForegroundColor Gray
            Write-Host "  [INFO] Neo4j User: $neo4jUser" -ForegroundColor Gray
            
            # Попытка подключения через Python
            $testConnection = python -c @"
try:
    from neo4j import GraphDatabase
    uri = '$neo4jUri'
    driver = GraphDatabase.driver(uri, auth=('$neo4jUser', '$neo4jPassword'))
    driver.verify_connectivity()
    print('OK')
    driver.close()
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
"@ 2>&1
            
            if ($LASTEXITCODE -eq 0 -and $testConnection -eq "OK") {
                Write-Host "  [OK] Neo4j connection successful" -ForegroundColor Green
            } else {
                Write-Host "  [WARNING] Could not connect to Neo4j: $testConnection" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  [WARNING] Neo4j credentials not set in environment" -ForegroundColor Yellow
            Write-Host "  [INFO] Check config.env file" -ForegroundColor Gray
        }
    } else {
        Write-Host "  [ERROR] Neo4j container is not running!" -ForegroundColor Red
        Write-Host "  [INFO] Start with: docker compose up -d neo4j" -ForegroundColor Yellow
        $allOk = $false
    }
} catch {
    Write-Host "  [ERROR] Could not check Neo4j: $($_.Exception.Message)" -ForegroundColor Red
    $allOk = $false
}
Write-Host ""

# 5. Проверка конфигурации миссии
Write-Host "[5/5] Checking mission configuration..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$missionConfig = "$scriptDir\data\mission_signals.yaml"

if (Test-Path $missionConfig) {
    Write-Host "  [OK] Mission config found: $missionConfig" -ForegroundColor Green
    
    # Проверка валидности YAML
    try {
        $yamlCheck = python -c @"
import yaml
with open(r'$missionConfig', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    mission_name = config.get('mission', {}).get('name', 'Unknown')
    print(f'OK: {mission_name}')
"@ 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Mission config is valid: $yamlCheck" -ForegroundColor Green
        } else {
            Write-Host "  [WARNING] Mission config validation failed: $yamlCheck" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  [WARNING] Could not validate config: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [ERROR] Mission config not found: $missionConfig" -ForegroundColor Red
    Write-Host "  [INFO] Create mission_signals.yaml in data directory" -ForegroundColor Yellow
    $allOk = $false
}
Write-Host ""

# Итоговый результат
Write-Host "========================================" -ForegroundColor Cyan
if ($allOk) {
    Write-Host "  ✓ All components are ready!" -ForegroundColor Green
    Write-Host "  You can now run the mission:" -ForegroundColor White
    Write-Host "  python start_mission.py --config ./data/mission_signals.yaml" -ForegroundColor Gray
} else {
    Write-Host "  ✗ Some components need attention" -ForegroundColor Red
    Write-Host "  Fix the errors above before running the mission" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""


















