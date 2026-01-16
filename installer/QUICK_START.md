# 🚀 TERAG Quick Start

## Быстрая установка (1 команда)

```powershell
cd D:\TERAG111-1\installer
powershell -ExecutionPolicy Bypass -File .\setup_terag.ps1
```

## Что будет установлено

- ✅ Структура каталогов на `E:\TERAG`
- ✅ FastAPI приложение (порт 8000)
- ✅ Neo4j (порты 7474, 7687)
- ✅ Prometheus (порт 9090)
- ✅ Grafana (порт 3000)

## После установки

Подождите 30-60 секунд и откройте:

- **TERAG API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Grafana:** http://localhost:3000 (admin/terag_admin)
- **Neo4j:** http://localhost:7474 (neo4j/terag_local)

## Управление

```powershell
cd E:\TERAG

# Остановка
docker compose down

# Запуск
docker compose up -d

# Логи
docker compose logs -f
```

## Интеграция с LLM

См. [LLM_INTEGRATION.md](LLM_INTEGRATION.md) для настройки Ollama или LM Studio.

---

**Версия:** 1.0  
**Дата:** 2025-01-27





















