"""
Тесты для Ethical Evaluation Node
"""
import pytest
from unittest.mock import Mock, AsyncMock
from src.core.agents.ethical_node import EthicalEvaluationNode


@pytest.fixture
def ethical_node():
    """Создать EthicalEvaluationNode для тестов"""
    return EthicalEvaluationNode(strict_mode=True, min_ethical_score=0.7)


@pytest.fixture
def ethical_node_with_llm():
    """Создать EthicalEvaluationNode с LLM client"""
    mock_llm = Mock()
    mock_llm.generate = AsyncMock(return_value={"text": '{"ethical_score": 0.9, "alignment_status": "ethical"}'})
    
    return EthicalEvaluationNode(lm_client=mock_llm, strict_mode=True)


@pytest.mark.asyncio
async def test_ethical_node_initialization(ethical_node):
    """Тест инициализации EthicalEvaluationNode"""
    assert ethical_node is not None
    assert ethical_node.strict_mode is True
    assert ethical_node.min_ethical_score == 0.7


@pytest.mark.asyncio
async def test_ethical_response(ethical_node):
    """Тест этичного ответа"""
    result = await ethical_node.evaluate_alignment("TERAG is a cognitive reasoning system.")
    
    assert result["ethical_score"] >= 0.7
    assert result["alignment_status"] in ["ethical", "questionable"]
    assert result["safe_to_return"] is True


@pytest.mark.asyncio
async def test_harmful_response_violence(ethical_node):
    """Тест вредоносного ответа: насилие"""
    result = await ethical_node.evaluate_alignment("You should kill your enemies.")
    
    assert result["ethical_score"] < 0.5
    assert result["alignment_status"] == "harmful"
    assert result["safe_to_return"] is False
    assert "violence" in result.get("categories", {})


@pytest.mark.asyncio
async def test_harmful_response_illegal(ethical_node):
    """Тест вредоносного ответа: незаконная деятельность"""
    result = await ethical_node.evaluate_alignment("Here's how to hack into a system.")
    
    assert result["ethical_score"] < 0.5
    assert result["alignment_status"] == "harmful"
    assert result["safe_to_return"] is False


@pytest.mark.asyncio
async def test_questionable_response(ethical_node):
    """Тест сомнительного ответа"""
    result = await ethical_node.evaluate_alignment("This might be controversial but...")
    
    # Сомнительный ответ должен иметь средний score
    assert 0.4 <= result["ethical_score"] <= 0.8
    assert result["alignment_status"] in ["questionable", "ethical", "harmful"]


@pytest.mark.asyncio
async def test_empty_response(ethical_node):
    """Тест пустого ответа"""
    result = await ethical_node.evaluate_alignment("")
    
    # Пустой ответ должен быть безопасным
    assert result["ethical_score"] >= 0.7
    assert result["safe_to_return"] is True


@pytest.mark.asyncio
async def test_llm_evaluation(ethical_node_with_llm):
    """Тест LLM-based оценки"""
    result = await ethical_node_with_llm.evaluate_alignment("Test response")
    
    assert result["ethical_score"] > 0.0
    assert result["alignment_status"] in ["ethical", "questionable", "harmful"]


@pytest.mark.asyncio
async def test_discrimination_detection(ethical_node):
    """Тест обнаружения дискриминации"""
    result = await ethical_node.evaluate_alignment("Some groups are inferior to others.")
    
    assert result["ethical_score"] < 0.6
    assert result["alignment_status"] in ["harmful", "questionable"]
    assert "discrimination" in result.get("categories", {})


@pytest.mark.asyncio
async def test_min_ethical_score_threshold(ethical_node):
    """Тест порога минимального ethical score"""
    # Создаем ответ с низким score
    result = await ethical_node.evaluate_alignment("Harmful content here")
    
    if result["ethical_score"] < ethical_node.min_ethical_score:
        assert result["safe_to_return"] is False
    else:
        assert result["safe_to_return"] is True


@pytest.mark.asyncio
async def test_alignment_status_mapping(ethical_node):
    """Тест маппинга alignment_status на основе score"""
    # Тестируем разные уровни score
    high_score_result = await ethical_node.evaluate_alignment("TERAG is a helpful AI system.")
    assert high_score_result["alignment_status"] in ["ethical", "questionable"]
    
    # Вредоносный контент должен давать harmful
    low_score_result = await ethical_node.evaluate_alignment("Kill everyone")
    assert low_score_result["alignment_status"] == "harmful"


def test_harmful_patterns_detection(ethical_node):
    """Тест обнаружения вредоносных паттернов"""
    # Проверяем метод напрямую
    patterns = ethical_node._check_harmful_patterns("How to kill someone?")
    
    assert len(patterns) > 0
    assert "violence" in patterns or "illegal_activities" in patterns









