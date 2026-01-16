"""
KAG-Solver — графовое рассуждение на основе Knowledge-Augmented Graph
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .causal_paths import CausalPathFinder

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


class KAGSolver:
    """
    KAG-Solver — графовое рассуждение
    
    Функции:
    1. Извлекает контекст из графа знаний
    2. Находит причинно-следственные пути
    3. Синтезирует рассуждения на основе найденных путей
    4. Использует LM Studio для финального синтеза
    """
    
    def __init__(
        self,
        graph_driver=None,
        lm_client=None,
        max_hops: int = 3
    ):
        """
        Инициализация KAG-Solver
        
        Args:
            graph_driver: Neo4j driver
            lm_client: LMStudioClient для синтеза
            max_hops: Максимальная глубина поиска в графе
        """
        self.driver = graph_driver
        self.lm_client = lm_client
        self.max_hops = max_hops
        self.path_finder = CausalPathFinder(driver=graph_driver)
        
        logger.info("KAGSolver initialized")
    
    async def reason(
        self,
        query: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Выполнить графовое рассуждение
        
        Args:
            query: Запрос для рассуждения
            context_data: Дополнительный контекст (опционально)
        
        Returns:
            Результат рассуждения с путями и выводами
        """
        logger.info(f"Starting reasoning for query: {query[:100]}")
        
        result = {
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "reasoning_paths": [],
            "causal_chains": [],
            "conclusion": None,
            "confidence": 0.0,
            "context_used": False
        }
        
        # 1. Извлекаем релевантные концепты из запроса
        concepts = await self._extract_concepts(query)
        logger.info(f"Extracted concepts: {concepts}")
        
        if not concepts and not self.driver:
            # Если нет графа, используем только LM Studio
            if self.lm_client:
                result["conclusion"] = await self._simple_reasoning(query)
            return result
        
        # 2. Находим пути в графе для каждого концепта
        all_paths = []
        all_chains = []
        
        for concept in concepts[:5]:  # Ограничиваем для производительности
            # Поиск путей
            paths = self.path_finder.find_paths(
                start_node=concept,
                max_hops=self.max_hops
            )
            all_paths.extend(paths)
            
            # Поиск причинно-следственных цепочек
            chains = self.path_finder.find_causal_chains(
                concept=concept,
                max_depth=self.max_hops
            )
            all_chains.extend(chains)
        
        # 3. Ранжируем пути по релевантности
        ranked_paths = self.path_finder.rank_paths_by_relevance(
            all_paths,
            query_context=query
        )
        
        result["reasoning_paths"] = ranked_paths[:10]  # Топ-10 путей
        result["causal_chains"] = all_chains[:10]  # Топ-10 цепочек
        result["context_used"] = len(ranked_paths) > 0
        
        # 4. Синтезируем вывод на основе найденных путей
        if self.lm_client and ranked_paths:
            result["conclusion"] = await self._synthesize_reasoning(
                query=query,
                paths=ranked_paths,
                chains=all_chains
            )
            result["confidence"] = self._calculate_confidence(ranked_paths, all_chains)
        elif ranked_paths:
            # Простой синтез без LM Studio
            result["conclusion"] = self._simple_synthesis(ranked_paths)
            result["confidence"] = self._calculate_confidence(ranked_paths, all_chains)
        else:
            # Нет путей в графе
            if self.lm_client:
                result["conclusion"] = await self._simple_reasoning(query)
            else:
                result["conclusion"] = "Недостаточно данных в графе знаний для рассуждения."
        
        logger.info(f"Reasoning completed. Confidence: {result['confidence']:.2f}")
        
        return result
    
    async def _extract_concepts(self, query: str) -> List[str]:
        """Извлечь концепты из запроса"""
        if not self.lm_client:
            # Простое извлечение через ключевые слова
            # В реальности можно использовать NER или другие методы
            words = query.split()
            # Фильтруем стоп-слова и возвращаем существительные
            return [w for w in words if len(w) > 3 and w[0].isupper()][:5]
        
        try:
            prompt = f"""Извлеки ключевые концепты из следующего запроса.
Верни только список концептов, разделённых запятыми, без дополнительных объяснений.

Запрос: {query}

Концепты:"""
            
            response = await self.lm_client.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=100
            )
            
            text = response.get("text", "")
            concepts = [c.strip() for c in text.split(",") if c.strip()]
            return concepts[:10]
        
        except Exception as e:
            logger.warning(f"Error extracting concepts: {e}")
            return []
    
    async def _synthesize_reasoning(
        self,
        query: str,
        paths: List[Dict[str, Any]],
        chains: List[Dict[str, Any]]
    ) -> str:
        """Синтезировать рассуждение на основе найденных путей"""
        if not self.lm_client:
            return self._simple_synthesis(paths)
        
        try:
            # Формируем контекст из путей
            paths_text = "\n".join([
                f"Путь {i+1}: {' -> '.join(p.get('nodes', [])[:5])}"
                for i, p in enumerate(paths[:5])
            ])
            
            chains_text = "\n".join([
                f"Цепочка {i+1}: {' -> '.join(c.get('path', [])[:5])}"
                for i, c in enumerate(chains[:5])
            ])
            
            prompt = f"""На основе следующего запроса и найденных связей в графе знаний, сформулируй вывод.

Запрос: {query}

Найденные пути в графе:
{paths_text}

Причинно-следственные цепочки:
{chains_text}

Сформулируй краткий вывод (2-3 предложения), основанный на этих связях:"""
            
            response = await self.lm_client.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=300
            )
            
            return response.get("text", "").strip()
        
        except Exception as e:
            logger.error(f"Error synthesizing reasoning: {e}")
            return self._simple_synthesis(paths)
    
    def _simple_synthesis(self, paths: List[Dict[str, Any]]) -> str:
        """Простой синтез без LM Studio"""
        if not paths:
            return "Не найдено связей в графе знаний."
        
        top_path = paths[0]
        nodes = top_path.get("nodes", [])
        
        if len(nodes) >= 2:
            return f"Найдена связь между {nodes[0]} и {nodes[-1]} через граф знаний."
        else:
            return f"Найден концепт {nodes[0]} в графе знаний."
    
    async def _simple_reasoning(self, query: str) -> str:
        """Простое рассуждение без графа"""
        if not self.lm_client:
            return "Недостаточно данных для рассуждения."
        
        try:
            response = await self.lm_client.generate(
                prompt=f"Ответь на вопрос: {query}",
                temperature=0.7,
                max_tokens=300
            )
            return response.get("text", "").strip()
        except Exception as e:
            logger.error(f"Error in simple reasoning: {e}")
            return "Ошибка при выполнении рассуждения."
    
    def _calculate_confidence(
        self,
        paths: List[Dict[str, Any]],
        chains: List[Dict[str, Any]]
    ) -> float:
        """Вычислить уверенность в результате с калибровкой"""
        if not paths and not chains:
            return 0.0
        
        # Базовая уверенность зависит от количества найденных путей
        path_score = min(len(paths) / 10.0, 1.0)  # Нормализуем до 1.0
        chain_score = min(len(chains) / 5.0, 1.0)  # Нормализуем до 1.0
        
        # Среднее значение
        raw_confidence = (path_score + chain_score) / 2.0
        
        # Учитываем длину путей (более короткие пути = выше уверенность)
        if paths:
            avg_length = sum(p.get("length", 0) for p in paths) / len(paths)
            length_factor = 1.0 / (avg_length + 1)
            raw_confidence = (raw_confidence + length_factor) / 2.0
        
        raw_confidence = min(raw_confidence, 1.0)
        
        # Применяем калибровку если доступна
        try:
            from src.core.confidence_calibration import get_calibrator
            calibrator = get_calibrator()
            calibrated_confidence = calibrator.get_calibrated_confidence(raw_confidence)
            return calibrated_confidence
        except Exception as e:
            logger.debug(f"Calibration not available: {e}")
            return raw_confidence













