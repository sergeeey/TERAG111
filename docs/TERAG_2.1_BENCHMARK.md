# 🧠 TERAG 2.1 — Benchmark & Validation

**Кодовое имя:** *Baseline Proof Cycle*  
**Дата:** 2025-01-27  
**Владелец:** Сергей Валерьевич  
**Цель:** Сравнить Vector-RAG, Graph-RAG и Hybrid GraphRAG по метрикам Faithfulness, Context Precision, Context Recall.

**Фаза:** Stage 1 / Foundation Benchmark

---

## 🎯 Задача

Построить воспроизводимый эксперимент, который подтверждает гипотезу из TERAG 2.0:

> **GraphRAG (Neo4j) обеспечивает более высокую фактологическую точность и контекстную полноту, чем стандартные Vector-RAG (ChromaDB).**

---

## ⚙️ Требования к среде

```bash
python >= 3.11
haystack-ai >= 2.0.0
neo4j >= 5.12
chromadb >= 0.4.15
sentence-transformers >= 2.2.2
ragas >= 0.1.2
mlflow >= 2.9.0
langchain >= 0.2.0
```

---

## 🧩 Структура проекта

```
src/benchmark/
├── config/
│   ├── vector_rag.yml          ✅ Создан
│   ├── graph_rag.yml           ✅ Создан
│   └── hybrid_rag.yml          ✅ Создан
├── loaders/
│   ├── dataset_loader.py       ✅ Создан
│   ├── neo4j_ingest.py         ✅ Создан
│   └── chroma_ingest.py         ✅ Создан
├── pipelines/
│   ├── vector_pipeline.py      ✅ Создан
│   ├── graph_pipeline.py       ✅ Создан
│   └── hybrid_pipeline.py     ✅ Создан
├── eval/
│   ├── metrics.py              ✅ Создан
│   └── report_builder.py        ✅ Создан
└── run_benchmark.py            ✅ Создан
```

---

## 🔬 Реализованные компоненты

### 1. Загрузчики данных

**✅ `dataset_loader.py`**
- Загрузка MultiHop-QA датасета
- Загрузка собственного корпуса TERAG
- Генерация QA из корпуса

**✅ `neo4j_ingest.py`**
- Загрузка SPO-триплетов в Neo4j
- Создание индексов для оптимизации
- Загрузка из graph_results

**✅ `chroma_ingest.py`**
- Загрузка документов в ChromaDB
- Генерация эмбеддингов
- Batch обработка

### 2. Пайплайны

**✅ `vector_pipeline.py`**
- Vector-RAG с ChromaDB
- Haystack интеграция
- Retriever + Reader

**✅ `graph_pipeline.py`**
- Graph-RAG с Neo4j
- Cypher запросы
- Извлечение концептов

**✅ `hybrid_pipeline.py`**
- Агентный router (LLM-based)
- Объединение Vector + Graph
- Reciprocal Rank Fusion

### 3. Система оценки

**✅ `metrics.py`**
- RAGAs интеграция
- Метрики: Faithfulness, Context Precision, Context Recall, Answer Relevancy
- Оценка pipeline на датасете

**✅ `report_builder.py`**
- Генерация отчетов JSON
- Сравнительные отчеты
- Анализ результатов

### 4. Главный скрипт

**✅ `run_benchmark.py`**
- CLI интерфейс
- Поддержка всех типов pipeline
- MLflow интеграция
- Автоматическая генерация отчетов

---

## 📊 Метрики RAGAs

### Целевые значения

| Метрика           | Целевое | Минимум |
|-------------------|---------|---------|
| Faithfulness      | ≥ 0.90  | 0.85    |
| Context Precision | ≥ 0.85  | 0.80    |
| Context Recall    | ≥ 0.90  | 0.85    |
| Answer Relevancy  | ≥ 0.95  | 0.90    |

### Использование

```python
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
```

---

## 🚀 Использование

### Запуск benchmark

```bash
# Все pipeline
python src/benchmark/run_benchmark.py --pipeline all

# Только Vector-RAG
python src/benchmark/run_benchmark.py \
  --config src/benchmark/config/vector_rag.yml \
  --pipeline vector

# Только Graph-RAG
python src/benchmark/run_benchmark.py \
  --config src/benchmark/config/graph_rag.yml \
  --pipeline graph

# Только Hybrid-RAG
python src/benchmark/run_benchmark.py \
  --config src/benchmark/config/hybrid_rag.yml \
  --pipeline hybrid
```

### Подготовка данных

```bash
# Загрузка данных в Neo4j
python -c "
from src.benchmark.loaders.neo4j_ingest import Neo4jIngester
ingester = Neo4jIngester()
ingester.ingest_from_graph_results()
"

# Загрузка данных в ChromaDB
python -c "
from src.benchmark.loaders.chroma_ingest import ChromaIngester
ingester = ChromaIngester()
ingester.ingest_from_processed()
"
```

---

## 📈 CI/CD интеграция

**Создан:** `.github/workflows/benchmark.yml`

**Функции:**
- ✅ Автоматический запуск при изменениях в benchmark
- ✅ Запуск каждую неделю (воскресенье)
- ✅ Поддержка Neo4j через Docker
- ✅ Запуск всех трех pipeline
- ✅ Сохранение отчетов в артефактах

---

## 📋 Критерии завершения

| Метрика           | Целевое значение | Минимум |
|-------------------|------------------|---------|
| Faithfulness      | ≥ 0.90           | 0.85    |
| Context Precision | ≥ 0.85           | 0.80    |
| Context Recall    | ≥ 0.90           | 0.85    |
| Answer Relevancy  | ≥ 0.95           | 0.90    |
| Runtime (среднее) | ≤ 5 сек          | —       |

---

## 🧠 Результат

После выполнения benchmark:

1. ✅ Файл `benchmark_report.json` с метриками всех трёх пайплайнов
2. ✅ В MLflow отображается сравнительный график Faithfulness/Recall
3. ✅ Вывод о преимуществе Hybrid GraphRAG
4. ✅ Baseline зафиксирован как вход для следующего этапа

---

## 📁 Созданные файлы

### Конфигурация (3 файла):
- `src/benchmark/config/vector_rag.yml`
- `src/benchmark/config/graph_rag.yml`
- `src/benchmark/config/hybrid_rag.yml`

### Загрузчики (3 файла):
- `src/benchmark/loaders/dataset_loader.py`
- `src/benchmark/loaders/neo4j_ingest.py`
- `src/benchmark/loaders/chroma_ingest.py`

### Пайплайны (3 файла):
- `src/benchmark/pipelines/vector_pipeline.py`
- `src/benchmark/pipelines/graph_pipeline.py`
- `src/benchmark/pipelines/hybrid_pipeline.py`

### Оценка (2 файла):
- `src/benchmark/eval/metrics.py`
- `src/benchmark/eval/report_builder.py`

### Главный скрипт:
- `src/benchmark/run_benchmark.py`

### CI/CD:
- `.github/workflows/benchmark.yml`

---

## 🔗 Следующие шаги

1. **Запустить benchmark** на реальных данных
2. **Проанализировать результаты** и сравнить pipeline
3. **Оптимизировать** пайплайны на основе результатов
4. **Зафиксировать baseline** для TERAG 2.1 / Cognitive Resonance Framework

---

**Статус:** ✅ Структура создана, готово к запуску  
**Последнее обновление:** 2025-01-27









