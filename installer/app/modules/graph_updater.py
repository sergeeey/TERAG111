"""
Graph Updater Module
Интеграция с Neo4j для записи открытий и концептов в граф знаний
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

# Импорт метрик (опционально)
try:
    from src.core.graph_metrics import get_metrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j driver not available. Graph updates will be disabled.")


class GraphUpdater:
    """Класс для обновления графа знаний в Neo4j"""
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None,
                 password: Optional[str] = None):
        """
        Инициализация обновлятора графа
        
        Args:
            uri: URI Neo4j (по умолчанию из переменных окружения)
            user: Пользователь Neo4j
            password: Пароль Neo4j
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "terag_local")
        
        self.driver = None
        if NEO4J_AVAILABLE:
            try:
                self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                self.driver.verify_connectivity()
                logger.info("Neo4j connection established")
            except Exception as e:
                logger.warning(f"Neo4j connection failed: {e}")
                self.driver = None
    
    def close(self):
        """Закрыть соединение с Neo4j"""
        if self.driver:
            self.driver.close()
    
    def insert_discovery(self, discovery: Dict[str, Any]) -> bool:
        """
        Вставить открытие в граф знаний
        
        Args:
            discovery: Словарь с данными открытия
            
        Returns:
            True если успешно, False иначе
        """
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return False
        
        try:
            with self.driver.session() as session:
                # Создание узла Discovery
                query = """
                MERGE (d:Discovery {name: $name})
                ON CREATE SET
                    d.name = $name,
                    d.domain = $domain,
                    d.novelty_index = $novelty_index,
                    d.confidence_ratio = $confidence_ratio,
                    d.signal_strength = $signal_strength,
                    d.source = $source,
                    d.source_url = $source_url,
                    d.description = $description,
                    d.discovered_at = $discovered_at,
                    d.created_at = datetime()
                ON MATCH SET
                    d.novelty_index = CASE WHEN $novelty_index > d.novelty_index 
                                          THEN $novelty_index ELSE d.novelty_index END,
                    d.confidence_ratio = CASE WHEN $confidence_ratio > d.confidence_ratio 
                                             THEN $confidence_ratio ELSE d.confidence_ratio END,
                    d.updated_at = datetime()
                RETURN d
                """
                
                result = session.run(query, {
                    'name': discovery.get('name', ''),
                    'domain': discovery.get('domain', 'unknown'),
                    'novelty_index': discovery.get('novelty_index', 0.0),
                    'confidence_ratio': discovery.get('confidence_ratio', discovery.get('confidence', 0.0)),
                    'signal_strength': discovery.get('signal_strength', 0.0),
                    'source': discovery.get('source', ''),
                    'source_url': discovery.get('source_url', ''),
                    'description': discovery.get('description', ''),
                    'discovered_at': discovery.get('discovered_at', datetime.now().isoformat())
                })
                
                record = result.single()
                if record:
                    logger.info(f"Inserted discovery: {discovery.get('name')}")
                    return True
                else:
                    logger.warning(f"Failed to insert discovery: {discovery.get('name')}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error inserting discovery: {e}")
            return False
    
    def insert_concept(self, concept: Dict[str, Any]) -> bool:
        """
        Вставить концепт в граф знаний
        
        Args:
            concept: Словарь с данными концепта
            
        Returns:
            True если успешно, False иначе
        """
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (c:Concept {name: $name})
                ON CREATE SET
                    c.name = $name,
                    c.type = $type,
                    c.domain = $domain,
                    c.novelty_index = $novelty_index,
                    c.confidence = $confidence,
                    c.description = $description,
                    c.created_at = datetime()
                ON MATCH SET
                    c.novelty_index = CASE WHEN $novelty_index > c.novelty_index 
                                          THEN $novelty_index ELSE c.novelty_index END,
                    c.updated_at = datetime()
                RETURN c
                """
                
                result = session.run(query, {
                    'name': concept.get('name', ''),
                    'type': concept.get('type', 'concept'),
                    'domain': concept.get('domain', 'unknown'),
                    'novelty_index': concept.get('novelty_index', 0.0),
                    'confidence': concept.get('confidence', 0.0),
                    'description': concept.get('description', '')
                })
                
                if result.single():
                    logger.info(f"Inserted concept: {concept.get('name')}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error inserting concept: {e}")
            return False
    
    def create_relationship(self, from_node: str, to_node: str, 
                          rel_type: str, properties: Optional[Dict] = None) -> bool:
        """
        Создать связь между узлами
        
        Args:
            from_node: Имя узла источника
            to_node: Имя узла назначения
            rel_type: Тип связи
            properties: Свойства связи
            
        Returns:
            True если успешно
        """
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                query = f"""
                MATCH (a), (b)
                WHERE a.name = $from_name AND b.name = $to_name
                MERGE (a)-[r:{rel_type}]->(b)
                SET r += $properties
                RETURN r
                """
                
                result = session.run(query, {
                    'from_name': from_node,
                    'to_name': to_node,
                    'properties': properties or {}
                })
                
                if result.single():
                    logger.debug(f"Created relationship: {from_node} -[{rel_type}]-> {to_node}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return False
    
    def link_discovery_to_source(self, discovery_name: str, source_url: str) -> bool:
        """
        Связать открытие с источником
        
        Args:
            discovery_name: Имя открытия
            source_url: URL источника
            
        Returns:
            True если успешно
        """
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (s:Source {url: $url})
                ON CREATE SET s.url = $url, s.created_at = datetime()
                WITH s
                MATCH (d:Discovery {name: $discovery_name})
                MERGE (d)-[:MENTIONED_IN]->(s)
                RETURN s
                """
                
                result = session.run(query, {
                    'url': source_url,
                    'discovery_name': discovery_name
                })
                
                if result.single():
                    logger.info(f"Linked discovery {discovery_name} to source {source_url}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error linking discovery to source: {e}")
            return False
    
    def add_fact(self, fact: Dict[str, Any], source: str = "", confidence: float = 1.0) -> bool:
        """
        Добавить факт в граф знаний (триплет: subject-predicate-object)
        
        Args:
            fact: Словарь с полями:
                - subject: субъект (источник связи)
                - predicate: предикат (тип связи)
                - object: объект (цель связи)
            source: URL источника факта
            confidence: Уровень уверенности (0.0-1.0)
            
        Returns:
            True если успешно, False иначе
        """
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return False
        
        subject = fact.get("subject", "")
        predicate = fact.get("predicate", "RELATED_TO")
        obj = fact.get("object", "")
        
        if not subject or not obj:
            logger.warning(f"Invalid fact: missing subject or object")
            return False
        
        start_time = time.time()
        try:
            with self.driver.session() as session:
                # Создаём узлы и связь
                query = """
                MERGE (a:Entity {name: $subject})
                ON CREATE SET 
                    a.created_at = datetime(),
                    a.type = 'concept'
                ON MATCH SET 
                    a.updated_at = datetime()
                
                MERGE (b:Entity {name: $object})
                ON CREATE SET 
                    b.created_at = datetime(),
                    b.type = 'concept'
                ON MATCH SET 
                    b.updated_at = datetime()
                
                WITH a, b
                MERGE (a)-[r:RELATION {type: $predicate}]->(b)
                ON CREATE SET 
                    r.confidence = $confidence,
                    r.source = $source,
                    r.created_at = datetime(),
                    r.uid = randomUUID()
                ON MATCH SET 
                    r.confidence = CASE 
                        WHEN $confidence > r.confidence THEN $confidence 
                        ELSE r.confidence 
                    END,
                    r.updated_at = datetime()
                
                RETURN a, r, b
                """
                
                result = session.run(query, {
                    'subject': subject,
                    'object': obj,
                    'predicate': predicate,
                    'confidence': confidence,
                    'source': source
                })
                
                record = result.single()
                duration = time.time() - start_time
                
                if record:
                    logger.info(f"Added fact: {subject} -[{predicate}]-> {obj} (confidence: {confidence})")
                    
                    # Записываем метрики
                    if METRICS_AVAILABLE:
                        metrics = get_metrics()
                        metrics.record_fact_added(relation_type=predicate)
                        metrics.record_fact_insertion_time(duration)
                    
                    return True
                
                # Записываем ошибку в метрики
                if METRICS_AVAILABLE:
                    metrics = get_metrics()
                    metrics.record_fact_failed(error_type="insertion_failed")
                
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error adding fact: {e}", exc_info=True)
            
            # Записываем ошибку в метрики
            if METRICS_AVAILABLE:
                metrics = get_metrics()
                metrics.record_fact_failed(error_type=type(e).__name__)
            
            return False
    
    def link_concept_to_domain(self, concept_name: str, domain_name: str) -> bool:
        """
        Связать концепт с доменом
        
        Args:
            concept_name: Имя концепта
            domain_name: Имя домена
            
        Returns:
            True если успешно
        """
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (dom:Domain {name: $domain_name})
                ON CREATE SET dom.name = $domain_name, dom.created_at = datetime()
                WITH dom
                MATCH (c:Concept {name: $concept_name})
                MERGE (c)-[:RELATED_TO]->(dom)
                RETURN dom
                """
                
                result = session.run(query, {
                    'domain_name': domain_name,
                    'concept_name': concept_name
                })
                
                return result.single() is not None
                
        except Exception as e:
            logger.error(f"Error linking concept to domain: {e}")
            return False
    
    def batch_insert_discoveries(self, discoveries: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Массовая вставка открытий
        
        Args:
            discoveries: Список открытий
            
        Returns:
            Статистика вставки
        """
        stats = {'success': 0, 'failed': 0, 'total': len(discoveries)}
        
        for discovery in discoveries:
            if self.insert_discovery(discovery):
                stats['success'] += 1
                
                # Связывание с источником
                if discovery.get('source_url'):
                    self.link_discovery_to_source(
                        discovery.get('name', ''),
                        discovery.get('source_url', '')
                    )
                
                # Связывание с доменом
                if discovery.get('domain'):
                    self.link_concept_to_domain(
                        discovery.get('name', ''),
                        discovery.get('domain', '')
                    )
            else:
                stats['failed'] += 1
        
        logger.info(f"Batch insert: {stats['success']}/{stats['total']} successful")
        return stats
    
    def get_existing_concepts(self) -> List[str]:
        """
        Получить список существующих концептов
        
        Returns:
            Список имен концептов
        """
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                query = "MATCH (c:Concept) RETURN c.name AS name"
                result = session.run(query)
                return [record['name'] for record in result]
        except Exception as e:
            logger.error(f"Error getting existing concepts: {e}")
            return []
    
    def add_signal(self, concept: str, domain: str, novelty_score: float, confidence: float) -> bool:
        """
        Добавить сигнал (новое открытие) в граф знаний
        
        Args:
            concept: Название концепта/сигнала
            domain: Домен (область знаний)
            novelty_score: Оценка новизны (0.0-1.0)
            confidence: Уровень уверенности (0.0-1.0)
            
        Returns:
            True если успешно, False иначе
        """
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return False
        
        start_time = time.time()
        try:
            with self.driver.session() as session:
                # Создаём узел Signal и связываем с доменом
                query = """
                MERGE (s:Signal {name: $concept})
                ON CREATE SET 
                    s.created_at = datetime(),
                    s.novelty_score = $novelty_score,
                    s.confidence = $confidence,
                    s.domain = $domain
                ON MATCH SET 
                    s.novelty_score = CASE 
                        WHEN $novelty_score > s.novelty_score THEN $novelty_score 
                        ELSE s.novelty_score 
                    END,
                    s.confidence = CASE 
                        WHEN $confidence > s.confidence THEN $confidence 
                        ELSE s.confidence 
                    END,
                    s.updated_at = datetime()
                
                WITH s
                MERGE (d:Domain {name: $domain})
                ON CREATE SET d.created_at = datetime()
                
                MERGE (s)-[:BELONGS_TO]->(d)
                
                RETURN s, d
                """
                
                result = session.run(query, {
                    'concept': concept,
                    'domain': domain,
                    'novelty_score': novelty_score,
                    'confidence': confidence
                })
                
                record = result.single()
                duration = time.time() - start_time
                
                if record:
                    logger.info(f"Added signal: {concept} in domain {domain} (novelty: {novelty_score}, confidence: {confidence})")
                    
                    # Записываем метрики
                    if METRICS_AVAILABLE:
                        metrics = get_metrics()
                        metrics.record_signal_added(domain=domain)
                        metrics.record_signal_insertion_time(duration)
                    
                    return True
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error adding signal: {e}", exc_info=True)
            return False
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Получить статистику графа знаний
        
        Returns:
            Словарь с количеством узлов, связей и другой статистикой
        """
        if not self.driver:
            return {
                "nodes": 0,
                "relations": 0,
                "entities": 0,
                "signals": 0,
                "domains": 0,
                "error": "Neo4j driver not available"
            }
        
        try:
            with self.driver.session() as session:
                # Общее количество узлов
                nodes_result = session.run("MATCH (n) RETURN count(n) as count")
                nodes_count = nodes_result.single()["count"]
                
                # Общее количество связей
                rels_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                rels_count = rels_result.single()["count"]
                
                # Количество Entity узлов
                entities_result = session.run("MATCH (n:Entity) RETURN count(n) as count")
                entities_count = entities_result.single()["count"]
                
                # Количество Signal узлов
                signals_result = session.run("MATCH (n:Signal) RETURN count(n) as count")
                signals_count = signals_result.single()["count"]
                
                # Количество Domain узлов
                domains_result = session.run("MATCH (n:Domain) RETURN count(n) as count")
                domains_count = domains_result.single()["count"]
                
                stats = {
                    "nodes": nodes_count,
                    "relations": rels_count,
                    "entities": entities_count,
                    "signals": signals_count,
                    "domains": domains_count
                }
                
                # Обновляем метрики
                if METRICS_AVAILABLE:
                    metrics = get_metrics()
                    metrics.update_graph_stats(stats)
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting graph stats: {e}")
            return {
                "nodes": 0,
                "relations": 0,
                "entities": 0,
                "signals": 0,
                "domains": 0,
                "error": str(e)
            }






