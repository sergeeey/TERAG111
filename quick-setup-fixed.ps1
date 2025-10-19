# Quick TERAG Setup - Fixed Version
Write-Host "Quick TERAG Setup" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in project root
if (-not (Test-Path "package.json")) {
    Write-Host "ERROR: Not in project root. Please run from project directory." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install chromadb --quiet

# Create simple indexer
$indexerCode = @"
import os
import sys
from pathlib import Path
import chromadb

def quick_index():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("codebase")
    
    files_to_index = [
        "src/**/*.tsx", "src/**/*.ts", "src/**/*.js", "src/**/*.jsx",
        "*.md", "*.json", "*.py"
    ]
    
    count = 0
    for pattern in files_to_index:
        for file_path in Path(".").glob(pattern):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    collection.add(
                        documents=[content],
                        metadatas=[{"file_path": str(file_path), "file_name": file_path.name}],
                        ids=[f"doc_{count}"]
                    )
                    count += 1
                    print(f"Indexed: {file_path}")
                except Exception as e:
                    print(f"Error indexing {file_path}: {e}")
    
    print(f"SUCCESS: Indexed {count} files")

if __name__ == "__main__":
    quick_index()
"@

$indexerCode | Out-File -FilePath "quick_index.py" -Encoding UTF8

# Create simple RAG
$ragCode = @"
import sys
import chromadb

def quick_search(query):
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("codebase")
    
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    print(f"Query: {query}")
    print("Results:")
    for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"{i+1}. {meta['file_name']}")
        print(f"   {doc[:200]}...")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        quick_search(" ".join(sys.argv[1:]))
    else:
        query = input("Enter query: ")
        quick_search(query)
"@

$ragCode | Out-File -FilePath "quick_rag.py" -Encoding UTF8

# Index project
Write-Host "Indexing project..." -ForegroundColor Yellow
python quick_index.py

# Create Cursor config
$config = @"
{
  "cursor_ai_models": {
    "local_ollama": {
      "provider": "openai",
      "model": "deepseek-coder",
      "baseURL": "http://localhost:11434/v1",
      "apiKey": "ollama"
    }
  },
  "mcp_servers": {
    "local_rag": {
      "name": "local_rag",
      "command": "python",
      "args": ["quick_rag.py"]
    }
  }
}
"@

$config | Out-File -FilePath "cursor_quick_config.json" -Encoding UTF8

Write-Host ""
Write-Host "SUCCESS: Quick setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Test it:" -ForegroundColor Cyan
Write-Host "python quick_rag.py 'loadGraph function'" -ForegroundColor White
Write-Host ""
Write-Host "In Cursor:" -ForegroundColor Cyan
Write-Host "1. Settings -> AI Models -> Add Custom Model" -ForegroundColor White
Write-Host "   Provider: OpenAI, Base URL: http://localhost:11434/v1, API Key: ollama" -ForegroundColor White
Write-Host "2. Settings -> MCP Servers -> Add Server" -ForegroundColor White
Write-Host "   Name: local_rag, Command: python, Args: quick_rag.py" -ForegroundColor White
Write-Host ""
Write-Host "Ready!" -ForegroundColor Green
