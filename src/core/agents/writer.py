"""
Writer Agent — составление отчётов
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


class Writer:
    """
    Writer Agent — составляет финальный отчёт
    
    Функции:
    1. Форматирует результаты рассуждения
    2. Создаёт структурированный отчёт
    3. Добавляет метаданные
    """
    
    def __init__(self, lm_client=None):
        """
        Инициализация Writer
        
        Args:
            lm_client: LMStudioClient для улучшения текста
        """
        self.lm_client = lm_client
        logger.info("Writer agent initialized")
    
    async def compose(self, verified: Dict[str, Any]) -> Dict[str, Any]:
        """
        Составить отчёт
        
        Args:
            verified: Проверенное рассуждение от Verifier
        
        Returns:
            Финальный отчёт
        """
        logger.info("Composing report")
        
        reasoning = verified.get("verified_reasoning", {})
        verification = verified.get("verification", {})
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": reasoning.get("query", ""),
            "conclusion": reasoning.get("conclusion", ""),
            "confidence": verification.get("confidence", 0.0),
            "paths_used": len(reasoning.get("reasoning_paths", [])),
            "verification_status": "valid" if verification.get("is_valid", False) else "invalid",
            "warnings": verified.get("warnings", []),
            "issues": verified.get("issues", []),
            "metadata": {
                "reasoning_paths_count": len(reasoning.get("reasoning_paths", [])),
                "causal_chains_count": len(reasoning.get("causal_chains", [])),
                "context_used": reasoning.get("context_used", False)
            }
        }
        
        # Улучшаем текст отчёта через LM Studio (опционально)
        if self.lm_client and report["conclusion"]:
            try:
                improved = await self._improve_report_text(report)
                if improved:
                    report["conclusion"] = improved
            except Exception as e:
                logger.debug(f"Could not improve report text: {e}")
        
        logger.info(f"Report composed: confidence={report['confidence']:.2f}")
        
        return report
    
    async def _improve_report_text(self, report: Dict[str, Any]) -> str:
        """Улучшить текст отчёта через LM Studio"""
        if not self.lm_client:
            return report["conclusion"]
        
        try:
            prompt = f"""Улучши следующий текст отчёта, сделав его более структурированным и понятным.

Исходный текст:
{report['conclusion']}

Улучшенный текст:"""
            
            response = await self.lm_client.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=400
            )
            
            return response.get("text", "").strip()
        
        except Exception as e:
            logger.debug(f"Error improving report text: {e}")
            return report["conclusion"]













