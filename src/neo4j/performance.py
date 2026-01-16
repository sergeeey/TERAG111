"""
Performance monitoring для Neo4j
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j driver not available")


class Neo4jPerformanceMonitor:
    """Монитор производительности Neo4j"""
    
    def __init__(self, driver=None):
        """
        Инициализация Neo4jPerformanceMonitor
        
        Args:
            driver: Neo4j driver (опционально)
        """
        self.driver = driver
        logger.info("Neo4jPerformanceMonitor initialized")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Получить метрики производительности Neo4j
        
        Returns:
            Словарь с метриками
        """
        if not self.driver:
            return {"error": "Neo4j driver not available"}
        
        try:
            with self.driver.session() as session:
                # Получаем информацию о базе данных
                result = session.run("CALL db.stats.retrieve('GRAPH COUNTS')")
                stats = {}
                for record in result:
                    stats.update(record.data())
                
                # Получаем информацию о индексах
                index_result = session.run("SHOW INDEXES")
                indexes = [record.data() for record in index_result]
                
                return {
                    "database_stats": stats,
                    "indexes_count": len(indexes),
                    "indexes": indexes,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}
