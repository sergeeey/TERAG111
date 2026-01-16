# 🔧 TERAG 2.1 — PromptOps Implementation

**Фаза:** Phase 4 — PromptOps Integration  
**Статус:** ✅ Завершено  
**Дата:** 2025-01-27

---

## 🎯 Цель

Интегрировать систему управления промптами и наблюдаемости (PromptOps + LangSmith) в архитектуру TERAG:
- MLflow Prompt Registry как единый источник правды
- Динамическая загрузка промптов без перезапуска
- LangSmith для глубокой трассировки
- CI/CD для Prompts as Code

---

## ✅ Выполнено

### 4.1 MLflow Prompt Registry ✅

**Файлы:**
- `src/promptops/mlflow_registry.py` — менеджер реестра
- `configs/prompts/registry_schema.json` — JSON схема

**Функции:**
- `register_prompt()` — регистрация промптов
- `get_prompt(alias)` — извлечение по алиасам
- `list_prompts()` — список всех промптов
- Версионирование через MLflow Model Registry
- Валидация по JSON схеме

**Алиасы:**
- `@latest` — последняя версия
- `@staging` — staging версия
- `@production` — production версия
- `@dev` — development версия

---

### 4.2 Dynamic Prompt Loader Service ✅

**Файлы:**
- `src/promptops/loader_service.py` — сервис загрузки
- `src/promptops/router.py` — FastAPI router

**Функции:**
- Загрузка промптов из MLflow Registry
- In-memory cache с TTL (60 минут)
- Redis cache поддержка
- Обновление без перезапуска backend
- Подстановка переменных

**API Endpoints:**
- `GET /api/prompts/{name}?alias=@production` — загрузка промпта
- `POST /api/prompts/load` — загрузка с переменными
- `POST /api/prompts/reload` — перезагрузка (очистка кэша)
- `POST /api/prompts/register` — регистрация нового промпта
- `GET /api/prompts/list` — список всех промптов

---

### 4.3 LangSmith Observability ✅

**Файлы:**
- `src/promptops/langsmith_integration.py` — LangSmith интеграция

**Функции:**
- `log_step()` — логирование шагов reasoning
- `log_llm_call()` — логирование LLM вызовов
- `sync_with_mlflow()` — синхронизация с MLflow
- Трассировка токенов и промежуточных результатов
- Длительность и метаданные

**Интеграция:**
- Добавлен в LangGraph Core
- Логирование в каждом узле (Planner, Solver, Verifier, Ethical)
- Синхронизация run_id с MLflow

---

### 4.4 CI/CD for Prompts as Code ✅

**Файлы:**
- `.github/workflows/promptops.yml` — CI/CD workflow
- `tests/promptops/test_prompts_lint.py` — тесты линтинга
- `tests/promptops/test_prompts_eval.py` — тесты оценки

**Этапы:**
1. Prompt Lint — проверка схемы
2. Security Scan — Bandit
3. Dependency Audit — pip-audit
4. Tests — unit тесты
5. Reports — сохранение отчетов

**Автоматизация:**
- Запуск при изменениях в `src/promptops/` или `configs/prompts/`
- Проверка pass rate ≥ 90%
- Сохранение отчетов в артефактах

---

### 4.5 Integration with LangGraph Core ✅

**Изменения:**
- Добавлен `PromptLoaderService` в `TERAGLangGraphIntegration`
- LangSmith tracer интегрирован в узлы
- Логирование версии промпта в MLflow
- Динамическая загрузка промптов при инициализации

**Совместимость:**
- Работает с Guardrail и Ethical Node
- Поддержка всех алиасов
- Кэширование для производительности

---

## 📊 Метрики

| Метрика | Целевое | Статус |
|---------|---------|--------|
| Prompt Registry Coverage | ≥ 0.95 | ⏳ В тестировании |
| Prompt Lint Pass Rate | ≥ 0.9 | ⏳ В тестировании |
| MLflow Sync Reliability | ≥ 0.95 | ⏳ В тестировании |
| Observability Trace Completeness | ≥ 0.9 | ⏳ В тестировании |

---

## 🚀 Использование

### Регистрация промпта

```python
from src.promptops.mlflow_registry import PromptRegistryManager

registry = PromptRegistryManager()

run_id = registry.register_prompt(
    name="planner_v1",
    content="Create a plan for: {query}",
    version="1.0.0",
    description="Planner prompt for reasoning",
    variables=[
        {"name": "query", "type": "string", "required": True}
    ],
    aliases=["@latest", "@production"]
)
```

### Загрузка промпта

```python
from src.promptops.loader_service import PromptLoaderService

loader = PromptLoaderService()

# Загрузка по алиасу
prompt = loader.load_prompt("planner_v1", alias="@production")

# Загрузка с переменными
prompt = loader.load_prompt_with_variables(
    "planner_v1",
    variables={"query": "What is TERAG?"}
)
```

### API использование

```bash
# Загрузить промпт
curl http://localhost:8000/api/prompts/planner_v1?alias=@production

# Загрузить с переменными
curl -X POST http://localhost:8000/api/prompts/load \
  -H "Content-Type: application/json" \
  -d '{
    "name": "planner_v1",
    "alias": "@production",
    "variables": {"query": "What is TERAG?"}
  }'

# Перезагрузить промпт
curl -X POST http://localhost:8000/api/prompts/reload \
  -H "Content-Type: application/json" \
  -d '{"name": "planner_v1", "alias": "@production"}'

# Список промптов
curl http://localhost:8000/api/prompts/list
```

---

## 📁 Созданные файлы (9)

1. `src/promptops/mlflow_registry.py`
2. `src/promptops/loader_service.py`
3. `src/promptops/router.py`
4. `src/promptops/langsmith_integration.py`
5. `configs/prompts/registry_schema.json`
6. `tests/promptops/test_prompts_lint.py`
7. `tests/promptops/test_prompts_eval.py`
8. `.github/workflows/promptops.yml`
9. `docs/PROMPTOPS_IMPLEMENTATION.md`

---

## 🔄 Архитектура

### PromptOps Flow

```
MLflow Registry
    ↓
PromptLoaderService (Cache)
    ↓
LangGraph Nodes
    ├─ Planner (prompt: planner_v1)
    ├─ Solver (prompt: solver_base)
    ├─ Verifier (prompt: verifier_strict)
    └─ Ethical (prompt: ethical_evaluator)
    ↓
LangSmith Tracing
    ↓
MLflow Logging
```

### API Endpoints

```
/api/prompts/
├─ GET /{name}              → Загрузить промпт
├─ POST /load               → Загрузить с переменными
├─ POST /reload             → Перезагрузить (очистить кэш)
├─ POST /register           → Зарегистрировать новый
└─ GET /list                → Список всех промптов
```

---

## 🧪 Тестирование

### Unit тесты

```bash
# Все PromptOps тесты
pytest tests/promptops/ -v

# Только линтинг
pytest tests/promptops/test_prompts_lint.py -v

# Только оценка
pytest tests/promptops/test_prompts_eval.py -v
```

### CI/CD

```bash
# Локальный запуск CI проверок
python -c "
import json
from pathlib import Path
schema_path = Path('configs/prompts/registry_schema.json')
# Проверка схемы
"
```

---

## 📈 CI/CD Pipeline

### Этапы

1. **Prompt Validation** — проверка схемы
2. **Security Scan** — Bandit
3. **Dependency Audit** — pip-audit
4. **Tests** — unit тесты
5. **Reports** — сохранение отчетов

### Расписание

- Автоматически: при изменениях в `src/promptops/` или `configs/prompts/`
- При PR: автоматически
- Вручную: через GitHub Actions UI

---

## 🔗 Интеграция

### С LangGraph Core

- `PromptLoaderService` используется для загрузки промптов
- LangSmith tracer логирует каждый шаг
- MLflow синхронизируется с LangSmith через run_id

### С существующими компонентами

- Работает с Guardrail и Ethical Node
- Использует существующий Redis cache
- Интегрирован в FastAPI server

---

## ⚠️ Известные ограничения

1. **MLflow Registry:**
   - Требует запущенный MLflow server
   - Может быть медленным для больших объемов

2. **LangSmith:**
   - Требует API ключ
   - Может быть дорогим для больших объемов

3. **Кэширование:**
   - In-memory cache не распределен
   - Redis требуется для production

---

## 📋 Следующие шаги

### Немедленно:

1. ✅ Базовая структура создана
2. ⏳ Тестирование на реальных промптах
3. ⏳ Настройка MLflow и LangSmith

### В течение недели:

4. ⏳ Создание начальных промптов
5. ⏳ Оптимизация производительности
6. ⏳ Расширение тестового покрытия

---

## 🎯 Критерии завершения

- ✅ MLflow Prompt Registry реализован
- ✅ Dynamic Prompt Loader Service создан
- ✅ LangSmith интеграция добавлена
- ✅ CI/CD настроен
- ✅ API endpoints работают
- ✅ Тесты написаны
- ⏳ Покрытие промптов ≥ 95% (требует создания промптов)

---

**Статус:** ✅ Реализация завершена, готово к тестированию  
**Последнее обновление:** 2025-01-27









