"""
Pattern Memory — модуль распознавания и сохранения шаблонов поведения

Концепция:
- TERAG анализирует результаты reasoning и OSINT-миссий
- Определяет успешные и ошибочные паттерны
- Сохраняет их как узлы :Pattern в Neo4j
- Формирует базу лучших практик для улучшения reasoning
"""
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

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


class PatternMemory:
    """
    Pattern Memory — распознавание и сохранение шаблонов поведения
    
    Функции:
    1. Классификация результатов как SUCCESS или FAILURE
    2. Сохранение паттернов в граф
    3. Связывание успешных и ошибочных паттернов
    4. Decay старых паттернов
    5. Извлечение лучших практик
    """
    
    def __init__(
        self,
        graph_updater: Optional[Any] = None,
        lm_client: Optional[Any] = None,
        decay_days: int = 7
    ):
        """
        Инициализация Pattern Memory
        
        Args:
            graph_updater: Экземпляр GraphUpdater
            lm_client: Экземпляр LMStudioClient
            decay_days: Количество дней до начала decay паттернов
        """
        self.graph_updater = graph_updater
        self.lm_client = lm_client
        self.decay_days = decay_days
        
        logger.info("PatternMemory initialized")
    
    async def classify_pattern(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Классифицировать результат как SUCCESS или FAILURE
        
        Args:
            result: Результат reasoning или миссии
        
        Returns:
            Словарь с классификацией:
            {
                "classification": "SUCCESS" | "FAILURE",
                "reason": "Explanation text",
                "pattern_name": "PatternName",
                "confidence": 0.0-1.0
            }
        """
        if not self.lm_client:
            # Fallback: простая классификация по quality_score
            quality = result.get("quality_score", result.get("confidence", 0.5))
            classification = "SUCCESS" if quality >= 0.7 else "FAILURE"
            
            return {
                "classification": classification,
                "reason": f"Quality score: {quality:.2f}",
                "pattern_name": self._extract_pattern_name(result),
                "confidence": abs(quality - 0.5) * 2  # Нормализуем к 0-1
            }
        
        try:
            # Формируем промпт для классификации
            result_text = self._format_result_for_classification(result)
            
            prompt = f"""Analyze the following result and classify it as SUCCESS or FAILURE.

Provide:
1. Classification: SUCCESS or FAILURE
2. Reason: Brief explanation (1-2 sentences)
3. Pattern name: Short name for this pattern (2-4 words, PascalCase)

Result:
{result_text}

Respond in this format:
Classification: SUCCESS/FAILURE
Reason: [explanation]
Pattern: [PatternName]"""

            response = await self.lm_client.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=150
            )
            
            text = response.get("text", "")
            
            # Парсим ответ
            classification = self._parse_classification(text)
            reason = self._parse_reason(text)
            pattern_name = self._parse_pattern_name(text, result)
            
            # Вычисляем confidence на основе качества результата
            quality = result.get("quality_score", result.get("confidence", 0.5))
            confidence = abs(quality - 0.5) * 2
            
            return {
                "classification": classification,
                "reason": reason,
                "pattern_name": pattern_name,
                "confidence": confidence
            }
        
        except Exception as e:
            logger.error(f"Error classifying pattern: {e}")
            # Fallback
            quality = result.get("quality_score", 0.5)
            return {
                "classification": "SUCCESS" if quality >= 0.7 else "FAILURE",
                "reason": f"Fallback classification (error: {e})",
                "pattern_name": self._extract_pattern_name(result),
                "confidence": 0.5
            }
    
    def _format_result_for_classification(self, result: Dict[str, Any]) -> str:
        """Форматировать результат для классификации"""
        parts = []
        
        if "task" in result:
            parts.append(f"Task: {result['task']}")
        if "output" in result:
            parts.append(f"Output: {result['output'][:200]}")
        if "quality_score" in result:
            parts.append(f"Quality: {result['quality_score']:.2f}")
        if "error" in result:
            parts.append(f"Error: {result['error']}")
        
        return "\n".join(parts) if parts else str(result)[:300]
    
    def _parse_classification(self, text: str) -> str:
        """Парсить классификацию из ответа LM Studio"""
        text_lower = text.lower()
        if "classification: success" in text_lower or "success" in text_lower[:50]:
            return "SUCCESS"
        elif "classification: failure" in text_lower or "failure" in text_lower[:50]:
            return "FAILURE"
        else:
            # Пытаемся найти в тексте
            if "success" in text_lower:
                return "SUCCESS"
            elif "failure" in text_lower or "error" in text_lower:
                return "FAILURE"
            return "SUCCESS"  # По умолчанию
    
    def _parse_reason(self, text: str) -> str:
        """Парсить reason из ответа LM Studio"""
        # Ищем строку "Reason:"
        match = re.search(r'Reason:\s*(.+?)(?:\n|Pattern:|$)', text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback: берём первые 2 предложения
        sentences = re.split(r'[.!?]+', text)
        return ". ".join(sentences[:2]).strip()[:200]
    
    def _parse_pattern_name(self, text: str, result: Dict[str, Any]) -> str:
        """Парсить pattern name из ответа LM Studio"""
        # Ищем строку "Pattern:"
        match = re.search(r'Pattern:\s*([A-Z][a-zA-Z0-9\s]+)', text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Убираем пробелы, делаем PascalCase
            name = "".join(word.capitalize() for word in name.split())
            return name[:50]
        
        # Fallback: извлекаем из результата
        return self._extract_pattern_name(result)
    
    def _extract_pattern_name(self, result: Dict[str, Any]) -> str:
        """Извлечь имя паттерна из результата (fallback)"""
        task = result.get("task", "Unknown")
        # Преобразуем в PascalCase
        words = re.findall(r'\w+', task)
        name = "".join(word.capitalize() for word in words[:3])
        return name or "UnknownPattern"
    
    async def store_pattern(self, pattern: Dict[str, Any]) -> bool:
        """
        Сохранить паттерн в граф знаний
        
        Args:
            pattern: Словарь с классификацией (результат classify_pattern)
        
        Returns:
            True если успешно, False иначе
        """
        if not self.graph_updater or not self.graph_updater.driver:
            logger.warning("GraphUpdater not available, cannot store pattern")
            return False
        
        try:
            pattern_name = pattern.get("pattern_name", "UnknownPattern")
            classification = pattern.get("classification", "UNKNOWN")
            reason = pattern.get("reason", "")
            confidence = pattern.get("confidence", 0.5)
            
            with self.graph_updater.driver.session() as session:
                query = """
                MERGE (p:Pattern {name: $pattern_name})
                ON CREATE SET
                    p.classification = $classification,
                    p.reason = $reason,
                    p.confidence = $confidence,
                    p.occurrences = 1,
                    p.created_at = datetime(),
                    p.last_seen = datetime()
                ON MATCH SET
                    p.occurrences = p.occurrences + 1,
                    p.last_seen = datetime(),
                    p.confidence = CASE 
                        WHEN $confidence > p.confidence THEN $confidence 
                        ELSE p.confidence 
                    END,
                    p.reason = CASE 
                        WHEN $reason IS NOT NULL AND $reason <> '' THEN $reason 
                        ELSE p.reason 
                    END
                RETURN p
                """
                
                result = session.run(query, {
                    "pattern_name": pattern_name,
                    "classification": classification,
                    "reason": reason,
                    "confidence": confidence
                })
                
                record = result.single()
                if record:
                    logger.info(f"Stored pattern: {pattern_name} ({classification})")
                    
                    # Отправляем уведомление в Telegram (если это SUCCESS)
                    if classification == "SUCCESS":
                        try:
                            from src.integration.telegram_service import send_pattern_notification_sync
                            send_pattern_notification_sync(pattern)
                        except Exception:
                            pass  # Telegram не обязателен
                    
                    return True
                
                return False
        
        except Exception as e:
            logger.error(f"Error storing pattern: {e}")
            return False
    
    def link_patterns(self, success_name: str, failure_name: str, strength: float = 0.1) -> bool:
        """
        Связать успешный и неудачный паттерн
        
        Args:
            success_name: Имя успешного паттерна
            failure_name: Имя неудачного паттерна
            strength: Усиление связи (по умолчанию 0.1)
        
        Returns:
            True если успешно, False иначе
        """
        if not self.graph_updater or not self.graph_updater.driver:
            return False
        
        try:
            with self.graph_updater.driver.session() as session:
                query = """
                MATCH (s:Pattern {name: $success_name, classification: 'SUCCESS'})
                MATCH (f:Pattern {name: $failure_name, classification: 'FAILURE'})
                MERGE (s)-[r:BEST_PRACTICE]->(f)
                ON CREATE SET
                    r.strength = $strength,
                    r.created_at = datetime()
                ON MATCH SET
                    r.strength = CASE 
                        WHEN r.strength + $strength > 1.0 THEN 1.0 
                        ELSE r.strength + $strength 
                    END,
                    r.updated_at = datetime()
                RETURN r
                """
                
                result = session.run(query, {
                    "success_name": success_name,
                    "failure_name": failure_name,
                    "strength": strength
                })
                
                record = result.single()
                if record:
                    logger.info(f"Linked patterns: {success_name} -> {failure_name}")
                    return True
                
                return False
        
        except Exception as e:
            logger.error(f"Error linking patterns: {e}")
            return False
    
    def decay_patterns(self):
        """
        Уменьшить силу связей и частоту старых паттернов
        
        Правило:
        - Если паттерн не обновлялся > decay_days дней → уменьшить occurrences
        - Уменьшить strength связей :BEST_PRACTICE
        """
        if not self.graph_updater or not self.graph_updater.driver:
            return
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.decay_days)
            
            with self.graph_updater.driver.session() as session:
                # Decay старых паттернов
                query_patterns = """
                MATCH (p:Pattern)
                WHERE p.last_seen < $cutoff_date OR p.last_seen IS NULL
                SET p.occurrences = p.occurrences * 0.95,
                    p.decay_score = COALESCE(p.decay_score, 1.0) * 0.95,
                    p.last_decay = datetime()
                RETURN count(p) as decayed
                """
                
                result = session.run(query_patterns, cutoff_date=cutoff_date)
                decayed_patterns = result.single()["decayed"]
                
                # Decay связей
                query_relations = """
                MATCH ()-[r:BEST_PRACTICE]->()
                SET r.strength = r.strength * 0.98,
                    r.last_decay = datetime()
                RETURN count(r) as decayed_relations
                """
                
                result = session.run(query_relations)
                decayed_relations = result.single()["decayed_relations"]
                
                logger.info(f"Decayed {decayed_patterns} patterns and {decayed_relations} relations")
        
        except Exception as e:
            logger.error(f"Error decaying patterns: {e}")
    
    async def get_best_practices(
        self,
        domain: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Получить лучшие практики (успешные паттерны)
        
        Args:
            domain: Домен для фильтрации (опционально)
            limit: Максимальное количество практик
        
        Returns:
            Список лучших практик
        """
        if not self.graph_updater or not self.graph_updater.driver:
            return []
        
        try:
            with self.graph_updater.driver.session() as session:
                if domain:
                    # Паттерны в конкретном домене
                    query = """
                    MATCH (d:Domain {name: $domain})<-[:BELONGS_TO]-(p:Pattern)
                    WHERE p.classification = 'SUCCESS'
                    RETURN p.name as name, p.reason as reason, p.occurrences as occurrences, p.confidence as confidence
                    ORDER BY p.occurrences DESC, p.confidence DESC
                    LIMIT $limit
                    """
                    result = session.run(query, domain=domain, limit=limit)
                else:
                    # Все успешные паттерны
                    query = """
                    MATCH (p:Pattern)
                    WHERE p.classification = 'SUCCESS'
                    RETURN p.name as name, p.reason as reason, p.occurrences as occurrences, p.confidence as confidence
                    ORDER BY p.occurrences DESC, p.confidence DESC
                    LIMIT $limit
                    """
                    result = session.run(query, limit=limit)
                
                practices = []
                for record in result:
                    practices.append({
                        "name": record["name"],
                        "reason": record.get("reason", ""),
                        "occurrences": record.get("occurrences", 0),
                        "confidence": record.get("confidence", 0.0)
                    })
                
                return practices
        
        except Exception as e:
            logger.error(f"Error getting best practices: {e}")
            return []
    
    async def learn_from_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обучение на результате (классификация + сохранение)
        
        Args:
            result: Результат reasoning или миссии
        
        Returns:
            Информация о сохранённом паттерне
        """
        # Классифицируем
        classification = await self.classify_pattern(result)
        
        # Сохраняем
        stored = await self.store_pattern(classification)
        
        if stored:
            # Если это SUCCESS, пытаемся связать с предыдущими FAILURE
            if classification["classification"] == "SUCCESS":
                # Ищем недавние FAILURE паттерны
                await self._link_success_to_recent_failures(classification["pattern_name"])
        
        return {
            "classification": classification,
            "stored": stored,
            "pattern_name": classification.get("pattern_name")
        }
    
    async def _link_success_to_recent_failures(self, success_name: str):
        """Связать успешный паттерн с недавними неудачными"""
        if not self.graph_updater or not self.graph_updater.driver:
            return
        
        try:
            with self.graph_updater.driver.session() as session:
                # Находим недавние FAILURE паттерны (за последние 24 часа)
                cutoff = datetime.utcnow() - timedelta(hours=24)
                
                query = """
                MATCH (f:Pattern)
                WHERE f.classification = 'FAILURE'
                  AND f.last_seen > $cutoff
                RETURN f.name as name
                ORDER BY f.last_seen DESC
                LIMIT 3
                """
                
                result = session.run(query, cutoff=cutoff)
                
                for record in result:
                    failure_name = record["name"]
                    self.link_patterns(success_name, failure_name, strength=0.1)
        
        except Exception as e:
            logger.debug(f"Could not link success to failures: {e}")
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """
        Получить статистику паттернов
        
        Returns:
            Словарь со статистикой
        """
        if not self.graph_updater or not self.graph_updater.driver:
            return {
                "total": 0,
                "success": 0,
                "failure": 0,
                "avg_strength": 0.0
            }
        
        try:
            with self.graph_updater.driver.session() as session:
                # Общая статистика
                query = """
                MATCH (p:Pattern)
                RETURN 
                    count(p) as total,
                    sum(CASE WHEN p.classification = 'SUCCESS' THEN 1 ELSE 0 END) as success,
                    sum(CASE WHEN p.classification = 'FAILURE' THEN 1 ELSE 0 END) as failure
                """
                
                result = session.run(query)
                record = result.single()
                
                total = record["total"] or 0
                success = record["success"] or 0
                failure = record["failure"] or 0
                
                # Средняя сила связей
                query_strength = """
                MATCH ()-[r:BEST_PRACTICE]->()
                RETURN avg(r.strength) as avg_strength
                """
                
                result = session.run(query_strength)
                avg_strength_record = result.single()
                avg_strength = avg_strength_record["avg_strength"] if avg_strength_record else 0.0
                
                return {
                    "total": total,
                    "success": success,
                    "failure": failure,
                    "avg_strength": float(avg_strength) if avg_strength else 0.0
                }
        
        except Exception as e:
            logger.error(f"Error getting pattern stats: {e}")
            return {
                "total": 0,
                "success": 0,
                "failure": 0,
                "avg_strength": 0.0
            }


async def example_usage():
    """Пример использования Pattern Memory"""
    from src.integration.lmstudio_client import LMStudioClient
    from installer.app.modules.graph_updater import GraphUpdater
    
    # Инициализация
    lm_client = LMStudioClient()
    await lm_client.connect()
    
    graph_updater = GraphUpdater()
    
    pattern_mem = PatternMemory(
        graph_updater=graph_updater,
        lm_client=lm_client
    )
    
    # Пример результата reasoning
    result = {
        "task": "OSINT summarization",
        "output": "Relevant summary generated",
        "quality_score": 0.92
    }
    
    # Обучение на результате
    learn_result = await pattern_mem.learn_from_result(result)
    
    print(f"Classification: {learn_result['classification']['classification']}")
    print(f"Pattern: {learn_result['pattern_name']}")
    
    # Получение лучших практик
    best = await pattern_mem.get_best_practices(limit=5)
    print(f"Best practices: {len(best)}")
    
    # Статистика
    stats = pattern_mem.get_pattern_stats()
    print(f"Patterns: {stats['total']} ({stats['success']} success, {stats['failure']} failure)")
    
    await lm_client.close()
    graph_updater.close()

