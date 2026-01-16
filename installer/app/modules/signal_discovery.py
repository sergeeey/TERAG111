"""
Signal Discovery Module
Модуль для обнаружения слабых сигналов, новых концептов и недооценённых открытий
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)


class SignalDiscovery:
    """Класс для обнаружения и извлечения слабых сигналов из контента"""
    
    def __init__(self, llm_client=None, novelty_threshold: float = 0.7, 
                 min_confidence: float = 0.6):
        """
        Инициализация модуля обнаружения сигналов
        
        Args:
            llm_client: Клиент LLM для анализа
            novelty_threshold: Порог новизны концепта
            min_confidence: Минимальная уверенность для сигнала
        """
        self.llm_client = llm_client
        self.novelty_threshold = novelty_threshold
        self.min_confidence = min_confidence
        
        # Паттерны для обнаружения новых концептов
        self.novelty_indicators = [
            r'first\s+application\s+of',
            r'novel\s+(?:architecture|approach|method|framework)',
            r'underreported',
            r'weak\s+signal',
            r'emerging\s+(?:technology|concept|trend)',
            r'paradigm\s+shift',
            r'breakthrough',
            r'unprecedented'
        ]
        
        # Паттерны для извлечения концептов
        self.concept_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',  # Многословные концепты
            r'\b[A-Z]{2,}\b',  # Аббревиатуры
            r'"[^"]+"',  # Концепты в кавычках
        ]
    
    def extract_novel_concepts(self, text: str, source_url: str = "", 
                              metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Извлечь новые концепты из текста
        
        Args:
            text: Текст для анализа
            source_url: URL источника
            metadata: Метаданные источника
            
        Returns:
            Список обнаруженных концептов
        """
        concepts = []
        
        # 1. Поиск концептов через паттерны
        pattern_concepts = self._extract_pattern_concepts(text)
        
        # 2. Поиск концептов через LLM (если доступен)
        if self.llm_client:
            llm_concepts = self._extract_llm_concepts(text)
            concepts.extend(llm_concepts)
        
        # 3. Объединение и дедупликация
        all_concepts = pattern_concepts + concepts
        unique_concepts = self._deduplicate_concepts(all_concepts)
        
        # 4. Вычисление индекса новизны для каждого концепта
        for concept in unique_concepts:
            concept['novelty_index'] = self._calculate_novelty_index(concept, text)
            concept['source_url'] = source_url
            concept['extracted_at'] = datetime.now().isoformat()
            if metadata:
                concept['metadata'] = metadata
        
        # Фильтрация по порогу новизны
        novel_concepts = [
            c for c in unique_concepts 
            if c.get('novelty_index', 0.0) >= self.novelty_threshold
        ]
        
        logger.info(f"Extracted {len(novel_concepts)} novel concepts from text")
        return novel_concepts
    
    def _extract_pattern_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Извлечь концепты через паттерны"""
        concepts = []
        text_lower = text.lower()
        
        # Проверка наличия индикаторов новизны
        has_novelty_indicators = any(
            re.search(pattern, text_lower, re.IGNORECASE)
            for pattern in self.novelty_indicators
        )
        
        if not has_novelty_indicators:
            return concepts
        
        # Извлечение многословных концептов
        for pattern in self.concept_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                concept_text = match.group(0).strip('"')
                if len(concept_text) > 3 and concept_text not in ['The', 'This', 'That']:
                    concepts.append({
                        'name': concept_text,
                        'type': 'concept',
                        'confidence': 0.6,
                        'extraction_method': 'pattern'
                    })
        
        return concepts
    
    def _extract_llm_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Извлечь концепты через LLM"""
        if not self.llm_client:
            return []
        
        try:
            system_prompt = """You are an expert at identifying novel concepts, emerging technologies, and underreported discoveries in text.
Extract concepts that are:
- New or emerging (2024+)
- Underreported or less known
- Potentially significant (weak signals)
- Related to cognitive architectures, AI, biotech, governance, or epistemology

Return JSON array with:
{
  "name": "concept name",
  "type": "concept|technology|framework|discovery",
  "domain": "domain category",
  "description": "brief description",
  "novelty_indicators": ["indicators in text"],
  "confidence": 0.0-1.0
}"""
            
            prompt = f"""Extract novel concepts from this text (limit to 5000 chars):

{text[:5000]}

Return JSON array of concepts."""
            
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1500
            )
            
            response_text = response.get('response', '')
            
            # Парсинг JSON ответа
            import json
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                concepts = json.loads(json_match.group())
                for concept in concepts:
                    concept['extraction_method'] = 'llm'
                return concepts
            else:
                return []
                
        except Exception as e:
            logger.warning(f"LLM concept extraction failed: {e}")
            return []
    
    def _deduplicate_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Удалить дубликаты концептов"""
        seen = {}
        unique = []
        
        for concept in concepts:
            name = concept.get('name', '').lower().strip()
            if name and name not in seen:
                seen[name] = True
                unique.append(concept)
            elif name in seen:
                # Объединить метаданные
                existing = next((c for c in unique if c.get('name', '').lower() == name), None)
                if existing:
                    existing['confidence'] = max(
                        existing.get('confidence', 0.0),
                        concept.get('confidence', 0.0)
                    )
        
        return unique
    
    def _calculate_novelty_index(self, concept: Dict[str, Any], context: str) -> float:
        """
        Вычислить индекс новизны концепта
        
        Args:
            concept: Концепт
            context: Контекстный текст
            
        Returns:
            Индекс новизны (0.0-1.0)
        """
        novelty_score = 0.0
        context_lower = context.lower()
        concept_name = concept.get('name', '').lower()
        
        # 1. Проверка наличия индикаторов новизны рядом с концептом
        concept_position = context_lower.find(concept_name)
        if concept_position != -1:
            window = context[max(0, concept_position-100):min(len(context), concept_position+100)]
            window_lower = window.lower()
            
            for indicator_pattern in self.novelty_indicators:
                if re.search(indicator_pattern, window_lower, re.IGNORECASE):
                    novelty_score += 0.2
                    break
        
        # 2. Проверка наличия в базовых паттернах (DOI, arXiv, year)
        if re.search(r'\b(20\d{2})\b', context) and re.search(r'20(2[4-9]|3[0-9])', context):
            novelty_score += 0.15  # Новые публикации
        
        if re.search(r'arxiv\.org|doi\.org|10\.\d+', context, re.IGNORECASE):
            novelty_score += 0.1  # Академические источники
        
        # 3. Базовая уверенность из концепта
        novelty_score += concept.get('confidence', 0.0) * 0.3
        
        # 4. Тип концепта влияет на новизну
        concept_type = concept.get('type', '').lower()
        if concept_type in ['discovery', 'framework', 'technology']:
            novelty_score += 0.1
        
        return min(1.0, novelty_score)
    
    def detect_weak_signals(self, concepts: List[Dict[str, Any]], 
                          existing_concepts: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Обнаружить слабые сигналы среди концептов
        
        Args:
            concepts: Список концептов
            existing_concepts: Список существующих концептов (для сравнения)
            
        Returns:
            Список слабых сигналов
        """
        weak_signals = []
        existing_set = set((c.lower() for c in (existing_concepts or [])))
        
        for concept in concepts:
            concept_name = concept.get('name', '').lower()
            
            # Слабый сигнал = новый концепт с низкой частотой упоминаний
            is_new = concept_name not in existing_set
            novelty = concept.get('novelty_index', 0.0)
            confidence = concept.get('confidence', 0.0)
            
            if is_new and novelty >= 0.6 and confidence >= self.min_confidence:
                signal_strength = (novelty + confidence) / 2.0
                
                weak_signals.append({
                    **concept,
                    'signal_strength': signal_strength,
                    'is_weak_signal': True,
                    'detected_at': datetime.now().isoformat()
                })
        
        logger.info(f"Detected {len(weak_signals)} weak signals")
        return weak_signals
    
    def analyze_trends(self, concepts: List[Dict[str, Any]], 
                       time_period: str = "weekly") -> Dict[str, Any]:
        """
        Анализировать тренды в концептах
        
        Args:
            concepts: Список концептов
            time_period: Период анализа
            
        Returns:
            Результаты анализа трендов
        """
        # Подсчет частоты концептов по доменам
        domain_counts = Counter()
        type_counts = Counter()
        
        for concept in concepts:
            domain = concept.get('domain', 'unknown')
            concept_type = concept.get('type', 'unknown')
            domain_counts[domain] += 1
            type_counts[concept_type] += 1
        
        # Выявление растущих доменов
        growing_domains = [
            domain for domain, count in domain_counts.most_common(5)
            if count >= 2
        ]
        
        return {
            'total_concepts': len(concepts),
            'domain_distribution': dict(domain_counts),
            'type_distribution': dict(type_counts),
            'growing_domains': growing_domains,
            'analysis_period': time_period,
            'analyzed_at': datetime.now().isoformat()
        }


















