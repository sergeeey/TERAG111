#!/usr/bin/env python3
"""
CURSOR ENVIRONMENT CONNECTIVITY CHECKER
Проверяет связность GitHub ↔ Cursor ↔ Ollama ↔ RAG
"""

import subprocess
import sys
import json
import requests
from pathlib import Path

def run_command(cmd, shell=True):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def check_git():
    """Проверяет Git и GitHub подключение"""
    print("1. GITHUB CONNECTION")
    print("-------------------")
    
    # Проверяем git remote
    success, output, error = run_command("git remote -v")
    if success and "github.com" in output:
        print("OK: GitHub remote configured")
        print(f"   {output}")
    else:
        print("ERROR: No GitHub remote found")
        print(f"   Error: {error}")
    
    # Проверяем статус
    success, output, error = run_command("git status --porcelain")
    if success:
        if output:
            print("WARNING: Uncommitted changes detected")
            print(f"   {output}")
        else:
            print("OK: Working directory clean")
    else:
        print("ERROR: Git status check failed")
    
    print()

def check_ollama():
    """Проверяет Ollama runtime"""
    print("2. OLLAMA RUNTIME")
    print("-----------------")
    
    try:
        response = requests.get("http://localhost:11434", timeout=5)
        if response.status_code == 200:
            print("OK: Ollama is running")
            print(f"   Response: {response.text}")
        else:
            print(f"ERROR: Ollama responded with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print("ERROR: Ollama not accessible")
        print(f"   Error: {e}")
        print("   TIP: Start Ollama: ollama serve")
    
    # Проверяем модели
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('models'):
                print("OK: Available models:")
                for model in data['models']:
                    print(f"   - {model['name']}")
            else:
                print("WARNING: No models found")
                print("   TIP: Pull a model: ollama pull deepseek-coder")
        else:
            print("ERROR: Cannot list models")
    except requests.exceptions.RequestException as e:
        print("ERROR: Cannot list models")
        print(f"   Error: {e}")
    
    print()

def check_python():
    """Проверяет Python окружение"""
    print("3. PYTHON ENVIRONMENT")
    print("---------------------")
    
    # Проверяем Python
    success, output, error = run_command("python --version")
    if success:
        print(f"OK: Python available: {output}")
    else:
        print("ERROR: Python not found")
        print(f"   Error: {error}")
    
    # Проверяем пакеты
    required_packages = ["chromadb", "langchain", "fastapi", "uvicorn"]
    for package in required_packages:
        success, output, error = run_command(f"pip show {package}")
        if success and "Version:" in output:
            version = [line for line in output.split('\n') if line.startswith('Version:')][0].split(':')[1].strip()
            print(f"OK: {package} v{version}")
        else:
            print(f"ERROR: {package} not installed")
    
    print()

def check_rag():
    """Проверяет RAG сервис"""
    print("4. RAG SERVICE")
    print("--------------")
    
    # Проверяем скрипты
    scripts = ["index_codebase.py", "ask_rag.py"]
    for script in scripts:
        if Path(script).exists():
            print(f"OK: {script} found")
        else:
            print(f"ERROR: {script} missing")
    
    # Проверяем базу данных
    if Path("chroma_db").exists():
        print("OK: ChromaDB database exists")
    else:
        print("WARNING: ChromaDB database not found")
        print("   TIP: Run: python index_codebase.py")
    
    print()

def check_cursor_config():
    """Проверяет конфигурацию Cursor"""
    print("5. CURSOR INTEGRATION")
    print("---------------------")
    
    if Path("cursor_config.json").exists():
        print("OK: Cursor config file found")
        try:
            with open("cursor_config.json", 'r') as f:
                config = json.load(f)
                print("OK: Config file is valid JSON")
        except json.JSONDecodeError as e:
            print(f"ERROR: Config file has invalid JSON: {e}")
    else:
        print("ERROR: Cursor config file missing")
    
    print("INFO: Manual steps required:")
    print("   1. Cursor Settings -> AI Models -> Add Custom Model")
    print("      Provider: OpenAI")
    print("      Base URL: http://localhost:11434/v1")
    print("      API Key: ollama")
    print("")
    print("   2. Cursor Settings -> MCP Servers -> Add Server")
    print("      Name: local_rag")
    print("      Command: python")
    print("      Args: ask_rag.py")
    
    print()

def main():
    print("CURSOR ENVIRONMENT CONNECTIVITY CHECKER")
    print("===============================================")
    print()
    
    check_git()
    check_ollama()
    check_python()
    check_rag()
    check_cursor_config()
    
    print("6. SUMMARY")
    print("----------")
    
    issues = 0
    if not Path("index_codebase.py").exists():
        issues += 1
    if not Path("ask_rag.py").exists():
        issues += 1
    if not Path("chroma_db").exists():
        issues += 1
    
    if issues == 0:
        print("SUCCESS: All systems ready for Cursor integration!")
    else:
        print(f"WARNING: {issues} issues found - see recommendations above")
    
    print()
    print("NEXT STEPS:")
    print("   1. Fix any issues above")
    print("   2. Configure Cursor AI models")
    print("   3. Set up MCP servers")
    print("   4. Test with: @local_rag search your query")

if __name__ == "__main__":
    main()
