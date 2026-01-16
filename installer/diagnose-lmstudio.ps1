# Полная диагностика LM Studio API
# Проверяет все возможные проблемы и помогает их решить

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LM Studio Full Diagnostics" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Шаг 1: Проверка процессов LM Studio
Write-Host "[1/8] Checking LM Studio processes..." -ForegroundColor Yellow
$lmProcesses = Get-Process | Where-Object { $_.ProcessName -like "*lmstudio*" -or $_.ProcessName -like "*lm-studio*" }
if ($lmProcesses) {
    Write-Host "  ✅ Found LM Studio processes:" -ForegroundColor Green
    foreach ($proc in $lmProcesses) {
        Write-Host "     - $($proc.ProcessName) (PID: $($proc.Id), Path: $($proc.Path))" -ForegroundColor White
    }
} else {
    Write-Host "  ❌ No LM Studio processes running" -ForegroundColor Red
    Write-Host "     → Start LM Studio first!" -ForegroundColor Yellow
}

Write-Host ""

# Шаг 2: Проверка портов
Write-Host "[2/8] Checking ports 1234 and 11434..." -ForegroundColor Yellow
$ports = @(1234, 11434)
$activePorts = @()

foreach ($port in $ports) {
    $listening = netstat -ano | Select-String "LISTENING" | Select-String ":$port\s"
    if ($listening) {
        $pid = ($listening.ToString() -split '\s+')[-1]
        Write-Host "  ✅ Port $port is LISTENING (PID: $pid)" -ForegroundColor Green
        $activePorts += $port
    } else {
        Write-Host "  ❌ Port $port is NOT listening" -ForegroundColor Red
    }
}

Write-Host ""

# Шаг 3: Проверка блокировки портов
Write-Host "[3/8] Checking if ports are blocked by other processes..." -ForegroundColor Yellow
foreach ($port in $ports) {
    $connection = netstat -ano | Select-String ":$port\s"
    if ($connection -and -not ($connection | Select-String "LISTENING")) {
        $otherConnections = $connection | Where-Object { $_ -notmatch "LISTENING" }
        if ($otherConnections) {
            Write-Host "  ⚠️  Port $port has other connections (not listening):" -ForegroundColor Yellow
            Write-Host "     $otherConnections" -ForegroundColor Gray
        }
    }
}

Write-Host ""

# Шаг 4: Поиск lmstudio-server.exe
Write-Host "[4/8] Searching for lmstudio-server.exe..." -ForegroundColor Yellow
$serverPath = $null
$searchPaths = @(
    "$env:LOCALAPPDATA\Programs\LM Studio\resources\server\lmstudio-server.exe",
    "$env:ProgramFiles\LM Studio\resources\server\lmstudio-server.exe",
    "$env:ProgramFiles(x86)\LM Studio\resources\server\lmstudio-server.exe",
    "$env:USERPROFILE\AppData\Local\Programs\LM Studio\resources\server\lmstudio-server.exe"
)

foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        $serverPath = $path
        Write-Host "  ✅ Found: $path" -ForegroundColor Green
        
        # Проверка размера файла
        $fileInfo = Get-Item $path
        Write-Host "     Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Gray
        Write-Host "     Modified: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
        break
    }
}

if (-not $serverPath) {
    Write-Host "  ❌ lmstudio-server.exe not found in standard locations" -ForegroundColor Red
    Write-Host "     Searching system-wide..." -ForegroundColor Yellow
    try {
        $foundServer = Get-ChildItem -Path "$env:LOCALAPPDATA", "$env:ProgramFiles", "$env:ProgramFiles(x86)" -Filter "lmstudio-server.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($foundServer) {
            $serverPath = $foundServer.FullName
            Write-Host "  ✅ Found: $serverPath" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Not found anywhere" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ⚠️  Could not search system-wide: $_" -ForegroundColor Yellow
    }
}

Write-Host ""

# Шаг 5: Проверка директории server
Write-Host "[5/8] Checking server directory contents..." -ForegroundColor Yellow
if ($serverPath) {
    $serverDir = Split-Path $serverPath -Parent
    Write-Host "  Server directory: $serverDir" -ForegroundColor Gray
    
    if (Test-Path $serverDir) {
        $files = Get-ChildItem $serverDir -File | Select-Object Name, Length, LastWriteTime
        Write-Host "  Files in server directory:" -ForegroundColor Gray
        foreach ($file in $files) {
            Write-Host "     - $($file.Name) ($([math]::Round($file.Length / 1KB, 2)) KB)" -ForegroundColor White
        }
    }
} else {
    Write-Host "  ⚠️  Cannot check - server path not found" -ForegroundColor Yellow
}

Write-Host ""

# Шаг 6: Проверка API доступности
Write-Host "[6/8] Testing API endpoints..." -ForegroundColor Yellow
foreach ($port in $activePorts) {
    $apiUrl = "http://localhost:$port"
    $modelsUrl = "$apiUrl/v1/models"
    
    Write-Host "  Testing: $modelsUrl" -ForegroundColor Gray
    try {
        $response = Invoke-RestMethod -Uri $modelsUrl -Method Get -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  ✅ API is responding!" -ForegroundColor Green
        
        if ($response.data -and $response.data.Count -gt 0) {
            Write-Host "     Available models:" -ForegroundColor Cyan
            foreach ($model in $response.data) {
                $modelId = if ($model.id) { $model.id } else { $model.name }
                Write-Host "       - $modelId" -ForegroundColor White
            }
        } else {
            Write-Host "     ⚠️  No models loaded" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ API not responding: $($_.Exception.Message)" -ForegroundColor Red
        
        # Проверка TCP соединения
        Write-Host "     Testing TCP connection..." -ForegroundColor Gray
        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $result = $tcpClient.BeginConnect("localhost", $port, $null, $null)
            $wait = $result.AsyncWaitHandle.WaitOne(2000, $false)
            
            if ($wait) {
                $tcpClient.EndConnect($result)
                Write-Host "     ✅ TCP connection works" -ForegroundColor Green
                Write-Host "     ⚠️  Port is open but HTTP API not responding" -ForegroundColor Yellow
                Write-Host "     → Server might not be fully started or API endpoint is different" -ForegroundColor Yellow
            } else {
                Write-Host "     ❌ TCP connection failed" -ForegroundColor Red
            }
            $tcpClient.Close()
        } catch {
            Write-Host "     ❌ TCP connection error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""

# Шаг 7: Проверка прав доступа
Write-Host "[7/8] Checking administrator rights..." -ForegroundColor Yellow
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host "  ✅ Running as Administrator" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  NOT running as Administrator" -ForegroundColor Yellow
    Write-Host "     → Some operations may require admin rights" -ForegroundColor Gray
}

Write-Host ""

# Шаг 8: Рекомендации и решения
Write-Host "[8/8] Recommendations..." -ForegroundColor Yellow
Write-Host ""

if (-not $activePorts) {
    Write-Host "❌ PROBLEM: No LM Studio API ports are listening" -ForegroundColor Red
    Write-Host ""
    Write-Host "SOLUTIONS:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Close LM Studio completely (Task Manager → End all LM Studio processes)" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Start LM Studio as Administrator:" -ForegroundColor White
    Write-Host "   - Right-click LM Studio.exe → 'Run as Administrator'" -ForegroundColor Gray
    Write-Host "   - Or: Start PowerShell as Admin, then run:" -ForegroundColor Gray
    if ($lmProcesses) {
        $lmExe = $lmProcesses[0].Path
        Write-Host "      Start-Process '$lmExe' -Verb RunAs" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "3. In LM Studio:" -ForegroundColor White
    Write-Host "   - Load any model (wait for 'Ready' status)" -ForegroundColor Gray
    Write-Host "   - Go to Settings → Developer" -ForegroundColor Gray
    Write-Host "   - Toggle 'Enable Local LLM Service' OFF → ON" -ForegroundColor Gray
    Write-Host "   - Wait 10-15 seconds for confirmation message" -ForegroundColor Gray
    Write-Host ""
    
    if ($serverPath) {
        Write-Host "4. If GUI doesn't work, try manual server start:" -ForegroundColor White
        Write-Host "   Open PowerShell as Administrator and run:" -ForegroundColor Gray
        Write-Host "   cd `"$(Split-Path $serverPath -Parent)`"" -ForegroundColor White
        Write-Host "   .\lmstudio-server.exe --port 1234" -ForegroundColor White
        Write-Host ""
        Write-Host "   Or in one line:" -ForegroundColor Gray
        Write-Host "   & `"$serverPath`" --port 1234" -ForegroundColor White
        Write-Host ""
        
        # Попытка запуска сервера
        Write-Host "   💡 Try to start server now? (requires admin rights)" -ForegroundColor Cyan
        $response = Read-Host "   Press Enter to continue or type 'start' to attempt manual start"
        if ($response -eq "start" -and $isAdmin) {
            Write-Host "   Starting server..." -ForegroundColor Yellow
            try {
                $serverDir = Split-Path $serverPath -Parent
                Start-Process -FilePath $serverPath -ArgumentList "--port 1234" -WorkingDirectory $serverDir -NoNewWindow
                Write-Host "   ✅ Server process started" -ForegroundColor Green
                Write-Host "   Wait 5 seconds and check again..." -ForegroundColor Yellow
                Start-Sleep -Seconds 5
                
                # Повторная проверка
                $check = netstat -ano | Select-String "LISTENING" | Select-String ":1234\s"
                if ($check) {
                    Write-Host "   ✅ Port 1234 is now LISTENING!" -ForegroundColor Green
                } else {
                    Write-Host "   ⚠️  Port still not listening - check server logs" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "   ❌ Failed to start server: $_" -ForegroundColor Red
            }
        } elseif ($response -eq "start" -and -not $isAdmin) {
            Write-Host "   ⚠️  Admin rights required for manual start" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "✅ Ports are active!" -ForegroundColor Green
    Write-Host ""
    Write-Host "If API still doesn't respond, check:" -ForegroundColor Cyan
    Write-Host "  - Is a model loaded in LM Studio?" -ForegroundColor White
    Write-Host "  - Are there any error messages in LM Studio logs?" -ForegroundColor White
    Write-Host "  - Try restarting LM Studio completely" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Run this script again after trying fixes" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
















