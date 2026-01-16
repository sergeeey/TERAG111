"""
Confidence Calibration для TERAG
Калибровка confidence scores для достижения ECE <0.1
"""

import logging
from typing import List, Optional
import numpy as np
from sklearn.isotonic import IsotonicRegression

from src.core.metrics.ece import calculate_ece, calculate_brier_score
from src.core.metrics.confidence import get_confidence_metrics

logger = logging.getLogger(__name__)


class ConfidenceCalibrator:
    """
    Калибровщик confidence scores
    
    Использует Isotonic Regression для калибровки confidence scores
    на основе исторических данных (confidence, accuracy pairs)
    """
    
    def __init__(self):
        """Инициализация ConfidenceCalibrator"""
        self.calibrator: Optional[IsotonicRegression] = None
        self.is_calibrated = False
        self.metrics = get_confidence_metrics()
        logger.info("ConfidenceCalibrator initialized")
    
    def calibrate(self, confidences: List[float], accuracies: List[float]) -> bool:
        """
        Обучить калибровщик на исторических данных
        
        Args:
            confidences: Список confidence scores [0.0, 1.0]
            accuracies: Список фактических accuracy (1.0 если правильно, 0.0 если неправильно)
        
        Returns:
            True если калибровка успешна
        """
        if len(confidences) != len(accuracies):
            raise ValueError("confidences and accuracies must have the same length")
        
        if len(confidences) < 10:
            logger.warning("Not enough data for calibration (need at least 10 samples)")
            return False
        
        try:
            # Обучаем Isotonic Regression
            self.calibrator = IsotonicRegression(out_of_bounds='clip')
            self.calibrator.fit(confidences, accuracies)
            
            # Проверяем качество калибровки
            calibrated_confidences = self.calibrator.predict(confidences)
            ece = calculate_ece(calibrated_confidences, accuracies)
            brier = calculate_brier_score(calibrated_confidences, accuracies)
            
            self.is_calibrated = ece < 0.1 and brier < 0.05
            
            logger.info(
                f"Calibration completed: ECE={ece:.4f}, Brier={brier:.4f}, "
                f"calibrated={self.is_calibrated}"
            )
            
            return self.is_calibrated
        
        except Exception as e:
            logger.error(f"Failed to calibrate: {e}")
            return False
    
    def get_calibrated_confidence(self, raw_confidence: float) -> float:
        """
        Получить калиброванный confidence score
        
        Args:
            raw_confidence: Исходный confidence score [0.0, 1.0]
        
        Returns:
            Калиброванный confidence score [0.0, 1.0]
        """
        if not self.is_calibrated or self.calibrator is None:
            # Если не калиброван, возвращаем исходный
            return raw_confidence
        
        try:
            calibrated = self.calibrator.predict([raw_confidence])[0]
            # Ограничиваем [0.0, 1.0]
            return max(0.0, min(1.0, calibrated))
        except Exception as e:
            logger.warning(f"Failed to calibrate confidence: {e}")
            return raw_confidence
    
    def calculate_ece(self, confidences: List[float], accuracies: List[float]) -> float:
        """
        Рассчитать ECE для данных
        
        Args:
            confidences: Список confidence scores
            accuracies: Список фактических accuracy
        
        Returns:
            ECE значение
        """
        return calculate_ece(confidences, accuracies)
    
    def auto_calibrate_from_metrics(self) -> bool:
        """
        Автоматическая калибровка на основе накопленных метрик
        
        Returns:
            True если калибровка успешна
        """
        stats = self.metrics.get_stats()
        
        if stats["count"] < 10:
            logger.warning(f"Not enough metrics for calibration: {stats['count']}")
            return False
        
        return self.calibrate(self.metrics.confidences, self.metrics.accuracies)


# Глобальный экземпляр
_calibrator: Optional[ConfidenceCalibrator] = None


def get_calibrator() -> ConfidenceCalibrator:
    """Получить глобальный экземпляр ConfidenceCalibrator"""
    global _calibrator
    if _calibrator is None:
        _calibrator = ConfidenceCalibrator()
    return _calibrator
