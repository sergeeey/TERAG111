"""
Causal Path Finder — поиск причинно-следственных путей в графе
"""
import logging
from typing import List, Dict, Any, Optional
from collections import deque

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j not available")


class CausalPathFinder:
    """
    Поиск причинно-следственных путей в графе знаний
    
    Использует алгоритмы:
    - Multi-hop traversal для поиска связей
    - Personalized PageRank для ранжирования путей
    - Causal reasoning для построения цепочек
    """
    
    def __init__(self, driver=None):
        """
        Инициализация поисковика путей
        
        Args:
            driver: Neo4j driver (опционально)
        """
        self.driver = driver
    
    def find_paths(
        self,
        start_node: str,
        end_node: Optional[str] = None,
        max_hops: int = 3,
        relation_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Найти пути между узлами
        
        Args:
            start_node: Начальный узел (имя или ID)
            end_node: Конечный узел (опционально)
            max_hops: Максимальная глубина поиска
            relation_types: Типы связей для поиска
        
        Returns:
            Список путей с метаданными
        """
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return []
        
        if relation_types is None:
            relation_types = ["RELATES_TO", "CAUSES", "INFLUENCES", "LEADS_TO", "BEST_PRACTICE"]
        
        try:
            with self.driver.session() as session:
                if end_node:
                    # Поиск конкретного пути
                    query = f"""
                    MATCH path = shortestPath(
                        (start)-[*1..{max_hops}]-(end)
                    )
                    WHERE start.name = $start_name OR id(start) = $start_id
                      AND (end.name = $end_name OR id(end) = $end_id)
                      AND ALL(r in relationships(path) WHERE type(r) IN $rel_types)
                    RETURN path, length(path) as path_length
                    ORDER BY path_length
                    LIMIT 10
                    """
                    
                    result = session.run(query, {
                        "start_name": start_node if isinstance(start_node, str) else None,
                        "start_id": int(start_node) if not isinstance(start_node, str) else None,
                        "end_name": end_node if isinstance(end_node, str) else None,
                        "end_id": int(end_node) if not isinstance(end_node, str) else None,
                        "rel_types": relation_types
                    })
                else:
                    # Поиск всех путей от начального узла
                    query = f"""
                    MATCH path = (start)-[*1..{max_hops}]->(connected)
                    WHERE start.name = $start_name OR id(start) = $start_id
                      AND ALL(r in relationships(path) WHERE type(r) IN $rel_types)
                    RETURN path, length(path) as path_length, connected.name as target
                    ORDER BY path_length, connected.name
                    LIMIT 50
                    """
                    
                    result = session.run(query, {
                        "start_name": start_node if isinstance(start_node, str) else None,
                        "start_id": int(start_node) if not isinstance(start_node, str) else None,
                        "rel_types": relation_types
                    })
                
                paths = []
                for record in result:
                    path = record["path"]
                    path_data = {
                        "length": record.get("path_length", 0),
                        "nodes": [node.get("name", str(node.id)) for node in path.nodes],
                        "relationships": [
                            {
                                "type": rel.type,
                                "start": rel.start_node.get("name", str(rel.start_node.id)),
                                "end": rel.end_node.get("name", str(rel.end_node.id))
                            }
                            for rel in path.relationships
                        ],
                        "target": record.get("target")
                    }
                    paths.append(path_data)
                
                return paths
        
        except Exception as e:
            logger.error(f"Error finding paths: {e}")
            return []
    
    def find_causal_chains(
        self,
        concept: str,
        max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Найти причинно-следственные цепочки для концепта
        
        Args:
            concept: Концепт для анализа
            max_depth: Максимальная глубина цепочки
        
        Returns:
            Список причинно-следственных цепочек
        """
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                # Ищем цепочки типа: A -> CAUSES -> B -> CAUSES -> C
                query = f"""
                    MATCH chain = (start)-[:CAUSES|INFLUENCES|LEADS_TO*1..{max_depth}]->(end)
                    WHERE start.name = $concept
                    RETURN chain, length(chain) as depth, end.name as conclusion
                    ORDER BY depth, end.name
                    LIMIT 20
                """
                
                result = session.run(query, {"concept": concept})
                
                chains = []
                for record in result:
                    chain = record["chain"]
                    chains.append({
                        "depth": record.get("depth", 0),
                        "conclusion": record.get("conclusion"),
                        "path": [node.get("name", str(node.id)) for node in chain.nodes]
                    })
                
                return chains
        
        except Exception as e:
            logger.error(f"Error finding causal chains: {e}")
            return []
    
    def rank_paths_by_relevance(
        self,
        paths: List[Dict[str, Any]],
        query_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Ранжировать пути по релевантности
        
        Args:
            paths: Список путей
            query_context: Контекст запроса для ранжирования
        
        Returns:
            Отсортированный список путей
        """
        # Простое ранжирование по длине пути и количеству связей
        # В будущем можно добавить семантическое ранжирование
        
        scored_paths = []
        for path in paths:
            score = 1.0 / (path.get("length", 1) + 1)  # Более короткие пути лучше
            path["relevance_score"] = score
            scored_paths.append(path)
        
        # Сортируем по релевантности
        scored_paths.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return scored_paths













