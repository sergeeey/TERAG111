# Health Check Script for TERAG Environment
# Запускать через Windows Task Scheduler ежедневно

$LogFile = "health-check.log"
$Date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Log {
    param($Message)
    $LogEntry = "$Date - $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

Write-Log "Starting TERAG Health Check..."

# 1. Check Ollama
try {
    $ollamaResponse = Invoke-RestMethod -Uri "http://localhost:11434" -Method Get -TimeoutSec 5
    Write-Log "OK: Ollama is running"
} catch {
    Write-Log "ERROR: Ollama not accessible - $($_.Exception.Message)"
    Write-Log "ACTION: Start Ollama with 'ollama serve'"
}

# 2. Check Python
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Log "OK: Python available - $pythonVersion"
    } else {
        Write-Log "ERROR: Python not found"
    }
} catch {
    Write-Log "ERROR: Python check failed"
}

# 3. Check ChromaDB
if (Test-Path "chroma_db") {
    Write-Log "OK: ChromaDB database exists"
} else {
    Write-Log "WARNING: ChromaDB database not found"
    Write-Log "ACTION: Run quick-setup-fixed.ps1"
}

# 4. Check RAG functionality
try {
    $ragTest = python quick_rag.py "test query" 2>$null
    if ($ragTest) {
        Write-Log "OK: RAG system functional"
    } else {
        Write-Log "WARNING: RAG system not responding"
    }
} catch {
    Write-Log "ERROR: RAG system test failed"
}

# 5. Check project files
$criticalFiles = @("package.json", "quick-setup-fixed.ps1", "quick_rag.py")
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Log "OK: $file exists"
    } else {
        Write-Log "ERROR: $file missing"
    }
}

Write-Log "Health check completed"

# Send summary to console
Write-Host ""
Write-Host "TERAG Health Check Summary" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Log file: $LogFile" -ForegroundColor Gray
Write-Host "Date: $Date" -ForegroundColor Gray
Write-Host ""
