"""
Query Optimizer для TERAG
Автоматическое обнаружение slow queries и создание индексов
"""

import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j driver not available")


class QueryOptimizer:
    """
    Оптимизатор запросов Neo4j
    
    Функции:
    - Мониторинг slow queries (>100ms)
    - Автоматическое предложение индексов
    - Применение индексов для оптимизации
    """
    
    def __init__(
        self,
        neo4j_driver=None,
        slow_query_threshold_ms: float = 100.0
    ):
        """
        Инициализация Query Optimizer
        
        Args:
            neo4j_driver: Neo4j driver (опционально)
            slow_query_threshold_ms: Порог для slow queries (по умолчанию 100ms)
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not installed")
        
        self.driver = neo4j_driver
        self.slow_query_threshold = slow_query_threshold_ms
        self.slow_queries: List[Dict[str, Any]] = []
        
        logger.info(f"QueryOptimizer initialized (threshold={slow_query_threshold_ms}ms)")
    
    def monitor_queries(self) -> List[Dict[str, Any]]:
        """
        Мониторинг slow queries из Neo4j logs
        
        Returns:
            Список slow queries с метаданными
        """
        # В production это должно парсить Neo4j logs
        # Для MVP возвращаем накопленные slow queries
        return self.slow_queries
    
    def record_slow_query(
        self,
        query: str,
        execution_time_ms: float,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Записать slow query
        
        Args:
            query: Cypher запрос
            execution_time_ms: Время выполнения в миллисекундах
            context: Дополнительный контекст
        """
        if execution_time_ms > self.slow_query_threshold:
            slow_query = {
                "query": query,
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.utcnow(),
                "context": context or {}
            }
            self.slow_queries.append(slow_query)
            
            # Предлагаем индекс
            index_suggestion = self.suggest_index(query)
            if index_suggestion:
                slow_query["suggested_index"] = index_suggestion
            
            logger.warning(
                f"Slow query detected: {execution_time_ms:.2f}ms\n"
                f"Query: {query[:100]}...\n"
                f"Suggested index: {index_suggestion}"
            )
    
    def suggest_index(self, query: str) -> Optional[str]:
        """
        Предложить индекс для Cypher запроса
        
        Анализирует запрос и предлагает CREATE INDEX statement
        
        Args:
            query: Cypher запрос
        
        Returns:
            CREATE INDEX statement или None
        """
        if not query:
            return None
        
        # Паттерны для поиска индексов
        patterns = [
            # WHERE n.property = value
            (r'WHERE\s+(\w+):(\w+)\s*=\s*', r'CREATE INDEX idx_\1_\2 IF NOT EXISTS FOR (n:\1) ON (n.\2)'),
            # MATCH (n:Label) WHERE n.property
            (r'MATCH\s+\((\w+):(\w+)\)\s+WHERE\s+\1\.(\w+)', r'CREATE INDEX idx_\2_\3 IF NOT EXISTS FOR (n:\2) ON (n.\3)'),
            # MATCH (a:Label)-[r:REL]->(b:Label) WHERE a.property
            (r'MATCH\s+\((\w+):(\w+)\)\s+-.*WHERE\s+\1\.(\w+)', r'CREATE INDEX idx_\2_\3 IF NOT EXISTS FOR (n:\2) ON (n.\3)'),
        ]
        
        for pattern, index_template in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                # Извлекаем label и property
                groups = match.groups()
                if len(groups) >= 2:
                    label = groups[1] if len(groups) > 1 else groups[0]
                    property_name = groups[-1]
                    
                    # Генерируем имя индекса
                    index_name = f"idx_{label.lower()}_{property_name.lower()}"
                    
                    # Генерируем CREATE INDEX statement
                    index_cypher = f"CREATE INDEX {index_name} IF NOT EXISTS FOR (n:{label}) ON (n.{property_name})"
                    
                    return index_cypher
        
        return None
    
    def apply_index(self, index_cypher: str) -> bool:
        """
        Применить индекс к Neo4j
        
        Args:
            index_cypher: CREATE INDEX statement
        
        Returns:
            True если успешно применен
        """
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return False
        
        try:
            with self.driver.session() as session:
                result = session.run(index_cypher)
                result.consume()  # Выполняем запрос
                logger.info(f"Index applied: {index_cypher}")
                return True
        except Exception as e:
            logger.error(f"Failed to apply index: {e}")
            return False
    
    def optimize_query(self, query: str) -> Dict[str, Any]:
        """
        Оптимизировать запрос (анализ + предложение индексов)
        
        Args:
            query: Cypher запрос
        
        Returns:
            Словарь с рекомендациями по оптимизации
        """
        suggestions = []
        
        # Предлагаем индекс
        index_suggestion = self.suggest_index(query)
        if index_suggestion:
            suggestions.append({
                "type": "index",
                "suggestion": index_suggestion,
                "description": "Create index to improve query performance"
            })
        
        # Проверяем использование LIMIT
        if "LIMIT" not in query.upper() and "MATCH" in query.upper():
            suggestions.append({
                "type": "limit",
                "suggestion": "Add LIMIT clause to restrict result size",
                "description": "Large result sets can be slow"
            })
        
        return {
            "query": query,
            "suggestions": suggestions,
            "optimization_score": len(suggestions)  # Простая метрика
        }


# Глобальный экземпляр
_query_optimizer: Optional[QueryOptimizer] = None


def get_query_optimizer(neo4j_driver=None) -> QueryOptimizer:
    """Получить глобальный экземпляр QueryOptimizer"""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer(neo4j_driver=neo4j_driver)
    return _query_optimizer
