# Расширенный поиск установки LM Studio
# Ищет все возможные файлы и расположения LM Studio

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LM Studio Deep Search" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Шаг 1: Поиск LM Studio.exe
Write-Host "[1/5] Searching for LM Studio.exe..." -ForegroundColor Yellow
$lmStudioExe = $null

$exePaths = @(
    "$env:LOCALAPPDATA\Programs\LM Studio\LM Studio.exe",
    "$env:ProgramFiles\LM Studio\LM Studio.exe",
    "$env:ProgramFiles(x86)\LM Studio\LM Studio.exe",
    "$env:USERPROFILE\AppData\Local\Programs\LM Studio\LM Studio.exe",
    "$env:ProgramFiles\LMStudio\LM Studio.exe",
    "$env:LOCALAPPDATA\Programs\LMStudio\LM Studio.exe"
)

foreach ($path in $exePaths) {
    if (Test-Path $path) {
        $lmStudioExe = $path
        Write-Host "  ✅ Found LM Studio.exe: $path" -ForegroundColor Green
        $fileInfo = Get-Item $path
        Write-Host "     Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Gray
        Write-Host "     Modified: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
        break
    }
}

if (-not $lmStudioExe) {
    Write-Host "  ❌ LM Studio.exe not found in standard locations" -ForegroundColor Red
    Write-Host "     Searching system-wide (this may take a while)..." -ForegroundColor Yellow
    
    try {
        $foundExe = Get-ChildItem -Path "$env:LOCALAPPDATA", "$env:ProgramFiles", "$env:ProgramFiles(x86)", "$env:USERPROFILE\AppData\Local" -Filter "*lmstudio*.exe" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*LM Studio*" -or $_.Name -like "*lmstudio*" } | Select-Object -First 5
        
        if ($foundExe) {
            Write-Host "  ✅ Found potential LM Studio executables:" -ForegroundColor Green
            foreach ($exe in $foundExe) {
                Write-Host "     - $($exe.FullName)" -ForegroundColor White
                if ($exe.Name -like "*LM Studio*") {
                    $lmStudioExe = $exe.FullName
                }
            }
        } else {
            Write-Host "  ❌ Not found" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ⚠️  Search failed: $_" -ForegroundColor Yellow
    }
}

Write-Host ""

# Шаг 2: Поиск директории установки
Write-Host "[2/5] Searching for LM Studio installation directory..." -ForegroundColor Yellow
if ($lmStudioExe) {
    $installDir = Split-Path $lmStudioExe -Parent
    Write-Host "  ✅ Installation directory: $installDir" -ForegroundColor Green
    
    # Проверяем структуру директории
    Write-Host "  📁 Directory contents:" -ForegroundColor Cyan
    try {
        $items = Get-ChildItem $installDir -ErrorAction SilentlyContinue | Select-Object Name, PSIsContainer
        foreach ($item in $items) {
            $type = if ($item.PSIsContainer) { "📁" } else { "📄" }
            Write-Host "     $type $($item.Name)" -ForegroundColor White
        }
    } catch {
        Write-Host "     ⚠️  Cannot list contents: $_" -ForegroundColor Yellow
    }
    
    # Ищем resources/server
    Write-Host ""
    Write-Host "  🔍 Looking for resources/server directory..." -ForegroundColor Yellow
    $serverDirs = @(
        "$installDir\resources\server",
        "$installDir\resources",
        "$installDir\server",
        "$installDir\app.asar.unpacked\resources\server"
    )
    
    foreach ($serverDir in $serverDirs) {
        if (Test-Path $serverDir) {
            Write-Host "     ✅ Found: $serverDir" -ForegroundColor Green
            
            # Ищем серверные файлы
            $serverFiles = Get-ChildItem $serverDir -File -ErrorAction SilentlyContinue | Where-Object { 
                $_.Name -like "*server*" -or 
                $_.Name -like "*lmstudio*" -or 
                $_.Extension -eq ".exe" 
            }
            
            if ($serverFiles) {
                Write-Host "     📄 Server files found:" -ForegroundColor Cyan
                foreach ($file in $serverFiles) {
                    Write-Host "        - $($file.Name) ($([math]::Round($file.Length / 1KB, 2)) KB)" -ForegroundColor White
                }
            } else {
                Write-Host "     ⚠️  No server executables found in this directory" -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host "  ⚠️  Cannot check - LM Studio.exe not found" -ForegroundColor Yellow
}

Write-Host ""

# Шаг 3: Поиск всех файлов *server*.exe
Write-Host "[3/5] Searching for any *server*.exe files..." -ForegroundColor Yellow
try {
    $serverExes = Get-ChildItem -Path "$env:LOCALAPPDATA", "$env:ProgramFiles", "$env:ProgramFiles(x86)" -Filter "*server*.exe" -Recurse -ErrorAction SilentlyContinue | Where-Object {
        $_.DirectoryName -like "*lmstudio*" -or $_.DirectoryName -like "*lm-studio*"
    } | Select-Object -First 10
    
    if ($serverExes) {
        Write-Host "  ✅ Found server executables:" -ForegroundColor Green
        foreach ($exe in $serverExes) {
            Write-Host "     - $($exe.FullName)" -ForegroundColor White
            Write-Host "       Size: $([math]::Round($exe.Length / 1KB, 2)) KB" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ❌ No server executables found" -ForegroundColor Red
    }
} catch {
    Write-Host "  ⚠️  Search failed: $_" -ForegroundColor Yellow
}

Write-Host ""

# Шаг 4: Проверка процессов LM Studio (даже если не запущены)
Write-Host "[4/5] Checking installed programs..." -ForegroundColor Yellow
try {
    $installed = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue | Where-Object {
        $_.DisplayName -like "*LM Studio*" -or $_.DisplayName -like "*lmstudio*"
    }
    
    if ($installed) {
        Write-Host "  ✅ Found in installed programs:" -ForegroundColor Green
        foreach ($app in $installed) {
            Write-Host "     - $($app.DisplayName)" -ForegroundColor White
            if ($app.InstallLocation) {
                Write-Host "       Location: $($app.InstallLocation)" -ForegroundColor Gray
                
                # Проверяем эту директорию
                if (Test-Path $app.InstallLocation) {
                    $serverPath = Join-Path $app.InstallLocation "resources\server\lmstudio-server.exe"
                    if (Test-Path $serverPath) {
                        Write-Host "       ✅ Server found at: $serverPath" -ForegroundColor Green
                    }
                }
            }
        }
    } else {
        Write-Host "  ⚠️  Not found in registry (may be portable installation)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠️  Cannot check registry: $_" -ForegroundColor Yellow
}

Write-Host ""

# Шаг 5: Поиск по ярлыкам
Write-Host "[5/5] Checking desktop and start menu shortcuts..." -ForegroundColor Yellow
$shortcutPaths = @(
    "$env:USERPROFILE\Desktop\LM Studio.lnk",
    "$env:USERPROFILE\Desktop\lmstudio.lnk",
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\LM Studio.lnk",
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\lmstudio.lnk"
)

foreach ($shortcut in $shortcutPaths) {
    if (Test-Path $shortcut) {
        Write-Host "  ✅ Found shortcut: $shortcut" -ForegroundColor Green
        try {
            $shell = New-Object -ComObject WScript.Shell
            $link = $shell.CreateShortcut($shortcut)
            if ($link.TargetPath) {
                Write-Host "     Target: $($link.TargetPath)" -ForegroundColor White
                if (Test-Path $link.TargetPath) {
                    $targetDir = Split-Path $link.TargetPath -Parent
                    Write-Host "     Directory: $targetDir" -ForegroundColor Gray
                }
            }
        } catch {
            Write-Host "     ⚠️  Cannot read shortcut: $_" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($lmStudioExe) {
    Write-Host "✅ LM Studio is installed at:" -ForegroundColor Green
    Write-Host "   $lmStudioExe" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Start LM Studio from this location" -ForegroundColor White
    Write-Host "2. Run it as Administrator" -ForegroundColor White
    Write-Host "3. Load a model and enable 'Local LLM Service' in Settings → Developer" -ForegroundColor White
    Write-Host ""
    Write-Host "If server files are missing, you may need to:" -ForegroundColor Yellow
    Write-Host "- Reinstall LM Studio" -ForegroundColor White
    Write-Host "- Update to latest version" -ForegroundColor White
    Write-Host "- Check if this is a portable version (server may be in different location)" -ForegroundColor White
} else {
    Write-Host "❌ LM Studio installation not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible reasons:" -ForegroundColor Yellow
    Write-Host "- LM Studio is not installed" -ForegroundColor White
    Write-Host "- Installed in non-standard location" -ForegroundColor White
    Write-Host "- Portable version in unexpected location" -ForegroundColor White
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Cyan
    Write-Host "1. Install LM Studio from https://lmstudio.ai" -ForegroundColor White
    Write-Host "2. Or provide the installation path manually" -ForegroundColor White
}

Write-Host ""
















