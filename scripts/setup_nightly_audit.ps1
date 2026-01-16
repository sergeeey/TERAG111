# PowerShell скрипт для настройки ночного аудита в Windows Task Scheduler
# Запуск: .\scripts\setup_nightly_audit.ps1

param(
    [string]$PythonPath = "python",
    [string]$ProjectPath = (Get-Location).Path,
    [string]$TaskName = "TERAG-Nightly-Audit",
    [string]$StartTime = "02:00"
)

Write-Host "🔧 Настройка ночного аудита TERAG AI-REPS" -ForegroundColor Cyan
Write-Host "Проект: $ProjectPath" -ForegroundColor Gray
Write-Host "Python: $PythonPath" -ForegroundColor Gray
Write-Host "Время запуска: $StartTime" -ForegroundColor Gray

# Проверяем права администратора
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "⚠️ Для создания задачи в Task Scheduler требуются права администратора"
    Write-Host "Запустите PowerShell от имени администратора и повторите команду" -ForegroundColor Yellow
    exit 1
}

# Создаём директории для отчётов
$reportsDir = Join-Path $ProjectPath "audit_reports\nightly"
$logsDir = Join-Path $ProjectPath "logs"

if (-not (Test-Path $reportsDir)) {
    New-Item -ItemType Directory -Path $reportsDir -Force | Out-Null
    Write-Host "✅ Создана директория отчётов: $reportsDir" -ForegroundColor Green
}

if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    Write-Host "✅ Создана директория логов: $logsDir" -ForegroundColor Green
}

# Путь к скрипту ночного аудита
$auditScript = Join-Path $ProjectPath "scripts\nightly_audit.py"
$configFile = Join-Path $ProjectPath ".auditconfig.yaml"

# Проверяем существование файлов
if (-not (Test-Path $auditScript)) {
    Write-Error "❌ Скрипт ночного аудита не найден: $auditScript"
    exit 1
}

if (-not (Test-Path $configFile)) {
    Write-Warning "⚠️ Файл конфигурации не найден: $configFile"
    Write-Host "Создайте .auditconfig.yaml перед запуском" -ForegroundColor Yellow
}

# Создаём команду для выполнения
$command = "`"$PythonPath`" `"$auditScript`" --config `"$configFile`""
$workingDirectory = $ProjectPath

Write-Host "Команда для выполнения:" -ForegroundColor Cyan
Write-Host "  $command" -ForegroundColor Gray
Write-Host "Рабочая директория: $workingDirectory" -ForegroundColor Gray

# Удаляем существующую задачу, если есть
try {
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "🗑️ Удалена существующая задача: $TaskName" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ℹ️ Задача $TaskName не существует" -ForegroundColor Gray
}

# Создаём новую задачу
try {
    # Действие задачи
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$command`"" -WorkingDirectory $workingDirectory
    
    # Триггер (ежедневно в указанное время)
    $trigger = New-ScheduledTaskTrigger -Daily -At $StartTime
    
    # Настройки задачи
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
    
    # Принципал (пользователь)
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    
    # Создаём задачу
    $task = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "TERAG AI-REPS Nightly Environment Audit - автоматический ночной аудит окружения разработки"
    
    # Регистрируем задачу
    Register-ScheduledTask -TaskName $TaskName -InputObject $task | Out-Null
    
    Write-Host "✅ Задача создана успешно: $TaskName" -ForegroundColor Green
    Write-Host "📅 Время запуска: ежедневно в $StartTime" -ForegroundColor Green
    
} catch {
    Write-Error "❌ Ошибка создания задачи: $($_.Exception.Message)"
    exit 1
}

# Проверяем созданную задачу
try {
    $createdTask = Get-ScheduledTask -TaskName $TaskName
    Write-Host "`n📋 Информация о задаче:" -ForegroundColor Cyan
    Write-Host "  Имя: $($createdTask.TaskName)" -ForegroundColor Gray
    Write-Host "  Состояние: $($createdTask.State)" -ForegroundColor Gray
    Write-Host "  Автор: $($createdTask.Author)" -ForegroundColor Gray
    Write-Host "  Описание: $($createdTask.Description)" -ForegroundColor Gray
} catch {
    Write-Warning "⚠️ Не удалось получить информацию о созданной задаче"
}

# Создаём тестовый скрипт
$testScript = Join-Path $ProjectPath "scripts\test_nightly_audit.ps1"
$testScriptContent = @"
# Тестовый запуск ночного аудита
Write-Host "🧪 Тестовый запуск ночного аудита TERAG AI-REPS" -ForegroundColor Cyan

Set-Location "$ProjectPath"

# Устанавливаем переменные окружения
`$env:PYTHONPATH = "$ProjectPath\src"

# Запускаем аудит
& "$PythonPath" "$auditScript" --environment-only --config "$configFile"

Write-Host "`n✅ Тест завершён. Проверьте результаты в audit_reports/nightly/" -ForegroundColor Green
"@

Set-Content -Path $testScript -Value $testScriptContent -Encoding UTF8
Write-Host "`n✅ Создан тестовый скрипт: $testScript" -ForegroundColor Green

# Создаём скрипт для ручного запуска
$manualScript = Join-Path $ProjectPath "scripts\run_nightly_audit.ps1"
$manualScriptContent = @"
# Ручной запуск ночного аудита
Write-Host "🌙 Ручной запуск ночного аудита TERAG AI-REPS" -ForegroundColor Cyan

Set-Location "$ProjectPath"

# Устанавливаем переменные окружения
`$env:PYTHONPATH = "$ProjectPath\src"

# Запускаем полный аудит
& "$PythonPath" "$auditScript" --config "$configFile"

Write-Host "`n✅ Аудит завершён. Проверьте результаты в audit_reports/nightly/" -ForegroundColor Green
"@

Set-Content -Path $manualScript -Value $manualScriptContent -Encoding UTF8
Write-Host "✅ Создан скрипт ручного запуска: $manualScript" -ForegroundColor Green

Write-Host "`n🎉 Настройка ночного аудита завершена!" -ForegroundColor Green
Write-Host "`n📝 Доступные команды:" -ForegroundColor Cyan
Write-Host "  Тест аудита: .\scripts\test_nightly_audit.ps1" -ForegroundColor Gray
Write-Host "  Ручной запуск: .\scripts\run_nightly_audit.ps1" -ForegroundColor Gray
Write-Host "  Просмотр задач: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "  Запуск задачи: Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "  Остановка задачи: Stop-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray

Write-Host "`n🌐 Дашборд мониторинга:" -ForegroundColor Cyan
Write-Host "  URL: http://localhost:8000/audit-dashboard.html" -ForegroundColor Gray
Write-Host "  (запустите API: python scripts/run_api.py)" -ForegroundColor Gray



































