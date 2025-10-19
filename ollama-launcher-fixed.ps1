# Ollama Model Launcher
# Quick launch of Ollama models for testing

Write-Host "Ollama Model Launcher" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

# Check if Ollama is running
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

# Get available models
Write-Host "Available models:" -ForegroundColor Yellow
Write-Host "================" -ForegroundColor Yellow

$models = @(
    @{Name="nous-hermes2:10.7b"; Description="Judge / Consensus Agent (6.1 GB)"; Role="Evaluation and argument weighting"},
    @{Name="qwen2.5:7b-instruct"; Description="Philosopher / Reasoning Analyst (4.7 GB)"; Role="Analysis and reasoning"},
    @{Name="deepseek-coder:6.7b"; Description="Programmer / Engineering Agent (3.8 GB)"; Role="Coding and engineering"},
    @{Name="mistral:latest"; Description="Reasoning Architect (4.4 GB)"; Role="Scenario generation"},
    @{Name="phi3:latest"; Description="Fast Hypothetical (2.2 GB)"; Role="Lightweight reasoning"},
    @{Name="deepseek-coder:latest"; Description="Quantized Coder (776 MB)"; Role="Fast responses"}
)

for ($i = 0; $i -lt $models.Count; $i++) {
    $model = $models[$i]
    Write-Host "$($i + 1). $($model.Name)" -ForegroundColor White
    Write-Host "   $($model.Description)" -ForegroundColor Gray
    Write-Host "   Role: $($model.Role)" -ForegroundColor DarkGray
    Write-Host ""
}

# Model selection
Write-Host "Select model (1-$($models.Count)): " -NoNewline -ForegroundColor Cyan
$choice = Read-Host

if ($choice -match "^\d+$" -and [int]$choice -ge 1 -and [int]$choice -le $models.Count) {
    $selectedModel = $models[[int]$choice - 1]
    Write-Host ""
    Write-Host "Selected: $($selectedModel.Name)" -ForegroundColor Green
    Write-Host "Description: $($selectedModel.Description)" -ForegroundColor Gray
    Write-Host "Role: $($selectedModel.Role)" -ForegroundColor DarkGray
    Write-Host ""
    
    # Launch model
    Write-Host "Starting model..." -ForegroundColor Yellow
    Write-Host "Type 'exit' to quit the chat" -ForegroundColor DarkGray
    Write-Host "=" * 50 -ForegroundColor DarkGray
    
    # Run ollama
    & "C:\Users\serge\AppData\Local\Programs\Ollama\ollama.exe" run $selectedModel.Name
} else {
    Write-Host "Invalid selection. Exiting..." -ForegroundColor Red
}

Write-Host ""
Write-Host "Launcher finished." -ForegroundColor Cyan
