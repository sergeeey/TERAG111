# 🤖 LLM Integration Guide

Интеграция TERAG с локальными LLM (Ollama, LM Studio)

## 📋 Поддерживаемые провайдеры

### Ollama
- **URL:** `http://localhost:11434` (или `http://host.docker.internal:11434` из Docker)
- **API:** `/api/generate`
- **Модели:** llama3, mistral, codellama, и другие

### LM Studio
- **URL:** `http://localhost:1234` (или `http://host.docker.internal:1234` из Docker)
- **API:** OpenAI-compatible (`/v1/chat/completions`)
- **Модели:** Любые модели, загруженные в LM Studio

## ⚙️ Настройка

### 1. Установка Ollama (рекомендуется)

1. Скачайте Ollama с https://ollama.ai
2. Установите и запустите
3. Загрузите модель:
   ```bash
   ollama pull llama3
   ```

### 2. Установка LM Studio

1. Скачайте LM Studio с https://lmstudio.ai
2. Установите и запустите
3. Загрузите модель через интерфейс
4. Запустите локальный сервер (порт 1234)

### 3. Конфигурация в TERAG

Отредактируйте `config.env`:

#### Для Ollama:
```env
LLM_PROVIDER=ollama
LLM_URL=http://host.docker.internal:11434
LLM_MODEL=llama3
```

#### Для LM Studio:
```env
LLM_PROVIDER=lm_studio
LLM_URL=http://host.docker.internal:1234
LLM_MODEL=local-model
```

### 4. Перезапуск сервисов

```powershell
cd E:\TERAG
docker compose restart terag-api
```

## 🚀 Использование

### API Endpoints

#### Get Context with LLM
```bash
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is TERAG?",
    "use_llm": true,
    "temperature": 0.7,
    "max_tokens": 512
  }'
```

#### List Available Models
```bash
curl http://localhost:8000/llm/models
```

#### Check LLM Health
```bash
curl http://localhost:8000/llm/health
```

### Swagger UI

Откройте http://localhost:8000/docs и используйте интерактивные эндпоинты.

## 🔍 Проверка работы

### 1. Проверка LLM сервиса

```powershell
# Для Ollama
curl http://localhost:11434/api/tags

# Для LM Studio
curl http://localhost:1234/v1/models
```

### 2. Проверка через TERAG API

```powershell
# Health check
curl http://localhost:8000/llm/health

# List models
curl http://localhost:8000/llm/models
```

### 3. Тестовый запрос

```powershell
curl -X POST http://localhost:8000/context `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Hello, who are you?\", \"use_llm\": true}'
```

## 🐛 Устранение проблем

### Проблема: LLM не подключается из Docker

**Решение:** Используйте `host.docker.internal` вместо `localhost`:
```env
LLM_URL=http://host.docker.internal:11434
```

### Проблема: Таймауты при запросах

**Решение:** Увеличьте timeout в `llm_client.py` или убедитесь, что модель загружена.

### Проблема: Модель не найдена

**Решение:** Проверьте доступные модели:
```bash
# Ollama
ollama list

# LM Studio
curl http://localhost:1234/v1/models
```

### Проблема: LLM возвращает ошибки

**Решение:** 
1. Проверьте логи: `docker compose logs terag-api`
2. Убедитесь, что LLM сервис запущен
3. Проверьте порты (не заблокированы ли firewall)

## 📊 Мониторинг

LLM метрики автоматически собираются в Prometheus и доступны в Grafana:

- **Endpoint:** http://localhost:8000/metrics
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000

## 💡 Примеры использования

### Простой запрос
```python
import requests

response = requests.post(
    "http://localhost:8000/context",
    json={
        "question": "Explain TERAG architecture",
        "use_llm": True
    }
)
print(response.json()["answer"])
```

### С кастомными параметрами
```python
response = requests.post(
    "http://localhost:8000/context",
    json={
        "question": "What is knowledge graph?",
        "use_llm": True,
        "temperature": 0.5,  # Более детерминированные ответы
        "max_tokens": 1024   # Более длинные ответы
    }
)
```

### Без LLM (только контекст)
```python
response = requests.post(
    "http://localhost:8000/context",
    json={
        "question": "What is TERAG?",
        "use_llm": False  # Только извлечение контекста
    }
)
```

## 🔗 Полезные ссылки

- [Ollama Documentation](https://github.com/ollama/ollama)
- [LM Studio Documentation](https://lmstudio.ai/docs)
- [TERAG API Documentation](http://localhost:8000/docs)

---

**Версия:** 1.0.0  
**Дата:** 2025-01-27





















