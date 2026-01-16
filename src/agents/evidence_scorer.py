"""
Evidence Scorer для оценки confidence связей
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EvidenceScorer:
    """
    Scorer для оценки confidence на основе evidence
    
    Использует взвешенную модель для расчета confidence
    """
    
    def __init__(self):
        """Инициализация EvidenceScorer"""
        self.weights = {
            "phone_match": 0.3,
            "address_match": 0.2,
            "fio_match": 0.4,
            "additional_data": 0.1
        }
        logger.info("EvidenceScorer initialized")
    
    def score(
        self,
        case: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> float:
        """
        Рассчитать confidence score для связи
        
        Args:
            case: Данные кейса
            candidate: Данные кандидата (клиента)
        
        Returns:
            Confidence score [0.0, 1.0]
        """
        # Используем те же веса, что и FuzzyMatcher
        from src.agents.fuzzy_matcher import FuzzyMatcher
        
        matcher = FuzzyMatcher()
        score = matcher.calculate_score(case, candidate)
        
        return score
