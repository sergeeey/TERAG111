"""
TERAG Evolution Loop — главный оркестратор цикла рассуждения

Объединяет:
- KAG-Solver (графовое рассуждение)
- Multi-Agent System (планирование, исследование, проверка, написание, критика)
- Auto-Eval (самооценка)
- Ethical Filter (этическая фильтрация)
- Visualization (визуализация)
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from .kag_solver.solver import KAGSolver
from .auto_eval.evaluator import AutoEvaluator
from .ethics.filter import EthicalFilter
from .agents import Planner, Researcher, Verifier, Writer, Critic
from .visualization.graph_dashboard import GraphDashboard

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j not available")

try:
    from src.integration.lmstudio_client import LMStudioClient
    LMSTUDIO_AVAILABLE = True
except ImportError:
    LMSTUDIO_AVAILABLE = False
    logger.warning("LMStudioClient not available")


class TERAGEvolutionLoop:
    """
    TERAG Evolution Loop — главный цикл рассуждения
    
    Процесс:
    1. Planner создаёт план
    2. Researcher собирает данные из графа
    3. KAGSolver выполняет рассуждение
    4. Verifier проверяет достоверность
    5. EthicalFilter фильтрует контент
    6. Writer составляет отчёт
    7. Critic анализирует результат
    8. AutoEvaluator обновляет метрики
    9. Visualization создаёт визуализацию
    """
    
    def __init__(
        self,
        graph_driver=None,
        lm_client=None,
        enable_visualization: bool = True
    ):
        """
        Инициализация Evolution Loop
        
        Args:
            graph_driver: Neo4j driver
            lm_client: LMStudioClient
            enable_visualization: Включить визуализацию
        """
        self.graph_driver = graph_driver
        self.lm_client = lm_client
        self.enable_visualization = enable_visualization
        
        # Инициализация компонентов
        self.solver = KAGSolver(graph_driver=graph_driver, lm_client=lm_client)
        self.evaluator = AutoEvaluator()
        self.ethics = EthicalFilter(lm_client=lm_client)
        self.dashboard = GraphDashboard(graph_driver=graph_driver) if enable_visualization else None
        
        # Инициализация агентов
        self.agents = {
            "planner": Planner(lm_client=lm_client),
            "researcher": Researcher(graph_driver=graph_driver),
            "verifier": Verifier(lm_client=lm_client),
            "writer": Writer(lm_client=lm_client),
            "critic": Critic(lm_client=lm_client)
        }
        
        logger.info("TERAGEvolutionLoop initialized")
    
    async def run(self, query: str, visualize: bool = True) -> Dict[str, Any]:
        """
        Запустить цикл рассуждения
        
        Args:
            query: Запрос пользователя
            visualize: Создать визуализацию
        
        Returns:
            Финальный отчёт со всеми метаданными
        """
        start_time = datetime.utcnow()
        logger.info(f"Starting Evolution Loop for query: {query[:100]}")
        
        result = {
            "query": query,
            "timestamp": start_time.isoformat(),
            "stages": {}
        }
        
        try:
            # Этап 1: Планирование
            logger.info("Stage 1: Planning")
            plan = await self.agents["planner"].plan(query)
            result["stages"]["planning"] = plan
            
            # Этап 2: Исследование
            logger.info("Stage 2: Research")
            data = await self.agents["researcher"].collect(plan)
            result["stages"]["research"] = data
            
            # Этап 3: Рассуждение
            logger.info("Stage 3: Reasoning")
            reasoning = await self.solver.reason(query, context_data=data)
            result["stages"]["reasoning"] = reasoning
            
            # Этап 4: Проверка
            logger.info("Stage 4: Verification")
            verified = await self.agents["verifier"].check(reasoning)
            result["stages"]["verification"] = verified
            
            # Этап 5: Этическая фильтрация
            logger.info("Stage 5: Ethical Filtering")
            ethical = await self.ethics.filter(verified.get("verified_reasoning", {}))
            result["stages"]["ethical_filtering"] = ethical
            
            # Этап 6: Составление отчёта
            logger.info("Stage 6: Writing")
            report = await self.agents["writer"].compose(ethical.get("filtered_content", verified))
            result["stages"]["writing"] = report
            
            # Этап 7: Критический анализ
            logger.info("Stage 7: Criticism")
            feedback = await self.agents["critic"].analyze(report)
            result["stages"]["criticism"] = feedback
            
            # Этап 8: Обновление метрик
            logger.info("Stage 8: Evaluation")
            self.evaluator.update_metrics(feedback)
            result["stages"]["evaluation"] = self.evaluator.get_metrics()
            
            # Этап 9: Визуализация (опционально)
            if visualize and self.dashboard:
                logger.info("Stage 9: Visualization")
                try:
                    viz_path = await self.dashboard.visualize_reasoning_paths(reasoning)
                    result["visualization"] = str(viz_path)
                except Exception as e:
                    logger.warning(f"Could not create visualization: {e}")
            
            # Финальный результат
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            result["final_report"] = report
            result["duration_seconds"] = duration
            result["success"] = True
            result["system_health"] = self.evaluator.get_system_health()
            
            logger.info(f"Evolution Loop completed in {duration:.2f}s")
        
        except Exception as e:
            logger.error(f"Error in Evolution Loop: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получить статус системы"""
        return {
            "health": self.evaluator.get_system_health(),
            "metrics": self.evaluator.get_metrics(),
            "components": {
                "solver": self.solver is not None,
                "evaluator": self.evaluator is not None,
                "ethics": self.ethics is not None,
                "agents": {name: agent is not None for name, agent in self.agents.items()},
                "visualization": self.dashboard is not None
            }
        }













