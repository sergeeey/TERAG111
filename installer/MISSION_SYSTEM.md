# 🧠 TERAG Mission System - Cognitive OSINT Collector

## Обзор

TERAG Mission System — это автономный OSINT-конвейер нового поколения, который автоматически собирает, валидирует и структурирует информацию из открытых источников в когнитивный граф знаний.

## 🎯 Архитектура

### Трёхкомпонентный цикл

1. **BRAVE LAYER — Exploration**
   - Использует Brave Search API
   - Формирует запросы на основе тем или графовых пробелов
   - Извлекает уникальные источники

2. **BRIGHT LAYER — Extraction**
   - Через Bright Data MCP получает текст (JS-рендеринг, обход CAPTCHA)
   - Использует `scrape_as_markdown` для превращения веб-страниц в чистый контент
   - Автоматически извлекает сущности: имена, концепты, факты

3. **DEEPCONF LAYER — Validation**
   - Модуль *Контекстор 2025* выступает как **Актор**, формируя утверждения
   - LLM-Критик проверяет их и проставляет **confidence score**
   - PEMM-архитектура (Role, Context, Task, Format) задаёт рамки рассуждения
   - Валидированные факты сохраняются в **Neo4j Knowledge Graph**

## 🚀 Быстрый старт

### 1. Настройка переменных окружения

```powershell
# Brave Search API
$env:BRAVE_API_KEY = "your-brave-api-key"

# Bright Data (опционально)
$env:BRIGHT_DATA_API_KEY = "your-bright-data-key"
$env:BRIGHT_DATA_MCP_SERVER = "bright_data"

# TERAG Installation Path
$env:TERAG_INSTALL_PATH = "E:\TERAG"
```

### 2. Запуск миссии

```powershell
cd D:\TERAG111-1\installer
python start_mission.py --config ./data/mission.yaml
```

### 3. Проверка результатов

После выполнения миссии результаты будут в:

- **Daily Report**: `E:\TERAG\data\daily_summary.md`
- **Graph Snapshot**: `E:\TERAG\data\graph_snapshot.json`
- **Mission Log**: `E:\TERAG\data\mission_log.jsonl`
- **Confidence Matrix**: `E:\TERAG\data\confidence_matrix.csv`

## 📋 Конфигурация миссии

### Структура `mission.yaml`

```yaml
mission:
  name: "TERAG Cognitive OSINT Collector"
  duration: 7  # days
  schedule: "daily"
  
  components:
    - brave_search
    - bright_extraction
    - deepconf_validation
    - graph_rag_update
    - reasoning_phase
    - metrics_logging
    - daily_report
  
  topics:
    - "AI cognitive architectures"
    - "OSINT methodologies"
    - "Graph-RAG implementations"
```

### Настройка компонентов

#### Brave Search

```yaml
brave_search:
  enabled: true
  api_key: "${BRAVE_API_KEY}"
  max_results_per_query: 10
  max_queries_per_day: 50
  languages: ["en", "ru"]
```

#### Bright Extraction

```yaml
bright_extraction:
  enabled: true
  mcp_server: "bright_data"
  scrape_method: "scrape_as_markdown"
  max_pages_per_day: 100
```

#### DeepConf Validation

```yaml
deepconf_validation:
  enabled: true
  confidence_threshold: 0.7
  pemm_enabled: true
  llm_critic_model: "qwen3"
```

## 🔄 Рабочий цикл миссии

1. **Инициализация** — загрузка конфигурации из `mission.yaml`
2. **Brave Search Sweep** — генерация поисковых запросов по темам
3. **Bright Extraction** — скачивание и очистка данных
4. **DeepConf Validation** — проверка, фильтрация и построение графа
5. **Graph Update** — запись новых узлов и связей в Neo4j
6. **Reasoning Phase** — формирование выводов и аномалий
7. **Metrics Logging** — запись метрик (нагрузка, ошибки кодировки, достоверность)
8. **Daily Report** — экспорт в `daily_summary.md`

## 📊 Метрики и мониторинг

### Доступные метрики

- **Facts Validated** — количество валидированных фактов
- **High Confidence Facts** — факты с confidence ≥ threshold
- **Graph Nodes** — количество узлов в графе
- **Graph Relationships** — количество связей
- **Encoding Errors** — ошибки кодировки (если включено)

### Просмотр метрик

```powershell
# Через Prometheus
curl http://localhost:9090/api/v1/query?query=terag_llm_encoding_errors_total

# Через Grafana
# Открой http://localhost:3000 и перейди в дашборд "TERAG LLM Monitoring"
```

## 🛠️ Расширенные возможности

### Dry Run Mode

Проверка конфигурации без выполнения миссии:

```powershell
python start_mission.py --config ./data/mission.yaml --dry-run
```

### Verbose Logging

Подробное логирование:

```powershell
python start_mission.py --config ./data/mission.yaml --verbose
```

### Кастомный путь установки

```powershell
python start_mission.py --config ./data/mission.yaml --install-path D:\TERAG
```

## 🔧 Интеграция с существующими компонентами

### Neo4j

Миссия автоматически использует настройки Neo4j из `config.env`:

```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=terag_local
```

### LLM Client

Использует существующий LLM клиент из `modules/llm_client.py`:

```env
LLM_PROVIDER=ollama
LLM_URL=http://host.docker.internal:11434
LLM_MODEL=qwen3
```

### Prometheus Metrics

Метрики автоматически экспортируются в Prometheus через `metrics_collector.py`.

## 📝 Примеры использования

### Ежедневная миссия

```powershell
# Настройка Task Scheduler для ежедневного запуска
# (см. AUTO_START.md)

# Или ручной запуск
python start_mission.py --config ./data/mission.yaml
```

### Миссия с кастомными темами

Отредактируй `mission.yaml`:

```yaml
topics:
  - "Your custom topic 1"
  - "Your custom topic 2"
```

Затем запусти:

```powershell
python start_mission.py --config ./data/mission.yaml
```

### Миссия только с Brave Search

Отключи другие компоненты в `mission.yaml`:

```yaml
components:
  - brave_search
  # - bright_extraction  # отключено
  # - deepconf_validation  # отключено
```

## 🐛 Устранение проблем

### Ошибка: "Brave API key not configured"

```powershell
# Установи переменную окружения
$env:BRAVE_API_KEY = "your-key-here"

# Или добавь в config.env
BRAVE_API_KEY=your-key-here
```

### Ошибка: "LLM client not available"

Проверь настройки LLM в `config.env`:

```env
LLM_PROVIDER=ollama
LLM_URL=http://host.docker.internal:11434
LLM_MODEL=qwen3
```

### Ошибка: "Mission config not found"

Убедись, что файл `mission.yaml` существует:

```powershell
# Проверь путь
Test-Path .\data\mission.yaml

# Или укажи полный путь
python start_mission.py --config D:\TERAG111-1\installer\data\mission.yaml
```

## 📚 Связанные документы

- [AUTO_START.md](AUTO_START.md) - Автозапуск TERAG
- [GRAFANA_LLM_MONITORING.md](GRAFANA_LLM_MONITORING.md) - Мониторинг метрик
- [LLM_INTEGRATION.md](LLM_INTEGRATION.md) - Интеграция с LLM
- [INSTALL.md](INSTALL.md) - Установка TERAG

## 🎯 Следующие шаги

1. **Настройка Brave API** — получи ключ на [brave.com/search/api](https://brave.com/search/api)
2. **Настройка Bright Data** (опционально) — для расширенного извлечения
3. **Настройка тем** — отредактируй `topics` в `mission.yaml`
4. **Запуск первой миссии** — `python start_mission.py --config ./data/mission.yaml`
5. **Мониторинг** — проверь результаты в Grafana и daily_summary.md

---

**TERAG Mission System** — автономный когнитивный OSINT-организм для построения графа знаний 🧠


















