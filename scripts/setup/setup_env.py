#!/usr/bin/env python3
"""
Скрипт для создания .env файла с API ключами
Запустите: python scripts/setup/setup_env.py
"""
import os
from pathlib import Path

def create_env_file():
    """Создание .env файла с настройками"""
    env_content = """# TERAG Environment Configuration
# ВАЖНО: Этот файл содержит конфиденциальные данные
# Убедитесь, что .env в .gitignore!

# ============================================
# SAFE MODE (Security Settings)
# ============================================
# Enable safe mode by default (restricts external requests)
SAFE_MODE=true

# External request limits (per minute/hour)
MAX_EXTERNAL_REQUESTS_PER_MINUTE=10
MAX_EXTERNAL_REQUESTS_PER_HOUR=100

# Allowed external domains (whitelist, comma-separated)
ALLOWED_EXTERNAL_DOMAINS=api.search.brave.com,localhost,127.0.0.1,brd.superproxy.io

# Simulate external requests (only for testing, use localhost)
SIMULATE_EXTERNAL=false

# Log all external requests for audit
LOG_EXTERNAL_REQUESTS=true

# ============================================
# Application Settings
# ============================================
SIM_MODE=true
PORT=8000
LOG_LEVEL=INFO
API_URL=http://localhost:8000

# ============================================
# Database Configuration
# ============================================
# Neo4j (local development defaults - CHANGE IN PRODUCTION!)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=terag_local

# ============================================
# OSINT API Keys
# ============================================
# Brave Search API Key
BRAVE_API_KEY=BSAUyRp7HWX4-kGYYO6rnukUrNyLojU

# Bright Data Proxy (рекомендуется)
# Используется для скрапинга через proxy
BRIGHTDATA_PROXY_HTTP=https://brd-customer-hl_16abad82-zone-tttt:46ju8s7m4bcz@brd.superproxy.io:9515

# Bright Data WebSocket Proxy (опционально)
BRIGHTDATA_PROXY_WS=wss://brd-customer-hl_16abad82-zone-tttt:46ju8s7m4bcz@brd.superproxy.io:9222

# Bright Data API Key (альтернатива, если нет proxy)
# BRIGHT_DATA_API_KEY=your_brightdata_api_key_here

# Bright Data MCP Server (для интеграции)
BRIGHT_DATA_MCP_SERVER=bright_data

# ============================================
# Supabase Configuration
# ============================================
# URL проекта Supabase
SUPABASE_URL=https://lkmyliwjleegjkcgespp.supabase.co

# Anon/Public ключ (безопасен для браузера с RLS)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxrbXlsaXdqbGVlZ2prY2dlc3BwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIxOTAzNDEsImV4cCI6MjA3Nzc2NjM0MX0._SVPagOjW4uTjZclDk-5HihvlNY6s76wH8vLD5EyRlQ

# Service ключ (опционально, только для серверного использования)
# ВНИМАНИЕ: Service ключ обходит RLS! Используйте только на сервере!
# SUPABASE_SERVICE_KEY=your_service_key_here

# ============================================
# LLM Configuration
# ============================================
# LLM Provider (ollama, lmstudio, openai)
LLM_PROVIDER=lmstudio

# LM Studio URL (для локального reasoning)
LM_STUDIO_URL=http://localhost:1234/v1

# Ollama URL (альтернатива)
LLM_URL=http://127.0.0.1:11434
LLM_MODEL=qwen2.5:7b-instruct

# Reasoning Backend Configuration
REASONING_BACKEND=lmstudio
REASONING_URL=http://localhost:1234/v1
REASONING_MODEL=openai/gpt-oss-20b
REASONING_TEMPERATURE=0.7
REASONING_MAX_TOKENS=1024

# ============================================
# Security Warnings
# ============================================
# ⚠️ NEVER commit real API keys or passwords to git!
# ⚠️ Use environment variables or secret managers in production
# ⚠️ Rotate credentials regularly
# ⚠️ This file is in .gitignore - DO NOT remove it from there!
"""
    
    env_path = Path(__file__).parent / ".env"
    
    # Проверяем, существует ли файл
    if env_path.exists():
        response = input(f"⚠️  Файл .env уже существует. Перезаписать? (y/N): ")
        if response.lower() != 'y':
            print("❌ Отменено. Файл .env не изменён.")
            return False
    
    # Создаём файл
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ Файл .env успешно создан: {env_path}")
        print("\n📋 Добавленные ключи:")
        print("  ✅ BRAVE_API_KEY")
        print("  ✅ BRIGHTDATA_PROXY_HTTP")
        print("  ✅ BRIGHTDATA_PROXY_WS")
        print("  ✅ SUPABASE_URL")
        print("  ✅ SUPABASE_ANON_KEY")
        print("  ✅ LM Studio configuration")
        print("\n🔒 Убедитесь, что .env в .gitignore!")
        
        # Проверяем .gitignore
        gitignore_path = Path(__file__).parent / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
                if '.env' in gitignore_content:
                    print("✅ .env уже в .gitignore - безопасно!")
                else:
                    print("⚠️  ВНИМАНИЕ: .env не найден в .gitignore!")
        
        return True
    
    except Exception as e:
        print(f"❌ Ошибка при создании .env файла: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Настройка .env файла для TERAG")
    print("=" * 60)
    create_env_file()
    print("\n💡 Следующий шаг: запустите проверку")
    print("   python check_terag_full_stack.py")













