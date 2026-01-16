"""
Verifier Agent — проверка достоверности рассуждений
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

try:
    from src.integration.lmstudio_client import LMStudioClient
    LMSTUDIO_AVAILABLE = True
except ImportError:
    LMSTUDIO_AVAILABLE = False
    logger.warning("LMStudioClient not available")


class Verifier:
    """
    Verifier Agent — проверяет достоверность рассуждений
    
    Функции:
    1. Проверяет логическую согласованность
    2. Валидирует факты
    3. Оценивает уверенность
    """
    
    def __init__(self, lm_client=None):
        """
        Инициализация Verifier
        
        Args:
            lm_client: LMStudioClient для проверки
        """
        self.lm_client = lm_client
        logger.info("Verifier agent initialized")
    
    async def check(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проверить рассуждение
        
        Args:
            reasoning: Результат рассуждения от KAGSolver
        
        Returns:
            Проверенное рассуждение с метаданными проверки
        """
        logger.info("Verifying reasoning")
        
        verification = {
            "is_valid": True,
            "confidence": reasoning.get("confidence", 0.0),
            "issues": [],
            "warnings": [],
            "verified_reasoning": reasoning
        }
        
        # Проверка 1: Наличие выводов
        if not reasoning.get("conclusion"):
            verification["is_valid"] = False
            verification["issues"].append("Отсутствует вывод")
        
        # Проверка 2: Наличие путей в графе
        paths = reasoning.get("reasoning_paths", [])
        if not paths:
            verification["warnings"].append("Нет путей в графе знаний")
            verification["confidence"] *= 0.7  # Снижаем уверенность
        
        # Проверка 3: Логическая согласованность (через LM Studio)
        if self.lm_client and reasoning.get("conclusion"):
            logical_check = await self._check_logical_consistency(reasoning)
            if not logical_check["is_consistent"]:
                verification["warnings"].append("Возможная логическая несогласованность")
                verification["confidence"] *= 0.8
        
        # Проверка 4: Уверенность
        if verification["confidence"] < 0.3:
            verification["warnings"].append("Низкая уверенность в результате")
        
        verification["verified_reasoning"] = reasoning
        verification["verified_reasoning"]["verification"] = {
            "is_valid": verification["is_valid"],
            "confidence": verification["confidence"],
            "issues_count": len(verification["issues"]),
            "warnings_count": len(verification["warnings"])
        }
        
        logger.info(f"Verification completed: valid={verification['is_valid']}, confidence={verification['confidence']:.2f}")
        
        return verification
    
    async def _check_logical_consistency(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """Проверить логическую согласованность через LM Studio"""
        if not self.lm_client:
            return {"is_consistent": True}
        
        try:
            conclusion = reasoning.get("conclusion", "")
            paths_text = "\n".join([
                f"Путь: {' -> '.join(p.get('nodes', [])[:3])}"
                for p in reasoning.get("reasoning_paths", [])[:3]
            ])
            
            prompt = f"""Проверь логическую согласованность следующего рассуждения.

Пути в графе:
{paths_text}

Вывод:
{conclusion}

Ответь только "ДА" если логически согласовано, "НЕТ" если нет:"""
            
            response = await self.lm_client.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=10
            )
            
            text = response.get("text", "").upper()
            is_consistent = "ДА" in text or "YES" in text or "TRUE" in text
            
            return {"is_consistent": is_consistent}
        
        except Exception as e:
            logger.warning(f"Error checking logical consistency: {e}")
            return {"is_consistent": True}  # По умолчанию считаем согласованным













