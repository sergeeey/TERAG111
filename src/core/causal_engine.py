"""
Causal Engine MVP - What-If анализ и counterfactual симуляции
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j driver not available")


class CausalEngine:
    """
    Causal Engine для What-If анализа
    
    Функции:
    - What-If анализ (что если бы заблокировали клиента N дней назад)
    - Расчет prevented losses
    - Counterfactual симуляции
    """
    
    def __init__(self, neo4j_driver=None):
        """
        Инициализация CausalEngine
        
        Args:
            neo4j_driver: Neo4j driver
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not installed")
        
        self.driver = neo4j_driver
        logger.info("CausalEngine initialized")
    
    def what_if_analysis(
        self,
        query: str,
        client_id: Optional[str] = None,
        days_ago: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Выполнить What-If анализ
        
        Пример: "Что если бы заблокировали клиента ID=123 30 дней назад?"
        
        Args:
            query: Текстовый запрос What-If
            client_id: ID клиента (если указан в query)
            days_ago: Количество дней назад (если указано в query)
        
        Returns:
            Результат What-If анализа
        """
        # Парсим query (простая версия)
        if "заблокировали" in query.lower() or "blocked" in query.lower():
            if client_id and days_ago:
                return self.prevent_ent_losses(client_id, days_ago)
        
        # Общий What-If анализ
        return {
            "query": query,
            "result": "What-If analysis not implemented for this query",
            "impact_usd": 0.0,
            "confidence": 0.0
        }
    
    def prevent_ent_losses(
        self,
        client_id: str,
        days_ago: int
    ) -> Dict[str, Any]:
        """
        Рассчитать предотвращенные потери при блокировке клиента
        
        Args:
            client_id: ID клиента
            days_ago: Количество дней назад
        
        Returns:
            Оценка предотвращенных потерь
        """
        if not self.driver:
            return {
                "client_id": client_id,
                "days_ago": days_ago,
                "prevented_losses_usd": 0.0,
                "fraud_cases_prevented": 0,
                "confidence": 0.0
            }
        
        try:
            with self.driver.session() as session:
                # Находим все fraud cases, связанные с клиентом за последние N дней
                result = session.run("""
                    MATCH (c:Client {id: $client_id})-[r:LINKED_TO]-(case:Case)
                    WHERE case.created_at >= datetime() - duration({days: $days_ago})
                      AND case.fraud_score > 0.7
                    RETURN sum(case.amount) as total_loss, count(case) as case_count
                """, client_id=client_id, days_ago=days_ago)
                
                record = result.single()
                total_loss = record["total_loss"] if record and record["total_loss"] else 0.0
                case_count = record["case_count"] if record else 0
                
                # Рассчитываем confidence на основе количества случаев
                confidence = min(1.0, case_count / 10.0) if case_count > 0 else 0.0
                
                return {
                    "client_id": client_id,
                    "days_ago": days_ago,
                    "prevented_losses_usd": float(total_loss),
                    "fraud_cases_prevented": case_count,
                    "confidence": confidence
                }
        except Exception as e:
            logger.error(f"Failed to calculate prevented losses: {e}")
            return {
                "client_id": client_id,
                "days_ago": days_ago,
                "prevented_losses_usd": 0.0,
                "fraud_cases_prevented": 0,
                "confidence": 0.0,
                "error": str(e)
            }
