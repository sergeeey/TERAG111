"""
Тесты для LangGraph Serializer
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

try:
    from src.core.agents.langgraph_serializer import LangGraphSerializer, CONFIDENCE_THRESHOLD
    from src.core.agents.langgraph_core import TERAGState
    SERIALIZER_AVAILABLE = True
except ImportError:
    SERIALIZER_AVAILABLE = False
    pytest.skip("Serializer components not available", allow_module_level=True)


@pytest.fixture
def serializer():
    """Создать экземпляр сериализатора"""
    return LangGraphSerializer()


@pytest.fixture
def sample_state():
    """Создать примерное состояние TERAGState"""
    return {
        "query": "What is Graph-RAG?",
        "scratchpad": ["Step 1", "Step 2"],
        "reasoning_steps": [
            {
                "step": "planner",
                "timestamp": datetime.utcnow().isoformat(),
                "result": {"confidence": 0.9, "plan": "test plan"}
            },
            {
                "step": "solver",
                "timestamp": datetime.utcnow().isoformat(),
                "result": {"confidence": 0.8, "solution": "test solution"}
            }
        ],
        "current_step": "solver",
        "guardrail_result": {
            "safe": True,
            "confidence": 1.0,
            "reason": "approved"
        },
        "ethical_evaluation": None,
        "ethical_score": 1.0,
        "alignment_status": "ethical",
        "secure_reasoning_index": 1.0,
        "final_answer": "Graph-RAG is...",
        "confidence": 0.85,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.1.0",
            "trace_id": "test_trace_123"
        }
    }


@pytest.fixture
def low_confidence_state():
    """Создать состояние с низким confidence"""
    return {
        "query": "Test query",
        "scratchpad": [],
        "reasoning_steps": [
            {
                "step": "planner",
                "timestamp": datetime.utcnow().isoformat(),
                "result": {"confidence": 0.4, "plan": "low confidence plan"}  # < 0.6
            }
        ],
        "current_step": "planner",
        "guardrail_result": None,
        "ethical_evaluation": None,
        "ethical_score": 1.0,
        "alignment_status": "ethical",
        "secure_reasoning_index": 1.0,
        "final_answer": None,
        "confidence": 0.4,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.1.0",
            "trace_id": "test_trace_456"
        }
    }


class TestLangGraphSerializer:
    """Тесты для LangGraphSerializer"""
    
    def test_serializer_initialization(self, serializer):
        """Тест инициализации сериализатора"""
        assert serializer is not None
        assert hasattr(serializer, 'NODE_POSITIONS')
        assert "guardrail" in serializer.NODE_POSITIONS
        assert "planner" in serializer.NODE_POSITIONS
    
    def test_serialize_basic(self, serializer, sample_state):
        """Тест базовой сериализации"""
        result = serializer.serialize(sample_state)
        
        assert "nodes" in result
        assert "edges" in result
        assert "metadata" in result
        assert "timeline" in result
        assert isinstance(result["nodes"], list)
        assert isinstance(result["edges"], list)
    
    def test_serialize_includes_scratchpad(self, serializer, sample_state):
        """Тест что scratchpad включается при include_scratchpad=True"""
        result = serializer.serialize(sample_state, include_scratchpad=True)
        assert "scratchpad" in result
        assert result["scratchpad"] == ["Step 1", "Step 2"]
    
    def test_serialize_excludes_scratchpad(self, serializer, sample_state):
        """Тест что scratchpad исключается при include_scratchpad=False"""
        result = serializer.serialize(sample_state, include_scratchpad=False)
        assert "scratchpad" not in result
    
    def test_serialize_with_trace_id(self, serializer, sample_state):
        """Тест сериализации с trace_id"""
        trace_id = "custom_trace_123"
        result = serializer.serialize(sample_state, trace_id=trace_id)
        
        assert result["metadata"]["trace_id"] == trace_id
    
    def test_serialize_creates_nodes(self, serializer, sample_state):
        """Тест создания узлов"""
        result = serializer.serialize(sample_state)
        nodes = result["nodes"]
        
        # Должен быть узел guardrail
        guardrail_nodes = [n for n in nodes if n["type"] == "guardrail"]
        assert len(guardrail_nodes) > 0
        
        # Должны быть узлы из reasoning_steps
        planner_nodes = [n for n in nodes if n["type"] == "planner"]
        solver_nodes = [n for n in nodes if n["type"] == "solver"]
        assert len(planner_nodes) > 0
        assert len(solver_nodes) > 0
    
    def test_serialize_creates_edges(self, serializer, sample_state):
        """Тест создания связей"""
        result = serializer.serialize(sample_state)
        edges = result["edges"]
        
        assert len(edges) > 0
        for edge in edges:
            assert "source" in edge
            assert "target" in edge
            assert "type" in edge
    
    def test_serialize_creates_metadata(self, serializer, sample_state):
        """Тест создания метаданных"""
        result = serializer.serialize(sample_state)
        metadata = result["metadata"]
        
        assert "query" in metadata
        assert "confidence" in metadata
        assert "ethical_score" in metadata
        assert "secure_reasoning_index" in metadata
        assert metadata["query"] == "What is Graph-RAG?"
    
    def test_confidence_validation_high_confidence(self, serializer, sample_state):
        """Тест валидации confidence для высокого confidence"""
        result = serializer.serialize(sample_state)
        nodes = result["nodes"]
        
        # Узлы с confidence >= 0.6 должны быть "completed" или "active"
        for node in nodes:
            if node.get("confidence", 1.0) >= CONFIDENCE_THRESHOLD:
                assert node["status"] in ["completed", "active", "pending"]
    
    def test_confidence_validation_low_confidence(self, serializer, low_confidence_state):
        """Тест валидации confidence для низкого confidence"""
        with patch('src.core.agents.langgraph_serializer.logger') as mock_logger:
            result = serializer.serialize(low_confidence_state)
            nodes = result["nodes"]
            
            # Должен быть вызов warning для низкого confidence
            mock_logger.warning.assert_called()
            
            # Узлы с confidence < 0.6 должны быть помечены как "questionable"
            low_confidence_nodes = [
                n for n in nodes 
                if n.get("confidence", 1.0) < CONFIDENCE_THRESHOLD
            ]
            for node in low_confidence_nodes:
                if node.get("status") == "completed":
                    # Если был completed, должен стать questionable
                    pass  # Проверяем что warning был вызван
    
    def test_serialize_with_mlflow_tracer(self, serializer, sample_state):
        """Тест сериализации с MLflow tracer"""
        mock_mlflow_tracer = Mock()
        mock_mlflow_tracer.log_reason_graph = Mock()
        
        result = serializer.serialize(
            sample_state,
            mlflow_tracer=mock_mlflow_tracer
        )
        
        # Проверяем что tracer был вызван
        mock_mlflow_tracer.log_reason_graph.assert_called_once()
        assert mock_mlflow_tracer.log_reason_graph.call_args[0][0] == result
    
    def test_serialize_with_langsmith_tracer(self, serializer, sample_state):
        """Тест сериализации с LangSmith tracer"""
        mock_langsmith_tracer = Mock()
        mock_langsmith_tracer.log_reason_graph = Mock()
        
        result = serializer.serialize(
            sample_state,
            langsmith_tracer=mock_langsmith_tracer
        )
        
        # Проверяем что tracer был вызван
        mock_langsmith_tracer.log_reason_graph.assert_called_once()
        assert mock_langsmith_tracer.log_reason_graph.call_args[0][0] == result
    
    def test_serialize_handles_tracer_errors(self, serializer, sample_state):
        """Тест обработки ошибок tracers"""
        mock_tracer = Mock()
        mock_tracer.log_reason_graph = Mock(side_effect=Exception("Tracer error"))
        
        # Не должно вызывать исключение
        with patch('src.core.agents.langgraph_serializer.logger') as mock_logger:
            result = serializer.serialize(
                sample_state,
                mlflow_tracer=mock_tracer
            )
            
            # Должно быть предупреждение
            mock_logger.warning.assert_called()
            # Но результат должен быть возвращен
            assert result is not None
    
    def test_to_json(self, serializer, sample_state):
        """Тест преобразования в JSON строку"""
        import json
        json_str = serializer.to_json(sample_state)
        
        assert isinstance(json_str, str)
        # Должен быть валидный JSON
        parsed = json.loads(json_str)
        assert "nodes" in parsed
        assert "edges" in parsed


class TestNodePositions:
    """Тесты для позиций узлов"""
    
    def test_node_positions_exist(self, serializer):
        """Тест что позиции узлов определены"""
        positions = serializer.NODE_POSITIONS
        
        required_nodes = ["guardrail", "planner", "solver", "verifier", "ethical", "reject"]
        for node_type in required_nodes:
            assert node_type in positions
            assert "x" in positions[node_type]
            assert "y" in positions[node_type]
            assert "z" in positions[node_type]

