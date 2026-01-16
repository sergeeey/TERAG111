"""
Auto-Evaluator — автоматическая самооценка и адаптация системы
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class AutoEvaluator:
    """
    Auto-Evaluator — автоматическая самооценка TERAG
    
    Отслеживает метрики:
    - accuracy_score: Точность рассуждений
    - confidence: Уверенность системы
    - staleness: Устаревание данных
    - ethical_violation_rate: Частота этических нарушений
    - trust: Общий уровень доверия к системе
    """
    
    def __init__(self, history_size: int = 100):
        """
        Инициализация Auto-Evaluator
        
        Args:
            history_size: Размер истории для анализа
        """
        self.metrics = {
            "accuracy": 0.0,
            "confidence": 0.0,
            "staleness": 0.0,
            "ethical_violation_rate": 0.0,
            "trust": 1.0,
            "reasoning_quality": 0.0,
            "response_time": 0.0
        }
        
        # История для анализа трендов
        self.history = deque(maxlen=history_size)
        self.feedback_history = deque(maxlen=history_size)
        
        logger.info("AutoEvaluator initialized")
    
    def update_metrics(self, feedback: Dict[str, Any]):
        """
        Обновить метрики на основе обратной связи
        
        Args:
            feedback: Словарь с обратной связью от Critic или пользователя
        """
        timestamp = datetime.utcnow()
        
        # Сохраняем обратную связь
        feedback_record = {
            "timestamp": timestamp.isoformat(),
            "feedback": feedback
        }
        self.feedback_history.append(feedback_record)
        
        # Обновляем метрики
        accuracy = feedback.get("accuracy_score", self.metrics["accuracy"])
        confidence = feedback.get("confidence", self.metrics["confidence"])
        ethical_violations = feedback.get("ethical_violations", 0)
        reasoning_quality = feedback.get("reasoning_quality", self.metrics["reasoning_quality"])
        response_time = feedback.get("response_time", self.metrics["response_time"])
        
        # Экспоненциальное скользящее среднее для плавного обновления
        alpha = 0.1  # Коэффициент сглаживания
        
        self.metrics["accuracy"] = alpha * accuracy + (1 - alpha) * self.metrics["accuracy"]
        self.metrics["confidence"] = alpha * confidence + (1 - alpha) * self.metrics["confidence"]
        self.metrics["reasoning_quality"] = alpha * reasoning_quality + (1 - alpha) * self.metrics["reasoning_quality"]
        self.metrics["response_time"] = alpha * response_time + (1 - alpha) * self.metrics["response_time"]
        
        # Обновляем частоту этических нарушений
        if ethical_violations > 0:
            violation_rate = ethical_violations / max(len(self.feedback_history), 1)
            self.metrics["ethical_violation_rate"] = alpha * violation_rate + (1 - alpha) * self.metrics["ethical_violation_rate"]
        
        # Вычисляем общий уровень доверия
        self.metrics["trust"] = self._calculate_trust()
        
        # Сохраняем метрики в историю
        metrics_record = {
            "timestamp": timestamp.isoformat(),
            "metrics": self.metrics.copy()
        }
        self.history.append(metrics_record)
        
        logger.debug(f"Metrics updated: accuracy={self.metrics['accuracy']:.2f}, trust={self.metrics['trust']:.2f}")
    
    def _calculate_trust(self) -> float:
        """Вычислить общий уровень доверия"""
        # Trust = weighted average of accuracy, confidence, and ethical compliance
        accuracy_weight = 0.4
        confidence_weight = 0.3
        ethical_weight = 0.3
        
        ethical_score = 1.0 - min(self.metrics["ethical_violation_rate"], 1.0)
        
        trust = (
            accuracy_weight * self.metrics["accuracy"] +
            confidence_weight * self.metrics["confidence"] +
            ethical_weight * ethical_score
        )
        
        return max(0.0, min(1.0, trust))
    
    def get_metrics(self) -> Dict[str, Any]:
        """Получить текущие метрики"""
        return self.metrics.copy()
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Получить историю метрик за последние N часов
        
        Args:
            hours: Количество часов истории
        
        Returns:
            Список записей метрик
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            record for record in self.history
            if datetime.fromisoformat(record["timestamp"]) >= cutoff
        ]
    
    def evaluate_reasoning_quality(
        self,
        reasoning_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Оценить качество рассуждения
        
        Args:
            reasoning_result: Результат рассуждения от KAGSolver
        
        Returns:
            Оценка качества
        """
        quality_score = 0.0
        factors = {}
        
        # Фактор 1: Наличие путей в графе
        paths_count = len(reasoning_result.get("reasoning_paths", []))
        paths_factor = min(paths_count / 5.0, 1.0)
        factors["paths_available"] = paths_factor
        
        # Фактор 2: Уверенность
        confidence = reasoning_result.get("confidence", 0.0)
        factors["confidence"] = confidence
        
        # Фактор 3: Наличие вывода
        has_conclusion = bool(reasoning_result.get("conclusion"))
        factors["has_conclusion"] = 1.0 if has_conclusion else 0.0
        
        # Фактор 4: Использование контекста
        context_used = reasoning_result.get("context_used", False)
        factors["context_used"] = 1.0 if context_used else 0.5
        
        # Взвешенная сумма
        quality_score = (
            0.3 * paths_factor +
            0.3 * confidence +
            0.2 * factors["has_conclusion"] +
            0.2 * factors["context_used"]
        )
        
        return {
            "quality_score": quality_score,
            "factors": factors,
            "recommendation": self._get_recommendation(quality_score)
        }
    
    def _get_recommendation(self, quality_score: float) -> str:
        """Получить рекомендацию на основе оценки качества"""
        if quality_score >= 0.8:
            return "excellent"
        elif quality_score >= 0.6:
            return "good"
        elif quality_score >= 0.4:
            return "fair"
        else:
            return "needs_improvement"
    
    def should_retry_reasoning(self, reasoning_result: Dict[str, Any]) -> bool:
        """
        Определить, нужно ли повторить рассуждение
        
        Args:
            reasoning_result: Результат рассуждения
        
        Returns:
            True если нужно повторить
        """
        quality = self.evaluate_reasoning_quality(reasoning_result)
        
        # Повторяем, если качество низкое и уверенность низкая
        if quality["quality_score"] < 0.4 and reasoning_result.get("confidence", 0.0) < 0.5:
            return True
        
        return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Получить общее состояние системы
        
        Returns:
            Словарь с оценкой здоровья системы
        """
        trust = self.metrics["trust"]
        accuracy = self.metrics["accuracy"]
        ethical_rate = self.metrics["ethical_violation_rate"]
        
        # Определяем статус здоровья
        if trust >= 0.8 and ethical_rate < 0.1:
            health_status = "healthy"
        elif trust >= 0.6 and ethical_rate < 0.2:
            health_status = "good"
        elif trust >= 0.4:
            health_status = "fair"
        else:
            health_status = "degraded"
        
        return {
            "status": health_status,
            "trust": trust,
            "accuracy": accuracy,
            "ethical_violation_rate": ethical_rate,
            "metrics": self.metrics.copy(),
            "recommendations": self._get_health_recommendations()
        }
    
    def _get_health_recommendations(self) -> List[str]:
        """Получить рекомендации по улучшению здоровья системы"""
        recommendations = []
        
        if self.metrics["accuracy"] < 0.6:
            recommendations.append("Улучшить точность рассуждений через расширение графа знаний")
        
        if self.metrics["ethical_violation_rate"] > 0.1:
            recommendations.append("Усилить этическую фильтрацию")
        
        if self.metrics["confidence"] < 0.5:
            recommendations.append("Повысить уверенность через улучшение качества данных")
        
        if self.metrics["staleness"] > 0.5:
            recommendations.append("Обновить устаревшие данные в графе")
        
        return recommendations

