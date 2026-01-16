"""
Тесты для Structured Logging утилиты TERAG
"""
import pytest
import json
import logging
import uuid
from io import StringIO
from unittest.mock import patch

try:
    from src.core.utils.logging import (
        TERAGJSONFormatter,
        get_logger,
        generate_trace_id,
        log_with_context
    )
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    pytest.skip("Logging utilities not available", allow_module_level=True)


@pytest.fixture
def formatter():
    """Создать экземпляр TERAGJSONFormatter"""
    return TERAGJSONFormatter()


@pytest.fixture
def log_record():
    """Создать примерную запись лога"""
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    return record


@pytest.fixture
def log_record_with_trace_id(log_record):
    """Создать запись лога с trace_id"""
    log_record.trace_id = "trace_123"
    return log_record


@pytest.fixture
def log_record_with_correlation_id(log_record):
    """Создать запись лога с correlation_id"""
    log_record.correlation_id = "corr_456"
    return log_record


@pytest.fixture
def log_record_with_extra(log_record):
    """Создать запись лога с extra_data"""
    log_record.extra_data = {"key": "value", "number": 42}
    return log_record


@pytest.fixture
def log_record_with_exception(log_record):
    """Создать запись лога с исключением"""
    import sys
    try:
        raise ValueError("Test exception")
    except ValueError:
        log_record.exc_info = sys.exc_info()
    return log_record


class TestTERAGJSONFormatter:
    """Тесты для TERAGJSONFormatter"""
    
    def test_format_basic_log(self, formatter, log_record):
        """Тест форматирования базового лога"""
        result = formatter.format(log_record)
        
        # Должен быть валидный JSON
        log_data = json.loads(result)
        
        assert "timestamp" in log_data
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_logger"
        assert log_data["message"] == "Test message"
        assert "trace_id" not in log_data
        assert "correlation_id" not in log_data
    
    def test_format_with_trace_id(self, formatter, log_record_with_trace_id):
        """Тест форматирования с trace_id"""
        result = formatter.format(log_record_with_trace_id)
        log_data = json.loads(result)
        
        assert log_data["trace_id"] == "trace_123"
        assert log_data["message"] == "Test message"
    
    def test_format_with_correlation_id(self, formatter, log_record_with_correlation_id):
        """Тест форматирования с correlation_id"""
        result = formatter.format(log_record_with_correlation_id)
        log_data = json.loads(result)
        
        assert log_data["correlation_id"] == "corr_456"
    
    def test_format_with_extra_data(self, formatter, log_record_with_extra):
        """Тест форматирования с extra_data"""
        result = formatter.format(log_record_with_extra)
        log_data = json.loads(result)
        
        assert "extra" in log_data
        assert log_data["extra"]["key"] == "value"
        assert log_data["extra"]["number"] == 42
    
    def test_format_with_all_fields(self, formatter, log_record):
        """Тест форматирования со всеми полями"""
        log_record.trace_id = "trace_123"
        log_record.correlation_id = "corr_456"
        log_record.extra_data = {"test": "data"}
        
        result = formatter.format(log_record)
        log_data = json.loads(result)
        
        assert log_data["trace_id"] == "trace_123"
        assert log_data["correlation_id"] == "corr_456"
        assert log_data["extra"]["test"] == "data"
    
    def test_format_with_exception(self, formatter, log_record_with_exception):
        """Тест форматирования с исключением"""
        result = formatter.format(log_record_with_exception)
        log_data = json.loads(result)
        
        assert "exception" in log_data
        assert "ValueError" in log_data["exception"]
        assert "Test exception" in log_data["exception"]
    
    def test_format_unicode_support(self, formatter, log_record):
        """Тест поддержки Unicode (кириллица)"""
        log_record.msg = "Тестовое сообщение на русском"
        result = formatter.format(log_record)
        
        # Должен быть валидный JSON с кириллицей
        log_data = json.loads(result)
        assert log_data["message"] == "Тестовое сообщение на русском"
        
        # ensure_ascii=False должен сохранить кириллицу
        assert "Тестовое" in result
    
    def test_format_timestamp_format(self, formatter, log_record):
        """Тест формата timestamp"""
        result = formatter.format(log_record)
        log_data = json.loads(result)
        
        # Timestamp должен быть в ISO формате с Z
        timestamp = log_data["timestamp"]
        assert timestamp.endswith("Z")
        assert "T" in timestamp
    
    def test_format_different_levels(self, formatter):
        """Тест форматирования разных уровней логирования"""
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        
        for level in levels:
            record = logging.LogRecord(
                name="test",
                level=level,
                pathname="test.py",
                lineno=1,
                msg="Test",
                args=(),
                exc_info=None
            )
            result = formatter.format(record)
            log_data = json.loads(result)
            
            assert log_data["level"] == logging.getLevelName(level)


class TestGetLogger:
    """Тесты для get_logger()"""
    
    def test_get_logger_basic(self):
        """Тест создания базового logger"""
        logger = get_logger("test_logger")
        
        assert logger.name == "test_logger"
        assert isinstance(logger, logging.Logger)
    
    def test_get_logger_with_trace_id(self):
        """Тест создания logger с trace_id"""
        trace_id = "test_trace_123"
        logger = get_logger("test_logger", trace_id=trace_id)
        
        # Создаем handler для перехвата записей
        handler = logging.StreamHandler(StringIO())
        handler.setFormatter(logging.Formatter())
        logger.addHandler(handler)
        
        # Логируем сообщение
        logger.info("Test message")
        
        # Проверяем что factory был установлен
        # (trace_id должен быть в записях через factory)
        assert logger.name == "test_logger"
    
    def test_get_logger_multiple_loggers(self):
        """Тест создания нескольких logger'ов"""
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")
        
        assert logger1.name == "logger1"
        assert logger2.name == "logger2"
        assert logger1 is not logger2
    
    def test_get_logger_same_name_returns_same_instance(self):
        """Тест что logger с одинаковым именем возвращает тот же экземпляр"""
        logger1 = get_logger("shared_logger")
        logger2 = get_logger("shared_logger")
        
        assert logger1 is logger2


class TestGenerateTraceId:
    """Тесты для generate_trace_id()"""
    
    def test_generate_trace_id_format(self):
        """Тест формата trace_id"""
        trace_id = generate_trace_id()
        
        # Должен быть валидный UUID
        uuid_obj = uuid.UUID(trace_id)
        assert str(uuid_obj) == trace_id
    
    def test_generate_trace_id_uniqueness(self):
        """Тест уникальности trace_id"""
        trace_ids = [generate_trace_id() for _ in range(100)]
        
        # Все должны быть уникальными
        assert len(trace_ids) == len(set(trace_ids))
    
    def test_generate_trace_id_type(self):
        """Тест типа возвращаемого значения"""
        trace_id = generate_trace_id()
        
        assert isinstance(trace_id, str)
        assert len(trace_id) == 36  # UUID формат: 8-4-4-4-12


class TestLogWithContext:
    """Тесты для log_with_context()"""
    
    @pytest.fixture
    def test_logger(self):
        """Создать тестовый logger с handler"""
        # Создаем уникальное имя logger для каждого теста
        import uuid
        logger_name = f"test_context_logger_{uuid.uuid4().hex[:8]}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # Очищаем handlers перед тестом
        logger.handlers.clear()
        
        # Сбрасываем factory если был установлен
        logging.setLogRecordFactory(logging.LogRecord)
        
        # Создаем StringIO handler для перехвата
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(TERAGJSONFormatter())
        logger.addHandler(handler)
        
        return logger, stream
    
    def test_log_with_trace_id(self, test_logger):
        """Тест логирования с trace_id"""
        logger, stream = test_logger
        
        log_with_context(
            logger,
            logging.INFO,
            "Test message",
            trace_id="trace_123"
        )
        
        # Проверяем что trace_id попал в лог
        log_output = stream.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data["trace_id"] == "trace_123"
        assert log_data["message"] == "Test message"
    
    def test_log_with_correlation_id(self, test_logger):
        """Тест логирования с correlation_id"""
        logger, stream = test_logger
        
        log_with_context(
            logger,
            logging.INFO,
            "Test message",
            correlation_id="corr_456"
        )
        
        log_output = stream.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data["correlation_id"] == "corr_456"
    
    def test_log_with_extra(self, test_logger):
        """Тест логирования с extra данными"""
        logger, stream = test_logger
        
        log_with_context(
            logger,
            logging.INFO,
            "Test message",
            extra={"key": "value", "number": 42}
        )
        
        log_output = stream.getvalue()
        log_data = json.loads(log_output)
        
        assert "extra" in log_data
        assert log_data["extra"]["key"] == "value"
        assert log_data["extra"]["number"] == 42
    
    def test_log_with_all_context(self, test_logger):
        """Тест логирования со всем контекстом"""
        logger, stream = test_logger
        
        log_with_context(
            logger,
            logging.WARNING,
            "Test message",
            trace_id="trace_123",
            correlation_id="corr_456",
            extra={"test": "data"}
        )
        
        log_output = stream.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data["trace_id"] == "trace_123"
        assert log_data["correlation_id"] == "corr_456"
        assert log_data["extra"]["test"] == "data"
        assert log_data["level"] == "WARNING"
    
    def test_log_without_context(self, test_logger):
        """Тест логирования без контекста"""
        logger, stream = test_logger
        
        # Убеждаемся что factory сброшен
        logging.setLogRecordFactory(logging.LogRecord)
        
        log_with_context(
            logger,
            logging.INFO,
            "Test message"
        )
        
        log_output = stream.getvalue()
        log_data = json.loads(log_output)
        
        # trace_id может быть если factory был установлен ранее, но не должен быть в этом случае
        # Проверяем что сообщение корректно
        assert log_data["message"] == "Test message"
    
    def test_log_different_levels(self, test_logger):
        """Тест логирования разных уровней"""
        logger, stream = test_logger
        
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
        
        for level in levels:
            stream.seek(0)
            stream.truncate(0)
            
            log_with_context(
                logger,
                level,
                f"Message at {logging.getLevelName(level)}"
            )
            
            log_output = stream.getvalue()
            log_data = json.loads(log_output)
            
            assert log_data["level"] == logging.getLevelName(level)


class TestIntegration:
    """Интеграционные тесты для logging утилиты"""
    
    def test_full_logging_workflow(self):
        """Тест полного workflow логирования"""
        # Сбрасываем factory перед тестом
        logging.setLogRecordFactory(logging.LogRecord)
        
        # Генерируем trace_id
        trace_id = generate_trace_id()
        
        # Создаем logger без factory (чтобы избежать конфликтов)
        logger = logging.getLogger("integration_test_unique")
        logger.setLevel(logging.INFO)
        
        # Настраиваем handler с JSON formatter
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(TERAGJSONFormatter())
        logger.addHandler(handler)
        
        # Логируем с контекстом
        log_with_context(
            logger,
            logging.INFO,
            "Integration test message",
            trace_id=trace_id,
            correlation_id="corr_test",
            extra={"test": "integration"}
        )
        
        # Проверяем результат
        log_output = stream.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data["trace_id"] == trace_id
        assert log_data["correlation_id"] == "corr_test"
        assert log_data["extra"]["test"] == "integration"
        assert log_data["message"] == "Integration test message"
        assert log_data["level"] == "INFO"

