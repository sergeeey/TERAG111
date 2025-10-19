# Ollama Model Launcher
# Быстрый запуск моделей Ollama для тестирования

Write-Host "Ollama Model Launcher" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

# Проверяем, запущен ли Ollama
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "OK: Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Ollama is not running. Starting Ollama..." -ForegroundColor Red
    Start-Process -FilePath "C:\Users\serge\AppData\Local\Programs\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Minimized
    Start-Sleep -Seconds 3
    Write-Host "OK: Ollama started" -ForegroundColor Green
}

Write-Host ""

# Получаем список моделей
Write-Host "Available models:" -ForegroundColor Yellow
Write-Host "================" -ForegroundColor Yellow

$models = @(
    @{Name="nous-hermes2:10.7b"; Description="Судья / консенсус-агент (6.1 GB)"; Role="Оценка, взвешивание аргументов"},
    @{Name="qwen2.5:7b-instruct"; Description="Философ / аналитик-рассуждатель (4.7 GB)"; Role="Анализ и рассуждения"},
    @{Name="deepseek-coder:6.7b"; Description="Программист / инженерный агент (3.8 GB)"; Role="Кодирование и инженерия"},
    @{Name="mistral:latest"; Description="Архитектор рассуждений (4.4 GB)"; Role="Генерация сценариев"},
    @{Name="phi3:latest"; Description="Быстрый гипотетик (2.2 GB)"; Role="Lightweight reasoning"},
    @{Name="deepseek-coder:latest"; Description="Квантованная версия кодера (776 MB)"; Role="Быстрые ответы"}
)

for ($i = 0; $i -lt $models.Count; $i++) {
    $model = $models[$i]
    Write-Host "$($i + 1). $($model.Name)" -ForegroundColor White
    Write-Host "   $($model.Description)" -ForegroundColor Gray
    Write-Host "   Role: $($model.Role)" -ForegroundColor DarkGray
    Write-Host ""
}

# Выбор модели
Write-Host "Select model (1-$($models.Count)): " -NoNewline -ForegroundColor Cyan
$choice = Read-Host

if ($choice -match "^\d+$" -and [int]$choice -ge 1 -and [int]$choice -le $models.Count) {
    $selectedModel = $models[[int]$choice - 1]
    Write-Host ""
    Write-Host "Selected: $($selectedModel.Name)" -ForegroundColor Green
    Write-Host "Description: $($selectedModel.Description)" -ForegroundColor Gray
    Write-Host "Role: $($selectedModel.Role)" -ForegroundColor DarkGray
    Write-Host ""
    
    # Запуск модели
    Write-Host "Starting model..." -ForegroundColor Yellow
    Write-Host "Type 'exit' to quit the chat" -ForegroundColor DarkGray
    Write-Host "=" * 50 -ForegroundColor DarkGray
    
    # Запускаем ollama run
    & "C:\Users\serge\AppData\Local\Programs\Ollama\ollama.exe" run $selectedModel.Name
} else {
    Write-Host "Invalid selection. Exiting..." -ForegroundColor Red
}

Write-Host ""
Write-Host "Launcher finished." -ForegroundColor Cyan
