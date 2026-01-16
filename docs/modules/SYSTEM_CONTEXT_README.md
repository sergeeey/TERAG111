# 🧩 TERAG System Context Memory

## ✅ Что уже сделано

- ✅ `system_context.py` создан в `src/core/`
- ✅ Зависимости добавлены в `requirements.txt` (psutil, docker)
- ✅ Интеграция с Telegram Service (системный снимок в ежедневном отчёте)
- ✅ Тестовый скрипт `test_system_context.py` работает

## 🚀 Быстрый старт

### 1. Установите зависимости

```bash
pip install psutil docker
```

Или обновите все:
```bash
pip install -r requirements.txt
```

### 2. Протестируйте модуль

```bash
python scripts/tests/test_system_context.py
```

Должна собраться информация о системе, Docker, контейнерах и сервисах.

### 3. Проверьте сохранение

После теста проверьте файл:
```bash
cat data/system_context.json
```

## 📊 Что собирается

### Информация о хосте
- OS и версия
- Hostname
- Процессор
- Платформа

### Ресурсы
- CPU (количество ядер, загрузка)
- RAM (общий объём, доступно, используется)
- Диск (свободное место)

### Docker
- Версия Docker
- Список контейнеров (имя, статус, образ, порты)
- TERAG-контейнеры (специально помеченные)

### Сервисы
- LM Studio (порт 1234)
- Neo4j (порт 7687)
- Ollama (порт 11434)

### Порты
- Проверка занятых портов
- Ключевые порты TERAG

## 📱 Интеграция с Telegram

Системный снимок автоматически добавляется в ежедневный отчёт:

```
🧩 System Context

Host: DESKTOP-E9NI1TR
OS: Windows 10.0.26200

CPU: 24 cores
RAM: 95.4 GB
Disk free: 1643.4 GB

Docker: 28.5.1
Containers: 3/7 running
TERAG containers: terag-api, terag-grafana, terag-prometheus

Services:
✅ LM Studio
❌ Neo4j
❌ Ollama
```

## 💾 Сохранение данных

### В файл

```python
from src.core.system_context import SystemContext

context = SystemContext()
context.save_to_file("data/system_context.json")
```

### В Supabase (опционально)

Создайте таблицу в Supabase:

```sql
CREATE TABLE system_state_log (
  id BIGSERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL,
  host TEXT,
  os TEXT,
  docker_version TEXT,
  containers_json JSONB,
  cpu_count INT,
  ram_total_gb FLOAT,
  disk_free_gb FLOAT,
  notes JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Затем:

```python
context.save_to_supabase()
```

## 🔍 Использование

### Получить контекст

```python
from src.core.system_context import get_system_context

context = get_system_context()
print(f"Docker: {context['docker']['version']}")
print(f"Containers: {len(context['docker']['containers'])}")
```

### Сохранить снимок

```python
from src.core.system_context import save_system_snapshot

filepath = save_system_snapshot()
print(f"Saved to: {filepath}")
```

### Форматировать для Telegram

```python
from src.core.system_context import SystemContext

context = SystemContext()
message = context.format_for_telegram()
# Отправить в Telegram
```

## ⚠️ Предупреждения

Модуль автоматически обнаруживает проблемы:

- ❌ Контейнер Neo4j остановлен → предупреждение
- ❌ Критичные порты не заняты → предупреждение
- ⚠️ Ресурсы на исходе → предупреждение

## 🔄 Периодическое сохранение

В Telegram Service можно добавить задачу сохранения каждый час:

```python
scheduler.add_job(
    lambda: SystemContext().save_to_file(),
    'interval',
    hours=1,
    id="system_snapshot"
)
```

## 📝 Примеры данных

### Docker контейнеры

```json
{
  "name": "terag-api",
  "status": "running",
  "image": "terag:latest",
  "ports": {"8000/tcp": [{"HostPort": "8000"}]}
}
```

### Ресурсы

```json
{
  "cpu": {"count": 24, "percent": 15.5},
  "memory": {"total": 102400000000, "available": 50000000000, "percent": 51.2},
  "disk": {"total": 2000000000000, "free": 1760000000000, "percent": 12.0}
}
```

## 🚀 Будущие улучшения

- [ ] Сравнение с предыдущими снимками (детекция изменений)
- [ ] Автоматическое восстановление остановленных контейнеров
- [ ] Интеграция с Prometheus для метрик
- [ ] Визуализация истории изменений
- [ ] Предсказание проблем на основе истории

---

**Готово!** TERAG теперь знает свою инфраструктуру! 🎯✨













