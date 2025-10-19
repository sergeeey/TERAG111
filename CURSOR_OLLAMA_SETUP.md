# Cursor IDE + Ollama Setup Instructions

## Manual Setup Steps

### 1. AI Models Configuration
1. Open Cursor IDE
2. Go to Settings -> AI Models
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
1. Go to Settings -> MCP Servers
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

## Quick Commands

# Test Ollama directly
curl http://localhost:11434

# Test RAG search
python quick_rag.py "loadGraph function"

# Launch model launcher
powershell -ExecutionPolicy Bypass -File .\ollama-launcher.ps1

## Model Roles

- **deepseek-coder:6.7b** - Best for coding tasks
- **qwen2.5:7b-instruct** - Best for reasoning and analysis
- **nous-hermes2:10.7b** - Best for evaluation and consensus
- **mistral:latest** - Best for general tasks
- **phi3:latest** - Fastest for quick responses

---
Ready for development!
