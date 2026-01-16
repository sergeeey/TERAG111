"""
TERAG Custom Exceptions
Структурированные исключения для обработки ошибок в TERAG системе
"""
from typing import Optional, Dict, Any


class TERAGError(Exception):
    """
    Базовый класс для всех TERAG исключений
    
    Attributes:
        message: Сообщение об ошибке
        code: Код ошибки для клиентов
        details: Дополнительные детали
        trace_id: ID трассировки для логирования
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        self.trace_id = trace_id
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать исключение в словарь для API ответов"""
        return {
            "error": True,
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "trace_id": self.trace_id
        }


class StreamError(TERAGError):
    """Ошибка при работе с SSE потоком"""
    pass


class GraphError(TERAGError):
    """Ошибка при работе с графом (Neo4j, LangGraph)"""
    pass


class ValidationError(TERAGError):
    """Ошибка валидации входных данных"""
    pass


class ConfidenceError(TERAGError):
    """Ошибка связанная с низким confidence"""
    
    def __init__(
        self,
        confidence: float,
        threshold: float = 0.6,
        trace_id: Optional[str] = None
    ):
        message = f"Low confidence detected: {confidence:.2f} < {threshold:.2f}"
        details = {
            "confidence": confidence,
            "threshold": threshold,
            "status": "quarantine"
        }
        super().__init__(message, code="CONFIDENCE_ERROR", details=details, trace_id=trace_id)
        # Сохраняем атрибуты для доступа
        self.confidence = confidence
        self.threshold = threshold


class SerializationError(TERAGError):
    """Ошибка при сериализации данных"""
    pass


class IntegrationError(TERAGError):
    """Ошибка интеграции с внешними системами (MLflow, LangSmith)"""
    pass

