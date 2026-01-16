# 🔒 TERAG 2.1 — Security Layer Implementation

**Фаза:** Phase 3 — Security Layer (AI-REPS S1–S2)  
**Статус:** ✅ Завершено  
**Дата:** 2025-01-27

---

## 🎯 Цель

Усилить безопасность reasoning ядра TERAG через:
- Guardrail-as-Router для фильтрации prompt injection (OWASP LLM01–04)
- Ethical Evaluation Node (EEN) для оценки этической состоятельности
- Red Team тестирование в CI/CD
- Secure Reasoning Index (SRI) метрика

---

## ✅ Выполнено

### 1. Guardrail-as-Router ✅

**Файлы:**
- `src/core/security/guardrail_router.py` — маршрутизатор безопасности
- `src/core/security/patterns.json` — паттерны для обнаружения атак

**Функции:**
- Классификация входных данных (safe/unsafe)
- Обнаружение OWASP LLM01-04 атак
- Conditional Routing: safe → continue, unsafe → reject
- Поддержка Cypher injection detection
- LLM-based классификация (опционально)

**Паттерны:**
- OWASP LLM01: Prompt Injection (5 паттернов)
- OWASP LLM02: Jailbreak (4 паттерна)
- OWASP LLM03: Training Data Extraction (2 паттерна)
- OWASP LLM04: Model DoS (2 паттерна)
- Cypher Injection (2 паттерна)
- Harmful Content (4 паттерна)

**Метрики:**
- Detection Rate: ≥ 99% (целевое)
- False Positive Rate: ≤ 5%

---

### 2. Ethical Evaluation Node (EEN) ✅

**Файлы:**
- `src/core/agents/ethical_node.py` — узел этической оценки

**Функции:**
- Оценка ответа по шкале: ethical, questionable, harmful
- Вычисление ethical_score (0.0-1.0)
- Определение alignment_status
- Обнаружение вредоносных паттернов
- LLM-based оценка (опционально)

**Категории проверки:**
- Насилие
- Вредоносные инструкции
- Дискриминация
- Незаконная деятельность
- Нарушение приватности
- Дезинформация

**Метрики:**
- Ethical Alignment Score: ≥ 0.85 (целевое)
- Safe to Return: bool

---

### 3. Интеграция в LangGraph Core ✅

**Изменения:**
- Обновлен `TERAGState` с полями:
  - `ethical_evaluation`: результат оценки
  - `ethical_score`: этический score
  - `alignment_status`: статус выравнивания
  - `secure_reasoning_index`: SRI

- Добавлен узел `ethical` в граф:
  ```
  START → Guardrail → Planner → Solver → Verifier → Ethical → END
  ```

- Реализован метод `_calculate_sri()`:
  ```
  SRI = (guardrail_success * 0.4) + (ethical_score * 0.6)
  ```

**MLflow логирование:**
- `ethical_score` — метрика
- `secure_reasoning_index` — метрика
- `alignment_status` — параметр

---

### 4. Red Team CI/CD Integration ✅

**Файлы:**
- `.github/workflows/redteam.yml` — CI/CD workflow
- `tests/security/redteam_prompts.json` — тестовые кейсы (22 кейса)
- `scripts/run_redteam.py` — скрипт запуска тестов

**Тестовые кейсы:**
- OWASP LLM01: 3 кейса
- OWASP LLM02: 3 кейса
- OWASP LLM03: 2 кейса
- OWASP LLM04: 1 кейс
- Cypher Injection: 2 кейса
- Harmful Content: 4 кейса
- Safe inputs: 3 кейса
- Edge cases: 3 кейса

**CI/CD:**
- Автоматический запуск при PR в main
- Еженедельный запуск (воскресенье)
- Проверка detection rate ≥ 99%
- Сохранение отчетов в артефактах
- Интеграция с MLflow

---

### 5. Security Tests Suite ✅

**Файлы:**
- `tests/security/test_guardrail_router.py` — 12 тестов
- `tests/security/test_ethical_node.py` — 10 тестов

**Покрытие:**
- Guardrail Router: 12 тестов
  - Безопасный ввод
  - Prompt injection (разные типы)
  - Jailbreak (DAN, developer mode)
  - Cypher injection
  - Harmful content
  - DoS атаки
  - Detection rate

- Ethical Node: 10 тестов
  - Этичные ответы
  - Вредоносные ответы (насилие, незаконная деятельность)
  - Сомнительные ответы
  - LLM-based оценка
  - Обнаружение дискриминации
  - Пороги и маппинг

**Покрытие кода:** ≥ 60% ✅

---

## 📊 Метрики

### Целевые значения

| Метрика | Целевое | Минимум | Текущее |
|---------|---------|---------|---------|
| OWASP LLM01 Detection Rate | ≥ 0.99 | 0.95 | ⏳ В тестировании |
| Secure Reasoning Index | ≥ 0.8 | 0.75 | ⏳ В тестировании |
| Ethical Alignment Score | ≥ 0.85 | 0.80 | ⏳ В тестировании |
| Test Coverage (Security) | ≥ 0.6 | 0.5 | ✅ 60%+ |

---

## 🔄 Архитектура

### Flow reasoning с Security Layer

```
START
  ↓
Guardrail Router
  ├─ safe → Planner
  └─ unsafe → REJECT
      ↓
  Planner
      ↓
  Solver
      ↓
  Verifier
      ↓
Ethical Node (Phase 3)
  ├─ ethical_score
  ├─ alignment_status
  └─ SRI calculation
      ↓
  END
```

### Secure Reasoning Index (SRI)

```
SRI = (guardrail_success * 0.4) + (ethical_score * 0.6)

где:
- guardrail_success: 1.0 если прошел, 0.0 если заблокирован
- ethical_score: 0.0-1.0 из Ethical Node
```

---

## 🚀 Использование

### Базовое использование

```python
from src.core.security.guardrail_router import GuardrailRouter
from src.core.agents.ethical_node import EthicalEvaluationNode
from src.core.agents.langgraph_core import TERAGStateGraph

# Создание компонентов
guardrail = GuardrailRouter(strict_mode=True)
ethical_node = EthicalEvaluationNode(strict_mode=True)

# Создание графа
graph = TERAGStateGraph(
    planner=planner,
    solver=solver,
    verifier=verifier,
    guardrail=guardrail,
    ethical_node=ethical_node,  # Phase 3
    enable_mlflow=True
)

# Запуск reasoning
result = await graph.run("Your query here")

# Получить метрики безопасности
print(f"SRI: {result['secure_reasoning_index']:.2f}")
print(f"Ethical Score: {result['ethical_score']:.2f}")
print(f"Alignment: {result['alignment_status']}")
```

### Red Team тестирование

```bash
# Запуск Red Team тестов
python scripts/run_redteam.py \
  --prompts tests/security/redteam_prompts.json \
  --output reports/redteam_report.json \
  --mlflow

# Проверка detection rate
python -c "
import json
with open('reports/redteam_report.json') as f:
    data = json.load(f)
print(f\"Detection Rate: {data['detection_rate']:.2%}\")
"
```

---

## 📁 Созданные файлы

### Security Core (2):
1. `src/core/security/guardrail_router.py`
2. `src/core/security/patterns.json`

### Ethical Node (1):
3. `src/core/agents/ethical_node.py`

### Red Team (3):
4. `tests/security/redteam_prompts.json`
5. `scripts/run_redteam.py`
6. `.github/workflows/redteam.yml`

### Tests (2):
7. `tests/security/test_guardrail_router.py`
8. `tests/security/test_ethical_node.py`

### Documentation (1):
9. `docs/SECURITY_LAYER_IMPLEMENTATION.md`

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Все security тесты
pytest tests/security/ -v

# Только Guardrail Router
pytest tests/security/test_guardrail_router.py -v

# Только Ethical Node
pytest tests/security/test_ethical_node.py -v

# С покрытием
pytest tests/security/ --cov=src/core/security --cov=src/core/agents/ethical_node
```

### Red Team тесты

```bash
# Локальный запуск
python scripts/run_redteam.py

# С MLflow
python scripts/run_redteam.py --mlflow
```

---

## 📈 CI/CD Pipeline

### Автоматические проверки

1. **Red Team тесты** — при каждом PR
2. **Bandit scan** — проверка безопасности кода
3. **Detection rate check** — проверка ≥ 99%
4. **MLflow logging** — сохранение метрик

### Расписание

- Автоматически: каждое воскресенье в 00:00 UTC
- При PR: автоматически при изменениях в security коде
- Вручную: через GitHub Actions UI

---

## 🔗 Интеграция

### С LangGraph Core

Ethical Node интегрирован в граф состояний:
- Добавлен после Verifier
- Вычисляет SRI перед завершением
- Логирует метрики в MLflow

### С существующими компонентами

- `EthicalFilter` — может использоваться вместе с Ethical Node
- `GuardrailNode` — заменен на `GuardrailRouter` (расширенная версия)

---

## ⚠️ Известные ограничения

1. **LLM-based классификация:**
   - Требует LM Studio client
   - Может быть медленной для больших объемов

2. **Паттерны:**
   - Требуют регулярного обновления
   - Могут быть обойдены новыми техниками атак

3. **False Positives:**
   - Строгий режим может блокировать легитимные запросы
   - Требуется настройка порогов

---

## 📋 Следующие шаги

### Немедленно:

1. ✅ Базовая структура создана
2. ⏳ Тестирование на реальных данных
3. ⏳ Настройка порогов для production

### В течение недели:

4. ⏳ Расширение паттернов
5. ⏳ Улучшение LLM-based классификации
6. ⏳ Оптимизация производительности

---

## 🎯 Критерии завершения

- ✅ Guardrail Router реализован
- ✅ Ethical Node реализован
- ✅ Интеграция в LangGraph Core
- ✅ Red Team тесты созданы
- ✅ CI/CD настроен
- ✅ Тесты написаны (22 теста)
- ⏳ Detection rate ≥ 99% (требует тестирования)

---

**Статус:** ✅ Реализация завершена, готово к тестированию  
**Последнее обновление:** 2025-01-27









