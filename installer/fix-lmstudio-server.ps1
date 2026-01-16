# Автоматическое исправление отсутствующего LM Studio Server
# Скачивает ZIP-архив, распаковывает и копирует папку server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LM Studio Server Fix" -ForegroundColor Yellow
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

# Шаг 1: Поиск установки LM Studio
Write-Host "[1/6] Finding LM Studio installation..." -ForegroundColor Yellow
$lmStudioExe = $null
$installDir = $null

$searchPaths = @(
    "$env:LOCALAPPDATA\Programs\LM Studio\LM Studio.exe",
    "$env:ProgramFiles\LM Studio\LM Studio.exe",
    "$env:ProgramFiles(x86)\LM Studio\LM Studio.exe"
)

foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        $lmStudioExe = $path
        $installDir = Split-Path $path -Parent
        Write-Host "  ✅ Found: $installDir" -ForegroundColor Green
        break
    }
}

if (-not $installDir) {
    Write-Host "  ❌ LM Studio not found!" -ForegroundColor Red
    Write-Host "     Please install LM Studio first from https://lmstudio.ai" -ForegroundColor Yellow
    exit 1
}

$resourcesDir = Join-Path $installDir "resources"
$serverDir = Join-Path $resourcesDir "server"
$serverExe = Join-Path $serverDir "lmstudio-server.exe"

# Проверка, есть ли уже server
Write-Host ""
Write-Host "[2/6] Checking if server already exists..." -ForegroundColor Yellow
if (Test-Path $serverExe) {
    Write-Host "  ✅ Server already exists: $serverExe" -ForegroundColor Green
    $fileInfo = Get-Item $serverExe
    Write-Host "     Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Gray
    
    $response = Read-Host "  Server exists. Re-download and replace? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "  Skipping download. Server file exists." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  To start server, run:" -ForegroundColor Cyan
        Write-Host "  .\quick-start-lmstudio.ps1" -ForegroundColor White
        exit 0
    }
}

Write-Host "  ❌ Server not found or will be replaced" -ForegroundColor Yellow

Write-Host ""

# Шаг 3: Информация о скачивании
Write-Host "[3/6] Download Information:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  You need to download LM Studio ZIP archive manually:" -ForegroundColor White
Write-Host ""
Write-Host "  Option 1: GitHub Releases" -ForegroundColor Cyan
Write-Host "    https://github.com/LM-Studio/LM-Studio/releases" -ForegroundColor White
Write-Host "    Look for: Windows-x64.zip (latest stable version)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Option 2: Official Website" -ForegroundColor Cyan
Write-Host "    https://lmstudio.ai/downloads" -ForegroundColor White
Write-Host "    Download portable ZIP version" -ForegroundColor Gray
Write-Host ""

$response = Read-Host "Open GitHub releases page in browser? (y/N)"
if ($response -eq "y" -or $response -eq "Y") {
    Start-Process "https://github.com/LM-Studio/LM-Studio/releases"
    Write-Host "  ✅ Browser opened" -ForegroundColor Green
}

Write-Host ""
Write-Host "  After downloading, you have two options:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  A) Automatic: Provide path to downloaded ZIP file" -ForegroundColor Cyan
Write-Host "  B) Manual: Extract ZIP and provide path to extracted folder" -ForegroundColor Cyan
Write-Host ""

$option = Read-Host "Choose option (A/B) or press Enter to skip"
if ($option -eq "" -or $option -eq "skip") {
    Write-Host ""
    Write-Host "  Manual instructions:" -ForegroundColor Yellow
    Write-Host "  1. Download LM Studio ZIP archive" -ForegroundColor White
    Write-Host "  2. Extract it to a temporary folder (e.g., C:\Temp\LM-Studio)" -ForegroundColor White
    Write-Host "  3. Run this command:" -ForegroundColor White
    Write-Host "     Copy-Item -Path `"C:\Temp\LM-Studio\resources\server`" -Destination `"$resourcesDir`" -Recurse -Force" -ForegroundColor Gray
    Write-Host "  4. Then run: .\quick-start-lmstudio.ps1" -ForegroundColor White
    exit 0
}

# Шаг 4: Обработка ZIP или папки
Write-Host ""
Write-Host "[4/6] Processing..." -ForegroundColor Yellow

if ($option -eq "A" -or $option -eq "a") {
    # ZIP файл
    $zipPath = Read-Host "Enter full path to downloaded ZIP file"
    
    if (-not (Test-Path $zipPath)) {
        Write-Host "  ❌ File not found: $zipPath" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  ✅ ZIP file found" -ForegroundColor Green
    Write-Host "  📦 Extracting..." -ForegroundColor Yellow
    
    $tempDir = Join-Path $env:TEMP "LM-Studio-Extract"
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    try {
        Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
        Write-Host "  ✅ Extracted successfully" -ForegroundColor Green
        
        # Ищем папку server в распакованном архиве
        $extractedServer = Get-ChildItem -Path $tempDir -Filter "server" -Recurse -Directory -ErrorAction SilentlyContinue | Where-Object {
            $_.FullName -like "*resources\server" -or $_.Parent.Name -eq "resources"
        } | Select-Object -First 1
        
        if ($extractedServer) {
            $sourceServerDir = $extractedServer.FullName
        } else {
            # Попробуем найти через resources
            $resourcesInExtract = Get-ChildItem -Path $tempDir -Filter "resources" -Recurse -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($resourcesInExtract) {
                $sourceServerDir = Join-Path $resourcesInExtract.FullName "server"
            } else {
                Write-Host "  ❌ Could not find server folder in extracted archive" -ForegroundColor Red
                Write-Host "     Please check the archive structure manually" -ForegroundColor Yellow
                Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
                exit 1
            }
        }
        
        if (-not (Test-Path $sourceServerDir)) {
            Write-Host "  ❌ Server folder not found at: $sourceServerDir" -ForegroundColor Red
            Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
            exit 1
        }
        
    } catch {
        Write-Host "  ❌ Failed to extract ZIP: $_" -ForegroundColor Red
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        exit 1
    }
    
} elseif ($option -eq "B" -or $option -eq "b") {
    # Извлеченная папка
    $extractedPath = Read-Host "Enter full path to extracted LM Studio folder"
    
    if (-not (Test-Path $extractedPath)) {
        Write-Host "  ❌ Folder not found: $extractedPath" -ForegroundColor Red
        exit 1
    }
    
    # Ищем server в указанной папке
    $sourceServerDir = Join-Path $extractedPath "resources\server"
    
    if (-not (Test-Path $sourceServerDir)) {
        # Попробуем найти рекурсивно
        $foundServer = Get-ChildItem -Path $extractedPath -Filter "server" -Recurse -Directory -ErrorAction SilentlyContinue | Where-Object {
            $_.Parent.Name -eq "resources"
        } | Select-Object -First 1
        
        if ($foundServer) {
            $sourceServerDir = $foundServer.FullName
        } else {
            Write-Host "  ❌ Server folder not found in: $extractedPath" -ForegroundColor Red
            Write-Host "     Expected: $extractedPath\resources\server" -ForegroundColor Yellow
            exit 1
        }
    }
    
    $tempDir = $null
} else {
    Write-Host "  ❌ Invalid option selected. Please choose A or B." -ForegroundColor Red
    exit 1
}

# Проверка, что в папке server есть exe файл
if (-not $sourceServerDir -or -not (Test-Path (Join-Path $sourceServerDir "lmstudio-server.exe"))) {
    Write-Host "  ❌ lmstudio-server.exe not found in: $sourceServerDir" -ForegroundColor Red
    if ($tempDir) {
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    exit 1
}

Write-Host "  ✅ Server folder found: $sourceServerDir" -ForegroundColor Green

Write-Host ""

# Шаг 5: Копирование
Write-Host "[5/6] Copying server folder..." -ForegroundColor Yellow

# Создаем resources директорию, если её нет
if (-not (Test-Path $resourcesDir)) {
    Write-Host "  Creating resources directory..." -ForegroundColor Gray
    New-Item -ItemType Directory -Path $resourcesDir -Force | Out-Null
}

try {
    Write-Host "  Copying from: $sourceServerDir" -ForegroundColor Gray
    Write-Host "  Copying to: $serverDir" -ForegroundColor Gray
    
    # Удаляем старую папку server, если есть
    if (Test-Path $serverDir) {
        Write-Host "  Removing old server folder..." -ForegroundColor Gray
        Remove-Item $serverDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Copy-Item -Path $sourceServerDir -Destination $serverDir -Recurse -Force
    Write-Host "  ✅ Server folder copied successfully!" -ForegroundColor Green
    
    # Проверка
    if (Test-Path $serverExe) {
        $fileInfo = Get-Item $serverExe
        Write-Host "  ✅ Server file verified: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Warning: Server file not found after copy" -ForegroundColor Yellow
    }
    
    # Удаляем временную папку
    if ($tempDir -and (Test-Path $tempDir)) {
        Write-Host "  Cleaning up temporary files..." -ForegroundColor Gray
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    
} catch {
    Write-Host "  ❌ Failed to copy: $_" -ForegroundColor Red
    if ($tempDir) {
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    exit 1
}

Write-Host ""

# Шаг 6: Финальная проверка и запуск
Write-Host "[6/6] Final verification..." -ForegroundColor Yellow

if (Test-Path $serverExe) {
    Write-Host "  ✅ Server installation complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Server files installed to:" -ForegroundColor Cyan
    Write-Host "  $serverDir" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Start the server:" -ForegroundColor White
    Write-Host "     .\quick-start-lmstudio.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Or manually:" -ForegroundColor White
    Write-Host "     & `"$serverExe`" --port 1234" -ForegroundColor Gray
    Write-Host ""
    
    $startNow = Read-Host "Start server now? (y/N)"
    if ($startNow -eq "y" -or $startNow -eq "Y") {
        Write-Host ""
        Write-Host "Starting server..." -ForegroundColor Yellow
        & $serverExe --port 1234
    }
    
} else {
    Write-Host "  ❌ Server file not found after installation!" -ForegroundColor Red
    Write-Host "     Please check the copy operation manually" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

