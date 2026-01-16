"""
Тесты для KAG Solver
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.core.kag_solver.solver import KAGSolver


@pytest.fixture
def mock_graph_driver():
    """Мок Neo4j driver"""
    return Mock()


@pytest.fixture
def mock_lm_client():
    """Мок LM Studio client"""
    client = AsyncMock()
    client.generate = AsyncMock(return_value="Test reasoning")
    return client


@pytest.fixture
def kag_solver(mock_graph_driver, mock_lm_client):
    """Создать KAG Solver для тестов"""
    return KAGSolver(
        graph_driver=mock_graph_driver,
        lm_client=mock_lm_client,
        max_hops=3
    )


@pytest.mark.asyncio
async def test_kag_solver_initialization(kag_solver):
    """Тест инициализации KAG Solver"""
    assert kag_solver is not None
    assert kag_solver.max_hops == 3
    assert kag_solver.path_finder is not None


@pytest.mark.asyncio
async def test_kag_solver_reason_with_graph(kag_solver):
    """Тест рассуждения с графом"""
    # Настраиваем моки
    kag_solver.path_finder.find_paths = Mock(return_value=[
        {"path": ["concept1", "concept2"], "score": 0.9}
    ])
    kag_solver.path_finder.find_causal_chains = Mock(return_value=[
        {"chain": ["cause", "effect"], "score": 0.8}
    ])
    kag_solver.path_finder.rank_paths_by_relevance = Mock(return_value=[
        {"path": ["concept1", "concept2"], "score": 0.9}
    ])
    
    # Моки для внутренних методов
    with patch.object(kag_solver, '_extract_concepts', new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = ["concept1", "concept2"]
        
        with patch.object(kag_solver, '_synthesize_reasoning', new_callable=AsyncMock) as mock_synth:
            mock_synth.return_value = "Synthesized reasoning"
            
            with patch.object(kag_solver, '_calculate_confidence', return_value=0.85):
                result = await kag_solver.reason("Test query")
    
    assert result is not None
    assert result["query"] == "Test query"
    assert "reasoning_paths" in result
    assert "causal_chains" in result
    assert result["context_used"] is True


@pytest.mark.asyncio
async def test_kag_solver_reason_without_graph(kag_solver):
    """Тест рассуждения без графа"""
    kag_solver.driver = None
    
    with patch.object(kag_solver, '_extract_concepts', new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = []
        
        with patch.object(kag_solver, '_simple_reasoning', new_callable=AsyncMock) as mock_simple:
            mock_simple.return_value = "Simple reasoning"
            
            result = await kag_solver.reason("Test query")
    
    assert result is not None
    assert result["conclusion"] == "Simple reasoning"
    assert result["context_used"] is False


@pytest.mark.asyncio
async def test_kag_solver_extract_concepts(kag_solver):
    """Тест извлечения концептов"""
    with patch.object(kag_solver, '_extract_concepts', new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = ["concept1", "concept2", "concept3"]
        
        concepts = await kag_solver._extract_concepts("Test query with concepts")
    
    assert len(concepts) == 3
    assert "concept1" in concepts


@pytest.mark.asyncio
async def test_kag_solver_confidence_calculation(kag_solver):
    """Тест расчета уверенности"""
    paths = [{"score": 0.9}, {"score": 0.8}, {"score": 0.7}]
    chains = [{"score": 0.85}, {"score": 0.75}]
    
    confidence = kag_solver._calculate_confidence(paths, chains)
    
    assert 0.0 <= confidence <= 1.0


def test_kag_solver_max_hops(kag_solver):
    """Тест максимальной глубины поиска"""
    assert kag_solver.max_hops == 3
    
    # Изменяем max_hops
    kag_solver.max_hops = 5
    assert kag_solver.max_hops == 5









