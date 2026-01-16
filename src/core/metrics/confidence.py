"""
Confidence metrics для TERAG
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfidenceMetrics:
    """Класс для отслеживания метрик confidence"""
    
    def __init__(self):
        """Инициализация ConfidenceMetrics"""
        self.confidences: List[float] = []
        self.accuracies: List[float] = []
        self.timestamps: List[datetime] = []
        logger.info("ConfidenceMetrics initialized")
    
    def record(
        self,
        confidence: float,
        accuracy: float,
        timestamp: datetime = None
    ):
        """
        Записать confidence и accuracy
        
        Args:
            confidence: Confidence score [0.0, 1.0]
            accuracy: Фактическая accuracy (1.0 если правильно, 0.0 если неправильно)
            timestamp: Время записи (по умолчанию текущее)
        """
        if not (0.0 <= confidence <= 1.0):
            raise ValueError(f"Confidence must be in [0.0, 1.0], got {confidence}")
        
        if accuracy not in [0.0, 1.0]:
            raise ValueError(f"Accuracy must be 0.0 or 1.0, got {accuracy}")
        
        self.confidences.append(confidence)
        self.accuracies.append(accuracy)
        self.timestamps.append(timestamp or datetime.utcnow())
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику confidence
        
        Returns:
            Словарь со статистикой
        """
        if not self.confidences:
            return {
                "count": 0,
                "mean_confidence": 0.0,
                "mean_accuracy": 0.0,
                "ece": 0.0,
                "brier_score": 0.0
            }
        
        from src.core.metrics.ece import calculate_ece, calculate_brier_score
        
        ece = calculate_ece(self.confidences, self.accuracies)
        brier = calculate_brier_score(self.confidences, self.accuracies)
        
        return {
            "count": len(self.confidences),
            "mean_confidence": sum(self.confidences) / len(self.confidences),
            "mean_accuracy": sum(self.accuracies) / len(self.accuracies),
            "ece": ece,
            "brier_score": brier,
            "is_calibrated": ece < 0.1 and brier < 0.05
        }
    
    def clear(self):
        """Очистить все записи"""
        self.confidences.clear()
        self.accuracies.clear()
        self.timestamps.clear()


# Глобальный экземпляр
_confidence_metrics: ConfidenceMetrics = None


def get_confidence_metrics() -> ConfidenceMetrics:
    """Получить глобальный экземпляр ConfidenceMetrics"""
    global _confidence_metrics
    if _confidence_metrics is None:
        _confidence_metrics = ConfidenceMetrics()
    return _confidence_metrics
