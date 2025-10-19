# 🚀 Cursor IDE Setup Guide

## ✅ **СИСТЕМА ГОТОВА К ИНТЕГРАЦИИ**

Все компоненты настроены и протестированы. Осталось только настроить Cursor IDE.

---

## 📋 **ЧТО УЖЕ НАСТРОЕНО**

### ✅ **GitHub Integration**
- Репозиторий: `https://github.com/sergeeey/TERAG111.git`
- Все изменения синхронизированы
- Рабочая директория чистая

### ✅ **Ollama Runtime**
- Сервер запущен на `http://localhost:11434`
- Доступные модели:
  - `deepseek-coder:latest` (рекомендуется)
  - `mistral:latest`
  - `qwen2.5:7b-instruct`
  - `phi3:latest`

### ✅ **Python Environment**
- Python 3.13.5
- ChromaDB v1.2.0
- LangChain v1.0.0
- FastAPI v0.119.0
- Uvicorn v0.38.0

### ✅ **RAG Service**
- Индексировано: **98 файлов** → **441 чанк**
- База данных: `chroma_db/`
- Скрипты: `index_codebase.py`, `ask_rag.py`

---

## 🔧 **НАСТРОЙКА CURSOR IDE**

### 1️⃣ **Добавить локальную модель Ollama**

1. Откройте **Cursor Settings** (`Ctrl+,`)
2. Перейдите в **AI Models** → **Add Custom Model**
3. Заполните:
   ```
   Provider: OpenAI
   Model: deepseek-coder
   Base URL: http://localhost:11434/v1
   API Key: ollama
   ```
4. Сохраните и выберите эту модель

### 2️⃣ **Настроить MCP Server для RAG**

1. В **Cursor Settings** → **MCP Servers** → **Add Server**
2. Заполните:
   ```
   Name: local_rag
   Command: python
   Args: ask_rag.py
   ```
3. Сохраните

### 3️⃣ **Проверить интеграцию**

В Cursor теперь можно использовать:
- `@local_rag search "your query"` - поиск по коду
- `@local_rag search --function loadGraph` - поиск функций
- `@local_rag search --import-search react` - поиск импортов

---

## 🧪 **ТЕСТИРОВАНИЕ**

### Проверка RAG-поиска:
```bash
python ask_rag.py "loadGraph function"
python ask_rag.py --function loadGraph
python ask_rag.py --stats
```

### Проверка Ollama:
```bash
curl http://localhost:11434
```

### Полная диагностика:
```bash
python check_env_simple.py
```

---

## 📊 **СТАТИСТИКА ПРОЕКТА**

- **Файлов проиндексировано**: 98
- **Чанков создано**: 441
- **Языки**: TypeScript, JavaScript, Python, Markdown, JSON
- **Размер базы**: ~2.5 MB
- **Время индексации**: ~30 секунд

---

## 🔄 **ОБНОВЛЕНИЕ ИНДЕКСА**

При изменении кода:
```bash
python index_codebase.py --reset
```

---

## 🆘 **УСТРАНЕНИЕ ПРОБЛЕМ**

### Ollama не запущен:
```bash
ollama serve
```

### Модель не найдена:
```bash
ollama pull deepseek-coder
```

### RAG не работает:
```bash
python ask_rag.py --stats
```

### Полная переустановка:
```bash
rm -rf chroma_db
python index_codebase.py
```

---

## 🎯 **СЛЕДУЮЩИЕ ШАГИ**

1. ✅ Настроить Cursor AI Models
2. ✅ Настроить MCP Servers
3. ✅ Протестировать `@local_rag search`
4. 🚀 Начать разработку с локальным ИИ!

---

**Система готова к продуктивной работе!** 🎉
