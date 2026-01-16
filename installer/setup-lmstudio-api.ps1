# Настройка LM Studio API после установки
# Проверяет установку и помогает настроить API сервер

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LM Studio API Setup" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Шаг 1: Поиск установки
Write-Host "[1/6] Finding LM Studio installation..." -ForegroundColor Yellow
$lmStudioExe = $null
$serverPath = $null

$searchPaths = @(
    "$env:LOCALAPPDATA\Programs\LM Studio\LM Studio.exe",
    "$env:ProgramFiles\LM Studio\LM Studio.exe",
    "$env:ProgramFiles(x86)\LM Studio\LM Studio.exe"
)

foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        $lmStudioExe = $path
        Write-Host "  ✅ Found: $path" -ForegroundColor Green
        
        # Ищем server
        $installDir = Split-Path $path -Parent
        $serverPaths = @(
            "$installDir\resources\server\lmstudio-server.exe",
            "$installDir\server\lmstudio-server.exe"
        )
        
        foreach ($sp in $serverPaths) {
            if (Test-Path $sp) {
                $serverPath = $sp
                Write-Host "  ✅ Server found: $serverPath" -ForegroundColor Green
                break
            }
        }
        break
    }
}

if (-not $lmStudioExe) {
    Write-Host "  ❌ LM Studio not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Please install LM Studio first:" -ForegroundColor Yellow
    Write-Host "  1. Visit https://lmstudio.ai" -ForegroundColor White
    Write-Host "  2. Download and install LM Studio" -ForegroundColor White
    Write-Host "  3. Run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "  Or run: .\install-lmstudio.ps1" -ForegroundColor Gray
    exit 1
}

if (-not $serverPath) {
    Write-Host "  ⚠️  lmstudio-server.exe not found!" -ForegroundColor Yellow
    Write-Host "     This may mean:" -ForegroundColor White
    Write-Host "     - Installation is incomplete" -ForegroundColor Gray
    Write-Host "     - You have Store version (not supported)" -ForegroundColor Gray
    Write-Host "     - Need to update LM Studio" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Solution: Reinstall LM Studio from https://lmstudio.ai (EXE version)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Шаг 2: Проверка процессов
Write-Host "[2/6] Checking running processes..." -ForegroundColor Yellow
$lmProcesses = Get-Process | Where-Object { $_.ProcessName -like "*lmstudio*" }
if ($lmProcesses) {
    Write-Host "  ⚠️  LM Studio is already running" -ForegroundColor Yellow
    Write-Host "     You may need to close it first to enable API" -ForegroundColor Gray
    
    $response = Read-Host "     Close LM Studio processes? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        foreach ($proc in $lmProcesses) {
            try {
                Stop-Process -Id $proc.Id -Force
                Write-Host "     ✅ Stopped: $($proc.ProcessName)" -ForegroundColor Green
            } catch {
                Write-Host "     ⚠️  Could not stop: $($proc.ProcessName)" -ForegroundColor Yellow
            }
        }
        Start-Sleep -Seconds 2
    }
} else {
    Write-Host "  ✅ No LM Studio processes running" -ForegroundColor Green
}

Write-Host ""

# Шаг 3: Проверка портов
Write-Host "[3/6] Checking ports..." -ForegroundColor Yellow
$ports = @(1234, 11434)
$activePorts = @()

foreach ($port in $ports) {
    $listening = netstat -ano | Select-String "LISTENING" | Select-String ":$port\s"
    if ($listening) {
        Write-Host "  ⚠️  Port $port is already in use" -ForegroundColor Yellow
        $pid = ($listening.ToString() -split '\s+')[-1]
        Write-Host "     PID: $pid" -ForegroundColor Gray
    } else {
        Write-Host "  ✅ Port $port is free" -ForegroundColor Green
        $activePorts += $port
    }
}

Write-Host ""

# Шаг 4: Инструкции по запуску
Write-Host "[4/6] Setup Instructions:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  To enable LM Studio API:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Start LM Studio as Administrator:" -ForegroundColor White
Write-Host "     Right-click '$lmStudioExe' → 'Run as Administrator'" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. In LM Studio:" -ForegroundColor White
Write-Host "     a) Download/load a model (if not already done)" -ForegroundColor Gray
Write-Host "        - Go to 'Search' tab" -ForegroundColor Gray
Write-Host "        - Download any model (e.g., 'Llama 3.1 8B' or 'Phi-3')" -ForegroundColor Gray
Write-Host "        - Wait for download to complete" -ForegroundColor Gray
Write-Host "        - Click 'Load Model' and wait for 'Ready' status" -ForegroundColor Gray
Write-Host ""
Write-Host "     b) Enable API Server:" -ForegroundColor Gray
Write-Host "        - Go to Settings (gear icon) → Developer tab" -ForegroundColor Gray
Write-Host "        - Check 'Enable Local LLM Service (headless)'" -ForegroundColor Gray
Write-Host "        - Wait 5-10 seconds for confirmation message" -ForegroundColor Gray
Write-Host "        - You should see: 'Local LLM Service running on http://localhost:XXXX'" -ForegroundColor Gray
Write-Host ""

# Шаг 5: Автоматический запуск через GUI
Write-Host "[5/6] Quick Start Options:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Option A: Launch LM Studio as Administrator now" -ForegroundColor Cyan
$launch = Read-Host "  Launch LM Studio as Administrator? (y/N)"
if ($launch -eq "y" -or $launch -eq "Y") {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if ($isAdmin) {
        Write-Host "  ✅ Starting LM Studio..." -ForegroundColor Green
        Start-Process -FilePath $lmStudioExe -Verb RunAs
        Write-Host "  ✅ LM Studio launched!" -ForegroundColor Green
        Write-Host "  → Now follow step 2 instructions above in LM Studio" -ForegroundColor Yellow
    } else {
        Write-Host "  ⚠️  Need admin rights to launch as admin" -ForegroundColor Yellow
        Write-Host "  → Right-click LM Studio.exe → Run as Administrator" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "  Option B: Manual server start (if GUI doesn't work)" -ForegroundColor Cyan
Write-Host "  Use: .\start-lmstudio-server.ps1" -ForegroundColor Gray
Write-Host ""

# Шаг 6: Проверка после настройки
Write-Host "[6/6] Verification:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  After enabling API in LM Studio, verify it works:" -ForegroundColor White
Write-Host "  .\check-lmstudio.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  Or run full diagnostics:" -ForegroundColor White
Write-Host "  .\diagnose-lmstudio.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ LM Studio found: $lmStudioExe" -ForegroundColor Green
Write-Host "✅ Server found: $serverPath" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start LM Studio as Administrator" -ForegroundColor White
Write-Host "2. Load a model" -ForegroundColor White
Write-Host "3. Enable 'Local LLM Service' in Settings → Developer" -ForegroundColor White
Write-Host "4. Run: .\check-lmstudio.ps1" -ForegroundColor White
Write-Host ""
















