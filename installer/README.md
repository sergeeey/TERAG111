# TERAG Local Installer

Полный установочный комплект TERAG Dev Environment для Windows 11 с размещением на диске E:.

## 🚀 Быстрая установка

```powershell
# Запустить установщик
powershell -ExecutionPolicy Bypass -File .\setup_terag.ps1

# Или с указанием пути
powershell -ExecutionPolicy Bypass -File .\setup_terag.ps1 -InstallPath "E:\TERAG"
```

## 📋 Требования

- Windows 11
- Docker Desktop установлен и запущен
- Минимум 4GB свободного места на диске E:

## 🏗️ Структура проекта

```
E:\TERAG\
├── app\
│   ├── main.py              # FastAPI приложение
│   ├── modules\
│   │   ├── ideas_extractor.py
│   │   └── metrics_collector.py
│   ├── requirements.txt
│   └── Dockerfile
├── data\
│   ├── neo4j\              # Neo4j данные
│   ├── cache\              # Кэш приложения
│   └── logs\               # Логи
├── prometheus\
│   └── prometheus.yml      # Конфигурация Prometheus
├── grafana\
│   └── provisioning\       # Конфигурация Grafana
├── docker-compose.yml
├── config.env
└── setup_terag.ps1
```

## 🔧 Сервисы

После установки доступны следующие сервисы:

| Сервис | URL | Описание |
|--------|-----|----------|
| **TERAG API** | http://localhost:8000 | FastAPI приложение |
| **API Docs** | http://localhost:8000/docs | Swagger документация |
| **Grafana** | http://localhost:3000 | Дашборды и визуализация |
| **Prometheus** | http://localhost:9090 | Метрики и мониторинг |
| **Neo4j Browser** | http://localhost:7474 | Граф знаний |

## 🔐 Учётные данные

### Grafana
- **Username:** `admin`
- **Password:** `terag_admin`

### Neo4j
- **Username:** `neo4j`
- **Password:** `terag_local`

## 📝 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Get Context
```bash
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{"question": "What is TERAG?"}'
```

### Get Metrics
```bash
curl http://localhost:8000/metrics
```

## 🛠️ Управление

### Остановка сервисов
```powershell
cd E:\TERAG
docker compose down
```

### Просмотр логов
```powershell
cd E:\TERAG
docker compose logs -f
```

### Перезапуск сервисов
```powershell
cd E:\TERAG
docker compose restart
```

## 🔄 Обновление

Для обновления приложения:

```powershell
cd E:\TERAG
docker compose pull
docker compose up -d
```

## 📚 Документация

- [TERAG Documentation](../../docs/)
- [API Documentation](http://localhost:8000/docs) (после запуска)

## ⚠️ Устранение неполадок

### Проблема: Docker не запускается
**Решение:** Убедитесь, что Docker Desktop запущен и работает

### Проблема: Порты заняты
**Решение:** Измените порты в `config.env` или освободите занятые порты

### Проблема: Neo4j не подключается
**Решение:** Подождите 30-60 секунд после запуска для инициализации Neo4j

## 🤖 LLM Integration

TERAG поддерживает интеграцию с локальными LLM:

- **Ollama** (рекомендуется)
- **LM Studio**
- OpenAI-compatible APIs

Подробная инструкция: [LLM_INTEGRATION.md](LLM_INTEGRATION.md)

### Быстрая настройка Ollama

1. Установите Ollama: https://ollama.ai
2. Загрузите модель: `ollama pull llama3`
3. Обновите `config.env`:
   ```env
   LLM_PROVIDER=ollama
   LLM_URL=http://host.docker.internal:11434
   LLM_MODEL=llama3
   ```
4. Перезапустите: `docker compose restart terag-api`

## 📞 Поддержка

Для вопросов и проблем обращайтесь к документации проекта или создавайте issues в репозитории.

---

**Версия:** 1.0.0  
**Дата:** 2025-01-27

