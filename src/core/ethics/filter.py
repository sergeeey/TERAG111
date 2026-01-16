"""
Ethical Filter — этическая фильтрация контента
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

try:
    from src.integration.lmstudio_client import LMStudioClient
    LMSTUDIO_AVAILABLE = True
except ImportError:
    LMSTUDIO_AVAILABLE = False
    logger.warning("LMStudioClient not available")


class EthicalFilter:
    """
    Ethical Filter — фильтрует контент на этические нарушения
    
    Функции:
    1. Проверяет на токсичность
    2. Обнаруживает предвзятость
    3. Валидирует непроверяемые утверждения
    4. Фильтрует неэтичный контент
    """
    
    def __init__(self, rules_file: Optional[Path] = None, lm_client=None):
        """
        Инициализация Ethical Filter
        
        Args:
            rules_file: Путь к файлу с правилами этики (JSON)
            lm_client: LMStudioClient для проверки
        """
        self.lm_client = lm_client
        self.rules = self._load_rules(rules_file)
        logger.info("EthicalFilter initialized")
    
    def _load_rules(self, rules_file: Optional[Path]) -> Dict[str, Any]:
        """Загрузить правила этики"""
        if rules_file is None:
            rules_file = Path(__file__).parent.parent.parent / "data" / "ethics_rules.json"
        
        default_rules = {
            "check_toxicity": True,
            "check_bias": True,
            "check_unverifiable": True,
            "blocked_topics": [],
            "sensitivity_threshold": 0.7
        }
        
        if rules_file.exists():
            try:
                with open(rules_file, "r", encoding="utf-8") as f:
                    loaded_rules = json.load(f)
                    default_rules.update(loaded_rules)
                    logger.info(f"Loaded ethics rules from {rules_file}")
            except Exception as e:
                logger.warning(f"Could not load ethics rules: {e}, using defaults")
        else:
            # Создаём файл с правилами по умолчанию
            try:
                rules_file.parent.mkdir(parents=True, exist_ok=True)
                with open(rules_file, "w", encoding="utf-8") as f:
                    json.dump(default_rules, f, ensure_ascii=False, indent=2)
                logger.info(f"Created default ethics rules at {rules_file}")
            except Exception as e:
                logger.warning(f"Could not create ethics rules file: {e}")
        
        return default_rules
    
    async def filter(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отфильтровать контент
        
        Args:
            content: Контент для проверки (может быть reasoning или report)
        
        Returns:
            Отфильтрованный контент с метаданными проверки
        """
        logger.info("Filtering content for ethical violations")
        
        # Извлекаем текст для проверки
        text = self._extract_text(content)
        
        if not text:
            return {
                "is_ethical": True,
                "violations": [],
                "filtered_content": content
            }
        
        violations = []
        
        # Проверка 1: Токсичность
        if self.rules.get("check_toxicity", True):
            toxicity_check = await self._check_toxicity(text)
            if toxicity_check["is_toxic"]:
                violations.append({
                    "type": "toxicity",
                    "severity": toxicity_check.get("severity", "medium"),
                    "details": toxicity_check.get("details", "")
                })
        
        # Проверка 2: Предвзятость
        if self.rules.get("check_bias", True):
            bias_check = await self._check_bias(text)
            if bias_check["has_bias"]:
                violations.append({
                    "type": "bias",
                    "severity": bias_check.get("severity", "low"),
                    "details": bias_check.get("details", "")
                })
        
        # Проверка 3: Непроверяемые утверждения
        if self.rules.get("check_unverifiable", True):
            unverifiable_check = await self._check_unverifiable(text)
            if unverifiable_check["has_unverifiable"]:
                violations.append({
                    "type": "unverifiable_claims",
                    "severity": "low",
                    "details": unverifiable_check.get("details", "")
                })
        
        # Проверка 4: Заблокированные темы
        blocked_topics = self.rules.get("blocked_topics", [])
        for topic in blocked_topics:
            if topic.lower() in text.lower():
                violations.append({
                    "type": "blocked_topic",
                    "severity": "high",
                    "details": f"Обнаружена заблокированная тема: {topic}"
                })
        
        # Фильтруем контент
        is_ethical = len(violations) == 0
        filtered_content = content.copy()
        
        if not is_ethical:
            # Удаляем или заменяем проблемные части
            filtered_content = self._sanitize_content(content, violations)
        
        result = {
            "is_ethical": is_ethical,
            "violations": violations,
            "violations_count": len(violations),
            "filtered_content": filtered_content
        }
        
        logger.info(f"Ethical check completed: ethical={is_ethical}, violations={len(violations)}")
        
        return result
    
    def _extract_text(self, content: Dict[str, Any]) -> str:
        """Извлечь текст из контента"""
        # Пробуем разные поля
        text_fields = ["conclusion", "text", "output", "report", "reasoning"]
        
        for field in text_fields:
            if field in content and content[field]:
                return str(content[field])
        
        # Если это вложенный словарь
        if "verified_reasoning" in content:
            return self._extract_text(content["verified_reasoning"])
        
        return ""
    
    async def _check_toxicity(self, text: str) -> Dict[str, Any]:
        """Проверить на токсичность"""
        if not self.lm_client:
            # Простая проверка на ключевые слова
            toxic_keywords = ["ненависть", "убийство", "насилие"]  # Упрощённый список
            is_toxic = any(keyword in text.lower() for keyword in toxic_keywords)
            return {
                "is_toxic": is_toxic,
                "severity": "high" if is_toxic else "none"
            }
        
        try:
            prompt = f"""Проверь следующий текст на токсичность, ненависть или вредный контент.

Текст:
{text[:500]}

Ответь только "ДА" если токсичен, "НЕТ" если нет:"""
            
            response = await self.lm_client.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=10
            )
            
            text_response = response.get("text", "").upper()
            is_toxic = "ДА" in text_response or "YES" in text_response
            
            return {
                "is_toxic": is_toxic,
                "severity": "high" if is_toxic else "none",
                "details": "Проверено через LM Studio"
            }
        
        except Exception as e:
            logger.warning(f"Error checking toxicity: {e}")
            return {"is_toxic": False, "severity": "none"}
    
    async def _check_bias(self, text: str) -> Dict[str, Any]:
        """Проверить на предвзятость"""
        if not self.lm_client:
            return {"has_bias": False, "severity": "none"}
        
        try:
            prompt = f"""Проверь следующий текст на предвзятость или дискриминацию.

Текст:
{text[:500]}

Ответь только "ДА" если есть предвзятость, "НЕТ" если нет:"""
            
            response = await self.lm_client.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=10
            )
            
            text_response = response.get("text", "").upper()
            has_bias = "ДА" in text_response or "YES" in text_response
            
            return {
                "has_bias": has_bias,
                "severity": "medium" if has_bias else "none",
                "details": "Проверено через LM Studio"
            }
        
        except Exception as e:
            logger.warning(f"Error checking bias: {e}")
            return {"has_bias": False, "severity": "none"}
    
    async def _check_unverifiable(self, text: str) -> Dict[str, Any]:
        """Проверить на непроверяемые утверждения"""
        # Простая проверка на маркеры непроверяемых утверждений
        unverifiable_markers = [
            "всегда", "никогда", "все", "никто",
            "always", "never", "all", "none"
        ]
        
        has_unverifiable = any(marker in text.lower() for marker in unverifiable_markers)
        
        return {
            "has_unverifiable": has_unverifiable,
            "details": "Обнаружены абсолютные утверждения" if has_unverifiable else ""
        }
    
    def _sanitize_content(self, content: Dict[str, Any], violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Очистить контент от нарушений"""
        # Простая очистка: заменяем проблемный текст
        filtered = content.copy()
        
        # Если есть высокий уровень нарушений, заменяем вывод
        high_severity = any(v.get("severity") == "high" for v in violations)
        
        if high_severity and "conclusion" in filtered:
            filtered["conclusion"] = "[Контент отфильтрован из-за этических нарушений]"
            filtered["filtered"] = True
        
        return filtered













