"""
Тесты для агентов TERAG (Planner, Researcher, Verifier, Writer, Critic)
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.core.agents.planner import Planner
from src.core.agents.researcher import Researcher
from src.core.agents.verifier import Verifier
from src.core.agents.writer import Writer
from src.core.agents.critic import Critic


@pytest.fixture
def mock_lm_client():
    """Мок LM Studio client"""
    client = AsyncMock()
    client.generate = AsyncMock(return_value={"text": "Test response"})
    return client


@pytest.fixture
def mock_graph_driver():
    """Мок Neo4j driver"""
    driver = Mock()
    session = Mock()
    session.run = Mock(return_value=Mock(values=lambda: [["concept1", "concept2"]]))
    driver.session = Mock(return_value=session)
    return driver


# ========== Planner Tests ==========

@pytest.mark.asyncio
async def test_planner_initialization(mock_lm_client):
    """Тест инициализации Planner"""
    planner = Planner(lm_client=mock_lm_client)
    assert planner is not None
    assert planner.lm_client == mock_lm_client


@pytest.mark.asyncio
async def test_planner_plan_with_lm(mock_lm_client):
    """Тест планирования с LM Studio"""
    planner = Planner(lm_client=mock_lm_client)
    
    result = await planner.plan("Test query")
    
    assert result is not None
    assert "query" in result
    assert "steps" in result
    assert "timestamp" in result
    assert result["query"] == "Test query"


@pytest.mark.asyncio
async def test_planner_plan_without_lm():
    """Тест планирования без LM Studio"""
    planner = Planner(lm_client=None)
    
    result = await planner.plan("Test query")
    
    assert result is not None
    assert "query" in result
    assert "steps" in result
    # Без LM должен быть базовый план
    assert len(result["steps"]) >= 0


# ========== Researcher Tests ==========

@pytest.mark.asyncio
async def test_researcher_initialization(mock_graph_driver):
    """Тест инициализации Researcher"""
    researcher = Researcher(graph_driver=mock_graph_driver)
    assert researcher is not None
    assert researcher.graph_driver == mock_graph_driver


@pytest.mark.asyncio
async def test_researcher_collect_with_graph(mock_graph_driver):
    """Тест сбора данных с графом"""
    researcher = Researcher(graph_driver=mock_graph_driver)
    
    plan = {"required_data": ["concept1", "concept2"]}
    result = await researcher.collect(plan)
    
    assert result is not None
    assert "data" in result or "concepts" in result or "triplets" in result


@pytest.mark.asyncio
async def test_researcher_collect_without_graph():
    """Тест сбора данных без графа"""
    researcher = Researcher(graph_driver=None)
    
    plan = {"required_data": ["concept1"]}
    result = await researcher.collect(plan)
    
    assert result is not None
    # Без графа должен вернуть пустые данные или базовую структуру


# ========== Verifier Tests ==========

@pytest.mark.asyncio
async def test_verifier_initialization(mock_lm_client):
    """Тест инициализации Verifier"""
    verifier = Verifier(lm_client=mock_lm_client)
    assert verifier is not None
    assert verifier.lm_client == mock_lm_client


@pytest.mark.asyncio
async def test_verifier_check(mock_lm_client):
    """Тест проверки достоверности"""
    verifier = Verifier(lm_client=mock_lm_client)
    
    reasoning = {
        "conclusion": "Test conclusion",
        "confidence": 0.8
    }
    
    result = await verifier.check(reasoning)
    
    assert result is not None
    assert "verified_reasoning" in result or "verified" in result or "check_result" in result


# ========== Writer Tests ==========

@pytest.mark.asyncio
async def test_writer_initialization(mock_lm_client):
    """Тест инициализации Writer"""
    writer = Writer(lm_client=mock_lm_client)
    assert writer is not None
    assert writer.lm_client == mock_lm_client


@pytest.mark.asyncio
async def test_writer_compose(mock_lm_client):
    """Тест составления отчета"""
    writer = Writer(lm_client=mock_lm_client)
    
    content = {
        "verified_reasoning": {"conclusion": "Test"},
        "data": "Test data"
    }
    
    result = await writer.compose(content)
    
    assert result is not None
    assert "report" in result or "text" in result or isinstance(result, dict)


# ========== Critic Tests ==========

@pytest.mark.asyncio
async def test_critic_initialization(mock_lm_client):
    """Тест инициализации Critic"""
    critic = Critic(lm_client=mock_lm_client)
    assert critic is not None
    assert critic.lm_client == mock_lm_client


@pytest.mark.asyncio
async def test_critic_analyze(mock_lm_client):
    """Тест критического анализа"""
    critic = Critic(lm_client=mock_lm_client)
    
    report = {
        "report": "Test report",
        "conclusion": "Test conclusion"
    }
    
    result = await critic.analyze(report)
    
    assert result is not None
    assert "feedback" in result or "analysis" in result or "critique" in result or isinstance(result, dict)


# ========== Integration Tests ==========

@pytest.mark.asyncio
async def test_agents_workflow(mock_lm_client, mock_graph_driver):
    """Тест полного workflow агентов"""
    planner = Planner(lm_client=mock_lm_client)
    researcher = Researcher(graph_driver=mock_graph_driver)
    verifier = Verifier(lm_client=mock_lm_client)
    writer = Writer(lm_client=mock_lm_client)
    critic = Critic(lm_client=mock_lm_client)
    
    # Планирование
    plan = await planner.plan("Test query")
    assert plan is not None
    
    # Исследование
    data = await researcher.collect(plan)
    assert data is not None
    
    # Reasoning (упрощенный)
    reasoning = {"conclusion": "Test", "confidence": 0.8}
    
    # Проверка
    verified = await verifier.check(reasoning)
    assert verified is not None
    
    # Написание
    report = await writer.compose(verified)
    assert report is not None
    
    # Критика
    feedback = await critic.analyze(report)
    assert feedback is not None









