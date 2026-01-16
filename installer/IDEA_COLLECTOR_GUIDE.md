# 🧠 TERAG Idea Collector - Руководство

## Обзор

Модуль автоматического сбора идей позволяет TERAG извлекать структурированные знания из различных источников и сохранять их в граф знаний Neo4j.

### Поддерживаемые источники

1. **PDF документы** - научные статьи, исследования, отчёты
2. **Веб-статьи** - блоги, новости, документация
3. **X/Twitter треды** - обсуждения, твиты, треды

### Структура знаний

Идеи автоматически классифицируются в три категории:

- **DISCOVERY** (Открытие) - новые находки, прорывы, открытия
- **IDEA** (Идея) - концепции, принципы, инсайты
- **APPLICATION** (Применение) - практические применения, реализации

## 🚀 Быстрый старт

### 1. Сбор идей из PDF

```powershell
curl -X POST http://localhost:8000/ideas/collect `
  -H "Content-Type: application/json" `
  -d '{
    "source_type": "pdf",
    "source_path": "/app/data/documents/research.pdf",
    "auto_extract": true
  }'
```

**Примечание:** Путь к PDF должен быть доступен внутри контейнера. Используйте volume mapping в docker-compose.yml.

### 2. Сбор идей из веб-статьи

```powershell
curl -X POST http://localhost:8000/ideas/collect `
  -H "Content-Type: application/json" `
  -d '{
    "source_type": "article",
    "source_path": "https://example.com/article",
    "auto_extract": true
  }'
```

### 3. Сбор идей из X/Twitter треда

```powershell
curl -X POST http://localhost:8000/ideas/collect `
  -H "Content-Type: application/json" `
  -d '{
    "source_type": "x_thread",
    "source_path": "https://x.com/username/status/123456",
    "auto_extract": true
  }'
```

### 4. Просмотр собранных идей

```powershell
curl http://localhost:8000/ideas/list?limit=50
```

## 📊 Структура ответа

### Успешный сбор идей

```json
{
  "source": "article",
  "url": "https://example.com/article",
  "title": "Article Title",
  "ideas_extracted": 5,
  "ideas": [
    {
      "type": "discovery",
      "title": "New breakthrough in quantum computing",
      "description": "Researchers have discovered...",
      "keywords": ["quantum", "computing", "breakthrough"],
      "confidence": 0.85,
      "source_type": "article",
      "source_path": "https://example.com/article"
    }
  ],
  "timestamp": "2025-01-26T12:00:00"
}
```

## 🔧 Настройка

### Использование LLM для извлечения

По умолчанию модуль использует LLM (если доступен) для структурированного извлечения идей. Это обеспечивает:

- Более точную классификацию (Discovery/Idea/Application)
- Лучшее понимание контекста
- Извлечение ключевых слов

Если LLM недоступен, используется простое правило-основанное извлечение.

### Настройка LLM

Убедитесь, что в `config.env` указаны:

```env
LLM_PROVIDER=ollama
LLM_URL=http://host.docker.internal:11434
LLM_MODEL=llama3
```

## 📈 Структура Neo4j графа

### Узлы

- **Source** - источник данных (PDF, URL)
- **Discovery** - открытия
- **Idea** - идеи
- **Application** - применения
- **Keyword** - ключевые слова

### Связи

- `Source -[:CONTAINS]-> Idea` - источник содержит идею
- `Idea -[:HAS_KEYWORD]-> Keyword` - идея связана с ключевыми словами
- `Idea -[:RELATED_TO]-> Idea` - связанные идеи (по общим ключевым словам)

## 🔍 Просмотр графа в Neo4j Browser

1. Откройте http://localhost:7474
2. Войдите (neo4j / terag_local)
3. Выполните запрос:

```cypher
MATCH (s:Source)-[:CONTAINS]->(i)
WHERE i:Discovery OR i:Idea OR i:Application
RETURN s, i
LIMIT 50
```

## 🎯 Примеры использования

### Автоматический сбор из нескольких источников

```powershell
# Список статей для анализа
$articles = @(
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3"
)

foreach ($article in $articles) {
    Write-Host "Processing: $article"
    curl -X POST http://localhost:8000/ideas/collect `
      -H "Content-Type: application/json" `
      -d "{\"source_type\": \"article\", \"source_path\": \"$article\", \"auto_extract\": true}"
    Start-Sleep -Seconds 2
}
```

### Поиск связанных идей

После сбора идей, используйте Neo4j для поиска связей:

```cypher
// Найти все идеи, связанные с "quantum computing"
MATCH (k:Keyword {name: "quantum"})<-[:HAS_KEYWORD]-(i)
RETURN i.title, i.type, i.description
```

## ⚠️ Ограничения

1. **PDF файлы** - должны быть доступны внутри контейнера через volume mapping
2. **X/Twitter** - веб-скрапинг может быть ограничен политикой платформы
3. **LLM** - рекомендуется использовать для лучшего качества извлечения

## 🐛 Решение проблем

### Ошибка "PyPDF2 not installed"

```powershell
# Пересоберите контейнер
docker compose build --no-cache terag-api
docker compose up -d terag-api
```

### PDF файл не найден

Убедитесь, что файл доступен в контейнере. Добавьте volume в docker-compose.yml:

```yaml
volumes:
  - ${DATA_PATH}/documents:/app/data/documents
```

### LLM не используется

Проверьте настройки в `config.env` и доступность LLM сервиса:

```powershell
curl http://localhost:8000/llm/health
```

## 📚 Дополнительные ресурсы

- [TERAG API Documentation](http://localhost:8000/docs)
- [Neo4j Browser](http://localhost:7474)
- [Grafana Dashboards](http://localhost:3000)



















