"""
Structured Logging для TERAG
Поддержка trace_id и correlation_id во всех логах
"""
import logging
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class TERAGJSONFormatter(logging.Formatter):
    """
    JSON Formatter для структурированного логирования
    
    Формат:
    {
        "timestamp": "2025-01-27T10:00:00Z",
        "level": "INFO",
        "logger": "src.core.agents",
        "message": "Serializing TERAGState",
        "trace_id": "abc123",
        "correlation_id": "def456",
        "extra": {...}
    }
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Форматировать запись в JSON"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Добавляем trace_id если есть
        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id
        
        # Добавляем correlation_id если есть
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
        
        # Добавляем дополнительные поля
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data
        
        # Добавляем exception info если есть
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


def get_logger(name: str, trace_id: Optional[str] = None) -> logging.Logger:
    """
    Получить logger с поддержкой trace_id
    
    Args:
        name: Имя logger (обычно __name__)
        trace_id: ID трассировки (опционально)
    
    Returns:
        Настроенный logger
    """
    logger = logging.getLogger(name)
    
    # Добавляем trace_id в logger если указан
    if trace_id:
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.trace_id = trace_id
            return record
        
        logging.setLogRecordFactory(record_factory)
    
    return logger


def generate_trace_id() -> str:
    """Генерировать новый trace_id"""
    return str(uuid.uuid4())


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    trace_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
):
    """
    Логировать с контекстом (trace_id, correlation_id, extra)
    
    Args:
        logger: Logger instance
        level: Уровень логирования (logging.INFO, etc.)
        message: Сообщение
        trace_id: ID трассировки
        correlation_id: ID корреляции
        extra: Дополнительные данные
    """
    # Создаем extra словарь с безопасными именами полей
    extra_dict = {}
    if trace_id:
        extra_dict['terag_trace_id'] = trace_id
    if correlation_id:
        extra_dict['terag_correlation_id'] = correlation_id
    if extra:
        extra_dict['terag_extra_data'] = extra
    
    # Используем filter для добавления полей в record
    class ContextFilter(logging.Filter):
        def __init__(self, trace_id=None, correlation_id=None, extra_data=None):
            super().__init__()
            self.trace_id = trace_id
            self.correlation_id = correlation_id
            self.extra_data = extra_data
        
        def filter(self, record):
            if self.trace_id:
                record.trace_id = self.trace_id
            if self.correlation_id:
                record.correlation_id = self.correlation_id
            if self.extra_data:
                record.extra_data = self.extra_data
            return True
    
    # Добавляем filter временно
    context_filter = ContextFilter(trace_id, correlation_id, extra)
    logger.addFilter(context_filter)
    
    try:
        logger.log(level, message)
    finally:
        # Удаляем filter после использования
        logger.removeFilter(context_filter)


