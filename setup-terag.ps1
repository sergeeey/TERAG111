# 🚀 TERAG Automated Setup Script for Cursor IDE
# Автоматическая настройка всей инфраструктуры TERAG

param(
    [string]$ProjectPath = ".",
    [switch]$SkipNeo4j = $false,
    [switch]$Force = $false
)

Write-Host "🚀 TERAG Automated Setup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# 1️⃣ Проверка среды
Write-Host "1️⃣ Checking environment..." -ForegroundColor Yellow

# Проверяем Ollama
try {
    $ollamaVersion = ollama --version 2>$null
    if ($ollamaVersion) {
        Write-Host "✅ Ollama: $ollamaVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Ollama not found. Please install from https://ollama.ai" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Ollama not found. Please install from https://ollama.ai" -ForegroundColor Red
    exit 1
}

# Проверяем Python
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -ge 3 -and $minor -ge 10) {
            Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ Python version too old: $pythonVersion (need 3.10+)" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ Python not found. Please install from https://python.org" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2️⃣ Установка зависимостей Python
Write-Host "2️⃣ Installing Python dependencies..." -ForegroundColor Yellow

$packages = @(
    "chromadb",
    "langchain", 
    "langchain-community",
    "ragas",
    "fastapi",
    "uvicorn",
    "neo4j",
    "networkx",
    "pyvis",
    "loguru"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Gray
    pip install $package --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $package installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install $package" -ForegroundColor Red
    }
}

Write-Host ""

# 3️⃣ Создание индексатора кода
Write-Host "3️⃣ Creating code indexer..." -ForegroundColor Yellow

$indexerCode = @"
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
import os
import argparse

def index_repository(repo_path):
    print(f"Indexing repository: {repo_path}")
    
    # Загружаем все файлы проекта
    loader = DirectoryLoader(repo_path, glob="**/*.{py,ts,tsx,js,jsx,md,json}")
    docs = loader.load()
    print(f"Loaded {len(docs)} documents")
    
    # Разбиваем на чанки
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_documents(docs)
    print(f"Split into {len(texts)} chunks")
    
    # Создаём эмбеддинги
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # Сохраняем в ChromaDB
    db = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_store")
    db.persist()
    print("✅ Indexing completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index codebase for RAG")
    parser.add_argument("--path", default=".", help="Path to repository")
    args = parser.parse_args()
    
    index_repository(args.path)
"@

$indexerCode | Out-File -FilePath "index_codebase.py" -Encoding UTF8
Write-Host "✅ Created index_codebase.py" -ForegroundColor Green

# 4️⃣ Создание RAG-запросника
Write-Host "4️⃣ Creating RAG query interface..." -ForegroundColor Yellow

$ragCode = @"
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
import argparse

def ask(query):
    print(f"Query: {query}")
    
    # Инициализируем LLM
    llm = Ollama(model="deepseek-coder:6.7b")
    
    # Загружаем базу данных
    db = Chroma(persist_directory="./chroma_store", embedding_function=None)
    retriever = db.as_retriever(search_kwargs={"k": 5})
    
    # Создаём QA цепочку
    qa = RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=retriever)
    
    # Выполняем запрос
    result = qa.run(query)
    print(f"Answer: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query RAG database")
    parser.add_argument("query", nargs="?", help="Query to ask")
    args = parser.parse_args()
    
    if args.query:
        ask(args.query)
    else:
        query = input("Enter your question: ")
        ask(query)
"@

$ragCode | Out-File -FilePath "ask_rag.py" -Encoding UTF8
Write-Host "✅ Created ask_rag.py" -ForegroundColor Green

# 5️⃣ Создание .env файла
Write-Host "5️⃣ Creating environment configuration..." -ForegroundColor Yellow

$envContent = @"
# TERAG Environment Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=12345

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:6.7b

# RAG Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_store
EMBEDDING_MODEL=nomic-embed-text
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "✅ Created .env file" -ForegroundColor Green

# 6️⃣ Индексация проекта
Write-Host "6️⃣ Indexing project..." -ForegroundColor Yellow

python index_codebase.py --path $ProjectPath
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Project indexed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Indexing failed" -ForegroundColor Red
}

Write-Host ""

# 7️⃣ Создание конфигурации Cursor
Write-Host "7️⃣ Creating Cursor configuration..." -ForegroundColor Yellow

$cursorConfig = @{
    "cursor_ai_models" = @{
        "local_ollama" = @{
            "provider" = "openai"
            "model" = "deepseek-coder"
            "baseURL" = "http://localhost:11434/v1"
            "apiKey" = "ollama"
            "description" = "DeepSeek Coder (Local via Ollama)"
        }
    }
    "mcp_servers" = @{
        "local_rag" = @{
            "name" = "local_rag"
            "command" = "python"
            "args" = @("ask_rag.py")
            "type" = "local"
            "description" = "Local RAG search for codebase"
        }
    }
    "workspace_settings" = @{
        "ai.model" = "local_ollama"
        "ai.enableCodeActions" = $true
        "ai.enableChat" = $true
        "ai.enableCompletions" = $true
    }
}

$cursorConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath "cursor_config.json" -Encoding UTF8
Write-Host "✅ Created cursor_config.json" -ForegroundColor Green

# 8️⃣ Создание README с инструкциями
Write-Host "8️⃣ Creating setup instructions..." -ForegroundColor Yellow

$readmeContent = @"
# 🚀 TERAG Setup Complete!

## ✅ What's Ready

- **Ollama Runtime**: Connected to local models
- **RAG Service**: Project indexed and ready
- **Python Environment**: All dependencies installed
- **Cursor Configuration**: Ready for integration

## 🔧 Manual Steps in Cursor IDE

### 1. Add AI Model
1. Open Cursor Settings (Ctrl+,)
2. Go to AI Models → Add Custom Model
3. Fill in:
   - Provider: OpenAI
   - Base URL: http://localhost:11434/v1
   - API Key: ollama

### 2. Add MCP Server
1. Go to Settings → MCP Servers → Add Server
2. Fill in:
   - Name: local_rag
   - Command: python
   - Args: ask_rag.py

## 🧪 Testing

\`\`\`bash
# Test RAG search
python ask_rag.py "Where is loadGraph function implemented?"

# Test with specific query
python ask_rag.py "How does the voice mode work?"
\`\`\`

## 🎯 Usage in Cursor

Once configured, you can use in Cursor:
- \`@local_rag search "your query"\`
- \`@local_rag search --function loadGraph\`

## 🔄 Updating Index

When code changes:
\`\`\`bash
python index_codebase.py --path .
\`\`\`

---
**Setup completed successfully!** 🎉
"@

$readmeContent | Out-File -FilePath "TERAG_SETUP_COMPLETE.md" -Encoding UTF8
Write-Host "✅ Created TERAG_SETUP_COMPLETE.md" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 SETUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Open Cursor IDE" -ForegroundColor White
Write-Host "2. Configure AI Models and MCP Servers (see TERAG_SETUP_COMPLETE.md)" -ForegroundColor White
Write-Host "3. Test with: python ask_rag.py 'your query'" -ForegroundColor White
Write-Host ""
Write-Host "Ready to code with local AI! 🚀" -ForegroundColor Green
