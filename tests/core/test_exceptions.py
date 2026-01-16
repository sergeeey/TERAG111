"""
Тесты для кастомных исключений TERAG
"""
import pytest

try:
    from src.core.exceptions import (
        TERAGError,
        StreamError,
        GraphError,
        ValidationError,
        ConfidenceError,
        SerializationError,
        IntegrationError
    )
    EXCEPTIONS_AVAILABLE = True
except ImportError:
    EXCEPTIONS_AVAILABLE = False
    pytest.skip("Exception classes not available", allow_module_level=True)


class TestTERAGError:
    """Тесты для базового класса TERAGError"""
    
    def test_basic_error(self):
        """Тест базового исключения"""
        error = TERAGError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.code == "TERAGError"
        assert error.details == {}
        assert error.trace_id is None
    
    def test_error_with_code(self):
        """Тест исключения с кодом"""
        error = TERAGError("Test error", code="CUSTOM_CODE")
        assert error.code == "CUSTOM_CODE"
    
    def test_error_with_details(self):
        """Тест исключения с деталями"""
        details = {"field": "query", "value": "test"}
        error = TERAGError("Test error", details=details)
        assert error.details == details
    
    def test_error_with_trace_id(self):
        """Тест исключения с trace_id"""
        error = TERAGError("Test error", trace_id="trace_123")
        assert error.trace_id == "trace_123"
    
    def test_to_dict(self):
        """Тест преобразования в словарь"""
        error = TERAGError(
            "Test error",
            code="TEST_ERROR",
            details={"field": "query"},
            trace_id="trace_123"
        )
        
        error_dict = error.to_dict()
        assert error_dict["error"] is True
        assert error_dict["code"] == "TEST_ERROR"
        assert error_dict["message"] == "Test error"
        assert error_dict["details"] == {"field": "query"}
        assert error_dict["trace_id"] == "trace_123"


class TestStreamError:
    """Тесты для StreamError"""
    
    def test_stream_error_inheritance(self):
        """Тест что StreamError наследуется от TERAGError"""
        error = StreamError("Stream failed")
        assert isinstance(error, TERAGError)
        assert error.code == "StreamError"
    
    def test_stream_error_with_trace_id(self):
        """Тест StreamError с trace_id"""
        error = StreamError("Stream failed", trace_id="trace_123")
        assert error.trace_id == "trace_123"


class TestGraphError:
    """Тесты для GraphError"""
    
    def test_graph_error_inheritance(self):
        """Тест что GraphError наследуется от TERAGError"""
        error = GraphError("Graph unavailable")
        assert isinstance(error, TERAGError)
        assert error.code == "GraphError"


class TestValidationError:
    """Тесты для ValidationError"""
    
    def test_validation_error_inheritance(self):
        """Тест что ValidationError наследуется от TERAGError"""
        error = ValidationError("Invalid input")
        assert isinstance(error, TERAGError)
        assert error.code == "ValidationError"
    
    def test_validation_error_with_details(self):
        """Тест ValidationError с деталями"""
        error = ValidationError(
            "Invalid input",
            details={"field": "query", "reason": "too long"}
        )
        assert error.details["field"] == "query"


class TestConfidenceError:
    """Тесты для ConfidenceError"""
    
    def test_confidence_error_creation(self):
        """Тест создания ConfidenceError"""
        error = ConfidenceError(confidence=0.4, threshold=0.6, trace_id="trace_123")
        
        assert error.confidence == 0.4
        assert error.threshold == 0.6
        assert "0.40" in error.message
        assert "0.60" in error.message
        assert error.code == "CONFIDENCE_ERROR"
        assert error.details["confidence"] == 0.4
        assert error.details["threshold"] == 0.6
        assert error.details["status"] == "quarantine"
    
    def test_confidence_error_default_threshold(self):
        """Тест ConfidenceError с дефолтным threshold"""
        error = ConfidenceError(confidence=0.4)
        assert error.threshold == 0.6  # Дефолтное значение


class TestSerializationError:
    """Тесты для SerializationError"""
    
    def test_serialization_error_inheritance(self):
        """Тест что SerializationError наследуется от TERAGError"""
        error = SerializationError("Serialization failed")
        assert isinstance(error, TERAGError)
        assert error.code == "SerializationError"


class TestIntegrationError:
    """Тесты для IntegrationError"""
    
    def test_integration_error_inheritance(self):
        """Тест что IntegrationError наследуется от TERAGError"""
        error = IntegrationError("Integration failed")
        assert isinstance(error, TERAGError)
        assert error.code == "IntegrationError"

