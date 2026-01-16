"""
Тесты для TERAG Evolution Loop
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.core.evolution_loop import TERAGEvolutionLoop


@pytest.fixture
def mock_graph_driver():
    """Мок Neo4j driver"""
    return Mock()


@pytest.fixture
def mock_lm_client():
    """Мок LM Studio client"""
    client = AsyncMock()
    client.generate = AsyncMock(return_value="Test response")
    return client


@pytest.fixture
def evolution_loop(mock_graph_driver, mock_lm_client):
    """Создать Evolution Loop для тестов"""
    return TERAGEvolutionLoop(
        graph_driver=mock_graph_driver,
        lm_client=mock_lm_client,
        enable_visualization=False
    )


@pytest.mark.asyncio
async def test_evolution_loop_initialization(evolution_loop):
    """Тест инициализации Evolution Loop"""
    assert evolution_loop is not None
    assert evolution_loop.solver is not None
    assert evolution_loop.evaluator is not None
    assert evolution_loop.ethics is not None
    assert "planner" in evolution_loop.agents
    assert "researcher" in evolution_loop.agents
    assert "verifier" in evolution_loop.agents
    assert "writer" in evolution_loop.agents
    assert "critic" in evolution_loop.agents


@pytest.mark.asyncio
async def test_evolution_loop_run_success(evolution_loop):
    """Тест успешного выполнения Evolution Loop"""
    # Настраиваем моки агентов
    evolution_loop.agents["planner"].plan = AsyncMock(return_value={"plan": "test plan"})
    evolution_loop.agents["researcher"].collect = AsyncMock(return_value={"data": "test data"})
    evolution_loop.agents["verifier"].check = AsyncMock(return_value={"verified_reasoning": {"result": "test"}})
    evolution_loop.agents["writer"].compose = AsyncMock(return_value={"report": "test report"})
    evolution_loop.agents["critic"].analyze = AsyncMock(return_value={"feedback": "test feedback"})
    
    evolution_loop.solver.reason = AsyncMock(return_value={
        "conclusion": "test conclusion",
        "confidence": 0.9
    })
    evolution_loop.ethics.filter = AsyncMock(return_value={"filtered_content": {"result": "test"}})
    
    # Выполняем
    result = await evolution_loop.run("Test query", visualize=False)
    
    # Проверяем результат
    assert result["success"] is True
    assert result["query"] == "Test query"
    assert "stages" in result
    assert "planning" in result["stages"]
    assert "research" in result["stages"]
    assert "reasoning" in result["stages"]
    assert "verification" in result["stages"]
    assert "writing" in result["stages"]
    assert "criticism" in result["stages"]
    assert "duration_seconds" in result


@pytest.mark.asyncio
async def test_evolution_loop_run_error_handling(evolution_loop):
    """Тест обработки ошибок в Evolution Loop"""
    # Настраиваем мок для генерации ошибки
    evolution_loop.agents["planner"].plan = AsyncMock(side_effect=Exception("Test error"))
    
    # Выполняем
    result = await evolution_loop.run("Test query", visualize=False)
    
    # Проверяем обработку ошибки
    assert result["success"] is False
    assert "error" in result
    assert "Test error" in result["error"]


@pytest.mark.asyncio
async def test_evolution_loop_get_system_status(evolution_loop):
    """Тест получения статуса системы"""
    status = evolution_loop.get_system_status()
    
    assert "health" in status
    assert "metrics" in status
    assert "components" in status
    assert status["components"]["solver"] is True
    assert status["components"]["evaluator"] is True
    assert status["components"]["ethics"] is True


@pytest.mark.asyncio
async def test_evolution_loop_with_visualization(evolution_loop):
    """Тест Evolution Loop с визуализацией"""
    # Включаем визуализацию
    evolution_loop.enable_visualization = True
    evolution_loop.dashboard = Mock()
    evolution_loop.dashboard.visualize_reasoning_paths = AsyncMock(return_value="/path/to/viz")
    
    # Настраиваем моки
    evolution_loop.agents["planner"].plan = AsyncMock(return_value={"plan": "test"})
    evolution_loop.agents["researcher"].collect = AsyncMock(return_value={"data": "test"})
    evolution_loop.agents["verifier"].check = AsyncMock(return_value={"verified_reasoning": {}})
    evolution_loop.agents["writer"].compose = AsyncMock(return_value={"report": "test"})
    evolution_loop.agents["critic"].analyze = AsyncMock(return_value={"feedback": "test"})
    evolution_loop.solver.reason = AsyncMock(return_value={"conclusion": "test"})
    evolution_loop.ethics.filter = AsyncMock(return_value={"filtered_content": {}})
    
    # Выполняем
    result = await evolution_loop.run("Test query", visualize=True)
    
    # Проверяем визуализацию
    assert result["success"] is True
    assert "visualization" in result









