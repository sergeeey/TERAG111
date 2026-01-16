# 🧠 TERAG 2.1 Benchmark & Validation

**Кодовое имя:** *Baseline Proof Cycle*  
**Версия:** 2.1.0  
**Дата:** 2025-01-27

---

## 🎯 Цель

Сравнить три подхода к RAG:
- **Vector-RAG** (ChromaDB)
- **Graph-RAG** (Neo4j)
- **Hybrid GraphRAG** (комбинация)

По метрикам:
- Faithfulness
- Context Precision
- Context Recall
- Answer Relevancy

---

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Подготовка данных

```bash
# Загрузка в Neo4j
python -c "
from src.benchmark.loaders.neo4j_ingest import Neo4jIngester
ingester = Neo4jIngester()
ingester.ingest_from_graph_results()
"

# Загрузка в ChromaDB
python -c "
from src.benchmark.loaders.chroma_ingest import ChromaIngester
ingester = ChromaIngester()
ingester.ingest_from_processed()
"
```

### 3. Запуск benchmark

```bash
# Все pipeline
python src/benchmark/run_benchmark.py --pipeline all

# Конкретный pipeline
python src/benchmark/run_benchmark.py \
  --config src/benchmark/config/hybrid_rag.yml \
  --pipeline hybrid
```

---

## 📊 Результаты

Отчеты сохраняются в `reports/`:
- `benchmark_vector_rag_*.json`
- `benchmark_graph_rag_*.json`
- `benchmark_hybrid_rag_*.json`
- `benchmark_comparison.json`

---

## 📈 Метрики

Целевые значения:
- **Faithfulness**: ≥ 0.90
- **Context Precision**: ≥ 0.85
- **Context Recall**: ≥ 0.90
- **Answer Relevancy**: ≥ 0.95

---

## 🔗 Документация

- [Полная документация](../../docs/TERAG_2.1_BENCHMARK.md)
- [Комплексный аудит](../../docs/COMPREHENSIVE_AUDIT_REPORT.md)









