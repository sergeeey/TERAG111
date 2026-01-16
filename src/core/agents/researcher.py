"""
Researcher Agent — сбор данных из графа знаний
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j not available")


class Researcher:
    """
    Researcher Agent — собирает данные из графа знаний
    
    Функции:
    1. Извлекает релевантные узлы из графа
    2. Находит связи между концептами
    3. Собирает контекст для рассуждения
    """
    
    def __init__(self, graph_driver=None):
        """
        Инициализация Researcher
        
        Args:
            graph_driver: Neo4j driver
        """
        self.driver = graph_driver
        logger.info("Researcher agent initialized")
    
    async def collect(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Собрать данные согласно плану
        
        Args:
            plan: План от Planner
        
        Returns:
            Собранные данные
        """
        logger.info("Collecting data from graph")
        
        data = {
            "nodes": [],
            "relations": [],
            "facts": [],
            "context": {}
        }
        
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return data
        
        try:
            query = plan.get("query", "")
            required_data = plan.get("required_data", [])
            
            # Извлекаем концепты из запроса (простая версия)
            concepts = self._extract_concepts_simple(query)
            
            with self.driver.session() as session:
                # Собираем узлы
                if "facts" in required_data or "general_knowledge" in required_data:
                    data["nodes"] = await self._collect_nodes(session, concepts)
                
                # Собираем связи
                if "relations" in required_data or "general_knowledge" in required_data:
                    data["relations"] = await self._collect_relations(session, concepts)
                
                # Собираем факты
                if "facts" in required_data:
                    data["facts"] = await self._collect_facts(session, concepts)
            
            # Формируем контекст
            data["context"] = self._build_context(data)
            
            logger.info(f"Collected {len(data['nodes'])} nodes, {len(data['relations'])} relations")
        
        except Exception as e:
            logger.error(f"Error collecting data: {e}")
        
        return data
    
    def _extract_concepts_simple(self, query: str) -> List[str]:
        """Простое извлечение концептов"""
        # В реальности можно использовать NER или LM Studio
        words = query.split()
        # Фильтруем стоп-слова
        stop_words = {"как", "что", "где", "когда", "почему", "the", "a", "an", "is", "are"}
        concepts = [w for w in words if len(w) > 3 and w.lower() not in stop_words]
        return concepts[:10]
    
    async def _collect_nodes(self, session, concepts: List[str]) -> List[Dict[str, Any]]:
        """Собрать узлы из графа"""
        if not concepts:
            return []
        
        try:
            query = """
            MATCH (n)
            WHERE n.name IN $concepts OR any(concept IN $concepts WHERE n.name CONTAINS concept)
            RETURN n.name as name, labels(n) as labels, properties(n) as props
            LIMIT 20
            """
            
            result = session.run(query, concepts=concepts)
            nodes = []
            for record in result:
                nodes.append({
                    "name": record["name"],
                    "labels": record["labels"],
                    "properties": dict(record["props"])
                })
            return nodes
        except Exception as e:
            logger.error(f"Error collecting nodes: {e}")
            return []
    
    async def _collect_relations(self, session, concepts: List[str]) -> List[Dict[str, Any]]:
        """Собрать связи из графа"""
        if not concepts:
            return []
        
        try:
            query = """
            MATCH (a)-[r]->(b)
            WHERE a.name IN $concepts OR b.name IN $concepts
               OR any(concept IN $concepts WHERE a.name CONTAINS concept OR b.name CONTAINS concept)
            RETURN a.name as start, type(r) as rel_type, b.name as end, properties(r) as props
            LIMIT 30
            """
            
            result = session.run(query, concepts=concepts)
            relations = []
            for record in result:
                relations.append({
                    "start": record["start"],
                    "type": record["rel_type"],
                    "end": record["end"],
                    "properties": dict(record["props"])
                })
            return relations
        except Exception as e:
            logger.error(f"Error collecting relations: {e}")
            return []
    
    async def _collect_facts(self, session, concepts: List[str]) -> List[Dict[str, Any]]:
        """Собрать факты из графа"""
        # Факты хранятся как связи Entity-RELATES_TO-Entity
        return await self._collect_relations(session, concepts)
    
    def _build_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Построить контекст из собранных данных"""
        context = {
            "nodes_count": len(data.get("nodes", [])),
            "relations_count": len(data.get("relations", [])),
            "facts_count": len(data.get("facts", [])),
            "has_sufficient_data": len(data.get("nodes", [])) > 0 or len(data.get("relations", [])) > 0
        }
        return context













