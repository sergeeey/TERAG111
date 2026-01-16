# TERAG Rebuild API Container
# Копирует исправленные файлы и пересобирает контейнер terag-api
# Автоматически регистрирует задачу автозапуска в Task Scheduler

param(
    [string]$InstallPath = "E:\TERAG",
    [switch]$EnableAutoStart = $false,
    [switch]$DisableAutoStart = $false,
    [switch]$EnableSignalMission = $false,
    [switch]$DisableSignalMission = $false,
    [switch]$CheckLMStudio = $false
)

$ErrorActionPreference = "Stop"

# Function to check LM Studio API status
function Check-LMStudioAPI {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  LM Studio API Check" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $ports = @(1234, 11434)
    $found = $false
    
    foreach ($p in $ports) {
        $net = netstat -ano | findstr "LISTENING" | findstr ":$p "
        
        if ($net) {
            $pid = ($net -split '\s+')[-1]
            Write-Host "[OK] Port $p is LISTENING (PID $pid)" -ForegroundColor Green
            $found = $true
            
            try {
                $resp = Invoke-RestMethod -Uri "http://localhost:$p/v1/models" -TimeoutSec 5
                Write-Host "`n[OK] API available at http://localhost:$p/v1/models" -ForegroundColor Green
                
                if ($resp.data) {
                    Write-Host "Available models:" -ForegroundColor Yellow
                    $resp.data | ForEach-Object { 
                        $modelId = if ($_.id) { $_.id } else { $_.name }
                        Write-Host "  - $modelId" -ForegroundColor White 
                    }
                }
                
                Write-Host "`n✅ Add to config.env:" -ForegroundColor Cyan
                Write-Host "   LLM_PROVIDER=lmstudio" -ForegroundColor White
                Write-Host "   LLM_URL=http://localhost:$p" -ForegroundColor White
                Write-Host ""
                
                return $true
            } catch {
                Write-Host "[!] Port $p is open, but API not responding: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
    
    if (-not $found) {
        Write-Host "[X] No active LM Studio ports found (1234 or 11434)." -ForegroundColor Red
        Write-Host ""
        
        # Поиск lmstudio-server.exe на системе
        Write-Host "🔍 Searching for lmstudio-server.exe..." -ForegroundColor Yellow
        
        $searchPaths = @(
            "$env:LOCALAPPDATA\Programs\LM Studio\resources\server\lmstudio-server.exe",
            "$env:ProgramFiles\LM Studio\resources\server\lmstudio-server.exe",
            "$env:ProgramFiles(x86)\LM Studio\resources\server\lmstudio-server.exe",
            "$env:USERPROFILE\AppData\Local\Programs\LM Studio\resources\server\lmstudio-server.exe"
        )
        
        $serverPath = $null
        foreach ($path in $searchPaths) {
            if (Test-Path $path) {
                $serverPath = $path
                Write-Host "  ✅ Found: $path" -ForegroundColor Green
                break
            }
        }
        
        # Если не найден в стандартных местах, ищем по всему диску
        if (-not $serverPath) {
            Write-Host "  ⚠️  Not found in standard locations. Searching system..." -ForegroundColor Yellow
            try {
                $foundServer = Get-ChildItem -Path "$env:LOCALAPPDATA", "$env:ProgramFiles", "$env:ProgramFiles(x86)" -Filter "lmstudio-server.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($foundServer) {
                    $serverPath = $foundServer.FullName
                    Write-Host "  ✅ Found: $serverPath" -ForegroundColor Green
                }
            } catch {
                Write-Host "  ⚠️  Could not search system-wide (may require admin rights)" -ForegroundColor Yellow
            }
        }
        
        Write-Host ""
        Write-Host "📋 Troubleshooting steps:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Close LM Studio completely (check Task Manager)" -ForegroundColor White
        Write-Host "2. Run LM Studio as Administrator (Right-click → Run as Administrator)" -ForegroundColor White
        Write-Host "3. Load any model and wait for 'Ready' status" -ForegroundColor White
        Write-Host "4. Go to Settings → Developer → Toggle 'Enable Local LLM Service' OFF → ON" -ForegroundColor White
        Write-Host "5. Wait 5-10 seconds for message: 'Local LLM Service running on http://localhost:XXXX'" -ForegroundColor White
        Write-Host ""
        
        if ($serverPath) {
            Write-Host "⚙️  Manual server start (if GUI doesn't work):" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "   Open PowerShell as Administrator and run:" -ForegroundColor Yellow
            Write-Host "   cd `"$(Split-Path $serverPath -Parent)`"" -ForegroundColor White
            Write-Host "   .\lmstudio-server.exe --port 1234" -ForegroundColor White
            Write-Host ""
            Write-Host "   Or in one line:" -ForegroundColor Gray
            Write-Host "   & `"$serverPath`" --port 1234" -ForegroundColor White
            Write-Host ""
        } else {
            Write-Host "⚠️  lmstudio-server.exe not found. Common locations:" -ForegroundColor Yellow
            Write-Host "   - $env:LOCALAPPDATA\Programs\LM Studio\resources\server\" -ForegroundColor Gray
            Write-Host "   - $env:ProgramFiles\LM Studio\resources\server\" -ForegroundColor Gray
            Write-Host ""
        }
        
        return $false
    }
    
    return $false
}

# Handle LM Studio check request
if ($CheckLMStudio) {
    Check-LMStudioAPI
    exit 0
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TERAG API Rebuild" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to register/unregister Task Scheduler task for auto-start
function Register-TeragAutoStart {
    param(
        [string]$TaskPath,
        [bool]$Enable
    )
    
    $taskName = "TERAG Auto Start"
    
    try {
        # Check if running as administrator
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        
        if (-not $isAdmin) {
            Write-Host "  [WARNING] Task Scheduler requires administrator rights" -ForegroundColor Yellow
            Write-Host "  Run PowerShell as Administrator to enable auto-start" -ForegroundColor Gray
            return $false
        }
        
        # Check if task already exists
        $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        
        if ($Enable) {
            # Normalize path (ensure it ends with backslash for docker compose)
            $normalizedPath = $TaskPath.TrimEnd('\')
            
            # Create action: PowerShell command to start docker compose
            $action = New-ScheduledTaskAction -Execute "powershell.exe" `
                -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"Set-Location '$normalizedPath'; docker compose --env-file config.env up -d`""
            
            # Create trigger: At system startup
            $trigger = New-ScheduledTaskTrigger -AtStartup
            
            # Create principal: Run with highest privileges
            $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
            
            # Create settings: Allow task to run on demand, restart on failure
            $settings = New-ScheduledTaskSettingsSet `
                -AllowStartIfOnBatteries `
                -DontStopIfGoingOnBatteries `
                -StartWhenAvailable `
                -RestartCount 3 `
                -RestartInterval (New-TimeSpan -Minutes 1)
            
            # Register or update task
            if ($existingTask) {
                Write-Host "  [INFO] Updating existing Task Scheduler task..." -ForegroundColor Yellow
                Set-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
            } else {
                Write-Host "  [INFO] Creating Task Scheduler task..." -ForegroundColor Yellow
                Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Automatically starts TERAG containers on system boot" | Out-Null
            }
            
            Write-Host "  [OK] Auto-start enabled: Task '$taskName' registered" -ForegroundColor Green
            Write-Host "  [INFO] TERAG will start automatically on system boot" -ForegroundColor Gray
            return $true
        } else {
            # Disable auto-start
            if ($existingTask) {
                Unregister-ScheduledTask -TaskName $taskName -Confirm:$false | Out-Null
                Write-Host "  [OK] Auto-start disabled: Task '$taskName' removed" -ForegroundColor Green
            } else {
                Write-Host "  [INFO] Auto-start task not found, nothing to remove" -ForegroundColor Gray
            }
            return $true
        }
    } catch {
        Write-Host "  [ERROR] Failed to manage Task Scheduler task: $_" -ForegroundColor Red
        Write-Host "  [INFO] You can manually create the task using Task Scheduler (taskschd.msc)" -ForegroundColor Yellow
        return $false
    }
}

# Step 0: Handle auto-start registration/unregistration
if ($DisableAutoStart) {
    Write-Host "[0/6] Disabling auto-start..." -ForegroundColor Yellow
    Register-TeragAutoStart -TaskPath $InstallPath -Enable $false | Out-Null
    Write-Host ""
}

# Function to register Signal Discovery Mission in Task Scheduler
function Register-SignalMission {
    param(
        [string]$TaskPath,
        [bool]$Enable
    )
    
    $taskName = "TERAG Signal Discovery Mission"
    
    try {
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        
        if (-not $isAdmin) {
            Write-Host "  [WARNING] Task Scheduler requires administrator rights" -ForegroundColor Yellow
            return $false
        }
        
        $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        
        if ($Enable) {
            $normalizedPath = $TaskPath.TrimEnd('\')
            $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
            $missionConfigPath = "$scriptDir\data\mission_signals.yaml"
            
            # Проверка существования конфигурации миссии
            if (-not (Test-Path $missionConfigPath)) {
                Write-Host "  [WARNING] Mission config not found: $missionConfigPath" -ForegroundColor Yellow
                Write-Host "  [INFO] Skipping signal mission registration" -ForegroundColor Gray
                return $false
            }
            
            # Создание действия: запуск миссии через Python
            # Используем python из PATH или из контейнера
            $pythonCmd = "python"
            if (Get-Command python -ErrorAction SilentlyContinue) {
                $pythonPath = (Get-Command python).Source
            } else {
                Write-Host "  [WARNING] Python not found in PATH, using 'python' command" -ForegroundColor Yellow
                $pythonCmd = "python"
            }
            
            $action = New-ScheduledTaskAction -Execute $pythonCmd `
                -Argument "$scriptDir\start_mission.py --config $missionConfigPath --install-path $normalizedPath"
            
            # Триггер: ежедневно в 3:00 AM
            $trigger = New-ScheduledTaskTrigger -Daily -At "03:00AM"
            
            # Principal: SYSTEM с наивысшими правами
            $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
            
            # Настройки: разрешить запуск на батарее, перезапуск при сбое
            $settings = New-ScheduledTaskSettingsSet `
                -AllowStartIfOnBatteries `
                -DontStopIfGoingOnBatteries `
                -StartWhenAvailable `
                -RestartCount 3 `
                -RestartInterval (New-TimeSpan -Minutes 5)
            
            if ($existingTask) {
                Write-Host "  [INFO] Updating existing Signal Mission task..." -ForegroundColor Yellow
                Set-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
            } else {
                Write-Host "  [INFO] Creating Signal Mission task..." -ForegroundColor Yellow
                Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Automatically runs TERAG Signal Discovery Mission to find weak signals and new concepts" | Out-Null
            }
            
            Write-Host "  [OK] Signal Discovery Mission enabled: Task '$taskName' registered" -ForegroundColor Green
            Write-Host "  [INFO] Mission will run daily at 3:00 AM" -ForegroundColor Gray
            return $true
        } else {
            if ($existingTask) {
                Unregister-ScheduledTask -TaskName $taskName -Confirm:$false | Out-Null
                Write-Host "  [OK] Signal Discovery Mission disabled: Task '$taskName' removed" -ForegroundColor Green
            } else {
                Write-Host "  [INFO] Signal Mission task not found, nothing to remove" -ForegroundColor Gray
            }
            return $true
        }
    } catch {
        Write-Host "  [ERROR] Failed to manage Signal Mission task: $_" -ForegroundColor Red
        return $false
    }
}

# Handle signal mission registration/unregistration
if ($DisableSignalMission) {
    Write-Host "[0/6] Disabling Signal Discovery Mission..." -ForegroundColor Yellow
    Register-SignalMission -TaskPath $InstallPath -Enable $false | Out-Null
    Write-Host ""
}

# Step 1: Check if install path exists
if (-not (Test-Path $InstallPath)) {
    Write-Host "  ERROR: Installation path not found: $InstallPath" -ForegroundColor Red
    Write-Host "  Run setup_terag.ps1 first!" -ForegroundColor Yellow
    exit 1
}

# Check and copy necessary files to install path
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path "$InstallPath\docker-compose.yml")) {
    Write-Host "  [WARNING] docker-compose.yml not found in $InstallPath" -ForegroundColor Yellow
    Write-Host "  [INFO] Copying docker-compose.yml from installer..." -ForegroundColor Gray
    if (Test-Path "$scriptDir\docker-compose.yml") {
        Copy-Item "$scriptDir\docker-compose.yml" "$InstallPath\docker-compose.yml" -Force
        Write-Host "  [OK] docker-compose.yml copied" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] docker-compose.yml not found in installer directory" -ForegroundColor Red
        exit 1
    }
}

# Copy prometheus config if needed
if (-not (Test-Path "$InstallPath\prometheus")) {
    if (Test-Path "$scriptDir\prometheus") {
        Write-Host "  [INFO] Copying prometheus configuration..." -ForegroundColor Gray
        Copy-Item "$scriptDir\prometheus" "$InstallPath\prometheus" -Recurse -Force
        Write-Host "  [OK] prometheus config copied" -ForegroundColor Green
    }
}

# Copy grafana config if needed
if (-not (Test-Path "$InstallPath\grafana")) {
    if (Test-Path "$scriptDir\grafana") {
        Write-Host "  [INFO] Copying grafana configuration..." -ForegroundColor Gray
        Copy-Item "$scriptDir\grafana" "$InstallPath\grafana" -Recurse -Force
        Write-Host "  [OK] grafana config copied" -ForegroundColor Green
    }
}

# Step 1.5: Validate and fix config.env
Write-Host "[1/6] Validating config.env..." -ForegroundColor Yellow
$validateScript = "$scriptDir\validate_config.ps1"
if (Test-Path $validateScript) {
    try {
        $output = & $validateScript -InstallPath $InstallPath -FixMissing 2>&1
        Write-Host $output
        Write-Host "  [OK] Config validated" -ForegroundColor Green
    } catch {
        Write-Host "  [WARNING] Config validation had issues: $_" -ForegroundColor Yellow
        Write-Host "  Continuing anyway..." -ForegroundColor Gray
    }
} else {
    Write-Host "  [WARNING] validate_config.ps1 not found, skipping validation" -ForegroundColor Yellow
}

# Step 2: Get installer directory (scriptDir already defined above)
$installerAppDir = "$scriptDir\app"
$targetAppDir = "$InstallPath\app"

if (-not (Test-Path $installerAppDir)) {
    Write-Host "  ERROR: Installer app directory not found: $installerAppDir" -ForegroundColor Red
    exit 1
}

# Step 2: Copy corrected files
Write-Host "[2/6] Copying corrected files..." -ForegroundColor Yellow
if (-not (Test-Path $targetAppDir)) {
    New-Item -ItemType Directory -Path $targetAppDir -Force | Out-Null
}

Copy-Item "$installerAppDir\main.py" "$targetAppDir\main.py" -Force
Write-Host "  [OK] Copied main.py (fixed imports)" -ForegroundColor Green

Copy-Item "$installerAppDir\Dockerfile" "$targetAppDir\Dockerfile" -Force
Write-Host "  [OK] Copied Dockerfile (with import validation)" -ForegroundColor Green

# Copy other files if needed
if (Test-Path "$installerAppDir\modules") {
    Copy-Item "$installerAppDir\modules\*" "$targetAppDir\modules\" -Recurse -Force
    Write-Host "  [OK] Copied modules directory" -ForegroundColor Green
}

if (Test-Path "$installerAppDir\requirements.txt") {
    Copy-Item "$installerAppDir\requirements.txt" "$targetAppDir\requirements.txt" -Force
    Write-Host "  [OK] Copied requirements.txt" -ForegroundColor Green
}

# Step 3: Stop and remove existing API container
Write-Host "[3/6] Stopping existing API container..." -ForegroundColor Yellow
Set-Location $InstallPath
docker compose --env-file config.env stop terag-api 2>&1 | Out-Null
docker compose --env-file config.env rm -f terag-api 2>&1 | Out-Null
Write-Host "  [OK] API container stopped and removed" -ForegroundColor Green

# Step 4: Rebuild API container with no cache
Write-Host "[4/6] Rebuilding API container (this may take a few minutes)..." -ForegroundColor Yellow
docker compose --env-file config.env build --no-cache terag-api
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Build failed! Check the errors above." -ForegroundColor Red
    Write-Host "  Common issues:" -ForegroundColor Yellow
    Write-Host "    - Import errors: Check main.py imports" -ForegroundColor Gray
    Write-Host "    - Missing dependencies: Check requirements.txt" -ForegroundColor Gray
    exit 1
}
Write-Host "  [OK] Container built successfully" -ForegroundColor Green

# Step 5: Start containers
Write-Host "[5/6] Starting containers..." -ForegroundColor Yellow
docker compose --env-file config.env up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Failed to start containers" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Containers started" -ForegroundColor Green

# Step 6: Register auto-start if requested
if ($EnableAutoStart) {
    Write-Host "[6/6] Registering auto-start..." -ForegroundColor Yellow
    $autoStartResult = Register-TeragAutoStart -TaskPath $InstallPath -Enable $true
    if (-not $autoStartResult) {
        Write-Host "  [WARNING] Auto-start registration failed, but installation completed" -ForegroundColor Yellow
    }
} else {
    Write-Host "[6/6] Skipping auto-start registration (use -EnableAutoStart to enable)" -ForegroundColor Gray
}

# Step 6.5: Register Signal Discovery Mission if requested
if ($EnableSignalMission) {
    Write-Host "[6.5/6] Registering Signal Discovery Mission..." -ForegroundColor Yellow
    $signalMissionResult = Register-SignalMission -TaskPath $InstallPath -Enable $true
    if (-not $signalMissionResult) {
        Write-Host "  [WARNING] Signal Mission registration failed, but installation completed" -ForegroundColor Yellow
    }
} else {
    Write-Host "[6.5/6] Skipping Signal Mission registration (use -EnableSignalMission to enable)" -ForegroundColor Gray
}

# Success
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TERAG API Rebuilt Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Waiting 30 seconds for API to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "Checking API container status..." -ForegroundColor Cyan
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "terag-api"

Write-Host ""
Write-Host "Checking API logs (last 20 lines)..." -ForegroundColor Cyan
docker logs terag-api --tail 20

Write-Host ""
Write-Host "Testing API health endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "  [OK] API is healthy! Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "  Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "  [WARNING] API not responding yet. Wait a bit longer and check:" -ForegroundColor Yellow
    Write-Host "     docker logs terag-api --tail 50" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  TERAG API:   http://localhost:8000/health" -ForegroundColor White
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  docker logs terag-api -f           - Follow API logs" -ForegroundColor Gray
Write-Host "  docker compose logs terag-api      - View all API logs" -ForegroundColor Gray
Write-Host ""
Write-Host "Auto-start management:" -ForegroundColor Cyan
Write-Host "  .\rebuild_api.ps1 -EnableAutoStart   - Enable auto-start on boot" -ForegroundColor Gray
Write-Host "  .\rebuild_api.ps1 -DisableAutoStart  - Disable auto-start" -ForegroundColor Gray
Write-Host ""
Write-Host "Signal Discovery Mission:" -ForegroundColor Cyan
Write-Host "  .\rebuild_api.ps1 -EnableSignalMission   - Enable daily signal discovery mission" -ForegroundColor Gray
Write-Host "  .\rebuild_api.ps1 -DisableSignalMission  - Disable signal discovery mission" -ForegroundColor Gray
Write-Host "  taskschd.msc                             - View Task Scheduler" -ForegroundColor Gray
Write-Host ""
Write-Host "LM Studio Check:" -ForegroundColor Cyan
Write-Host "  .\rebuild_api.ps1 -CheckLMStudio         - Check LM Studio API status" -ForegroundColor Gray
Write-Host "  .\check-lmstudio.ps1                     - Alternative: standalone check script" -ForegroundColor Gray
Write-Host ""

