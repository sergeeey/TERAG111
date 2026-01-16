#!/usr/bin/env pwsh
# TERAG Deployment Script
# Автоматическое развёртывание и настройка TERAG

Write-Host "🚀 TERAG Deployment Script" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Проверка Python
Write-Host "📋 Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green

# Проверка Ollama
Write-Host "📋 Checking Ollama..." -ForegroundColor Yellow
try {
    $ollamaList = ollama list 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Ollama not running. Install from: https://ollama.ai" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Ollama is ready" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Ollama not available" -ForegroundColor Yellow
}

# Проверка зависимостей
Write-Host "📋 Checking dependencies..." -ForegroundColor Yellow
$requirements = "requirements.txt"
if (Test-Path $requirements) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    pip install -r $requirements --quiet
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  No requirements.txt found" -ForegroundColor Yellow
}

# Проверка структуры данных
Write-Host "📋 Checking data structure..." -ForegroundColor Yellow
if (!(Test-Path "data/graph_results")) {
    New-Item -ItemType Directory -Path "data/graph_results" -Force | Out-Null
    Write-Host "✅ Created data/graph_results" -ForegroundColor Green
}

if (!(Test-Path "data/converted")) {
    New-Item -ItemType Directory -Path "data/converted" -Force | Out-Null
    Write-Host "✅ Created data/converted" -ForegroundColor Green
}

# Проверка конфигурации
Write-Host "📋 Checking configuration..." -ForegroundColor Yellow
if (!(Test-Path "data/config")) {
    New-Item -ItemType Directory -Path "data/config" -Force | Out-Null
    Write-Host "✅ Created data/config" -ForegroundColor Green
}

# Вывод информации о системе
Write-Host ""
Write-Host "📊 System Information" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host "📍 API Endpoint: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "🌐 Dashboard: http://127.0.0.1:8000/api/static/index.html" -ForegroundColor White
Write-Host "📚 Documentation: docs/TERAG_DEPLOYMENT_PACK.md" -ForegroundColor White
Write-Host ""

# Варианты запуска
Write-Host "🎯 Startup Options" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host "1. Local only (localhost)" -ForegroundColor White
Write-Host "2. Network access (0.0.0.0)" -ForegroundColor White
Write-Host "3. Background service" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Select option (1-3)"

switch ($choice) {
    "1" {
        Write-Host "🚀 Starting TERAG (localhost only)..." -ForegroundColor Green
        python scripts/run_api.py
    }
    "2" {
        Write-Host "🚀 Starting TERAG (network access)..." -ForegroundColor Green
        Write-Host "⚠️  Configuring firewall..." -ForegroundColor Yellow
        New-NetFirewallRule -DisplayName "TERAG API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -ErrorAction SilentlyContinue
        Write-Host "🌐 System accessible at: http://$(hostname):8000/api/static/index.html" -ForegroundColor Green
        python scripts/run_api.py --host 0.0.0.0 --port 8000
    }
    "3" {
        Write-Host "🚀 Starting TERAG as background service..." -ForegroundColor Green
        Start-Process python -ArgumentList "scripts/run_api.py" -WindowStyle Hidden
        Write-Host "✅ TERAG is running in background" -ForegroundColor Green
        Write-Host "📊 Open: http://127.0.0.1:8000/api/static/index.html" -ForegroundColor Cyan
    }
    default {
        Write-Host "❌ Invalid option" -ForegroundColor Red
    }
}



























