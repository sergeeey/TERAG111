# Автоматический запуск LM Studio Server
# Запускает lmstudio-server.exe если он найден

param(
    [int]$Port = 1234
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LM Studio Server Launcher" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️  This script requires Administrator rights!" -ForegroundColor Yellow
    Write-Host "   Restart PowerShell as Administrator and try again." -ForegroundColor White
    Write-Host ""
    Write-Host "   Or run:" -ForegroundColor Gray
    Write-Host "   Start-Process powershell -Verb RunAs -ArgumentList '-File `"$PSCommandPath`" -Port $Port'" -ForegroundColor White
    exit 1
}

# Поиск lmstudio-server.exe
Write-Host "🔍 Searching for lmstudio-server.exe..." -ForegroundColor Yellow
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
        break
    }
}

if (-not $serverPath) {
    Write-Host "  ❌ lmstudio-server.exe not found!" -ForegroundColor Red
    Write-Host "     Searching system-wide..." -ForegroundColor Yellow
    try {
        $foundServer = Get-ChildItem -Path "$env:LOCALAPPDATA", "$env:ProgramFiles", "$env:ProgramFiles(x86)" -Filter "lmstudio-server.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($foundServer) {
            $serverPath = $foundServer.FullName
            Write-Host "  ✅ Found: $serverPath" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Not found anywhere" -ForegroundColor Red
            Write-Host ""
            Write-Host "Please install LM Studio first or check the installation path." -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host "  ❌ Search failed: $_" -ForegroundColor Red
        exit 1
    }
}

# Проверка, не запущен ли уже сервер на этом порту
Write-Host ""
Write-Host "🔍 Checking if port $Port is already in use..." -ForegroundColor Yellow
$portInUse = netstat -ano | Select-String "LISTENING" | Select-String ":$Port\s"
if ($portInUse) {
    Write-Host "  ⚠️  Port $Port is already in use!" -ForegroundColor Yellow
    $pid = ($portInUse.ToString() -split '\s+')[-1]
    Write-Host "     PID: $pid" -ForegroundColor Gray
    
    $response = Read-Host "     Do you want to kill the process and start new server? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        try {
            Stop-Process -Id $pid -Force
            Write-Host "  ✅ Process killed" -ForegroundColor Green
            Start-Sleep -Seconds 2
        } catch {
            Write-Host "  ❌ Failed to kill process: $_" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  Exiting..." -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "  ✅ Port $Port is free" -ForegroundColor Green
}

# Запуск сервера
Write-Host ""
Write-Host "🚀 Starting LM Studio Server on port $Port..." -ForegroundColor Yellow
$serverDir = Split-Path $serverPath -Parent

try {
    # Запускаем сервер в новом окне
    $process = Start-Process -FilePath $serverPath -ArgumentList "--port $Port" -WorkingDirectory $serverDir -PassThru -NoNewWindow
    
    Write-Host "  ✅ Server process started (PID: $($process.Id))" -ForegroundColor Green
    Write-Host ""
    Write-Host "⏳ Waiting 5 seconds for server to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Проверка порта
    $check = netstat -ano | Select-String "LISTENING" | Select-String ":$Port\s"
    if ($check) {
        Write-Host "  ✅ Port $Port is now LISTENING!" -ForegroundColor Green
        Write-Host ""
        
        # Проверка API
        Write-Host "🔍 Testing API..." -ForegroundColor Yellow
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:$Port/v1/models" -Method Get -TimeoutSec 5
            Write-Host "  ✅ API is responding!" -ForegroundColor Green
            
            if ($response.data -and $response.data.Count -gt 0) {
                Write-Host "     Available models:" -ForegroundColor Cyan
                foreach ($model in $response.data) {
                    $modelId = if ($model.id) { $model.id } else { $model.name }
                    Write-Host "       - $modelId" -ForegroundColor White
                }
            } else {
                Write-Host "     ⚠️  No models loaded (you need to load a model in LM Studio GUI)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  ⚠️  API not responding yet: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host "     Server may need more time to start. Wait a bit and test manually:" -ForegroundColor Gray
            Write-Host "     Invoke-RestMethod -Uri 'http://localhost:$Port/v1/models'" -ForegroundColor White
        }
        
        Write-Host ""
        Write-Host "✅ Server is running!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 Add to config.env:" -ForegroundColor Cyan
        Write-Host "   LLM_PROVIDER=lmstudio" -ForegroundColor White
        Write-Host "   LLM_URL=http://localhost:$Port" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 To stop the server, press Ctrl+C or close this window" -ForegroundColor Gray
        Write-Host ""
        
        # Ждём, пока пользователь не остановит
        Write-Host "Server is running. Press Ctrl+C to stop..." -ForegroundColor Cyan
        try {
            Wait-Process -Id $process.Id
        } catch {
            Write-Host "`nServer stopped." -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "  ⚠️  Port $Port is still not listening" -ForegroundColor Yellow
        Write-Host "     Check server logs for errors" -ForegroundColor Gray
        Write-Host "     Process ID: $($process.Id)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "  ❌ Failed to start server: $_" -ForegroundColor Red
    exit 1
}
















