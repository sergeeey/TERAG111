"""
Ideas Extractor Module
Extracts key ideas and concepts from questions
"""

import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class IdeasExtractor:
    """Extract ideas and concepts from text"""
    
    def __init__(self):
        self.keywords_pattern = re.compile(r'\b(?:what|how|why|when|where|who|which|explain|describe|analyze|compare|define)\b', re.IGNORECASE)
        self.entity_pattern = re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b')
    
    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract ideas from text
        
        Args:
            text: Input text to extract ideas from
            
        Returns:
            List of extracted ideas with metadata
        """
        ideas = []
        
        # Extract question type
        question_type = self._detect_question_type(text)
        
        # Extract entities (simplified)
        entities = self._extract_entities(text)
        
        # Extract key concepts
        concepts = self._extract_concepts(text)
        
        ideas.append({
            "type": question_type,
            "entities": entities,
            "concepts": concepts,
            "confidence": 0.85
        })
        
        return ideas
    
    def _detect_question_type(self, text: str) -> str:
        """Detect question type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['what', 'define', 'explain']):
            return "definition"
        elif any(word in text_lower for word in ['how', 'process', 'method']):
            return "process"
        elif any(word in text_lower for word in ['why', 'reason', 'cause']):
            return "reasoning"
        elif any(word in text_lower for word in ['compare', 'difference', 'versus']):
            return "comparison"
        else:
            return "general"
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities (simplified)"""
        entities = self.entity_pattern.findall(text)
        # Filter out common words
        filtered = [e for e in entities if len(e) > 2 and e not in ['The', 'This', 'That', 'These']]
        return filtered[:5]  # Limit to 5 entities
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts"""
        # Simple keyword extraction
        words = text.lower().split()
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        concepts = [w for w in words if w not in stop_words and len(w) > 3]
        return list(set(concepts))[:10]  # Limit to 10 unique concepts





















