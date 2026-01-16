#!/usr/bin/env python3
"""
SPO Extractor - модуль для извлечения Subject-Predicate-Object триплетов
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ExtractionMethod(Enum):
    """Методы извлечения SPO-триплетов"""
    LLM = "llm"
    REGEX = "regex"
    HYBRID = "hybrid"

@dataclass
class ExtractedTriplet:
    """Извлеченный триплет"""
    subject: str
    predicate: str
    object: str
    confidence: float
    method: ExtractionMethod
    context: str
    position: Tuple[int, int]  # (start, end) в тексте

class SPOExtractor:
    """Класс для извлечения SPO-триплетов различными методами"""
    
    def __init__(self):
        self.technical_patterns = self._load_technical_patterns()
        self.logical_patterns = self._load_logical_patterns()
        self.temporal_patterns = self._load_temporal_patterns()
    
    def _load_technical_patterns(self) -> List[Dict[str, str]]:
        """Загрузка паттернов для технических триплетов"""
        return [
            {
                "pattern": r"(\w+)\s+(?:implements|extends|inherits from)\s+(\w+)",
                "predicate": "implements"
            },
            {
                "pattern": r"(\w+)\s+(?:calls|invokes|uses)\s+(\w+)",
                "predicate": "calls"
            },
            {
                "pattern": r"(\w+)\s+(?:defines|creates|instantiates)\s+(\w+)",
                "predicate": "defines"
            },
            {
                "pattern": r"(\w+)\s+(?:depends on|requires)\s+(\w+)",
                "predicate": "depends_on"
            },
            {
                "pattern": r"(\w+)\s+(?:contains|includes|has)\s+(\w+)",
                "predicate": "contains"
            }
        ]
    
    def _load_logical_patterns(self) -> List[Dict[str, str]]:
        """Загрузка паттернов для логических триплетов"""
        return [
            {
                "pattern": r"(\w+)\s+(?:causes|leads to|results in)\s+(\w+)",
                "predicate": "causes"
            },
            {
                "pattern": r"(\w+)\s+(?:influences|affects|impacts)\s+(\w+)",
                "predicate": "influences"
            },
            {
                "pattern": r"(\w+)\s+(?:supports|validates|confirms)\s+(\w+)",
                "predicate": "supports"
            },
            {
                "pattern": r"(\w+)\s+(?:contradicts|conflicts with|opposes)\s+(\w+)",
                "predicate": "contradicts"
            },
            {
                "pattern": r"(\w+)\s+(?:precedes|comes before|happens before)\s+(\w+)",
                "predicate": "precedes"
            }
        ]
    
    def _load_temporal_patterns(self) -> List[Dict[str, str]]:
        """Загрузка паттернов для временных триплетов"""
        return [
            {
                "pattern": r"(\w+)\s+(?:happens at|occurs at|takes place at)\s+(\w+)",
                "predicate": "happens_at"
            },
            {
                "pattern": r"(\w+)\s+(?:starts|begins|commences)\s+(\w+)",
                "predicate": "starts"
            },
            {
                "pattern": r"(\w+)\s+(?:ends|finishes|concludes)\s+(\w+)",
                "predicate": "ends"
            },
            {
                "pattern": r"(\w+)\s+(?:lasts|takes|requires)\s+(\w+)",
                "predicate": "duration"
            }
        ]
    
    def extract_with_regex(self, text: str) -> List[ExtractedTriplet]:
        """
        Извлечение триплетов с помощью регулярных выражений
        
        Args:
            text: Текст для обработки
            
        Returns:
            Список извлеченных триплетов
        """
        triplets = []
        
        # Объединяем все паттерны
        all_patterns = (
            self.technical_patterns + 
            self.logical_patterns + 
            self.temporal_patterns
        )
        
        for pattern_info in all_patterns:
            pattern = pattern_info["pattern"]
            predicate = pattern_info["predicate"]
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                subject = match.group(1).strip()
                object = match.group(2).strip()
                
                # Фильтрация по длине и содержанию
                if (len(subject) > 2 and len(object) > 2 and 
                    subject != object and
                    not self._is_stopword(subject) and
                    not self._is_stopword(object)):
                    
                    triplet = ExtractedTriplet(
                        subject=subject,
                        predicate=predicate,
                        object=object,
                        confidence=self._calculate_confidence(match, text),
                        method=ExtractionMethod.REGEX,
                        context=self._extract_context(text, match.start(), match.end()),
                        position=(match.start(), match.end())
                    )
                    triplets.append(triplet)
        
        logger.info(f"Extracted {len(triplets)} triplets using regex")
        return triplets
    
    def extract_with_llm(self, text: str, llm_client=None) -> List[ExtractedTriplet]:
        """
        Извлечение триплетов с помощью LLM
        
        Args:
            text: Текст для обработки
            llm_client: Клиент LLM (опционально)
            
        Returns:
            Список извлеченных триплетов
        """
        # Промпт для LLM
        prompt = f"""
        Извлеки SPO-триплеты (Subject-Predicate-Object) из следующего текста.
        Фокусируйся на технических концепциях, отношениях и зависимостях.
        
        Текст: {text}
        
        Верни результат в JSON формате:
        {{
            "triplets": [
                {{
                    "subject": "субъект",
                    "predicate": "предикат",
                    "object": "объект",
                    "confidence": 0.9,
                    "type": "technical|logical|temporal",
                    "context": "контекст"
                }}
            ]
        }}
        """
        
        try:
            # Здесь должен быть вызов LLM
            # Пока используем заглушку
            response = self._call_llm_stub(prompt)
            
            triplets = []
            for triplet_data in response.get("triplets", []):
                triplet = ExtractedTriplet(
                    subject=triplet_data["subject"],
                    predicate=triplet_data["predicate"],
                    object=triplet_data["object"],
                    confidence=triplet_data.get("confidence", 0.8),
                    method=ExtractionMethod.LLM,
                    context=triplet_data.get("context", ""),
                    position=(0, 0)  # LLM не предоставляет позиции
                )
                triplets.append(triplet)
            
            logger.info(f"Extracted {len(triplets)} triplets using LLM")
            return triplets
            
        except Exception as e:
            logger.error(f"Error extracting triplets with LLM: {e}")
            return []
    
    def extract_hybrid(self, text: str, llm_client=None) -> List[ExtractedTriplet]:
        """
        Гибридное извлечение: regex + LLM + объединение результатов
        
        Args:
            text: Текст для обработки
            llm_client: Клиент LLM (опционально)
            
        Returns:
            Список извлеченных триплетов
        """
        # Извлечение regex
        regex_triplets = self.extract_with_regex(text)
        
        # Извлечение LLM
        llm_triplets = self.extract_with_llm(text, llm_client)
        
        # Объединение и дедупликация
        all_triplets = regex_triplets + llm_triplets
        unique_triplets = self._deduplicate_triplets(all_triplets)
        
        # Повышение confidence для совпадающих триплетов
        for triplet in unique_triplets:
            if self._has_similar_triplet(triplet, all_triplets):
                triplet.confidence = min(1.0, triplet.confidence + 0.1)
        
        logger.info(f"Extracted {len(unique_triplets)} unique triplets using hybrid method")
        return unique_triplets
    
    def validate_triplets(self, triplets: List[ExtractedTriplet]) -> List[ExtractedTriplet]:
        """
        Валидация извлеченных триплетов
        
        Args:
            triplets: Список триплетов для валидации
            
        Returns:
            Список валидных триплетов
        """
        validated = []
        
        for triplet in triplets:
            # Проверка на пустые поля
            if not triplet.subject or not triplet.predicate or not triplet.object:
                continue
            
            # Проверка confidence
            if not (0 <= triplet.confidence <= 1):
                continue
            
            # Проверка на стоп-слова
            if (self._is_stopword(triplet.subject) or 
                self._is_stopword(triplet.object)):
                continue
            
            # Проверка на дубликаты
            if not self._is_duplicate(triplet, validated):
                validated.append(triplet)
        
        logger.info(f"Validated {len(validated)} out of {len(triplets)} triplets")
        return validated
    
    def normalize_entities(self, triplets: List[ExtractedTriplet]) -> List[ExtractedTriplet]:
        """
        Нормализация сущностей в триплетах
        
        Args:
            triplets: Список триплетов для нормализации
            
        Returns:
            Список нормализованных триплетов
        """
        normalized = []
        
        for triplet in triplets:
            # Нормализация субъекта
            normalized_subject = self._normalize_entity(triplet.subject)
            
            # Нормализация объекта
            normalized_object = self._normalize_entity(triplet.object)
            
            # Нормализация предиката
            normalized_predicate = self._normalize_predicate(triplet.predicate)
            
            normalized_triplet = ExtractedTriplet(
                subject=normalized_subject,
                predicate=normalized_predicate,
                object=normalized_object,
                confidence=triplet.confidence,
                method=triplet.method,
                context=triplet.context,
                position=triplet.position
            )
            normalized.append(normalized_triplet)
        
        logger.info(f"Normalized {len(normalized)} triplets")
        return normalized
    
    def _calculate_confidence(self, match, text: str) -> float:
        """Расчет confidence для regex match"""
        # Базовый confidence
        confidence = 0.7
        
        # Повышение для технических терминов
        if any(term in match.group(0).lower() for term in 
               ['function', 'class', 'method', 'variable', 'interface']):
            confidence += 0.1
        
        # Повышение для длинных совпадений
        if len(match.group(0)) > 20:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Извлечение контекста вокруг совпадения"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _is_stopword(self, word: str) -> bool:
        """Проверка на стоп-слово"""
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        return word.lower() in stopwords
    
    def _deduplicate_triplets(self, triplets: List[ExtractedTriplet]) -> List[ExtractedTriplet]:
        """Удаление дубликатов триплетов"""
        seen = set()
        unique = []
        
        for triplet in triplets:
            key = (triplet.subject.lower(), triplet.predicate.lower(), triplet.object.lower())
            if key not in seen:
                seen.add(key)
                unique.append(triplet)
        
        return unique
    
    def _has_similar_triplet(self, triplet: ExtractedTriplet, triplets: List[ExtractedTriplet]) -> bool:
        """Проверка на наличие похожего триплета"""
        for other in triplets:
            if (triplet.subject.lower() == other.subject.lower() and
                triplet.predicate.lower() == other.predicate.lower() and
                triplet.object.lower() == other.object.lower() and
                triplet != other):
                return True
        return False
    
    def _is_duplicate(self, triplet: ExtractedTriplet, triplets: List[ExtractedTriplet]) -> bool:
        """Проверка на дубликат"""
        for other in triplets:
            if (triplet.subject.lower() == other.subject.lower() and
                triplet.predicate.lower() == other.predicate.lower() and
                triplet.object.lower() == other.object.lower()):
                return True
        return False
    
    def _normalize_entity(self, entity: str) -> str:
        """Нормализация сущности"""
        # Удаление лишних пробелов
        entity = entity.strip()
        
        # Приведение к правильному регистру
        if entity.isupper():
            entity = entity.title()
        
        # Удаление специальных символов в начале/конце
        entity = re.sub(r'^[^\w]+|[^\w]+$', '', entity)
        
        return entity
    
    def _normalize_predicate(self, predicate: str) -> str:
        """Нормализация предиката"""
        # Приведение к нижнему регистру
        predicate = predicate.lower()
        
        # Замена подчеркиваний на пробелы
        predicate = predicate.replace('_', ' ')
        
        # Удаление лишних пробелов
        predicate = ' '.join(predicate.split())
        
        return predicate
    
    def _call_llm_stub(self, prompt: str) -> Dict[str, Any]:
        """Заглушка для вызова LLM"""
        # Здесь должен быть реальный вызов LLM
        return {
            "triplets": [
                {
                    "subject": "KAG Builder",
                    "predicate": "implements",
                    "object": "SPO extraction",
                    "confidence": 0.9,
                    "type": "technical",
                    "context": "KAG Builder implements SPO extraction for knowledge graphs"
                }
            ]
        }

# Пример использования
if __name__ == "__main__":
    extractor = SPOExtractor()
    
    text = """
    The KAG Builder implements SPO extraction for knowledge graphs.
    It calls the LLM API to process documents and creates triplets.
    The system depends on OpenSPG for graph storage.
    """
    
    triplets = extractor.extract_hybrid(text)
    for triplet in triplets:
        print(f"{triplet.subject} -> {triplet.predicate} -> {triplet.object} ({triplet.confidence:.2f})")





































