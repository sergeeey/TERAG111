# Скрипт проверки статуса LM Studio API
# Автоматически находит запущенный порт и проверяет доступность API

Write-Host "`n🔍 Проверка статуса LM Studio API...`n" -ForegroundColor Cyan

# Порты, которые может использовать LM Studio
$ports = @(1234, 11434)
$activePort = $null
$activePid = $null

# Шаг 1: Проверка открытых портов
Write-Host "📡 Шаг 1: Поиск активных портов LM Studio..." -ForegroundColor Yellow

foreach ($port in $ports) {
    $listening = netstat -ano | Select-String "LISTENING" | Select-String ":$port"
    
    if ($listening) {
        Write-Host "  ✅ Порт $port активен!" -ForegroundColor Green
        
        # Извлекаем PID из строки
        $pidMatch = $listening -match '\s+(\d+)$'
        if ($pidMatch) {
            $activePid = $matches[1]
            $activePort = $port
            Write-Host "     PID процесса: $activePid" -ForegroundColor Gray
            
            # Пытаемся получить имя процесса
            try {
                $process = Get-Process -Id $activePid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "     Процесс: $($process.ProcessName)" -ForegroundColor Gray
                }
            } catch {
                # Процесс может быть недоступен
            }
            break
        }
    } else {
        Write-Host "  ❌ Порт $port не слушается" -ForegroundColor Red
    }
}

if (-not $activePort) {
    Write-Host "`n⚠️  LM Studio API не запущен!" -ForegroundColor Red
    Write-Host ""
    
    # Поиск lmstudio-server.exe на системе
    Write-Host "🔍 Поиск lmstudio-server.exe..." -ForegroundColor Yellow
    
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
            Write-Host "  ✅ Найден: $path" -ForegroundColor Green
            break
        }
    }
    
    # Если не найден в стандартных местах, ищем по всему диску
    if (-not $serverPath) {
        Write-Host "  ⚠️  Не найден в стандартных местах. Поиск по системе..." -ForegroundColor Yellow
        try {
            $foundServer = Get-ChildItem -Path "$env:LOCALAPPDATA", "$env:ProgramFiles", "$env:ProgramFiles(x86)" -Filter "lmstudio-server.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($foundServer) {
                $serverPath = $foundServer.FullName
                Write-Host "  ✅ Найден: $serverPath" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ⚠️  Не удалось выполнить системный поиск (могут потребоваться права администратора)" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "📋 Рекомендации:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   1. Закройте LM Studio полностью (проверьте Диспетчер задач)" -ForegroundColor White
    Write-Host "   2. Запустите LM Studio от имени администратора (ПКМ → Запуск от имени администратора)" -ForegroundColor White
    Write-Host "   3. Загрузите любую модель и дождитесь статуса 'Ready'" -ForegroundColor White
    Write-Host "   4. Перейдите в Settings → Developer → Переключите 'Enable Local LLM Service' ВЫКЛ → ВКЛ" -ForegroundColor White
    Write-Host "   5. Подождите 5-10 секунд для сообщения: 'Local LLM Service running on http://localhost:XXXX'" -ForegroundColor White
    Write-Host ""
    
    if ($serverPath) {
        Write-Host "⚙️  Ручной запуск сервера (если GUI не работает):" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "   Откройте PowerShell от имени администратора и выполните:" -ForegroundColor Yellow
        Write-Host "   cd `"$(Split-Path $serverPath -Parent)`"" -ForegroundColor White
        Write-Host "   .\lmstudio-server.exe --port 1234" -ForegroundColor White
        Write-Host ""
        Write-Host "   Или одной командой:" -ForegroundColor Gray
        Write-Host "   & `"$serverPath`" --port 1234" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "⚠️  lmstudio-server.exe не найден. Стандартные расположения:" -ForegroundColor Yellow
        Write-Host "   - $env:LOCALAPPDATA\Programs\LM Studio\resources\server\" -ForegroundColor Gray
        Write-Host "   - $env:ProgramFiles\LM Studio\resources\server\" -ForegroundColor Gray
        Write-Host ""
    }
    
    Write-Host "   6. После запуска сервера запустите этот скрипт снова:" -ForegroundColor White
    Write-Host "      .\check-lmstudio.ps1" -ForegroundColor Gray
    Write-Host ""
    
    exit 1
}

# Шаг 2: Проверка доступности API через HTTP
Write-Host "`n🌐 Шаг 2: Проверка доступности API..." -ForegroundColor Yellow

$apiUrl = "http://localhost:$activePort"
$modelsUrl = "$apiUrl/v1/models"
$healthUrl = "$apiUrl/health"

$apiAvailable = $false
$modelsResponse = $null

try {
    Write-Host "   Проверка: $modelsUrl" -ForegroundColor Gray
    
    $response = Invoke-RestMethod -Uri $modelsUrl -Method Get -TimeoutSec 5 -ErrorAction Stop
    $apiAvailable = $true
    $modelsResponse = $response
    
    Write-Host "   ✅ API доступен!" -ForegroundColor Green
    Write-Host "   📊 Ответ API:" -ForegroundColor Cyan
    
    # Красиво форматируем JSON
    $jsonFormatted = ($response | ConvertTo-Json -Depth 3)
    Write-Host $jsonFormatted -ForegroundColor White
    
    # Проверяем наличие моделей
    if ($response.data -and $response.data.Count -gt 0) {
        Write-Host "`n   📦 Доступные модели:" -ForegroundColor Cyan
        foreach ($model in $response.data) {
            $modelId = if ($model.id) { $model.id } else { $model.name }
            Write-Host "      • $modelId" -ForegroundColor White
        }
    } else {
        Write-Host "   ⚠️  Модели не найдены (возможно, нужно загрузить модель в LM Studio)" -ForegroundColor Yellow
    }
    
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "   ❌ API недоступен: $errorMsg" -ForegroundColor Red
    
    # Дополнительная диагностика
    Write-Host "`n🔧 Дополнительная диагностика:" -ForegroundColor Yellow
    
    # Проверка брандмауэра
    Write-Host "   Проверка брандмауэра..." -ForegroundColor Gray
    try {
        $firewallRules = Get-NetFirewallRule | Where-Object { 
            $_.DisplayName -like "*LM Studio*" -or 
            $_.DisplayName -like "*lm-studio*" 
        }
        
        if ($firewallRules) {
            Write-Host "   ✅ Найдены правила брандмауэра для LM Studio" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Правила брандмауэра для LM Studio не найдены" -ForegroundColor Yellow
            Write-Host "      Рекомендуется добавить LM Studio в исключения брандмауэра" -ForegroundColor White
        }
    } catch {
        Write-Host "   ⚠️  Не удалось проверить брандмауэр (требуются права администратора)" -ForegroundColor Yellow
    }
    
    # Проверка простого TCP-соединения
    Write-Host "   Проверка TCP-соединения к порту $activePort..." -ForegroundColor Gray
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $result = $tcpClient.BeginConnect("localhost", $activePort, $null, $null)
        $wait = $result.AsyncWaitHandle.WaitOne(2000, $false)
        
        if ($wait) {
            $tcpClient.EndConnect($result)
            Write-Host "   ✅ TCP-соединение успешно" -ForegroundColor Green
            Write-Host "      Проблема, вероятно, в HTTP-протоколе или конфигурации API" -ForegroundColor Yellow
        } else {
            Write-Host "   ❌ TCP-соединение не установлено" -ForegroundColor Red
        }
        $tcpClient.Close()
    } catch {
        Write-Host "   ❌ TCP-соединение недоступно: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Итоговый результат
Write-Host "`n" + "="*60 -ForegroundColor Cyan
if ($apiAvailable) {
    Write-Host "✅ LM Studio API работает корректно!" -ForegroundColor Green
    Write-Host "`n📝 Для подключения TERAG используйте в config.env:" -ForegroundColor Cyan
    Write-Host "   LLM_PROVIDER=lmstudio" -ForegroundColor White
    Write-Host "   LLM_URL=$apiUrl" -ForegroundColor White
} else {
    Write-Host "❌ LM Studio API недоступен" -ForegroundColor Red
    Write-Host "`n📋 Действия для устранения:" -ForegroundColor Yellow
    Write-Host "   1. Убедитесь, что LM Studio запущен от имени администратора" -ForegroundColor White
    Write-Host "   2. Проверьте, что включена опция 'Enable Local LLM Service' в Settings → Developer" -ForegroundColor White
    Write-Host "   3. Проверьте брандмауэр Windows" -ForegroundColor White
    Write-Host "   4. Перезапустите LM Studio" -ForegroundColor White
}
Write-Host "="*60 -ForegroundColor Cyan
Write-Host ""

