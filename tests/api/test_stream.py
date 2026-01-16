"""
Тесты для SSE Stream API
"""
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Импорты для тестирования
try:
    from src.api.routes.stream import router, _filter_nodes
    from src.api.models.reasoning import ReasoningQuery
    from src.core.exceptions import (
        TERAGError,
        StreamError,
        GraphError,
        ValidationError
    )
    STREAM_AVAILABLE = True
except ImportError:
    STREAM_AVAILABLE = False
    pytest.skip("Stream components not available", allow_module_level=True)


@pytest.fixture
def app():
    """Создать тестовое приложение"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Создать тестовый клиент"""
    return TestClient(app)


@pytest.fixture
def mock_reason_graph():
    """Мок ReasonGraph"""
    return {
        "nodes": [
            {"id": "node_1", "type": "planner", "label": "Planner", "status": "completed"},
            {"id": "node_2", "type": "solver", "label": "Solver", "status": "active"},
            {"id": "node_3", "type": "verifier", "label": "Verifier", "status": "pending"}
        ],
        "edges": [
            {"id": "edge_1", "source": "node_1", "target": "node_2", "type": "reasoning_flow"},
            {"id": "edge_2", "source": "node_2", "target": "node_3", "type": "reasoning_flow"}
        ],
        "metadata": {
            "query": "test query",
            "confidence": 0.9
        }
    }


class TestReasoningQuery:
    """Тесты для Pydantic модели ReasoningQuery"""
    
    def test_valid_query(self):
        """Тест валидного запроса"""
        query = ReasoningQuery(query="What is Graph-RAG?")
        assert query.query == "What is Graph-RAG?"
        assert query.show is None
        assert query.thread_id is None
    
    def test_query_with_show(self):
        """Тест запроса с фильтром узлов"""
        query = ReasoningQuery(
            query="Test query",
            show=["planner", "solver"]
        )
        assert query.show == ["planner", "solver"]
    
    def test_query_with_thread_id(self):
        """Тест запроса с thread_id"""
        query = ReasoningQuery(
            query="Test query",
            thread_id="user_123_session_456"
        )
        assert query.thread_id == "user_123_session_456"
    
    def test_empty_query_raises_error(self):
        """Тест что пустой запрос вызывает ошибку"""
        # Pydantic валидирует min_length раньше, чем наш validator
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ReasoningQuery(query="")
    
    def test_whitespace_only_query_raises_error(self):
        """Тест что запрос только из пробелов вызывает ошибку"""
        with pytest.raises(ValueError, match="cannot be empty"):
            ReasoningQuery(query="   ")
    
    def test_dangerous_characters_raise_error(self):
        """Тест что опасные символы вызывают ошибку"""
        dangerous_chars = ['<', '>', '{', '}', '[', ']', '\\', '\x00']
        for char in dangerous_chars:
            with pytest.raises(ValueError, match="dangerous character"):
                ReasoningQuery(query=f"test{char}query")
    
    def test_invalid_node_types_raise_error(self):
        """Тест что недопустимые типы узлов вызывают ошибку"""
        with pytest.raises(ValueError, match="Invalid node types"):
            ReasoningQuery(query="test", show=["invalid_type"])
    
    def test_valid_node_types(self):
        """Тест что допустимые типы узлов проходят валидацию"""
        valid_types = ["guardrail", "planner", "solver", "verifier", "ethical", "reject"]
        query = ReasoningQuery(query="test", show=valid_types)
        assert query.show == valid_types


class TestFilterNodes:
    """Тесты для функции фильтрации узлов"""
    
    def test_filter_nodes_empty_filter(self, mock_reason_graph):
        """Тест фильтрации с пустым фильтром (возвращает все)"""
        result = _filter_nodes(mock_reason_graph, set())
        assert len(result["nodes"]) == 3
        assert len(result["edges"]) == 2
    
    def test_filter_nodes_single_type(self, mock_reason_graph):
        """Тест фильтрации по одному типу"""
        result = _filter_nodes(mock_reason_graph, {"planner"})
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["type"] == "planner"
        assert len(result["edges"]) == 0  # Нет связей для одного узла
    
    def test_filter_nodes_multiple_types(self, mock_reason_graph):
        """Тест фильтрации по нескольким типам"""
        result = _filter_nodes(mock_reason_graph, {"planner", "solver"})
        assert len(result["nodes"]) == 2
        node_types = {node["type"] for node in result["nodes"]}
        assert node_types == {"planner", "solver"}
        assert len(result["edges"]) == 1  # Одна связь между planner и solver


class TestStreamAPI:
    """Тесты для SSE Stream API"""
    
    @patch('src.api.routes.stream.get_terag_graph')
    @patch('src.api.routes.stream.LANGGRAPH_AVAILABLE', True)
    def test_stream_reasoning_endpoint_exists(self, mock_get_graph, client):
        """Тест что endpoint существует"""
        # Мокаем граф
        mock_graph = Mock()
        mock_graph.state_graph = Mock()
        mock_get_graph.return_value = mock_graph
        
        # Пропускаем реальный SSE stream, просто проверяем что endpoint доступен
        # В реальном тесте нужно использовать async клиент для SSE
        response = client.get("/api/stream/reasoning?query=test")
        # SSE endpoint может вернуть 200 или начать поток
        assert response.status_code in [200, 503]  # 503 если LangGraph недоступен
    
    @patch('src.api.routes.stream.LANGGRAPH_AVAILABLE', False)
    def test_stream_reasoning_langgraph_unavailable(self, client):
        """Тест что endpoint возвращает 503 если LangGraph недоступен"""
        response = client.get("/api/stream/reasoning?query=test")
        assert response.status_code == 503
        assert "LangGraph not available" in response.json()["detail"]
    
    def test_stream_status_endpoint(self, client):
        """Тест endpoint статуса потоков"""
        response = client.get("/api/stream/status")
        assert response.status_code == 200
        data = response.json()
        assert "active_streams" in data or "thread_id" in data
        assert "count" in data or "active" in data


class TestExceptions:
    """Тесты для кастомных исключений"""
    
    def test_terag_error_base(self):
        """Тест базового класса TERAGError"""
        error = TERAGError("Test error", code="TEST_ERROR", trace_id="trace_123")
        assert error.message == "Test error"
        assert error.code == "TEST_ERROR"
        assert error.trace_id == "trace_123"
        
        error_dict = error.to_dict()
        assert error_dict["error"] is True
        assert error_dict["code"] == "TEST_ERROR"
        assert error_dict["message"] == "Test error"
        assert error_dict["trace_id"] == "trace_123"
    
    def test_stream_error(self):
        """Тест StreamError"""
        error = StreamError("Stream failed", trace_id="trace_123")
        assert isinstance(error, TERAGError)
        assert error.code == "StreamError"
    
    def test_graph_error(self):
        """Тест GraphError"""
        error = GraphError("Graph unavailable", trace_id="trace_123")
        assert isinstance(error, TERAGError)
        assert error.code == "GraphError"
    
    def test_validation_error(self):
        """Тест ValidationError"""
        error = ValidationError("Invalid input", details={"field": "query"}, trace_id="trace_123")
        assert isinstance(error, TERAGError)
        assert error.code == "ValidationError"
        assert error.details["field"] == "query"

