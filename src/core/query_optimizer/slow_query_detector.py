"""
Slow Query Detector для парсинга Neo4j logs
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SlowQueryDetector:
    """Детектор slow queries из Neo4j logs"""
    
    def __init__(self, log_path: str = None):
        """
        Инициализация SlowQueryDetector
        
        Args:
            log_path: Путь к Neo4j log файлу (опционально)
        """
        self.log_path = log_path or "/var/log/neo4j/neo4j.log"
        logger.info(f"SlowQueryDetector initialized (log_path={self.log_path})")
    
    def parse_logs(self, threshold_ms: float = 100.0) -> List[Dict[str, Any]]:
        """
        Парсить Neo4j logs для поиска slow queries
        
        Args:
            threshold_ms: Порог для slow queries
        
        Returns:
            Список slow queries
        """
        slow_queries = []
        
        if not Path(self.log_path).exists():
            logger.warning(f"Neo4j log file not found: {self.log_path}")
            return slow_queries
        
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Ищем паттерны slow queries в логах
                    # Формат может варьироваться в зависимости от версии Neo4j
                    match = re.search(r'(\d+\.\d+)ms.*?(MATCH|CREATE|MERGE|DELETE).*', line, re.IGNORECASE)
                    if match:
                        execution_time = float(match.group(1))
                        if execution_time > threshold_ms:
                            query_start = match.end()
                            query = line[query_start:].strip()
                            
                            slow_queries.append({
                                "query": query,
                                "execution_time_ms": execution_time,
                                "timestamp": datetime.utcnow(),  # В production извлекать из лога
                                "source": "neo4j_log"
                            })
        except Exception as e:
            logger.error(f"Failed to parse Neo4j logs: {e}")
        
        return slow_queries
