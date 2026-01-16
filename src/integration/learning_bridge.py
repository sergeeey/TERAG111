"""
Learning Bridge — модуль двусторонней связи между LM Studio (reasoning) и TERAG (память)

Концепция:
- LM Studio = рабочая память и интеллект (рассуждает)
- TERAG Graph = долговременная память (хранит факты и связи)
- Learning Bridge = мост между ними (обмен знаниями)
"""
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Импорты (опциональные)
try:
    from src.integration.lmstudio_client import LMStudioClient
    LMSTUDIO_AVAILABLE = True
except ImportError:
    LMSTUDIO_AVAILABLE = False
    logger.warning("LMStudioClient not available")

try:
    from installer.app.modules.graph_updater import GraphUpdater
    GRAPH_UPDATER_AVAILABLE = True
except ImportError:
    GRAPH_UPDATER_AVAILABLE = False
    logger.warning("GraphUpdater not available")


class LearningBridge:
    """
    Мост между LM Studio (reasoning) и TERAG Graph (память)
    
    Функции:
    1. Получает контекст из графа перед reasoning
    2. Сохраняет результаты reasoning обратно в граф
    3. Классифицирует домены для новых знаний
    4. Извлекает "best practices" из графа
    """
    
    def __init__(
        self,
        lm_client: Optional[Any] = None,
        graph_updater: Optional[Any] = None,
        default_domain: str = "General"
    ):
        """
        Инициализация Learning Bridge
        
        Args:
            lm_client: Экземпляр LMStudioClient
            graph_updater: Экземпляр GraphUpdater
            default_domain: Домен по умолчанию для классификации
        """
        self.lm_client = lm_client
        self.graph_updater = graph_updater
        self.default_domain = default_domain
        
        # Кэш для доменов
        self.domain_cache: Dict[str, str] = {}
        
        logger.info("LearningBridge initialized")
    
    async def get_context_from_graph(
        self,
        domain: Optional[str] = None,
        concept: Optional[str] = None,
        limit: int = 5
    ) -> str:
        """
        Получить контекст из графа знаний для reasoning
        
        Args:
            domain: Домен для фильтрации (например, "Programming", "AI")
            concept: Концепт для поиска связанных фактов
            limit: Максимальное количество фактов
        
        Returns:
            Текстовый контекст для промпта
        """
        if not self.graph_updater or not self.graph_updater.driver:
            logger.warning("GraphUpdater not available, returning empty context")
            return ""
        
        try:
            with self.graph_updater.driver.session() as session:
                context_parts = []
                
                # Если указан концепт, ищем связанные факты
                if concept:
                    query = """
                    MATCH (a:Entity {name: $concept})-[r:RELATION]->(b:Entity)
                    RETURN a.name as subject, r.type as relation, b.name as object, r.confidence as confidence
                    ORDER BY r.confidence DESC
                    LIMIT $limit
                    """
                    result = session.run(query, concept=concept, limit=limit)
                    
                    for record in result:
                        context_parts.append(
                            f"{record['subject']} -[{record['relation']}]-> {record['object']} "
                            f"(confidence: {record['confidence']:.2f})"
                        )
                
                # Если указан домен, ищем факты в этом домене
                elif domain:
                    query = """
                    MATCH (d:Domain {name: $domain})<-[:BELONGS_TO]-(s:Signal)
                    RETURN s.name as concept, s.novelty_score as novelty, s.confidence as confidence
                    ORDER BY s.novelty_score DESC, s.confidence DESC
                    LIMIT $limit
                    """
                    result = session.run(query, domain=domain, limit=limit)
                    
                    for record in result:
                        context_parts.append(
                            f"Signal: {record['concept']} "
                            f"(novelty: {record['novelty']:.2f}, confidence: {record['confidence']:.2f})"
                        )
                
                # Если ничего не указано, берём последние факты
                else:
                    query = """
                    MATCH (a:Entity)-[r:RELATION]->(b:Entity)
                    RETURN a.name as subject, r.type as relation, b.name as object, r.confidence as confidence
                    ORDER BY r.created_at DESC
                    LIMIT $limit
                    """
                    result = session.run(query, limit=limit)
                    
                    for record in result:
                        context_parts.append(
                            f"{record['subject']} -[{record['relation']}]-> {record['object']} "
                            f"(confidence: {record['confidence']:.2f})"
                        )
                
                if context_parts:
                    context = "Context from knowledge graph:\n" + "\n".join(context_parts)
                    logger.debug(f"Retrieved {len(context_parts)} facts from graph")
                    return context
                else:
                    logger.debug("No context found in graph")
                    return ""
        
        except Exception as e:
            logger.error(f"Error getting context from graph: {e}")
            return ""
    
    async def classify_domain(self, text: str) -> str:
        """
        Классифицировать домен для текста с помощью LM Studio
        
        Args:
            text: Текст для классификации
        
        Returns:
            Название домена (например, "Programming", "AI", "Psychology")
        """
        # Проверяем кэш
        text_hash = hash(text[:100])  # Хэш первых 100 символов
        if text_hash in self.domain_cache:
            return self.domain_cache[text_hash]
        
        if not self.lm_client:
            logger.warning("LM Studio client not available, using default domain")
            return self.default_domain
        
        try:
            # Промпт для классификации
            prompt = f"""Classify the following text into one of these domains:
- Programming
- AI
- Psychology
- OSINT
- General

Text: {text[:500]}

Respond with only the domain name (one word)."""

            result = await self.lm_client.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=20
            )
            
            domain = result.get("text", "").strip().split()[0] if result.get("text") else self.default_domain
            
            # Нормализуем домен
            domain = domain.capitalize()
            if domain not in ["Programming", "AI", "Psychology", "OSINT", "General"]:
                domain = self.default_domain
            
            # Кэшируем результат
            self.domain_cache[text_hash] = domain
            
            logger.debug(f"Classified text as domain: {domain}")
            return domain
        
        except Exception as e:
            logger.error(f"Error classifying domain: {e}")
            return self.default_domain
    
    async def learn_from_result(
        self,
        category: str,
        text: str,
        confidence: float = 0.9,
        source_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Сохранить результат reasoning LM Studio как знание в граф
        
        Args:
            category: Категория знания (например, "BestPractice", "Pattern")
            text: Текст результата reasoning
            confidence: Уровень уверенности (0.0-1.0)
            source_url: URL источника (если есть)
        
        Returns:
            Словарь с информацией о сохранённом знании
        """
        if not self.graph_updater:
            logger.warning("GraphUpdater not available, cannot save knowledge")
            return {"saved": False, "error": "GraphUpdater not available"}
        
        try:
            # Классифицируем домен
            domain = await self.classify_domain(text)
            
            # Извлекаем ключевые концепты из текста
            concepts = await self._extract_concepts(text)
            
            saved_facts = []
            
            # Сохраняем связи между концептами
            for i, concept1 in enumerate(concepts):
                for concept2 in concepts[i+1:]:
                    fact = {
                        "subject": concept1,
                        "predicate": "RELATED_TO",
                        "object": concept2
                    }
                    
                    if self.graph_updater.add_fact(
                        fact,
                        source=source_url or "",
                        confidence=confidence * 0.8  # Немного снижаем confidence для автоматических связей
                    ):
                        saved_facts.append(f"{concept1} -> {concept2}")
            
            # Сохраняем основной факт: категория -> домен
            if category and domain:
                fact = {
                    "subject": category,
                    "predicate": "LEARNED_FROM",
                    "object": domain
                }
                
                if self.graph_updater.add_fact(
                    fact,
                    source=source_url or "",
                    confidence=confidence
                ):
                    saved_facts.append(f"{category} -> {domain}")
            
            logger.info(f"Saved {len(saved_facts)} facts from reasoning result")
            
            return {
                "saved": True,
                "domain": domain,
                "facts_count": len(saved_facts),
                "facts": saved_facts
            }
        
        except Exception as e:
            logger.error(f"Error learning from result: {e}")
            return {"saved": False, "error": str(e)}
    
    async def _extract_concepts(self, text: str, max_concepts: int = 5) -> List[str]:
        """
        Извлечь ключевые концепты из текста
        
        Args:
            text: Текст для анализа
            max_concepts: Максимальное количество концептов
        
        Returns:
            Список концептов
        """
        if not self.lm_client:
            # Простое извлечение через regex (fallback)
            # Ищем слова с заглавной буквы
            concepts = re.findall(r'\b[A-Z][a-z]+\b', text)
            return list(set(concepts))[:max_concepts]
        
        try:
            prompt = f"""Extract key concepts from the following text.
Return only the concept names, one per line, without explanations.

Text: {text[:500]}

Concepts:"""

            result = await self.lm_client.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=100
            )
            
            concepts_text = result.get("text", "")
            concepts = [c.strip() for c in concepts_text.split("\n") if c.strip()][:max_concepts]
            
            return concepts
        
        except Exception as e:
            logger.error(f"Error extracting concepts: {e}")
            # Fallback на regex
            concepts = re.findall(r'\b[A-Z][a-z]+\b', text)
            return list(set(concepts))[:max_concepts]
    
    async def reason_with_context(
        self,
        question: str,
        domain: Optional[str] = None,
        save_result: bool = True,
        learn_pattern: bool = True
    ) -> Dict[str, Any]:
        """
        Выполнить reasoning с контекстом из графа
        
        Args:
            question: Вопрос для reasoning
            domain: Домен для фильтрации контекста
            save_result: Сохранять ли результат в граф
        
        Returns:
            Результат reasoning с метаданными
        """
        if not self.lm_client:
            raise ValueError("LM Studio client not available")
        
        # Получаем контекст из графа
        context = await self.get_context_from_graph(domain=domain, limit=5)
        
        # Формируем промпт с контекстом
        if context:
            prompt = f"""{context}

Question: {question}

Answer based on the context above and your knowledge:"""
        else:
            prompt = question
        
        # Выполняем reasoning
        result = await self.lm_client.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=512
        )
        
        # Сохраняем результат в граф, если нужно
        if save_result and self.graph_updater:
            learn_result = await self.learn_from_result(
                category="ReasoningResult",
                text=result.get("text", ""),
                confidence=0.85,
                source_url=None
            )
            result["learned"] = learn_result
        
        # Обучение на паттернах, если включено
        if learn_pattern:
            try:
                from src.core.pattern_memory import PatternMemory
                pattern_mem = PatternMemory(
                    graph_updater=self.graph_updater,
                    lm_client=self.lm_client
                )
                
                pattern_result = await pattern_mem.learn_from_result({
                    "task": f"Reasoning: {question[:100]}",
                    "output": result.get("text", ""),
                    "quality_score": 0.85,  # Можно улучшить, анализируя результат
                    "domain": domain
                })
                
                result["pattern_learned"] = pattern_result
            except Exception as e:
                logger.debug(f"Could not learn pattern: {e}")
        
        result["context_used"] = bool(context)
        result["domain"] = domain
        
        return result
    
    def get_best_practices(self, domain: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Получить "best practices" из графа для домена
        
        Args:
            domain: Домен для поиска
            limit: Максимальное количество практик
        
        Returns:
            Список best practices
        """
        if not self.graph_updater or not self.graph_updater.driver:
            return []
        
        try:
            with self.graph_updater.driver.session() as session:
                query = """
                MATCH (d:Domain {name: $domain})<-[:BELONGS_TO]-(s:Signal)
                WHERE s.confidence > 0.8
                RETURN s.name as concept, s.novelty_score as novelty, s.confidence as confidence
                ORDER BY s.confidence DESC, s.novelty_score DESC
                LIMIT $limit
                """
                
                result = session.run(query, domain=domain, limit=limit)
                practices = []
                
                for record in result:
                    practices.append({
                        "concept": record["concept"],
                        "novelty": record["novelty"],
                        "confidence": record["confidence"]
                    })
                
                return practices
        
        except Exception as e:
            logger.error(f"Error getting best practices: {e}")
            return []


async def example_usage():
    """Пример использования Learning Bridge"""
    from src.integration.lmstudio_client import LMStudioClient
    from installer.app.modules.graph_updater import GraphUpdater
    
    # Инициализация
    lm_client = LMStudioClient()
    graph_updater = GraphUpdater()
    
    bridge = LearningBridge(lm_client=lm_client, graph_updater=graph_updater)
    
    # Reasoning с контекстом
    result = await bridge.reason_with_context(
        question="What are best practices for error handling in Python?",
        domain="Programming",
        save_result=True
    )
    
    print(f"Answer: {result['text']}")
    print(f"Context used: {result['context_used']}")
    print(f"Learned: {result.get('learned', {})}")
    
    # Получение best practices
    practices = bridge.get_best_practices("Programming", limit=5)
    print(f"Best practices: {practices}")

