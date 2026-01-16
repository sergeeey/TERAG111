"""
DeepConf Validation Module
Валидация фактов через DeepConf/PEMM архитектуру с LLM-критиком
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DeepConfValidator:
    """Валидатор фактов с использованием DeepConf и PEMM архитектуры"""
    
    def __init__(self, llm_client=None, confidence_threshold: float = 0.7, 
                 pemm_enabled: bool = True):
        """
        Инициализация валидатора
        
        Args:
            llm_client: Клиент LLM для критики
            confidence_threshold: Минимальный порог уверенности
            pemm_enabled: Использовать ли PEMM архитектуру
        """
        self.llm_client = llm_client
        self.confidence_threshold = confidence_threshold
        self.pemm_enabled = pemm_enabled
    
    def validate_fact(self, fact: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        """
        Валидировать факт через DeepConf
        
        Args:
            fact: Факт для валидации (subject, predicate, object)
            context: Контекст факта
            
        Returns:
            Валидированный факт с confidence score
        """
        if not self.llm_client:
            logger.warning("LLM client not available, using default confidence")
            return {
                **fact,
                "confidence": 0.5,
                "validated": False,
                "validation_method": "default"
            }
        
        try:
            # Генерация PEMM структуры, если включено
            if self.pemm_enabled:
                pemm_structure = self._generate_pemm_structure(fact, context)
                validation_result = self._validate_with_pemm(fact, pemm_structure)
            else:
                validation_result = self._validate_simple(fact, context)
            
            # Применение порога уверенности
            validation_result["validated"] = (
                validation_result.get("confidence", 0.0) >= self.confidence_threshold
            )
            validation_result["validated_at"] = datetime.now().isoformat()
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                **fact,
                "confidence": 0.0,
                "validated": False,
                "error": str(e),
                "validation_method": "error"
            }
    
    def _generate_pemm_structure(self, fact: Dict[str, Any], context: Optional[str] = None) -> Dict[str, str]:
        """
        Генерация PEMM структуры (Role, Context, Task, Format)
        
        Args:
            fact: Факт для анализа
            context: Контекст
            
        Returns:
            PEMM структура
        """
        system_prompt = """You are a fact validation expert. Generate a PEMM structure for fact validation.
PEMM stands for:
- Role: The role of the validator
- Context: The context in which the fact exists
- Task: The validation task
- Format: The expected output format

Return JSON with keys: role, context, task, format."""
        
        prompt = f"""Generate PEMM structure for validating this fact:
Subject: {fact.get('subject', '')}
Predicate: {fact.get('predicate', '')}
Object: {fact.get('object', '')}

Context: {context or 'No additional context'}

Return JSON PEMM structure."""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # Парсинг JSON ответа
            response_text = response.get("response", "")
            # Попытка извлечь JSON
            import re
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                pemm = json.loads(json_match.group())
                return pemm
            else:
                # Fallback структура
                return {
                    "role": "Fact Validator",
                    "context": context or "General knowledge",
                    "task": "Validate factual accuracy",
                    "format": "confidence_score"
                }
        except Exception as e:
            logger.warning(f"PEMM generation failed: {e}")
            return {
                "role": "Fact Validator",
                "context": context or "General knowledge",
                "task": "Validate factual accuracy",
                "format": "confidence_score"
            }
    
    def _validate_with_pemm(self, fact: Dict[str, Any], pemm: Dict[str, str]) -> Dict[str, Any]:
        """
        Валидация с использованием PEMM структуры
        
        Args:
            fact: Факт для валидации
            pemm: PEMM структура
            
        Returns:
            Результат валидации
        """
        system_prompt = f"""You are a {pemm.get('role', 'Fact Validator')}.
Your task: {pemm.get('task', 'Validate factual accuracy')}
Context: {pemm.get('context', 'General knowledge')}
Output format: {pemm.get('format', 'confidence_score')}

Critically evaluate the fact and provide a confidence score (0.0 to 1.0).
Consider:
- Factual accuracy
- Logical consistency
- Source reliability
- Contextual relevance

Return JSON with: confidence, reasoning, validated."""
        
        prompt = f"""Validate this fact:
Subject: {fact.get('subject', '')}
Predicate: {fact.get('predicate', '')}
Object: {fact.get('object', '')}

Provide confidence score and reasoning."""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,  # Низкая температура для более консистентной оценки
                max_tokens=300
            )
            
            response_text = response.get("response", "")
            
            # Извлечение confidence из ответа
            import re
            confidence_match = re.search(r'["\']?confidence["\']?\s*[:=]\s*([0-9.]+)', response_text, re.IGNORECASE)
            if confidence_match:
                confidence = float(confidence_match.group(1))
            else:
                # Fallback: анализ текста ответа
                confidence = self._extract_confidence_from_text(response_text)
            
            return {
                **fact,
                "confidence": min(1.0, max(0.0, confidence)),
                "reasoning": response_text[:500],  # Ограничение длины
                "validation_method": "pemm_llm",
                "pemm_structure": pemm
            }
            
        except Exception as e:
            logger.error(f"PEMM validation error: {e}")
            return self._validate_simple(fact, None)
    
    def _validate_simple(self, fact: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        """
        Простая валидация без PEMM
        
        Args:
            fact: Факт для валидации
            context: Контекст
            
        Returns:
            Результат валидации
        """
        # Базовая валидация: проверка наличия всех полей
        has_all_fields = all(key in fact for key in ['subject', 'predicate', 'object'])
        base_confidence = 0.7 if has_all_fields else 0.3
        
        return {
            **fact,
            "confidence": base_confidence,
            "reasoning": "Simple validation: all fields present" if has_all_fields else "Simple validation: missing fields",
            "validation_method": "simple"
        }
    
    def _extract_confidence_from_text(self, text: str) -> float:
        """
        Извлечь confidence из текстового ответа
        
        Args:
            text: Текст ответа
            
        Returns:
            Confidence score
        """
        # Анализ ключевых слов
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['high', 'very', 'strong', 'certain']):
            return 0.8
        elif any(word in text_lower for word in ['medium', 'moderate', 'likely']):
            return 0.6
        elif any(word in text_lower for word in ['low', 'uncertain', 'doubtful']):
            return 0.3
        else:
            return 0.5
    
    def validate_batch(self, facts: List[Dict[str, Any]], 
                      context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Валидация батча фактов
        
        Args:
            facts: Список фактов
            context: Общий контекст
            
        Returns:
            Список валидированных фактов
        """
        validated = []
        for fact in facts:
            result = self.validate_fact(fact, context)
            validated.append(result)
        
        return validated


















