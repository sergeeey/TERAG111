"""
Auto Index Creator для автоматического создания индексов
"""

import logging
from typing import List, Optional
from src.core.query_optimizer import QueryOptimizer

logger = logging.getLogger(__name__)


class AutoIndexCreator:
    """Автоматическое создание индексов на основе slow queries"""
    
    def __init__(self, query_optimizer: QueryOptimizer):
        """
        Инициализация AutoIndexCreator
        
        Args:
            query_optimizer: QueryOptimizer экземпляр
        """
        self.optimizer = query_optimizer
        self.created_indexes: List[str] = []
        logger.info("AutoIndexCreator initialized")
    
    def process_slow_queries(self, dry_run: bool = True) -> List[str]:
        """
        Обработать slow queries и создать индексы
        
        Args:
            dry_run: Если True, только предлагает индексы без создания
        
        Returns:
            Список созданных/предложенных индексов
        """
        slow_queries = self.optimizer.monitor_queries()
        suggested_indexes = []
        
        for slow_query in slow_queries:
            query = slow_query.get("query", "")
            suggested_index = self.optimizer.suggest_index(query)
            
            if suggested_index and suggested_index not in self.created_indexes:
                if not dry_run:
                    # Применяем индекс
                    if self.optimizer.apply_index(suggested_index):
                        self.created_indexes.append(suggested_index)
                        suggested_indexes.append(suggested_index)
                else:
                    # Только предлагаем
                    suggested_indexes.append(suggested_index)
        
        logger.info(f"Processed {len(slow_queries)} slow queries, suggested {len(suggested_indexes)} indexes")
        return suggested_indexes
