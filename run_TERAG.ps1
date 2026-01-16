# ============================================
# TERAG AI System Launcher
# Автоматический запуск TERAG одним кликом
# ============================================

Write-Host "🚀 Starting TERAG AI System..." -ForegroundColor Cyan
Write-Host ""

# Переходим в директорию проекта
$projectDir = "D:\TERAG111-1"
cd $projectDir

# Проверяем Python
Write-Host "📋 Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Запускаем API сервер
Write-Host ""
Write-Host "🌐 Starting API server..." -ForegroundColor Yellow
Write-Host "   Listening on: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""

# Открываем PowerShell для сервера в фоне
Start-Process powershell -ArgumentList @(
    '-NoExit',
    '-Command',
    "cd '$projectDir'; python scripts/run_api.py"
) -WindowStyle Normal

# Ждём запуска сервера
Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Проверяем доступность
$maxAttempts = 10
$attempt = 0
$serverReady = $false

while ($attempt -lt $maxAttempts -and -not $serverReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $serverReady = $true
        }
    } catch {
        $attempt++
        Start-Sleep -Seconds 1
    }
}

if ($serverReady) {
    Write-Host "✅ Server is ready!" -ForegroundColor Green
    Write-Host ""
    
    # Открываем дашборд в браузере
    Write-Host "🌐 Opening TERAG Dashboard..." -ForegroundColor Cyan
    $dashboardUrl = "http://127.0.0.1:8000/api/static/index.html"
    Start-Process $dashboardUrl
    
    Write-Host ""
    Write-Host "✅ TERAG is running!" -ForegroundColor Green
    Write-Host "📍 Dashboard: $dashboardUrl" -ForegroundColor White
    Write-Host "📍 API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Keep this window open to maintain the server" -ForegroundColor Yellow
    Write-Host "💡 Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    
    # Ждём нажатия клавиши для завершения
    Write-Host "Press any key to stop TERAG..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    Write-Host ""
    Write-Host "🛑 Stopping TERAG..." -ForegroundColor Yellow
    
    # Останавливаем все Python процессы
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    
    Write-Host "✅ TERAG stopped" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "❌ Server failed to start" -ForegroundColor Red
    Write-Host "💡 Check if port 8000 is available" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}



























