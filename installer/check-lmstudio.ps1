# LM Studio API Check
# Проверяет доступность LM Studio API и показывает активные модели

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
            
            exit 0
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
    
    Write-Host "6. After server starts, run this script again:" -ForegroundColor White
    Write-Host "   .\check-lmstudio.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "💡 Additional help:" -ForegroundColor Cyan
    Write-Host "   .\diagnose-lmstudio.ps1              - Full diagnostics" -ForegroundColor Gray
    if ($serverPath) {
        Write-Host "   .\start-lmstudio-server.ps1          - Auto-start server (requires admin)" -ForegroundColor Gray
    }
    Write-Host ""
    
    exit 1
}
