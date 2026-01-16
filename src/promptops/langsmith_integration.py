"""
LangSmith Integration для TERAG
Глубокая трассировка reasoning на уровне токенов и промежуточных шагов
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from langsmith import Client, traceable, RunEvaluator
    from langsmith.schemas import Run, Example
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    logger.warning("LangSmith not available. Install with: pip install langsmith")


class LangSmithTracer:
    """
    LangSmith Tracer для глубокой трассировки reasoning
    
    Функции:
    1. Логирование шагов reasoning
    2. Трассировка токенов и промежуточных результатов
    3. Синхронизация с MLflow через run_id
    4. Оценка качества reasoning
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        project_name: str = "TERAG_Reasoning",
        enable_tracing: bool = True
    ):
        """
        Инициализация LangSmith Tracer
        
        Args:
            api_key: LangSmith API ключ (из переменных окружения если None)
            project_name: Имя проекта в LangSmith
            enable_tracing: Включить трассировку
        """
        if not LANGSMITH_AVAILABLE:
            logger.warning("LangSmith not available, tracing disabled")
            self.enabled = False
            return
        
        self.enabled = enable_tracing
        self.project_name = project_name
        
        try:
            import os
            api_key = api_key or os.getenv("LANGSMITH_API_KEY")
            if api_key:
                self.client = Client(api_key=api_key)
            else:
                self.client = Client()  # Использует переменные окружения
            logger.info(f"LangSmithTracer initialized: {project_name}")
        except Exception as e:
            logger.warning(f"Could not initialize LangSmith client: {e}")
            self.enabled = False
            self.client = None
    
    def log_step(
        self,
        step_name: str,
        inputs: Dict[str, Any],
        outputs: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        mlflow_run_id: Optional[str] = None,
        parent_run_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Логировать шаг reasoning в LangSmith
        
        Args:
            step_name: Имя шага (planner, solver, verifier, ethical)
            inputs: Входные данные
            outputs: Выходные данные (опционально)
            metadata: Дополнительные метаданные
            mlflow_run_id: ID MLflow run для синхронизации
            parent_run_id: ID родительского run
        
        Returns:
            LangSmith run ID или None
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            # Формируем метаданные
            run_metadata = {
                "step": step_name,
                "timestamp": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            if mlflow_run_id:
                run_metadata["mlflow_run_id"] = mlflow_run_id
            
            # Создаем run
            run = self.client.create_run(
                name=step_name,
                run_type="chain",  # или "llm", "tool" в зависимости от типа
                inputs=inputs,
                outputs=outputs or {},
                metadata=run_metadata,
                project_name=self.project_name,
                parent_run_id=parent_run_id
            )
            
            logger.debug(f"LangSmith step logged: {step_name} (run_id: {run.id})")
            return run.id
        
        except Exception as e:
            logger.error(f"Error logging step to LangSmith: {e}")
            return None
    
    def log_llm_call(
        self,
        prompt: str,
        response: str,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        mlflow_run_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Логировать LLM вызов
        
        Args:
            prompt: Промпт
            response: Ответ
            model: Модель (опционально)
            tokens_used: Количество токенов (опционально)
            duration: Длительность в секундах (опционально)
            metadata: Дополнительные метаданные
            mlflow_run_id: ID MLflow run
        
        Returns:
            LangSmith run ID или None
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            run_metadata = {
                "model": model or "unknown",
                "tokens_used": tokens_used,
                "duration": duration,
                **(metadata or {})
            }
            
            if mlflow_run_id:
                run_metadata["mlflow_run_id"] = mlflow_run_id
            
            run = self.client.create_run(
                name="llm_call",
                run_type="llm",
                inputs={"prompt": prompt},
                outputs={"response": response},
                metadata=run_metadata,
                project_name=self.project_name
            )
            
            logger.debug(f"LangSmith LLM call logged (run_id: {run.id})")
            return run.id
        
        except Exception as e:
            logger.error(f"Error logging LLM call to LangSmith: {e}")
            return None
    
    def sync_with_mlflow(
        self,
        langsmith_run_id: str,
        mlflow_run_id: str
    ):
        """
        Синхронизировать LangSmith run с MLflow run
        
        Args:
            langsmith_run_id: ID LangSmith run
            mlflow_run_id: ID MLflow run
        """
        if not self.enabled or not self.client:
            return
        
        try:
            # Обновляем метаданные LangSmith run
            self.client.update_run(
                run_id=langsmith_run_id,
                metadata={"mlflow_run_id": mlflow_run_id}
            )
            
            logger.debug(f"Synced LangSmith run {langsmith_run_id} with MLflow {mlflow_run_id}")
        
        except Exception as e:
            logger.error(f"Error syncing with MLflow: {e}")









