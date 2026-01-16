# Скрипт установки и настройки LM Studio для TERAG
# Помогает скачать, установить и настроить LM Studio API

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LM Studio Installation Guide" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Write-Host "📋 Installation Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Download LM Studio" -ForegroundColor Yellow
Write-Host "   Visit: https://lmstudio.ai" -ForegroundColor White
Write-Host "   Or direct link: https://lmstudio.ai/download" -ForegroundColor White
Write-Host ""
Write-Host "   ⚠️  IMPORTANT: Download the EXE installer (not Store version)" -ForegroundColor Yellow
Write-Host "      Store version may not have server files!" -ForegroundColor Yellow
Write-Host ""

# Проверка, есть ли уже установка
Write-Host "2. Checking if LM Studio is already installed..." -ForegroundColor Yellow
$lmStudioExe = $null
$searchPaths = @(
    "$env:LOCALAPPDATA\Programs\LM Studio\LM Studio.exe",
    "$env:ProgramFiles\LM Studio\LM Studio.exe",
    "$env:ProgramFiles(x86)\LM Studio\LM Studio.exe"
)

foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        $lmStudioExe = $path
        Write-Host "   ✅ Found existing installation: $path" -ForegroundColor Green
        break
    }
}

if ($lmStudioExe) {
    Write-Host ""
    Write-Host "   💡 LM Studio is already installed!" -ForegroundColor Cyan
    Write-Host "   Run the setup script instead:" -ForegroundColor White
    Write-Host "   .\setup-lmstudio-api.ps1" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "   ❌ LM Studio not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "3. Installation Instructions:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   a) Run the downloaded installer" -ForegroundColor White
    Write-Host "   b) Install to default location (recommended)" -ForegroundColor Gray
    Write-Host "      Usually: $env:LOCALAPPDATA\Programs\LM Studio" -ForegroundColor Gray
    Write-Host "   c) Complete the installation" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   ⚠️  After installation:" -ForegroundColor Yellow
    Write-Host "      - DO NOT start LM Studio yet" -ForegroundColor White
    Write-Host "      - Run this script again to verify installation" -ForegroundColor White
    Write-Host "      - Or run: .\setup-lmstudio-api.ps1" -ForegroundColor White
    Write-Host ""
}

Write-Host "4. Post-Installation Setup:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   After installation, you need to:" -ForegroundColor White
Write-Host "   1. Start LM Studio as Administrator" -ForegroundColor Gray
Write-Host "   2. Download/load at least one model" -ForegroundColor Gray
Write-Host "   3. Enable Local LLM Service in Settings → Developer" -ForegroundColor Gray
Write-Host ""
Write-Host "   💡 Use the setup script to automate this:" -ForegroundColor Cyan
Write-Host "   .\setup-lmstudio-api.ps1" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Actions:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open LM Studio website:" -ForegroundColor White
Write-Host "   Start-Process 'https://lmstudio.ai'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Check if installed (after downloading):" -ForegroundColor White
Write-Host "   .\find-lmstudio.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Setup API (after installation):" -ForegroundColor White
Write-Host "   .\setup-lmstudio-api.ps1" -ForegroundColor Gray
Write-Host ""

$response = Read-Host "Open LM Studio download page in browser? (y/N)"
if ($response -eq "y" -or $response -eq "Y") {
    Start-Process "https://lmstudio.ai"
    Write-Host "✅ Browser opened" -ForegroundColor Green
}

Write-Host ""
















