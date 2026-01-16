"""
Critic Agent — критический анализ результатов
"""
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from src.integration.lmstudio_client import LMStudioClient
    LMSTUDIO_AVAILABLE = True
except ImportError:
    LMSTUDIO_AVAILABLE = False
    logger.warning("LMStudioClient not available")


class Critic:
    """
    Critic Agent — критически анализирует результаты
    
    Функции:
    1. Оценивает качество рассуждения
    2. Выявляет слабые места
    3. Предлагает улучшения
    4. Формирует обратную связь для Auto-Evaluator
    """
    
    def __init__(self, lm_client=None):
        """
        Инициализация Critic
        
        Args:
            lm_client: LMStudioClient для анализа
        """
        self.lm_client = lm_client
        logger.info("Critic agent initialized")
    
    async def analyze(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проанализировать отчёт
        
        Args:
            report: Отчёт от Writer
        
        Returns:
            Обратная связь для Auto-Evaluator
        """
        logger.info("Analyzing report")
        
        feedback = {
            "timestamp": datetime.utcnow().isoformat(),
            "accuracy_score": 0.0,
            "confidence": report.get("confidence", 0.0),
            "reasoning_quality": 0.0,
            "ethical_violations": 0,
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "response_time": 0.0  # Будет заполнено из метаданных
        }
        
        # Оценка качества на основе метаданных
        paths_count = report.get("metadata", {}).get("reasoning_paths_count", 0)
        context_used = report.get("metadata", {}).get("context_used", False)
        warnings_count = len(report.get("warnings", []))
        issues_count = len(report.get("issues", []))
        
        # Оценка точности
        if context_used and paths_count > 0:
            feedback["accuracy_score"] = min(0.5 + (paths_count / 10.0), 1.0)
        else:
            feedback["accuracy_score"] = 0.3
        
        # Штрафы за предупреждения и проблемы
        feedback["accuracy_score"] *= (1.0 - warnings_count * 0.1)
        feedback["accuracy_score"] *= (1.0 - issues_count * 0.2)
        feedback["accuracy_score"] = max(0.0, feedback["accuracy_score"])
        
        # Оценка качества рассуждения
        feedback["reasoning_quality"] = (
            feedback["accuracy_score"] * 0.4 +
            feedback["confidence"] * 0.3 +
            (1.0 if context_used else 0.3) * 0.3
        )
        
        # Определение сильных и слабых сторон
        if paths_count > 5:
            feedback["strengths"].append("Использовано много путей в графе")
        if context_used:
            feedback["strengths"].append("Использован контекст из графа")
        if feedback["confidence"] > 0.7:
            feedback["strengths"].append("Высокая уверенность")
        
        if paths_count == 0:
            feedback["weaknesses"].append("Не использованы пути в графе")
        if not context_used:
            feedback["weaknesses"].append("Не использован контекст")
        if warnings_count > 0:
            feedback["weaknesses"].append(f"Обнаружено {warnings_count} предупреждений")
        if issues_count > 0:
            feedback["weaknesses"].append(f"Обнаружено {issues_count} проблем")
        
        # Рекомендации
        if paths_count < 3:
            feedback["recommendations"].append("Расширить граф знаний для лучших результатов")
        if not context_used:
            feedback["recommendations"].append("Улучшить извлечение контекста из графа")
        if feedback["confidence"] < 0.5:
            feedback["recommendations"].append("Повысить уверенность через улучшение качества данных")
        
        # Анализ через LM Studio (опционально)
        if self.lm_client and report.get("conclusion"):
            try:
                lm_feedback = await self._lm_analysis(report)
                if lm_feedback:
                    feedback["lm_analysis"] = lm_feedback
            except Exception as e:
                logger.debug(f"Could not perform LM analysis: {e}")
        
        logger.info(f"Analysis completed: accuracy={feedback['accuracy_score']:.2f}, quality={feedback['reasoning_quality']:.2f}")
        
        return feedback
    
    async def _lm_analysis(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ через LM Studio"""
        if not self.lm_client:
            return None
        
        try:
            prompt = f"""Проанализируй следующий отчёт и оцени его качество.

Отчёт:
{report.get('conclusion', '')}

Уверенность: {report.get('confidence', 0.0):.2f}
Предупреждения: {len(report.get('warnings', []))}
Проблемы: {len(report.get('issues', []))}

Оцени качество отчёта (1-10) и дай краткую оценку:"""
            
            response = await self.lm_client.generate(
                prompt=prompt,
                temperature=0.5,
                max_tokens=150
            )
            
            return {
                "lm_rating": response.get("text", "").strip(),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.debug(f"Error in LM analysis: {e}")
            return None













