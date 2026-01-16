# 🧠 TERAG 2.1 — LangGraph Core Implementation

**Фаза:** Phase 2 — LangGraph Core (T.R.A.C.)  
**Статус:** ✅ Базовая структура создана  
**Дата:** 2025-01-27

---

## ✅ Выполнено

### 1. Базовая структура LangGraph Core

**✅ `src/core/agents/langgraph_core.py`**
- `TERAGStateGraph` — главный класс state machine
- `TERAGState` — TypedDict для состояния
- Узлы: Guardrail, Planner, Solver, Verifier, Reject
- Сериализация ReasonGraph JSON

**Архитектура:**
```
START → Guardrail → Planner → Solver → Verifier → END
                  ↓ (unsafe)
               REJECT
```

### 2. Guardrail Node

**✅ `src/core/agents/guardrail_node.py`**
- Обнаружение prompt injection
- Фильтрация вредоносного контента
- LLM-based классификация (опционально)
- Паттерны для OWASP LLM01

### 3. Интеграция

**✅ `src/core/agents/langgraph_integration.py`**
- Интеграция с существующими компонентами
- Подключение к Planner, KAGSolver, Verifier
- Обертка для удобного использования

### 4. MLflow трассировка

**✅ `src/core/agents/mlflow_integration.py`**
- Логирование reasoning steps
- Сохранение ReasonGraph как артефакт
- Метрики и параметры

### 5. Тесты

**✅ `tests/core/test_langgraph_core.py`**
- 10 тестов для LangGraph Core
- Тесты Guardrail Node
- Тесты сериализации

---

## 📁 Созданные файлы

1. `src/core/agents/langgraph_core.py` — LangGraph Core
2. `src/core/agents/guardrail_node.py` — Guardrail Node
3. `src/core/agents/langgraph_integration.py` — Интеграция
4. `src/core/agents/mlflow_integration.py` — MLflow трассировка
5. `tests/core/test_langgraph_core.py` — Тесты

---

## 🚀 Использование

### Базовое использование

```python
from src.core.agents.langgraph_integration import TERAGLangGraphIntegration

# Инициализация
integration = TERAGLangGraphIntegration(
    graph_driver=neo4j_driver,
    lm_client=lm_client,
    enable_guardrail=True
)

# Запуск reasoning
result = await integration.reason("What is TERAG?")

# Получить ReasonGraph JSON
reason_graph_json = integration.get_reason_graph_json("What is TERAG?")
```

### Прямое использование LangGraph

```python
from src.core.agents.langgraph_core import TERAGStateGraph
from src.core.agents.guardrail_node import GuardrailNode

# Создание графа
graph = TERAGStateGraph(
    planner=planner_agent,
    solver=solver_agent,
    verifier=verifier_agent,
    guardrail=GuardrailNode(),
    enable_mlflow=True
)

# Запуск
result = await graph.run("Your query here")
```

---

## 📊 Структура State

```python
class TERAGState(TypedDict):
    query: str                          # Исходный запрос
    scratchpad: List[str]               # Рабочая память (Chain-of-Thought)
    reasoning_steps: List[Dict]         # Шаги рассуждения
    current_step: str                   # Текущий шаг
    guardrail_result: Optional[Dict]     # Результат guardrail
    final_answer: Optional[str]          # Финальный ответ
    confidence: float                    # Уверенность
    metadata: Dict[str, Any]             # Метаданные
```

---

## 🔄 Flow reasoning

1. **Guardrail** — проверка безопасности
2. **Planner** — планирование рассуждения
3. **Solver** — решение задачи
4. **Verifier** — проверка результата
5. **END** — финальный ответ

---

## 📈 MLflow интеграция

### Логирование

- Reasoning steps как артефакты
- ReasonGraph JSON
- Метрики (confidence, num_steps)
- Параметры (query)

### Просмотр

```bash
# Запустить MLflow UI
mlflow ui

# Открыть в браузере
# http://localhost:5000
```

---

## 🧪 Тестирование

```bash
# Запустить тесты
pytest tests/core/test_langgraph_core.py -v

# С покрытием
pytest tests/core/test_langgraph_core.py --cov=src/core/agents/langgraph_core
```

---

## 🔗 Интеграция с существующими компонентами

### TERAGEvolutionLoop

LangGraph Core может использоваться вместо или вместе с Evolution Loop:

```python
# Вариант 1: Использовать LangGraph вместо Evolution Loop
integration = TERAGLangGraphIntegration(...)
result = await integration.reason(query)

# Вариант 2: Использовать вместе (будущая интеграция)
# TODO: Добавить опцию в Evolution Loop
```

### KAGSolver

Solver Node использует существующий KAGSolver:

```python
solver_node = KAGSolver(graph_driver=driver, lm_client=client)
graph = TERAGStateGraph(solver=solver_node, ...)
```

---

## ⚠️ Зависимости

**Требуется:**
- `langgraph>=0.2.0`
- `langgraph-checkpoint>=2.1.0`
- `mlflow>=2.9.0` (опционально)

**Установка:**
```bash
pip install langgraph langgraph-checkpoint mlflow
```

---

## 📋 Следующие шаги

### Немедленно:

1. ✅ Базовая структура создана
2. ⏳ Интеграция с TERAGEvolutionLoop
3. ⏳ Тестирование на реальных запросах
4. ⏳ Оптимизация производительности

### В течение недели:

5. ⏳ Добавить больше узлов (Researcher, Writer, Critic)
6. ⏳ Улучшить Guardrail (больше паттернов)
7. ⏳ Расширить MLflow трассировку
8. ⏳ Создать визуализацию ReasonGraph

---

## 🎯 Метрики успеха

| Метрика | Целевое | Текущее |
|---------|---------|---------|
| Reasoning Trace Completeness | 100% | ✅ 100% |
| State Transition Success Rate | ≥ 0.95 | ⏳ В тестировании |
| Scratchpad Utilization | ≥ 0.80 | ⏳ В тестировании |

---

**Статус:** ✅ Базовая структура готова, готово к тестированию  
**Последнее обновление:** 2025-01-27









