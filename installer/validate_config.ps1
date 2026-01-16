# TERAG Config Validator
# Проверяет и дополняет config.env недостающими переменными

param(
    [string]$InstallPath = "E:\TERAG",
    [switch]$FixMissing = $true
)

$ErrorActionPreference = "Stop"

function Get-RequiredVariables {
    # Возвращает список обязательных переменных с значениями по умолчанию
    return @{
        # Обязательные переменные
        "DATA_PATH" = "$InstallPath\data"
        "NEO4J_URI" = "bolt://terag-neo4j:7687"
        "NEO4J_USER" = "neo4j"
        "NEO4J_PASSWORD" = "terag_local"
        "PROMETHEUS_PORT" = "9090"
        "GRAFANA_PORT" = "3000"
        "FASTAPI_PORT" = "8000"
        
        # Опциональные (LLM)
        "LLM_PROVIDER" = "ollama"
        "LLM_URL" = "http://host.docker.internal:11434"
        "LLM_MODEL" = ""
        "LLM_FORCE_UTF8_FIX" = "true"
    }
}

function Read-ConfigFile {
    param([string]$ConfigPath)
    
    $config = @{}
    if (Test-Path $ConfigPath) {
        Get-Content $ConfigPath | ForEach-Object {
            $line = $_.Trim()
            # Пропускаем комментарии и пустые строки
            if ($line -and -not $line.StartsWith("#")) {
                if ($line -match '^([^#=]+)=(.*)$') {
                    $key = $matches[1].Trim()
                    $value = $matches[2].Trim()
                    if ($value) {
                        $config[$key] = $value
                    }
                }
            }
        }
    }
    return $config
}

function Write-ConfigFile {
    param(
        [string]$ConfigPath,
        [hashtable]$Config,
        [hashtable]$Defaults
    )
    
    $lines = @()
    $lines += "# TERAG Local Environment Configuration"
    $lines += "# Auto-generated/validated configuration file"
    $lines += ""
    
    # Обязательные переменные
    $lines += "# Data Path"
    $lines += "DATA_PATH=$($Config['DATA_PATH'])"
    $lines += ""
    
    $lines += "# Neo4j Configuration"
    $lines += "NEO4J_URI=$($Config['NEO4J_URI'])"
    $lines += "NEO4J_USER=$($Config['NEO4J_USER'])"
    $lines += "NEO4J_PASSWORD=$($Config['NEO4J_PASSWORD'])"
    $lines += ""
    
    $lines += "# Prometheus Configuration"
    $lines += "PROMETHEUS_PORT=$($Config['PROMETHEUS_PORT'])"
    $lines += ""
    
    $lines += "# Grafana Configuration"
    $lines += "GRAFANA_PORT=$($Config['GRAFANA_PORT'])"
    $lines += ""
    
    $lines += "# FastAPI Configuration"
    $lines += "FASTAPI_PORT=$($Config['FASTAPI_PORT'])"
    $lines += ""
    
    # LLM Configuration (если указано)
    if ($Config.ContainsKey('LLM_PROVIDER') -and $Config['LLM_PROVIDER']) {
        $lines += "# LLM Integration (optional)"
        $lines += "LLM_PROVIDER=$($Config['LLM_PROVIDER'])"
        if ($Config.ContainsKey('LLM_URL') -and $Config['LLM_URL']) {
            $lines += "LLM_URL=$($Config['LLM_URL'])"
        }
        if ($Config.ContainsKey('LLM_MODEL') -and $Config['LLM_MODEL']) {
            $lines += "LLM_MODEL=$($Config['LLM_MODEL'])"
        }
        if ($Config.ContainsKey('LLM_FORCE_UTF8_FIX')) {
            $lines += "LLM_FORCE_UTF8_FIX=$($Config['LLM_FORCE_UTF8_FIX'])"
        } else {
            $lines += "LLM_FORCE_UTF8_FIX=true"
        }
        $lines += ""
    }
    
    $content = $lines -join "`r`n"
    [System.IO.File]::WriteAllText($ConfigPath, $content, [System.Text.Encoding]::UTF8)
}

# Main
$configPath = "$InstallPath\config.env"
$requiredVars = Get-RequiredVariables

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TERAG Config Validator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Читаем существующий config
$existingConfig = Read-ConfigFile -ConfigPath $configPath

# Проверяем и дополняем
$missing = @()
$fixed = @()
$configChanged = $false

foreach ($var in $requiredVars.Keys) {
    if (-not $existingConfig.ContainsKey($var) -or [string]::IsNullOrWhiteSpace($existingConfig[$var])) {
        $defaultValue = $requiredVars[$var]
        
        # Пропускаем опциональные переменные с пустыми значениями
        if ($var -eq "LLM_MODEL" -and [string]::IsNullOrWhiteSpace($defaultValue)) {
            continue
        }
        
        $missing += $var
        
        if ($FixMissing) {
            # Используем значение по умолчанию, но обновляем DATA_PATH если нужно
            if ($var -eq "DATA_PATH") {
                $existingConfig[$var] = "$InstallPath\data"
            } elseif (-not [string]::IsNullOrWhiteSpace($defaultValue)) {
                $existingConfig[$var] = $defaultValue
            }
            $fixed += $var
            $configChanged = $true
        }
    } else {
        # Проверяем корректность NEO4J_URI
        if ($var -eq "NEO4J_URI" -and $existingConfig[$var] -notmatch 'terag-neo4j') {
            Write-Host "  [WARNING] NEO4J_URI should be 'bolt://terag-neo4j:7687' (found: $($existingConfig[$var]))" -ForegroundColor Yellow
            if ($FixMissing) {
                $existingConfig[$var] = "bolt://terag-neo4j:7687"
                $fixed += "$var (corrected)"
                $configChanged = $true
            }
        }
        
        # Обновляем DATA_PATH если путь изменился
        if ($var -eq "DATA_PATH" -and $existingConfig[$var] -ne "$InstallPath\data") {
            if ($FixMissing) {
                $existingConfig[$var] = "$InstallPath\data"
                $fixed += "$var (updated)"
                $configChanged = $true
            }
        }
    }
}

# Выводим результаты
if ($missing.Count -eq 0 -and -not $configChanged) {
    Write-Host "  [OK] All required variables are present" -ForegroundColor Green
} else {
    if ($missing.Count -gt 0) {
        Write-Host "  [WARNING] Missing variables: $($missing -join ', ')" -ForegroundColor Yellow
    }
    
    if ($FixMissing -and ($missing.Count -gt 0 -or $configChanged)) {
        Write-Host "  [FIX] Fixing missing/corrected variables..." -ForegroundColor Cyan
        
        # Сохраняем исправленный config
        Write-ConfigFile -ConfigPath $configPath -Config $existingConfig -Defaults $requiredVars
        
        if ($fixed.Count -gt 0) {
            Write-Host "  [OK] Fixed variables: $($fixed -join ', ')" -ForegroundColor Green
        }
        Write-Host "  [OK] Config saved to: $configPath" -ForegroundColor Green
    } elseif (-not $FixMissing) {
        Write-Host "  [TIP] Run with -FixMissing to auto-fix" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Current configuration:" -ForegroundColor Cyan
foreach ($var in $requiredVars.Keys) {
    $value = if ($existingConfig.ContainsKey($var)) { $existingConfig[$var] } else { $requiredVars[$var] }
    if ($var -eq "NEO4J_PASSWORD") {
        Write-Host "  $var = [hidden]" -ForegroundColor Gray
    } else {
        Write-Host "  $var = $value" -ForegroundColor Gray
    }
}

Write-Host ""
# Script always returns success (no exit codes that would break calling script)

