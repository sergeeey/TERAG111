# 🛠️ TERAG 2.1 — Implementation Guide

**Кодовое имя:** *Vizier's Bridge*  
**Версия:** 1.0  
**Дата:** 2025-01-27

---

## 📋 Быстрая навигация

- [Phase 1: Benchmark & Validation](#phase-1-benchmark--validation) ✅
- [Phase 2: LangGraph Core (T.R.A.C.)](#phase-2-langgraph-core-trac) 🔴
- [Phase 3: Security Layer](#phase-3-security-layer) 🔴
- [Phase 4: PromptOps Integration](#phase-4-promptops-integration) 🔴
- [Phase 5: Vizier's Bridge UX](#phase-5-viziers-bridge-ux) 🟡

---

## Phase 1: Benchmark & Validation ✅

**Статус:** ✅ Завершено

### Что сделано

- ✅ Создана структура `src/benchmark/`
- ✅ Реализованы 3 пайплайна (Vector, Graph, Hybrid)
- ✅ Интегрирован RAGAs для оценки
- ✅ Настроен MLflow
- ✅ Создан CI/CD workflow

### Использование

```bash
# Запуск benchmark
python src/benchmark/run_benchmark.py --pipeline all
```

### Документация

- [TERAG 2.1 Benchmark](TERAG_2.1_BENCHMARK.md)
- [Benchmark Implementation Summary](BENCHMARK_IMPLEMENTATION_SUMMARY.md)

---

## Phase 2: LangGraph Core (T.R.A.C.) 🔴

**Статус:** ⏳ В очереди  
**Приоритет:** CRITICAL  
**Срок:** 2 недели

### Задачи

1. **Создать LangGraph Core**
   ```python
   # src/core/agents/langgraph_core.py
   from langgraph.graph import StateGraph, END
   
   class TERAGStateGraph:
       def __init__(self):
           self.graph = StateGraph(TERAGState)
           self._build_graph()
   ```

2. **Реализовать узлы**
   - `Planner_Node` — планирование
   - `Solver_Node` — решение
   - `Verifier_Node` — проверка
   - `Guardrail_Node` — фильтрация

3. **Интегрировать Scratchpad**
   ```python
   class TERAGState(TypedDict):
       query: str
       scratchpad: List[str]
       reasoning_steps: List[Dict]
       final_answer: Optional[str]
   ```

4. **Сериализация ReasonGraph**
   ```python
   def serialize_reason_graph(self) -> Dict:
       return {
           "nodes": [...],
           "edges": [...],
           "state": self.current_state
       }
   ```

### Интеграция

- Подключить к `TERAGEvolutionLoop`
- Интегрировать с `KAGSolver`
- Связать с `AI-REPS` метриками

### Тестирование

```bash
# Тесты для LangGraph Core
pytest tests/core/test_langgraph_core.py
```

---

## Phase 3: Security Layer 🔴

**Статус:** ⏳ В очереди  
**Приоритет:** HIGH  
**Срок:** 2 недели

### Задачи

1. **Guardrail_Node**
   ```python
   # src/core/agents/guardrail_node.py
   class GuardrailNode:
       async def classify(self, input: str) -> Dict:
           # Классификация safe/harmful
           return {"safe": bool, "confidence": float}
   ```

2. **Условные переходы**
   ```python
   if guardrail_result["safe"]:
       return "continue"
   else:
       return "reject"
   ```

3. **Promptfoo интеграция**
   ```yaml
   # promptfoo.yml
   tests:
     - vars:
         prompt: "{{input}}"
       assert:
         - type: contains
           value: "harmful"
   ```

### Red Team тесты

```bash
# Запуск Red Team тестов
promptfoo test
```

---

## Phase 4: PromptOps Integration 🔴

**Статус:** ⏳ В очереди  
**Приоритет:** HIGH  
**Срок:** 2 недели

### Задачи

1. **MLflow Prompt Registry**
   ```python
   # prompts/registry/
   prompts/
     registry/
       planner_v1.yaml
       planner_v2.yaml
       solver_v1.yaml
   ```

2. **Backend интеграция**
   ```python
   # src/api/prompt_loader.py
   class PromptLoader:
       def load(self, alias: str) -> str:
           # @dev, @staging, @prod
   ```

3. **CI/CD автоматизация**
   ```yaml
   # .github/workflows/promptops.yml
   - name: PromptLint
     run: promptlint prompts/registry/
   ```

---

## Phase 5: Vizier's Bridge UX 🟡

**Статус:** ⏳ В очереди  
**Приоритет:** MEDIUM  
**Срок:** 2 недели

### Задачи

1. **SSE endpoint**
   ```python
   # src/api/server.py
   @app.get("/api/reasoning/stream")
   async def stream_reasoning():
       async def event_generator():
           while reasoning_active:
               yield f"data: {reason_graph_json}\n\n"
   ```

2. **3D компонент**
   ```tsx
   // src/components/vizier/TeragVizierScene.tsx
   export function TeragVizierScene({ reasonGraph }) {
     return (
       <Canvas>
         <ReasonGraphNodes nodes={reasonGraph.nodes} />
         <ReasonGraphEdges edges={reasonGraph.edges} />
       </Canvas>
     )
   }
   ```

3. **UX метрики**
   ```typescript
   // A.R.I. (Average Resonance Index)
   const ari = calculateARI(userFeedback)
   ```

---

## 🔧 Инструменты разработки

### Установка зависимостей

```bash
# Основные зависимости
pip install -r requirements.txt

# LangGraph
pip install langgraph langgraph-checkpoint

# Promptfoo
npm install -g promptfoo

# MLflow
pip install mlflow
```

### Настройка окружения

```bash
# Neo4j
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"

# MLflow
export MLFLOW_TRACKING_URI="http://localhost:5000"

# LangSmith (опционально)
export LANGCHAIN_API_KEY="your-key"
```

---

## 📊 Метрики и KPI

### Общие метрики

| Метрика | Целевое | Текущее |
|---------|---------|---------|
| Faithfulness | ≥ 0.90 | ⏳ |
| Context Recall | ≥ 0.90 | ⏳ |
| OWASP LLM01 Detection | ≥ 0.99 | ⏳ |
| Cognitive Resonance | ≥ 0.8 | ⏳ |

### Метрики по фазам

См. [Roadmap](ROADMAP_TERAG_2.1.md) для детальных метрик каждой фазы.

---

## 🚀 Быстрый старт

### 1. Клонировать и установить

```bash
git clone <repo>
cd TERAG111-1
pip install -r requirements.txt
```

### 2. Настроить окружение

```bash
cp env.example .env
# Отредактировать .env
```

### 3. Запустить Phase 1 (Benchmark)

```bash
python src/benchmark/run_benchmark.py --pipeline all
```

### 4. Начать Phase 2 (LangGraph Core)

```bash
# Создать структуру
mkdir -p src/core/agents/langgraph
# Начать реализацию
```

---

## 📚 Дополнительные ресурсы

- [Roadmap](ROADMAP_TERAG_2.1.md) — детальная дорожная карта
- [Implementation Plan](../cursor_task.json) — JSON план
- [Benchmark Documentation](TERAG_2.1_BENCHMARK.md) — Benchmark детали

---

**Последнее обновление:** 2025-01-27









