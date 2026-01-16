"""
MLflow Adapter для визуализации ReasonGraph
Связывает MLflow метрики с ReasonGraph
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not available")


class MLflowAdapter:
    """
    Адаптер для получения данных из MLflow и связывания их с ReasonGraph
    
    Функции:
    1. Получение метрик для конкретного run_id
    2. Получение параметров run
    3. Сохранение ReasonGraph как артефакт
    """
    
    def __init__(self, tracking_uri: Optional[str] = None):
        """
        Инициализация адаптера
        
        Args:
            tracking_uri: MLflow tracking URI (опционально)
        """
        if not MLFLOW_AVAILABLE:
            logger.warning("MLflow not available, adapter will be disabled")
            self.client = None
            return
        
        try:
            if tracking_uri:
                mlflow.set_tracking_uri(tracking_uri)
            self.client = mlflow.tracking.MlflowClient()
            logger.info("MLflowAdapter initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MLflow client: {e}")
            self.client = None
    
    def get_run_metrics(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить метрики для конкретного run
        
        Args:
            run_id: ID MLflow run
        
        Returns:
            Словарь с метриками или None
        """
        if not self.client:
            return None
        
        try:
            run = self.client.get_run(run_id)
            
            metrics = {}
            for key, value in run.data.metrics.items():
                metrics[key] = value
            
            return {
                "run_id": run_id,
                "metrics": metrics,
                "params": run.data.params,
                "tags": run.data.tags,
                "status": run.info.status,
                "start_time": datetime.fromtimestamp(run.info.start_time / 1000).isoformat() if run.info.start_time else None,
                "end_time": datetime.fromtimestamp(run.info.end_time / 1000).isoformat() if run.info.end_time else None
            }
        except Exception as e:
            logger.error(f"Error getting MLflow metrics: {e}")
            return None
    
    def enrich_reason_graph(self, reason_graph: Dict[str, Any], mlflow_run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Обогатить ReasonGraph данными из MLflow
        
        Args:
            reason_graph: ReasonGraph JSON
            mlflow_run_id: ID MLflow run (опционально)
        
        Returns:
            Обогащенный ReasonGraph
        """
        if not mlflow_run_id or not self.client:
            return reason_graph
        
        run_data = self.get_run_metrics(mlflow_run_id)
        if not run_data:
            return reason_graph
        
        # Обновляем метаданные
        if "metadata" not in reason_graph:
            reason_graph["metadata"] = {}
        
        reason_graph["metadata"]["mlflow_run_id"] = mlflow_run_id
        reason_graph["metadata"]["mlflow_metrics"] = run_data.get("metrics", {})
        reason_graph["metadata"]["mlflow_status"] = run_data.get("status")
        
        # Обновляем метрики из MLflow
        mlflow_metrics = run_data.get("metrics", {})
        if "confidence" in mlflow_metrics:
            reason_graph["metadata"]["confidence"] = mlflow_metrics["confidence"]
        if "ethical_score" in mlflow_metrics:
            reason_graph["metadata"]["ethical_score"] = mlflow_metrics["ethical_score"]
        if "secure_reasoning_index" in mlflow_metrics:
            reason_graph["metadata"]["secure_reasoning_index"] = mlflow_metrics["secure_reasoning_index"]
        
        return reason_graph
    
    def save_reason_graph(self, reason_graph: Dict[str, Any], mlflow_run_id: Optional[str] = None) -> bool:
        """
        Сохранить ReasonGraph как артефакт в MLflow
        
        Args:
            reason_graph: ReasonGraph JSON
            mlflow_run_id: ID MLflow run (опционально, используется активный run)
        
        Returns:
            True если успешно сохранено
        """
        if not MLFLOW_AVAILABLE:
            return False
        
        try:
            import json
            import tempfile
            import os
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(reason_graph, f, indent=2, ensure_ascii=False)
                temp_path = f.name
            
            try:
                # Логируем как артефакт
                if mlflow_run_id:
                    # Используем активный run
                    mlflow.log_artifact(temp_path, "reason_graph")
                else:
                    # Используем текущий активный run
                    mlflow.log_artifact(temp_path, "reason_graph")
                
                logger.info(f"ReasonGraph saved to MLflow as artifact")
                return True
            finally:
                # Удаляем временный файл
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        except Exception as e:
            logger.error(f"Error saving ReasonGraph to MLflow: {e}")
            return False
    
    def get_timeline_metrics(self, mlflow_run_id: str) -> List[Dict[str, Any]]:
        """
        Получить временную линию метрик из MLflow
        
        Args:
            mlflow_run_id: ID MLflow run
        
        Returns:
            Список метрик по времени
        """
        if not self.client:
            return []
        
        run_data = self.get_run_metrics(mlflow_run_id)
        if not run_data:
            return []
        
        # MLflow хранит метрики как ключ-значение, не как временную линию
        # Возвращаем метрики в формате timeline
        timeline = []
        metrics = run_data.get("metrics", {})
        
        for key, value in metrics.items():
            timeline.append({
                "metric": key,
                "value": value,
                "timestamp": run_data.get("start_time")
            })
        
        return timeline








