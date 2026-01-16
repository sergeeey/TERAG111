"""
LangSmith Adapter для визуализации ReasonGraph
Связывает LangSmith traces с узлами ReasonGraph
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import langsmith
    from langsmith import Client
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    logger.warning("LangSmith not available")


class LangSmithAdapter:
    """
    Адаптер для получения данных из LangSmith и связывания их с ReasonGraph
    
    Функции:
    1. Получение traces для конкретного run_id
    2. Связывание traces с узлами ReasonGraph
    3. Извлечение метрик (tokens, latency)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация адаптера
        
        Args:
            api_key: LangSmith API ключ (опционально, берется из env)
        """
        if not LANGSMITH_AVAILABLE:
            logger.warning("LangSmith not available, adapter will be disabled")
            self.client = None
            return
        
        try:
            self.client = Client(api_key=api_key) if api_key else Client()
            logger.info("LangSmithAdapter initialized")
        except Exception as e:
            logger.error(f"Failed to initialize LangSmith client: {e}")
            self.client = None
    
    def get_run_traces(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить traces для конкретного run
        
        Args:
            run_id: ID LangSmith run
        
        Returns:
            Словарь с traces или None
        """
        if not self.client:
            return None
        
        try:
            run = self.client.read_run(run_id)
            
            # Получаем все child runs
            child_runs = self.client.list_runs(
                project_name=run.project_name if hasattr(run, 'project_name') else None,
                filter=f'parent_run_id == "{run_id}"'
            )
            
            traces = []
            for child_run in child_runs:
                trace = {
                    "run_id": str(child_run.id),
                    "name": child_run.name,
                    "run_type": child_run.run_type,
                    "start_time": child_run.start_time.isoformat() if child_run.start_time else None,
                    "end_time": child_run.end_time.isoformat() if child_run.end_time else None,
                    "duration": (child_run.end_time - child_run.start_time).total_seconds() if child_run.end_time and child_run.start_time else None,
                    "inputs": child_run.inputs if hasattr(child_run, 'inputs') else {},
                    "outputs": child_run.outputs if hasattr(child_run, 'outputs') else {},
                    "extra": child_run.extra if hasattr(child_run, 'extra') else {}
                }
                
                # Извлекаем метрики токенов
                if hasattr(child_run, 'extra') and child_run.extra:
                    trace["tokens_used"] = child_run.extra.get("tokens_used", 0)
                    trace["latency_ms"] = child_run.extra.get("latency_ms", 0)
                
                traces.append(trace)
            
            return {
                "run_id": run_id,
                "traces": traces,
                "total_traces": len(traces)
            }
        except Exception as e:
            logger.error(f"Error getting LangSmith traces: {e}")
            return None
    
    def enrich_reason_graph(self, reason_graph: Dict[str, Any], langsmith_run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Обогатить ReasonGraph данными из LangSmith
        
        Args:
            reason_graph: ReasonGraph JSON
            langsmith_run_id: ID LangSmith run (опционально)
        
        Returns:
            Обогащенный ReasonGraph
        """
        if not langsmith_run_id or not self.client:
            return reason_graph
        
        traces_data = self.get_run_traces(langsmith_run_id)
        if not traces_data:
            return reason_graph
        
        # Связываем traces с узлами
        nodes = reason_graph.get("nodes", [])
        traces = traces_data.get("traces", [])
        
        # Создаем маппинг по имени узла
        trace_map = {trace["name"]: trace for trace in traces}
        
        # Обогащаем узлы данными из traces
        for node in nodes:
            node_type = node.get("type")
            trace = trace_map.get(node_type)
            
            if trace:
                # Добавляем метрики из LangSmith
                if "data" not in node:
                    node["data"] = {}
                
                node["data"]["langsmith"] = {
                    "run_id": trace.get("run_id"),
                    "duration": trace.get("duration"),
                    "tokens_used": trace.get("tokens_used", 0),
                    "latency_ms": trace.get("latency_ms", 0)
                }
        
        # Обновляем метаданные
        if "metadata" not in reason_graph:
            reason_graph["metadata"] = {}
        
        reason_graph["metadata"]["langsmith_run_id"] = langsmith_run_id
        reason_graph["metadata"]["total_traces"] = traces_data.get("total_traces", 0)
        
        return reason_graph
    
    def get_timeline_metrics(self, langsmith_run_id: str) -> List[Dict[str, Any]]:
        """
        Получить временную линию метрик из LangSmith
        
        Args:
            langsmith_run_id: ID LangSmith run
        
        Returns:
            Список метрик по времени
        """
        if not self.client:
            return []
        
        traces_data = self.get_run_traces(langsmith_run_id)
        if not traces_data:
            return []
        
        timeline = []
        for trace in traces_data.get("traces", []):
            timeline.append({
                "step": trace.get("name", "unknown"),
                "timestamp": trace.get("start_time"),
                "duration": trace.get("duration", 0),
                "tokens_used": trace.get("tokens_used", 0),
                "latency_ms": trace.get("latency_ms", 0)
            })
        
        return timeline








