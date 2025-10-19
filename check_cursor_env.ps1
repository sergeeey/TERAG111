# 🔍 CURSOR ENVIRONMENT CONNECTIVITY CHECKER
# Проверяет связность GitHub ↔ Cursor ↔ Ollama ↔ RAG

Write-Host "🔍 CURSOR ENVIRONMENT CONNECTIVITY CHECKER" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# 1️⃣ GitHub Connection Check
Write-Host "1️⃣ GITHUB CONNECTION" -ForegroundColor Yellow
Write-Host "-------------------" -ForegroundColor Yellow

try {
    $gitRemote = git remote -v 2>$null
    if ($gitRemote -match "github.com") {
        Write-Host "✅ GitHub remote configured" -ForegroundColor Green
        Write-Host "   $gitRemote" -ForegroundColor Gray
    } else {
        Write-Host "❌ No GitHub remote found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Git not available" -ForegroundColor Red
}

$gitStatus = git status --porcelain 2>$null
if ($gitStatus) {
    Write-Host "⚠️  Uncommitted changes detected" -ForegroundColor Yellow
    Write-Host "   $gitStatus" -ForegroundColor Gray
} else {
    Write-Host "✅ Working directory clean" -ForegroundColor Green
}

Write-Host ""

# 2️⃣ Ollama Runtime Check
Write-Host "2️⃣ OLLAMA RUNTIME" -ForegroundColor Yellow
Write-Host "-----------------" -ForegroundColor Yellow

try {
    $ollamaResponse = Invoke-RestMethod -Uri "http://localhost:11434" -Method Get -TimeoutSec 5
    Write-Host "✅ Ollama is running" -ForegroundColor Green
    Write-Host "   Response: $ollamaResponse" -ForegroundColor Gray
} catch {
    Write-Host "❌ Ollama not accessible" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
    Write-Host "   💡 Start Ollama: ollama serve" -ForegroundColor Cyan
}

# Check available models
try {
    $models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 5
    if ($models.models) {
        Write-Host "✅ Available models:" -ForegroundColor Green
        foreach ($model in $models.models) {
            Write-Host "   - $($model.name)" -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠️  No models found" -ForegroundColor Yellow
        Write-Host "   💡 Pull a model: ollama pull deepseek-coder" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Cannot list models" -ForegroundColor Red
}

Write-Host ""

# 3️⃣ Python Environment Check
Write-Host "3️⃣ PYTHON ENVIRONMENT" -ForegroundColor Yellow
Write-Host "---------------------" -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python available: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
}

# Check required packages
$requiredPackages = @("chromadb", "langchain", "fastapi", "uvicorn")
foreach ($package in $requiredPackages) {
    try {
        $packageInfo = pip show $package 2>$null
        if ($packageInfo) {
            $version = ($packageInfo | Select-String "Version:").ToString().Split(":")[1].Trim()
            Write-Host "✅ $package v$version" -ForegroundColor Green
        } else {
            Write-Host "❌ $package not installed" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ $package check failed" -ForegroundColor Red
    }
}

Write-Host ""

# 4️⃣ RAG Service Check
Write-Host "4️⃣ RAG SERVICE" -ForegroundColor Yellow
Write-Host "--------------" -ForegroundColor Yellow

if (Test-Path "index_codebase.py") {
    Write-Host "✅ RAG indexer script found" -ForegroundColor Green
} else {
    Write-Host "❌ RAG indexer script missing" -ForegroundColor Red
    Write-Host "   💡 Create index_codebase.py" -ForegroundColor Cyan
}

if (Test-Path "ask_rag.py") {
    Write-Host "✅ RAG query script found" -ForegroundColor Green
} else {
    Write-Host "❌ RAG query script missing" -ForegroundColor Red
    Write-Host "   💡 Create ask_rag.py" -ForegroundColor Cyan
}

if (Test-Path "chroma_db") {
    Write-Host "✅ ChromaDB database exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  ChromaDB database not found" -ForegroundColor Yellow
    Write-Host "   💡 Run: python index_codebase.py" -ForegroundColor Cyan
}

Write-Host ""

# 5️⃣ Cursor Integration Check
Write-Host "5️⃣ CURSOR INTEGRATION" -ForegroundColor Yellow
Write-Host "---------------------" -ForegroundColor Yellow

Write-Host "ℹ️  Manual checks required:" -ForegroundColor Cyan
Write-Host "   1. Cursor Settings → AI Models → Add Custom Model" -ForegroundColor Gray
Write-Host "      Provider: OpenAI" -ForegroundColor Gray
Write-Host "      Base URL: http://localhost:11434/v1" -ForegroundColor Gray
Write-Host "      API Key: ollama" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Cursor Settings → MCP Servers → Add Server" -ForegroundColor Gray
Write-Host "      Name: local_rag" -ForegroundColor Gray
Write-Host "      Command: python" -ForegroundColor Gray
Write-Host "      Args: ask_rag.py" -ForegroundColor Gray

Write-Host ""

# 6️⃣ Summary
Write-Host "6️⃣ SUMMARY" -ForegroundColor Yellow
Write-Host "----------" -ForegroundColor Yellow

$issues = 0
if (-not (Test-Path "index_codebase.py")) { $issues++ }
if (-not (Test-Path "ask_rag.py")) { $issues++ }
if (-not (Test-Path "chroma_db")) { $issues++ }

if ($issues -eq 0) {
    Write-Host "🎉 All systems ready for Cursor integration!" -ForegroundColor Green
} else {
    Write-Host "⚠️  $issues issues found - see recommendations above" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Fix any issues above" -ForegroundColor Gray
Write-Host "   2. Configure Cursor AI models" -ForegroundColor Gray
Write-Host "   3. Set up MCP servers" -ForegroundColor Gray
Write-Host "   4. Test with: @local_rag search your query" -ForegroundColor Gray
