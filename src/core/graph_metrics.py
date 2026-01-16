"""
Prometheus метрики для Graph Updater
Экспорт метрик роста графа знаний для мониторинга в Grafana
"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Проверяем наличие prometheus_client
try:
    from prometheus_client import Counter, Gauge, Histogram, start_http_server, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("prometheus_client not available. Metrics will be disabled.")

# Глобальные переменные для метрик
if PROMETHEUS_AVAILABLE:
    facts_added_total = None
    facts_failed_total = None
    signals_added_total = None
    graph_nodes_total = None
    graph_relations_total = None
    graph_entities_total = None
    graph_signals_total = None
    graph_domains_total = None
    fact_insertion_duration = None
    signal_insertion_duration = None
    _metrics_initialized = False
    
    def _init_metrics():
        """Инициализировать метрики (только один раз, избегаем дублирования)"""
        global _metrics_initialized, facts_added_total, facts_failed_total, signals_added_total
        global graph_nodes_total, graph_relations_total, graph_entities_total
        global graph_signals_total, graph_domains_total
        global fact_insertion_duration, signal_insertion_duration
        
        if _metrics_initialized:
            return
        
        try:
            # Метрики для фактов
            facts_added_total = Counter(
                'terag_graph_facts_added_total',
                'Total number of facts added to the graph',
                ['relation_type']
            )
            
            facts_failed_total = Counter(
                'terag_graph_facts_failed_total',
                'Total number of failed fact insertions',
                ['error_type']
            )
            
            # Метрики для сигналов
            signals_added_total = Counter(
                'terag_graph_signals_added_total',
                'Total number of signals added to the graph',
                ['domain']
            )
            
            # Метрики состояния графа
            graph_nodes_total = Gauge(
                'terag_graph_nodes_total',
                'Total number of nodes in the graph',
                ['node_type']
            )
            
            graph_relations_total = Gauge(
                'terag_graph_relations_total',
                'Total number of relations in the graph'
            )
            
            graph_entities_total = Gauge(
                'terag_graph_entities_total',
                'Total number of Entity nodes in the graph'
            )
            
            graph_signals_total = Gauge(
                'terag_graph_signals_total',
                'Total number of Signal nodes in the graph'
            )
            
            graph_domains_total = Gauge(
                'terag_graph_domains_total',
                'Total number of Domain nodes in the graph'
            )
            
            # Метрики производительности
            fact_insertion_duration = Histogram(
                'terag_graph_fact_insertion_duration_seconds',
                'Time spent inserting a fact into the graph',
                buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
            )
            
            signal_insertion_duration = Histogram(
                'terag_graph_signal_insertion_duration_seconds',
                'Time spent inserting a signal into the graph',
                buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
            )
            
            _metrics_initialized = True
            logger.debug("Graph metrics initialized")
        
        except ValueError as e:
            # Метрики уже существуют (дублирование при повторном импорте)
            logger.warning(f"Metrics already exist, reusing existing: {e}")
            _metrics_initialized = True
    
    # Инициализируем метрики при импорте
    _init_metrics()


class GraphMetrics:
    """Класс для управления метриками графа"""
    
    def __init__(self, enable_prometheus: bool = True):
        self.enabled = enable_prometheus and PROMETHEUS_AVAILABLE
        self.metrics_port = int(os.getenv("PROMETHEUS_METRICS_PORT", "8000"))
        self.server_started = False
        
        if self.enabled:
            logger.info(f"Graph metrics enabled (Prometheus port: {self.metrics_port})")
        else:
            logger.warning("Graph metrics disabled (prometheus_client not available)")
    
    def start_metrics_server(self):
        """Запустить HTTP сервер для экспорта метрик"""
        if not self.enabled or self.server_started:
            return
        
        try:
            start_http_server(self.metrics_port)
            self.server_started = True
            logger.info(f"Prometheus metrics server started on port {self.metrics_port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
    
    def record_fact_added(self, relation_type: str = "unknown"):
        """Записать добавление факта"""
        if self.enabled and facts_added_total is not None:
            try:
                facts_added_total.labels(relation_type=relation_type).inc()
            except Exception as e:
                logger.debug(f"Could not record fact added metric: {e}")
    
    def record_fact_failed(self, error_type: str = "unknown"):
        """Записать ошибку добавления факта"""
        if self.enabled and facts_failed_total is not None:
            try:
                facts_failed_total.labels(error_type=error_type).inc()
            except Exception as e:
                logger.debug(f"Could not record fact failed metric: {e}")
    
    def record_signal_added(self, domain: str = "unknown"):
        """Записать добавление сигнала"""
        if self.enabled and signals_added_total is not None:
            try:
                signals_added_total.labels(domain=domain).inc()
            except Exception as e:
                logger.debug(f"Could not record signal added metric: {e}")
    
    def update_graph_stats(self, stats: Dict[str, Any]):
        """Обновить метрики состояния графа"""
        if not self.enabled:
            return
        
        try:
            # Обновляем gauges
            if graph_relations_total is not None:
                graph_relations_total.set(stats.get("relations", 0))
            if graph_entities_total is not None:
                graph_entities_total.set(stats.get("entities", 0))
            if graph_signals_total is not None:
                graph_signals_total.set(stats.get("signals", 0))
            if graph_domains_total is not None:
                graph_domains_total.set(stats.get("domains", 0))
            
            # Обновляем узлы по типам
            if graph_nodes_total is not None:
                graph_nodes_total.labels(node_type="Entity").set(stats.get("entities", 0))
                graph_nodes_total.labels(node_type="Signal").set(stats.get("signals", 0))
                graph_nodes_total.labels(node_type="Domain").set(stats.get("domains", 0))
                graph_nodes_total.labels(node_type="total").set(stats.get("nodes", 0))
        except Exception as e:
            logger.debug(f"Could not update graph stats metrics: {e}")
    
    def record_fact_insertion_time(self, duration: float):
        """Записать время вставки факта"""
        if self.enabled and fact_insertion_duration is not None:
            try:
                fact_insertion_duration.observe(duration)
            except Exception as e:
                logger.debug(f"Could not record fact insertion time metric: {e}")
    
    def record_signal_insertion_time(self, duration: float):
        """Записать время вставки сигнала"""
        if self.enabled and signal_insertion_duration is not None:
            try:
                signal_insertion_duration.observe(duration)
            except Exception as e:
                logger.debug(f"Could not record signal insertion time metric: {e}")


# Глобальный экземпляр метрик
_metrics_instance: Optional[GraphMetrics] = None


def get_metrics() -> GraphMetrics:
    """Получить глобальный экземпляр метрик"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = GraphMetrics()
    return _metrics_instance


def start_metrics_server():
    """Запустить сервер метрик (вызывается при старте приложения)"""
    metrics = get_metrics()
    metrics.start_metrics_server()
