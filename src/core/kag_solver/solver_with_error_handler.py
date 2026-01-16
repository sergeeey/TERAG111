"""
Пример интеграции TeragErrorHandler в KAG Solver
Это демонстрационный файл, показывающий как интегрировать error handler
"""

import logging
from typing import Dict, Any, Optional
from src.core.error_handler import TeragErrorHandler

logger = logging.getLogger(__name__)


def solve_with_error_handler(
    query: str,
    error_handler: Optional[TeragErrorHandler] = None
) -> Dict[str, Any]:
    """
    Решение запроса с использованием error handler
    
    Args:
        query: Запрос для решения
        error_handler: Экземпляр TeragErrorHandler (создается автоматически если не передан)
        
    Returns:
        Результат решения
    """
    if error_handler is None:
        error_handler = TeragErrorHandler()
    
    context = {
        "query": query,
        "module": "kag_solver",
        "operation": "solve"
    }
    
    try:
        # Используем error handler для выполнения операций с Neo4j
        with error_handler.handle_errors(context) as session:
            # Выполняем запрос к Neo4j
            result = session.run(
                "MATCH (n) RETURN count(n) as total",
                {}
            )
            
            total = result.single()["total"]
            
            return {
                "status": "success",
                "query": query,
                "result": {
                    "total_nodes": total
                }
            }
    except Exception as e:
        logger.error(f"Error in solve_with_error_handler: {e}")
        return {
            "status": "error",
            "query": query,
            "error": str(e)
        }
