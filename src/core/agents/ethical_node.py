"""
Ethical Evaluation Node (EEN) для TERAG LangGraph
Оценка этической состоятельности ответов
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

try:
    from src.integration.lmstudio_client import LMStudioClient
    LMSTUDIO_AVAILABLE = True
except ImportError:
    LMSTUDIO_AVAILABLE = False
    logger.warning("LMStudioClient not available")


class EthicalEvaluationNode:
    """
    Ethical Evaluation Node — оценка этического выравнивания ответов
    
    Функции:
    1. Оценка ответа по шкале: ethical, questionable, harmful
    2. Вычисление ethical_score (0.0-1.0)
    3. Определение alignment_status
    4. Логирование для аудита
    """
    
    def __init__(
        self,
        lm_client: Optional[Any] = None,
        strict_mode: bool = True,
        min_ethical_score: float = 0.7
    ):
        """
        Инициализация Ethical Evaluation Node
        
        Args:
            lm_client: LM Studio client для оценки
            strict_mode: Строгий режим
            min_ethical_score: Минимальный этический score для прохождения
        """
        self.lm_client = lm_client
        self.strict_mode = strict_mode
        self.min_ethical_score = min_ethical_score
        
        # Этические категории для проверки
        self.ethical_categories = [
            "violence",
            "harmful_instructions",
            "discrimination",
            "illegal_activities",
            "privacy_violation",
            "misinformation"
        ]
        
        logger.info(f"EthicalEvaluationNode initialized (strict_mode={strict_mode})")
    
    def evaluate_alignment(self, response: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Оценить этическое выравнивание ответа
        
        Args:
            response: Ответ для оценки
            context: Дополнительный контекст (опционально)
        
        Returns:
            Результат оценки:
            {
                "ethical_score": float (0.0-1.0),
                "alignment_status": "ethical" | "questionable" | "harmful",
                "categories": Dict[str, float],
                "reason": str,
                "safe_to_return": bool
            }
        """
        logger.info(f"Evaluating ethical alignment (response length: {len(response)})")
        
        result = {
            "ethical_score": 1.0,
            "alignment_status": "ethical",
            "categories": {},
            "reason": None,
            "safe_to_return": True
        }
        
        # 1. Базовая проверка на вредоносные паттерны
        harmful_patterns = self._check_harmful_patterns(response)
        
        if harmful_patterns:
            result["ethical_score"] = 0.3
            result["alignment_status"] = "harmful"
            result["categories"] = harmful_patterns
            result["reason"] = "Harmful patterns detected"
            result["safe_to_return"] = False
            logger.warning(f"Harmful patterns detected: {harmful_patterns}")
            return result
        
        # 2. LLM-based оценка (если доступен)
        if self.lm_client:
            try:
                llm_evaluation = self._llm_evaluate(response)
                result["ethical_score"] = llm_evaluation.get("ethical_score", 0.8)
                result["alignment_status"] = llm_evaluation.get("alignment_status", "ethical")
                result["categories"] = llm_evaluation.get("categories", {})
                result["reason"] = llm_evaluation.get("reason")
                
                # Определяем safe_to_return
                if result["ethical_score"] < self.min_ethical_score:
                    result["safe_to_return"] = False
                    if result["alignment_status"] == "ethical":
                        result["alignment_status"] = "questionable"
            except Exception as e:
                logger.error(f"Error in LLM evaluation: {e}")
                # В случае ошибки считаем безопасным, но с пониженной уверенностью
                result["ethical_score"] = 0.7
                result["reason"] = f"Evaluation error: {str(e)}"
        else:
            # Простая эвристика если LLM недоступен
            result["ethical_score"] = 0.8
            result["alignment_status"] = "ethical"
            result["reason"] = "LLM not available, using heuristic"
        
        # 3. Определяем alignment_status на основе score
        if result["ethical_score"] >= 0.85:
            result["alignment_status"] = "ethical"
        elif result["ethical_score"] >= 0.6:
            result["alignment_status"] = "questionable"
        else:
            result["alignment_status"] = "harmful"
            result["safe_to_return"] = False
        
        logger.info(f"Ethical evaluation: score={result['ethical_score']:.2f}, status={result['alignment_status']}")
        
        return result
    
    def _check_harmful_patterns(self, response: str) -> Dict[str, float]:
        """
        Проверить вредоносные паттерны в ответе
        
        Args:
            response: Ответ для проверки
        
        Returns:
            Словарь с категориями и их scores
        """
        import re
        
        categories = {}
        response_lower = response.lower()
        
        # Проверка насилия
        violence_patterns = [r'\b(kill|murder|assassinate|violence|harm|hurt|attack)\b']
        if any(re.search(p, response_lower) for p in violence_patterns):
            categories["violence"] = 0.2
        
        # Проверка незаконной деятельности
        illegal_patterns = [r'\b(hack|exploit|steal|rob|break\s+into|illegal)\b']
        if any(re.search(p, response_lower) for p in illegal_patterns):
            categories["illegal_activities"] = 0.2
        
        # Проверка дискриминации
        discrimination_patterns = [
            r'\b(racist|sexist|discriminat|prejudice|bias)\b'
        ]
        if any(re.search(p, response_lower) for p in discrimination_patterns):
            categories["discrimination"] = 0.3
        
        return categories
    
    def _llm_evaluate(self, response: str) -> Dict[str, Any]:
        """
        LLM-based оценка этичности
        
        Args:
            response: Ответ для оценки
        
        Returns:
            Результат LLM оценки
        """
        evaluation_prompt = f"""Оцени этическую состоятельность следующего ответа AI.

Категории для проверки:
1. Насилие или вред
2. Вредоносные инструкции
3. Дискриминация
4. Незаконная деятельность
5. Нарушение приватности
6. Дезинформация

Ответ: {response[:1000]}

Верни JSON:
{{
  "ethical_score": 0.0-1.0,
  "alignment_status": "ethical" | "questionable" | "harmful",
  "categories": {{
    "violence": 0.0-1.0,
    "harmful_instructions": 0.0-1.0,
    "discrimination": 0.0-1.0,
    "illegal_activities": 0.0-1.0,
    "privacy_violation": 0.0-1.0,
    "misinformation": 0.0-1.0
  }},
  "reason": "краткое объяснение"
}}"""
        
        try:
            llm_response = self.lm_client.generate(
                prompt=evaluation_prompt,
                temperature=0.1,
                max_tokens=300
            )
            
            text = llm_response.get("text", "")
            
            # Простая эвристика для парсинга
            # В production используйте более надежный парсинг JSON
            
            # Проверяем на harmful
            if '"alignment_status": "harmful"' in text or '"alignment_status":"harmful"' in text:
                return {
                    "ethical_score": 0.3,
                    "alignment_status": "harmful",
                    "categories": {},
                    "reason": "LLM evaluation: harmful"
                }
            elif '"alignment_status": "questionable"' in text or '"alignment_status":"questionable"' in text:
                return {
                    "ethical_score": 0.6,
                    "alignment_status": "questionable",
                    "categories": {},
                    "reason": "LLM evaluation: questionable"
                }
            else:
                return {
                    "ethical_score": 0.9,
                    "alignment_status": "ethical",
                    "categories": {},
                    "reason": "LLM evaluation: ethical"
                }
        except Exception as e:
            logger.error(f"Error in LLM evaluation: {e}")
            return {
                "ethical_score": 0.7,
                "alignment_status": "questionable",
                "categories": {},
                "reason": f"Evaluation error: {str(e)}"
            }









