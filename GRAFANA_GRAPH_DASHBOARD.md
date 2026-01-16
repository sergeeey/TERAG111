# 📊 Grafana Dashboard для Graph Updater

## 🎯 Настройка дашборда для мониторинга графа знаний

### 1. Установка Prometheus

Убедитесь, что Prometheus настроен и собирает метрики с TERAG:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'terag-graph'
    static_configs:
      - targets: ['localhost:8000']  # Порт метрик Graph Updater
    scrape_interval: 15s
```

### 2. Запуск метрик

В вашем приложении TERAG:

```python
from src.core.graph_metrics import start_metrics_server

# Запустить сервер метрик
start_metrics_server()
```

Метрики будут доступны по адресу: `http://localhost:8000/metrics`

### 3. Создание Grafana Dashboard

#### Панель 1: Рост графа

**Запрос:**
```promql
terag_graph_nodes_total{node_type="total"}
```

**Визуализация:** Graph (линия)
**Название:** Total Nodes in Graph

---

#### Панель 2: Количество связей

**Запрос:**
```promql
terag_graph_relations_total
```

**Визуализация:** Stat
**Название:** Total Relations

---

#### Панель 3: Распределение узлов по типам

**Запросы:**
```promql
terag_graph_entities_total
terag_graph_signals_total
terag_graph_domains_total
```

**Визуализация:** Pie Chart
**Название:** Nodes by Type

---

#### Панель 4: Скорость добавления фактов

**Запрос:**
```promql
rate(terag_graph_facts_added_total[5m])
```

**Визуализация:** Graph (линия)
**Название:** Facts Added per Second

---

#### Панель 5: Скорость добавления сигналов

**Запрос:**
```promql
rate(terag_graph_signals_added_total[5m])
```

**Визуализация:** Graph (линия)
**Название:** Signals Added per Second

---

#### Панель 6: Ошибки добавления

**Запрос:**
```promql
rate(terag_graph_facts_failed_total[5m])
```

**Визуализация:** Graph (линия, красный цвет)
**Название:** Failed Fact Insertions

---

#### Панель 7: Время вставки фактов (p95)

**Запрос:**
```promql
histogram_quantile(0.95, rate(terag_graph_fact_insertion_duration_seconds_bucket[5m]))
```

**Визуализация:** Graph (линия)
**Название:** Fact Insertion Duration (p95)

---

#### Панель 8: Топ доменов по сигналам

**Запрос:**
```promql
topk(5, sum by (domain) (terag_graph_signals_added_total))
```

**Визуализация:** Bar Chart
**Название:** Top Domains by Signals

---

#### Панель 9: Топ типов связей

**Запрос:**
```promql
topk(5, sum by (relation_type) (terag_graph_facts_added_total))
```

**Визуализация:** Bar Chart
**Название:** Top Relation Types

---

### 4. JSON конфигурация дашборда

Создайте файл `grafana-graph-dashboard.json` и импортируйте его в Grafana:

```json
{
  "dashboard": {
    "title": "TERAG Graph Knowledge Base",
    "panels": [
      {
        "title": "Total Nodes",
        "targets": [{
          "expr": "terag_graph_nodes_total{node_type=\"total\"}"
        }]
      }
      // ... остальные панели
    ]
  }
}
```

### 5. Алерты

Настройте алерты для критичных метрик:

**Алерт 1: Высокий процент ошибок**
```promql
rate(terag_graph_facts_failed_total[5m]) / rate(terag_graph_facts_added_total[5m]) > 0.1
```

**Алерт 2: Медленная вставка**
```promql
histogram_quantile(0.95, rate(terag_graph_fact_insertion_duration_seconds_bucket[5m])) > 1.0
```

**Алерт 3: Граф не растёт**
```promql
rate(terag_graph_facts_added_total[1h]) == 0
```

---

## 📈 Примеры запросов для анализа

### Средняя скорость роста графа за час

```promql
rate(terag_graph_nodes_total{node_type="total"}[1h])
```

### Процент успешных вставок

```promql
rate(terag_graph_facts_added_total[5m]) / (rate(terag_graph_facts_added_total[5m]) + rate(terag_graph_facts_failed_total[5m])) * 100
```

### Распределение времени вставки

```promql
histogram_quantile(0.50, rate(terag_graph_fact_insertion_duration_seconds_bucket[5m]))  # p50
histogram_quantile(0.95, rate(terag_graph_fact_insertion_duration_seconds_bucket[5m]))  # p95
histogram_quantile(0.99, rate(terag_graph_fact_insertion_duration_seconds_bucket[5m]))  # p99
```

---

## 🚀 Быстрый старт

1. Установите `prometheus-client`:
   ```bash
   pip install prometheus-client
   ```

2. Запустите метрики в вашем приложении:
   ```python
   from src.core.graph_metrics import start_metrics_server
   start_metrics_server()
   ```

3. Настройте Prometheus для сбора метрик с `localhost:8000`

4. Импортируйте дашборд в Grafana

5. Наслаждайтесь визуализацией роста графа знаний! 🎯













