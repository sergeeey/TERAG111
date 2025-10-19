# Cursor IDE + Ollama Setup
# Быстрая настройка Cursor для работы с локальным Ollama

Write-Host "Cursor IDE + Ollama Setup" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Проверяем Ollama
Write-Host "1. Checking Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "OK: Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Ollama is not running. Starting Ollama..." -ForegroundColor Red
    Start-Process -FilePath "C:\Users\serge\AppData\Local\Programs\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Minimized
    Start-Sleep -Seconds 3
    Write-Host "OK: Ollama started" -ForegroundColor Green
}

# Получаем список моделей
Write-Host "2. Available models:" -ForegroundColor Yellow
try {
    $modelsResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET
    $modelsData = $modelsResponse.Content | ConvertFrom-Json
    $models = $modelsData.models | ForEach-Object { $_.name }
    
    Write-Host "Found models:" -ForegroundColor Green
    foreach ($model in $models) {
        Write-Host "  - $model" -ForegroundColor White
    }
} catch {
    Write-Host "WARNING: Could not fetch models list" -ForegroundColor Yellow
}

Write-Host ""

# Создаем конфигурацию Cursor
Write-Host "3. Creating Cursor configuration..." -ForegroundColor Yellow

$cursorConfig = @{
    "cursor_ai_models" = @{
        "deepseek-coder" = @{
            "provider" = "openai"
            "model" = "deepseek-coder:6.7b"
            "baseURL" = "http://localhost:11434/v1"
            "apiKey" = "ollama"
            "description" = "DeepSeek Coder - Программист / инженерный агент"
        }
        "qwen2.5-instruct" = @{
            "provider" = "openai"
            "model" = "qwen2.5:7b-instruct"
            "baseURL" = "http://localhost:11434/v1"
            "apiKey" = "ollama"
            "description" = "Qwen2.5 - Философ / аналитик-рассуждатель"
        }
        "nous-hermes2" = @{
            "provider" = "openai"
            "model" = "nous-hermes2:10.7b"
            "baseURL" = "http://localhost:11434/v1"
            "apiKey" = "ollama"
            "description" = "Nous Hermes2 - Судья / консенсус-агент"
        }
        "mistral" = @{
            "provider" = "openai"
            "model" = "mistral:latest"
            "baseURL" = "http://localhost:11434/v1"
            "apiKey" = "ollama"
            "description" = "Mistral - Архитектор рассуждений"
        }
        "phi3" = @{
            "provider" = "openai"
            "model" = "phi3:latest"
            "baseURL" = "http://localhost:11434/v1"
            "apiKey" = "ollama"
            "description" = "Phi3 - Быстрый гипотетик"
        }
    }
    "mcp_servers" = @{
        "local_rag" = @{
            "name" = "local_rag"
            "command" = "python"
            "args" = @("ask_rag.py")
            "type" = "local"
            "description" = "RAG поиск по кодовой базе"
        }
        "quick_rag" = @{
            "name" = "quick_rag"
            "command" = "python"
            "args" = @("quick_rag.py")
            "type" = "local"
            "description" = "Быстрый RAG поиск"
        }
    }
    "workspace_settings" = @{
        "ai.model" = "deepseek-coder"
        "ai.enableCodeActions" = $true
        "ai.enableChat" = $true
        "ai.enableCompletions" = $true
        "ai.enableVoice" = $true
    }
}

# Сохраняем конфигурацию
$configPath = "cursor_ollama_config.json"
$cursorConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "OK: Configuration saved to $configPath" -ForegroundColor Green

# Создаем инструкции
$instructions = @"
# Cursor IDE + Ollama Setup Instructions

## 🎯 Manual Setup Steps

### 1. AI Models Configuration
1. Open Cursor IDE
2. Go to Settings → AI Models
3. Click "Add Custom Model"
4. Configure each model:

**DeepSeek Coder (Recommended for coding):**
- Provider: OpenAI
- Base URL: http://localhost:11434/v1
- API Key: ollama
- Model: deepseek-coder:6.7b

**Qwen2.5 (For reasoning):**
- Provider: OpenAI
- Base URL: http://localhost:11434/v1
- API Key: ollama
- Model: qwen2.5:7b-instruct

**Nous Hermes2 (For evaluation):**
- Provider: OpenAI
- Base URL: http://localhost:11434/v1
- API Key: ollama
- Model: nous-hermes2:10.7b

### 2. MCP Servers Configuration
1. Go to Settings → MCP Servers
2. Click "Add Server"
3. Configure RAG servers:

**Local RAG:**
- Name: local_rag
- Command: python
- Args: ask_rag.py

**Quick RAG:**
- Name: quick_rag
- Command: python
- Args: quick_rag.py

### 3. Test the Setup
1. Open a chat in Cursor
2. Select "deepseek-coder" as your model
3. Ask: "Explain the loadGraph function in this codebase"
4. Use @local_rag to search the codebase

## 🚀 Quick Commands

# Test Ollama directly
curl http://localhost:11434

# Test RAG search
python quick_rag.py "loadGraph function"

# Launch model launcher
powershell -ExecutionPolicy Bypass -File .\ollama-launcher.ps1

## 📊 Model Roles

- **deepseek-coder:6.7b** - Best for coding tasks
- **qwen2.5:7b-instruct** - Best for reasoning and analysis
- **nous-hermes2:10.7b** - Best for evaluation and consensus
- **mistral:latest** - Best for general tasks
- **phi3:latest** - Fastest for quick responses

---
Ready for development! 🚀
"@

$instructions | Out-File -FilePath "CURSOR_OLLAMA_SETUP.md" -Encoding UTF8
Write-Host "OK: Instructions saved to CURSOR_OLLAMA_SETUP.md" -ForegroundColor Green

Write-Host ""
Write-Host "4. Testing setup..." -ForegroundColor Yellow

# Тестируем RAG
if (Test-Path "quick_rag.py") {
    Write-Host "Testing RAG search..." -ForegroundColor Gray
    python quick_rag.py "loadGraph function" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: RAG search working" -ForegroundColor Green
    } else {
        Write-Host "WARNING: RAG search not working" -ForegroundColor Yellow
    }
} else {
    Write-Host "WARNING: quick_rag.py not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "===============" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Open Cursor IDE" -ForegroundColor White
Write-Host "2. Follow instructions in CURSOR_OLLAMA_SETUP.md" -ForegroundColor White
Write-Host "3. Test with: python quick_rag.py 'loadGraph function'" -ForegroundColor White
Write-Host "4. Launch model launcher: powershell -ExecutionPolicy Bypass -File .\ollama-launcher.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Ready for AI-powered development! 🚀" -ForegroundColor Green
