"""
Query Optimizer module
"""

from src.core.query_optimizer import QueryOptimizer, get_query_optimizer
from src.core.query_optimizer.auto_index import AutoIndexCreator
from src.core.query_optimizer.slow_query_detector import SlowQueryDetector

__all__ = [
    "QueryOptimizer",
    "get_query_optimizer",
    "AutoIndexCreator",
    "SlowQueryDetector",
]
