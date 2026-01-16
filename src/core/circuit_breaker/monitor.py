"""
Мониторинг Circuit Breaker
"""

import logging
from typing import Dict, Any
from src.core.circuit_breaker import get_neo4j_circuit_breaker

logger = logging.getLogger(__name__)


class CircuitBreakerMonitor:
    """Монитор для отслеживания состояния Circuit Breaker"""
    
    def __init__(self):
        """Инициализация монитора"""
        self.breaker = get_neo4j_circuit_breaker()
        logger.info("CircuitBreakerMonitor initialized")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Получить метрики Circuit Breaker
        
        Returns:
            Словарь с метриками
        """
        state = self.breaker.get_state()
        
        return {
            "circuit_breaker_state": state["state"],
            "circuit_breaker_failures": state["failure_count"],
            "circuit_breaker_successes": state["success_count"],
            "circuit_breaker_last_failure": state["last_failure_time"],
            "circuit_breaker_last_success": state["last_success_time"]
        }
    
    def is_healthy(self) -> bool:
        """
        Проверить, здоров ли Circuit Breaker
        
        Returns:
            True если circuit закрыт (здоров)
        """
        return self.breaker.state.value == "CLOSED"
    
    def get_status(self) -> str:
        """
        Получить текстовый статус
        
        Returns:
            Статус Circuit Breaker
        """
        state = self.breaker.get_state()
        if state["state"] == "CLOSED":
            return "healthy"
        elif state["state"] == "OPEN":
            return "unhealthy"
        else:
            return "recovering"
