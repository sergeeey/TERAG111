# Быстрый запуск LM Studio Server вручную
# Проверяет наличие файла и запускает сервер

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LM Studio Server Quick Start" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️  This script requires Administrator rights!" -ForegroundColor Yellow
    Write-Host "   Restart PowerShell as Administrator and try again." -ForegroundColor White
    Write-Host ""
    Write-Host "   Or run:" -ForegroundColor Gray
    Write-Host "   Start-Process powershell -Verb RunAs -ArgumentList '-File `"$PSCommandPath`"'" -ForegroundColor White
    exit 1
}

# Шаг 1: Поиск lmstudio-server.exe во всех возможных местах
Write-Host "[1/4] Searching for lmstudio-server.exe..." -ForegroundColor Yellow
$serverPath = $null

# Все возможные пути
$searchPaths = @(
    "$env:LOCALAPPDATA\Programs\LM Studio\resources\server\lmstudio-server.exe",
    "$env:LOCALAPPDATA\Programs\LM Studio\resources\lmstudio-server.exe",
    "$env:ProgramFiles\LM Studio\resources\server\lmstudio-server.exe",
    "$env:ProgramFiles(x86)\LM Studio\resources\server\lmstudio-server.exe",
    "$env:USERPROFILE\AppData\Local\Programs\LM Studio\resources\server\lmstudio-server.exe"
)

Write-Host "   Checking standard locations..." -ForegroundColor Gray
foreach ($path in $searchPaths) {
    Write-Host "   - $path" -ForegroundColor DarkGray -NoNewline
    if (Test-Path $path) {
        $serverPath = $path
        Write-Host " ✅ FOUND!" -ForegroundColor Green
        break
    } else {
        Write-Host " ❌" -ForegroundColor DarkGray
    }
}

# Если не найден, ищем в resources напрямую
if (-not $serverPath) {
    Write-Host "   Not found in standard locations. Checking resources directory..." -ForegroundColor Yellow
    
    $resourcesPaths = @(
        "$env:LOCALAPPDATA\Programs\LM Studio\resources",
        "$env:ProgramFiles\LM Studio\resources"
    )
    
    foreach ($resourcesPath in $resourcesPaths) {
        if (Test-Path $resourcesPath) {
            Write-Host "   Found resources directory: $resourcesPath" -ForegroundColor Cyan
            
            # Ищем все .exe файлы
            $exeFiles = Get-ChildItem -Path $resourcesPath -Filter "*.exe" -Recurse -ErrorAction SilentlyContinue | Where-Object {
                $_.Name -like "*server*" -or $_.Name -like "*lmstudio*"
            }
            
            if ($exeFiles) {
                Write-Host "   Found potential server files:" -ForegroundColor Yellow
                foreach ($exe in $exeFiles) {
                    Write-Host "     - $($exe.FullName)" -ForegroundColor White
                    if ($exe.Name -like "*server*") {
                        $serverPath = $exe.FullName
                        Write-Host "       ✅ Using this one!" -ForegroundColor Green
                    }
                }
                
                if (-not $serverPath -and $exeFiles.Count -eq 1) {
                    $serverPath = $exeFiles[0].FullName
                    Write-Host "   ✅ Using: $serverPath" -ForegroundColor Green
                }
            }
            
            # Проверяем структуру папок
            Write-Host "   Directory structure:" -ForegroundColor Gray
            $items = Get-ChildItem -Path $resourcesPath -ErrorAction SilentlyContinue | Select-Object Name, PSIsContainer
            foreach ($item in $items) {
                $type = if ($item.PSIsContainer) { "📁" } else { "📄" }
                Write-Host "     $type $($item.Name)" -ForegroundColor DarkGray
            }
        }
    }
}

if (-not $serverPath) {
    Write-Host ""
    Write-Host "❌ lmstudio-server.exe NOT FOUND!" -ForegroundColor Red
    Write-Host ""
    Write-Host "The server component is missing from your LM Studio installation." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Possible reasons:" -ForegroundColor Cyan
    Write-Host "  - Incomplete installation" -ForegroundColor White
    Write-Host "  - Store version (which doesn't include server files)" -ForegroundColor White
    Write-Host "  - Installation in non-standard location" -ForegroundColor White
    Write-Host ""
    Write-Host "Solutions:" -ForegroundColor Cyan
    Write-Host "  1. Reinstall LM Studio from https://lmstudio.ai (EXE version, not Store)" -ForegroundColor White
    Write-Host "  2. Update LM Studio to latest version" -ForegroundColor White
    Write-Host "  3. Check if LM Studio is installed in a different location" -ForegroundColor White
    Write-Host ""
    Write-Host "To find installation:" -ForegroundColor Yellow
    Write-Host "  .\find-lmstudio.ps1" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "✅ Found server: $serverPath" -ForegroundColor Green
$fileInfo = Get-Item $serverPath
Write-Host "   Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Gray
Write-Host "   Modified: $($fileInfo.LastWriteTime)" -ForegroundColor Gray

Write-Host ""

# Шаг 2: Проверка порта
Write-Host "[2/4] Checking port 1234..." -ForegroundColor Yellow
$port = 1234
$portInUse = netstat -ano | Select-String "LISTENING" | Select-String ":$port\s"

if ($portInUse) {
    $pid = ($portInUse.ToString() -split '\s+')[-1]
    Write-Host "  ⚠️  Port $port is already in use by PID: $pid" -ForegroundColor Yellow
    
    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "     Process: $($process.ProcessName)" -ForegroundColor Gray
    }
    
    $response = Read-Host "  Kill this process and start server? (y/N)"
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
    Write-Host "  ✅ Port $port is free" -ForegroundColor Green
}

Write-Host ""

# Шаг 3: Запуск сервера
Write-Host "[3/4] Starting LM Studio Server..." -ForegroundColor Yellow
$serverDir = Split-Path $serverPath -Parent

Write-Host "   Working directory: $serverDir" -ForegroundColor Gray
Write-Host "   Command: $serverPath --port $port" -ForegroundColor Gray
Write-Host ""

try {
    # Запускаем сервер в новом окне, чтобы видеть вывод
    Write-Host "   🚀 Launching server..." -ForegroundColor Cyan
    
    $process = Start-Process -FilePath $serverPath -ArgumentList "--port $port" -WorkingDirectory $serverDir -PassThru -WindowStyle Normal
    
    Write-Host "  ✅ Server process started (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "  💡 Server window should be visible now" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  ⏳ Waiting 5 seconds for server to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
} catch {
    Write-Host "  ❌ Failed to start server: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Try running manually:" -ForegroundColor Yellow
    Write-Host "  cd `"$serverDir`"" -ForegroundColor White
    Write-Host "  .\$(Split-Path $serverPath -Leaf) --port $port" -ForegroundColor White
    exit 1
}

Write-Host ""

# Шаг 4: Проверка работы
Write-Host "[4/4] Verifying server is running..." -ForegroundColor Yellow

# Проверка порта
$check = netstat -ano | Select-String "LISTENING" | Select-String ":$port\s"
if ($check) {
    Write-Host "  ✅ Port $port is now LISTENING!" -ForegroundColor Green
    Write-Host ""
    
    # Проверка API
    Write-Host "  🔍 Testing API endpoint..." -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/v1/models" -Method Get -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  ✅ API is responding!" -ForegroundColor Green
        Write-Host ""
        
        if ($response.data -and $response.data.Count -gt 0) {
            Write-Host "  📦 Available models:" -ForegroundColor Cyan
            foreach ($model in $response.data) {
                $modelId = if ($model.id) { $model.id } else { $model.name }
                Write-Host "     - $modelId" -ForegroundColor White
            }
        } else {
            Write-Host "  ⚠️  No models loaded" -ForegroundColor Yellow
            Write-Host "     Load a model in LM Studio GUI first" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "✅ SUCCESS! Server is running!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📝 Add to config.env:" -ForegroundColor Cyan
        Write-Host "   LLM_PROVIDER=lmstudio" -ForegroundColor White
        Write-Host "   LLM_URL=http://localhost:$port" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 Server will keep running until you close the window" -ForegroundColor Gray
        Write-Host "   Or press Ctrl+C in the server window to stop" -ForegroundColor Gray
        Write-Host ""
        
    } catch {
        Write-Host "  ⚠️  API not responding yet: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "     Server may need more time. Wait a bit and test:" -ForegroundColor Gray
        Write-Host "     Invoke-RestMethod -Uri 'http://localhost:$port/v1/models'" -ForegroundColor White
        Write-Host ""
        Write-Host "  ✅ Port is listening, so server should be working" -ForegroundColor Green
    }
    
} else {
    Write-Host "  ❌ Port $port is still not listening" -ForegroundColor Red
    Write-Host "     Check the server window for error messages" -ForegroundColor Yellow
    Write-Host "     Process ID: $($process.Id)" -ForegroundColor Gray
}

Write-Host ""
















