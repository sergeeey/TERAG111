"""
MLflow интеграция для TERAG LangGraph
Логирование reasoning traces и метрик
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not available")


class MLflowTracer:
    """
    MLflow Tracer для логирования reasoning traces
    """
    
    def __init__(self, experiment_name: str = "TERAG_Reasoning"):
        """
        Инициализация MLflow Tracer
        
        Args:
            experiment_name: Имя эксперимента
        """
        if not MLFLOW_AVAILABLE:
            logger.warning("MLflow not available, tracing disabled")
            self.enabled = False
            return
        
        self.enabled = True
        mlflow.set_experiment(experiment_name)
        logger.info(f"MLflowTracer initialized: {experiment_name}")
    
    def start_run(self, run_name: Optional[str] = None):
        """Начать MLflow run"""
        if not self.enabled:
            return None
        
        return mlflow.start_run(run_name=run_name)
    
    def end_run(self):
        """Завершить MLflow run"""
        if not self.enabled:
            return
        
        mlflow.end_run()
    
    def log_reasoning_step(
        self,
        step_name: str,
        step_data: Dict[str, Any],
        timestamp: Optional[str] = None
    ):
        """
        Логировать шаг reasoning
        
        Args:
            step_name: Имя шага
            step_data: Данные шага
            timestamp: Временная метка
        """
        if not self.enabled:
            return
        
        timestamp = timestamp or datetime.utcnow().isoformat()
        
        # Логируем как параметры
        mlflow.log_param(f"step_{step_name}_timestamp", timestamp)
        
        # Логируем метрики если есть
        if "confidence" in step_data:
            mlflow.log_metric(f"step_{step_name}_confidence", step_data["confidence"])
        
        # Логируем артефакт (JSON)
        import json
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(step_data, f, indent=2, ensure_ascii=False)
            mlflow.log_artifact(f.name, artifact_path=f"reasoning_steps/{step_name}")
            os.unlink(f.name)
    
    def log_reason_graph(self, reason_graph: Dict[str, Any]):
        """
        Логировать ReasonGraph как артефакт
        
        Args:
            reason_graph: ReasonGraph JSON
        """
        if not self.enabled:
            return
        
        import json
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(reason_graph, f, indent=2, ensure_ascii=False)
            mlflow.log_artifact(f.name, artifact_path="reason_graph")
            os.unlink(f.name)
    
    def log_metrics(self, metrics: Dict[str, float]):
        """
        Логировать метрики
        
        Args:
            metrics: Словарь метрик
        """
        if not self.enabled:
            return
        
        for metric_name, value in metrics.items():
            mlflow.log_metric(metric_name, value)
    
    def log_params(self, params: Dict[str, Any]):
        """
        Логировать параметры
        
        Args:
            params: Словарь параметров
        """
        if not self.enabled:
            return
        
        for param_name, value in params.items():
            mlflow.log_param(param_name, str(value))









