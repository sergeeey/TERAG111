"""
Интеграция LangGraph Core с существующими компонентами TERAG
"""
import logging
from typing import Dict, Any, Optional, Any as AnyType

logger = logging.getLogger(__name__)

from .langgraph_core import TERAGStateGraph, TERAGState
from .guardrail_node import GuardrailNode

try:
    from src.core.evolution_loop import TERAGEvolutionLoop
    from src.core.kag_solver.solver import KAGSolver
    from src.core.agents import Planner, Researcher, Verifier
    from src.integration.lmstudio_client import LMStudioClient
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    logger.warning("Some integration components not available")

try:
    from src.promptops.loader_service import PromptLoaderService
    PROMPT_LOADER_AVAILABLE = True
except ImportError:
    PROMPT_LOADER_AVAILABLE = False
    logger.warning("PromptLoaderService not available")


# Глобальный экземпляр для dependency injection
_terag_graph_instance: Optional['TERAGLangGraphIntegration'] = None


def get_terag_graph() -> 'TERAGLangGraphIntegration':
    """
    Factory функция для получения TERAG графа (Dependency Injection)
    
    Returns:
        TERAGLangGraphIntegration instance
    """
    global _terag_graph_instance
    
    if _terag_graph_instance is None:
        _terag_graph_instance = TERAGLangGraphIntegration(
            enable_guardrail=True
        )
        logger.info("TERAGLangGraphIntegration instance created (singleton)")
    
    return _terag_graph_instance


def reset_terag_graph():
    """Сбросить глобальный экземпляр (для тестирования)"""
    global _terag_graph_instance
    _terag_graph_instance = None


class TERAGLangGraphIntegration:
    """
    Интеграция LangGraph Core с TERAG компонентами
    """
    
    def __init__(
        self,
        graph_driver=None,
        lm_client=None,
        enable_guardrail: bool = True,
        prompt_loader: Optional[AnyType] = None  # Phase 4
    ):
        """
        Инициализация интеграции
        
        Args:
            graph_driver: Neo4j driver
            lm_client: LM Studio client
            enable_guardrail: Включить guardrail
            prompt_loader: PromptLoaderService (Phase 4)
        """
        # Инициализируем компоненты
        self.graph_driver = graph_driver
        self.lm_client = lm_client
        self.prompt_loader = prompt_loader  # Phase 4
        
        # Создаем агенты
        self.planner = Planner(lm_client=lm_client) if INTEGRATION_AVAILABLE else None
        self.solver = KAGSolver(graph_driver=graph_driver, lm_client=lm_client) if INTEGRATION_AVAILABLE else None
        self.verifier = Verifier(lm_client=lm_client) if INTEGRATION_AVAILABLE else None
        
        # Guardrail
        self.guardrail = None
        if enable_guardrail:
            self.guardrail = GuardrailNode(lm_client=lm_client, strict_mode=True)
        
        # Создаем LangGraph
        self.state_graph = TERAGStateGraph(
            planner=self.planner,
            solver=self.solver,
            verifier=self.verifier,
            guardrail=self.guardrail,
            enable_checkpointing=True
        )
        
        logger.info("TERAGLangGraphIntegration initialized")
    
    async def reason(self, query: str) -> Dict[str, Any]:
        """
        Выполнить reasoning через LangGraph
        
        Args:
            query: Запрос пользователя
        
        Returns:
            Результат reasoning с полной трассировкой
        """
        logger.info(f"Starting LangGraph reasoning for: {query[:100]}")
        
        # Запускаем граф
        result = await self.state_graph.run(query)
        
        return result
    
    def get_reason_graph_json(self, query: str) -> str:
        """
        Получить ReasonGraph JSON для визуализации
        
        Args:
            query: Запрос (для получения состояния)
        
        Returns:
            JSON строка с ReasonGraph
        """
        import json
        # TODO: Реализовать получение состояния из checkpoint
        # Пока возвращаем пустой граф
        return json.dumps({
            "nodes": [],
            "edges": [],
            "metadata": {"query": query}
        }, indent=2, ensure_ascii=False)

