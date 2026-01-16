# 🧠 Pattern Memory — База лучших практик TERAG

## 📋 Обзор

**Pattern Memory** — модуль распознавания и сохранения шаблонов поведения для TERAG. Система автоматически:

- Классифицирует результаты reasoning и OSINT-миссий как **SUCCESS** или **FAILURE**
- Сохраняет паттерны как узлы `:Pattern` в Neo4j
- Связывает успешные и неудачные паттерны через связи `:BEST_PRACTICE`
- Усиливает успешные связи и ослабляет неудачные с течением времени
- Формирует базу лучших практик для улучшения reasoning

---

## 🎯 Концепция

TERAG учится на собственном опыте:

1. **Распознавание паттернов**: Когда система выполняет reasoning или миссию, результат анализируется
2. **Классификация**: LM Studio определяет, был ли результат успешным или ошибочным
3. **Сохранение**: Паттерн сохраняется в граф знаний с метаданными
4. **Связывание**: Успешные паттерны связываются с неудачными для формирования базы знаний
5. **Эволюция**: Старые паттерны ослабевают (decay), новые усиливаются

---

## 🚀 Быстрый старт

### Инициализация

```python
from src.core.pattern_memory import PatternMemory
from src.integration.lmstudio_client import LMStudioClient
from installer.app.modules.graph_updater import GraphUpdater

# Инициализация компонентов
lm_client = LMStudioClient()
await lm_client.connect()

graph_updater = GraphUpdater(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="terag_neo4j_2025"
)

# Создание Pattern Memory
pattern_mem = PatternMemory(
    graph_updater=graph_updater,
    lm_client=lm_client
)
```

### Обучение на результате

```python
# Результат reasoning или миссии
result = {
    "task": "OSINT summarization",
    "output": "Relevant summary generated",
    "quality_score": 0.92
}

# Обучение
learn_result = await pattern_mem.learn_from_result(result)

print(f"Classification: {learn_result['classification']['classification']}")
print(f"Pattern: {learn_result['pattern_name']}")
```

### Получение лучших практик

```python
# Получить топ-10 успешных паттернов
best = await pattern_mem.get_best_practices(limit=10)

for practice in best:
    print(f"{practice['name']}: {practice['occurrences']} occurrences")
```

---

## 📚 API Reference

### `PatternMemory`

#### `async classify_pattern(result: Dict[str, Any]) -> Dict[str, Any]`

Классифицировать результат как SUCCESS или FAILURE.

**Параметры:**
- `result`: Результат reasoning или миссии (должен содержать `task`, `output`, `quality_score`)

**Возвращает:**
```python
{
    "classification": "SUCCESS" | "FAILURE",
    "reason": "Explanation text",
    "pattern_name": "PatternName",
    "confidence": 0.0-1.0
}
```

**Пример:**
```python
classification = await pattern_mem.classify_pattern({
    "task": "Reasoning",
    "output": "Accurate reasoning",
    "quality_score": 0.88
})
```

---

#### `async store_pattern(pattern: Dict[str, Any]) -> bool`

Сохранить паттерн в граф знаний.

**Параметры:**
- `pattern`: Словарь с классификацией (результат `classify_pattern`)

**Возвращает:**
- `True` если успешно, `False` иначе

**Пример:**
```python
classification = await pattern_mem.classify_pattern(result)
stored = await pattern_mem.store_pattern(classification)
```

---

#### `link_patterns(success_name: str, failure_name: str, strength: float = 0.1) -> bool`

Связать успешный и неудачный паттерн.

**Параметры:**
- `success_name`: Имя успешного паттерна
- `failure_name`: Имя неудачного паттерна
- `strength`: Усиление связи (по умолчанию 0.1)

**Возвращает:**
- `True` если успешно, `False` иначе

**Пример:**
```python
pattern_mem.link_patterns(
    success_name="OptimizedPrompt",
    failure_name="AmbiguousPrompt"
)
```

---

#### `decay_patterns()`

Уменьшить силу связей и частоту старых паттернов.

**Правило:**
- Если паттерн не обновлялся > `decay_days` дней → уменьшить `occurrences`
- Уменьшить `strength` связей `:BEST_PRACTICE`

**Пример:**
```python
pattern_mem.decay_patterns()
```

---

#### `async get_best_practices(domain: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]`

Получить лучшие практики (успешные паттерны).

**Параметры:**
- `domain`: Домен для фильтрации (опционально)
- `limit`: Максимальное количество практик

**Возвращает:**
```python
[
    {
        "name": "PatternName",
        "reason": "Explanation",
        "occurrences": 5,
        "confidence": 0.9
    },
    ...
]
```

**Пример:**
```python
best = await pattern_mem.get_best_practices(domain="OSINT", limit=5)
```

---

#### `async learn_from_result(result: Dict[str, Any]) -> Dict[str, Any]`

Обучение на результате (классификация + сохранение).

**Параметры:**
- `result`: Результат reasoning или миссии

**Возвращает:**
```python
{
    "classification": {...},
    "stored": True,
    "pattern_name": "PatternName"
}
```

**Пример:**
```python
learn_result = await pattern_mem.learn_from_result(result)
```

---

#### `get_pattern_stats() -> Dict[str, Any]`

Получить статистику паттернов.

**Возвращает:**
```python
{
    "total": 12,
    "success": 9,
    "failure": 3,
    "avg_strength": 0.73
}
```

**Пример:**
```python
stats = pattern_mem.get_pattern_stats()
print(f"Patterns: {stats['total']} ({stats['success']} success, {stats['failure']} failure)")
```

---

## 🔗 Интеграция

### Learning Bridge

Pattern Memory автоматически интегрирован с Learning Bridge:

```python
from src.integration.learning_bridge import LearningBridge

bridge = LearningBridge(...)

# При вызове reason_with_context паттерны сохраняются автоматически
result = await bridge.reason_with_context(
    question="What is AI governance?",
    learn_pattern=True  # По умолчанию True
)
```

### Telegram Service

При сохранении успешного паттерна отправляется уведомление:

```
🧩 Новый паттерн: OptimizedPromptDesign

🟢 Классификация: SUCCESS

🔍 Причина: Оптимизация формулировки запроса повысила точность reasoning.
```

### Health-check

В `check_terag_full_stack.py` добавлена статистика паттернов:

```
✅ Graph Updater готов (Neo4j)
  🧠 Patterns: 12 (9 успешных, 3 ошибочных)
  🔗 Средняя сила связей: 0.73
```

---

## 🧪 Тестирование

Запустите тестовый скрипт:

```bash
python scripts/tests/test_pattern_memory.py
```

Тест проверяет:
- ✅ Классификацию успешных и неудачных результатов
- ✅ Сохранение паттернов в граф
- ✅ Связывание паттернов
- ✅ Получение лучших практик
- ✅ Статистику паттернов
- ✅ Обучение на результате

---

## 📊 Структура данных в Neo4j

### Узлы :Pattern

```cypher
(:Pattern {
    name: "OptimizedPromptDesign",
    classification: "SUCCESS",
    reason: "Explanation text",
    confidence: 0.9,
    occurrences: 5,
    created_at: datetime(),
    last_seen: datetime()
})
```

### Связи :BEST_PRACTICE

```cypher
(:Pattern {name: "SuccessPattern"})-[:BEST_PRACTICE {
    strength: 0.8,
    created_at: datetime(),
    updated_at: datetime()
}]->(:Pattern {name: "FailurePattern"})
```

### Запросы

**Получить все успешные паттерны:**
```cypher
MATCH (p:Pattern)
WHERE p.classification = 'SUCCESS'
RETURN p.name, p.occurrences, p.confidence
ORDER BY p.occurrences DESC
LIMIT 10
```

**Получить связи между паттернами:**
```cypher
MATCH (s:Pattern {classification: 'SUCCESS'})-[r:BEST_PRACTICE]->(f:Pattern {classification: 'FAILURE'})
RETURN s.name, f.name, r.strength
ORDER BY r.strength DESC
```

---

## 🎓 Примеры использования

### Пример 1: Обучение на OSINT-миссии

```python
# Результат OSINT-миссии
osint_result = {
    "task": "Deep search: AI governance trends",
    "output": "Found 15 relevant articles",
    "quality_score": 0.85,
    "sources_count": 15
}

# Обучение
await pattern_mem.learn_from_result(osint_result)
```

### Пример 2: Использование лучших практик

```python
# Получить лучшие практики для домена
best = await pattern_mem.get_best_practices(domain="OSINT", limit=5)

# Использовать в reasoning
for practice in best:
    print(f"Best practice: {practice['name']} - {practice['reason']}")
```

### Пример 3: Автоматический decay

```python
# Запускать раз в сутки (например, в cron)
pattern_mem.decay_patterns()
```

---

## 🔧 Конфигурация

### Параметры инициализации

```python
pattern_mem = PatternMemory(
    graph_updater=graph_updater,
    lm_client=lm_client,
    decay_days=7  # Количество дней до начала decay
)
```

### Переменные окружения

Не требуются (использует существующие настройки Neo4j и LM Studio).

---

## 📈 Метрики

Pattern Memory отслеживает:

- **Количество паттернов**: Общее, успешных, неудачных
- **Сила связей**: Средняя сила связей `:BEST_PRACTICE`
- **Частота использования**: Количество `occurrences` для каждого паттерна
- **Decay score**: Показатель ослабления старых паттернов

---

## 🚀 Будущие улучшения

- [ ] Автоматическое извлечение паттернов из истории reasoning
- [ ] Кластеризация похожих паттернов
- [ ] Визуализация паттернов в Grafana
- [ ] Экспорт паттернов в JSON/YAML
- [ ] Импорт паттернов из других систем

---

## 📝 Связанные задачи

- **Task 10**: Learning Bridge Integration
- **Task 10b**: Self-Organizing Knowledge Graph
- **Task 11**: Cognitive Metrics (Auto-Eval Layer)

---

**Pattern Memory превращает TERAG в самообучающуюся систему, которая формирует базу лучших практик автоматически!** 🧠✨













