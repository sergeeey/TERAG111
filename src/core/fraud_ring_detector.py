"""
Fraud Ring Detector - обнаружение мошеннических колец через Leiden algorithm
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j driver not available")


class FraudRingDetector:
    """
    Детектор мошеннических колец
    
    Использует Leiden algorithm через Neo4j GDS для обнаружения сообществ
    """
    
    def __init__(
        self,
        neo4j_driver=None,
        density_threshold: float = 0.7,
        min_community_size: int = 3
    ):
        """
        Инициализация FraudRingDetector
        
        Args:
            neo4j_driver: Neo4j driver
            density_threshold: Порог плотности для fraud ring (0.7)
            min_community_size: Минимальный размер сообщества (3)
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not installed")
        
        self.driver = neo4j_driver
        self.density_threshold = density_threshold
        self.min_community_size = min_community_size
        
        logger.info(
            f"FraudRingDetector initialized "
            f"(density_threshold={density_threshold}, min_size={min_community_size})"
        )
    
    def detect_communities(self) -> List[Dict[str, Any]]:
        """
        Обнаружить сообщества через Leiden algorithm (GDS)
        
        Returns:
            Список сообществ
        """
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                # Проверяем наличие GDS
                gds_check = session.run("CALL gds.version() YIELD version RETURN version")
                gds_available = gds_check.single() is not None
                
                if not gds_available:
                    logger.warning("Neo4j GDS not available - using fallback method")
                    return self._detect_communities_fallback(session)
                
                # Создаем граф в GDS
                session.run("""
                    CALL gds.graph.project(
                        'clientGraph',
                        ['Client', 'Case'],
                        {
                            LINKED_TO: {properties: 'confidence'},
                            RELATED_TO: {}
                        }
                    )
                """)
                
                # Запускаем Leiden algorithm
                result = session.run("""
                    CALL gds.leiden.stream('clientGraph')
                    YIELD nodeId, communityId
                    WITH communityId, collect(nodeId) as nodes
                    WHERE size(nodes) >= $min_size
                    RETURN communityId, nodes
                """, min_size=self.min_community_size)
                
                communities = []
                for record in result:
                    communities.append({
                        "community_id": record["communityId"],
                        "nodes": record["nodes"],
                        "size": len(record["nodes"])
                    })
                
                return communities
        except Exception as e:
            logger.error(f"Failed to detect communities: {e}")
            return []
    
    def _detect_communities_fallback(self, session) -> List[Dict[str, Any]]:
        """Fallback метод без GDS (простой анализ связей)"""
        result = session.run("""
            MATCH (c:Client)-[r:LINKED_TO|RELATED_TO]-(other)
            WITH c, count(DISTINCT other) as connections
            WHERE connections >= $min_size
            RETURN c.id as client_id, connections
        """, min_size=self.min_community_size)
        
        communities = []
        for record in result:
            communities.append({
                "community_id": f"fallback_{record['client_id']}",
                "nodes": [record["client_id"]],
                "size": record["connections"]
            })
        
        return communities
    
    def calculate_density(self, community: Dict[str, Any]) -> float:
        """
        Рассчитать плотность сообщества
        
        Density = (2 * edges) / (nodes * (nodes - 1))
        
        Args:
            community: Данные сообщества
        
        Returns:
            Плотность [0.0, 1.0]
        """
        nodes = community.get("nodes", [])
        node_count = len(nodes)
        
        if node_count < 2:
            return 0.0
        
        # Подсчитываем связи между узлами сообщества
        if not self.driver:
            return 0.0
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n)-[r:LINKED_TO|RELATED_TO]-(m)
                    WHERE n.id IN $nodes AND m.id IN $nodes
                    RETURN count(r) as edge_count
                """, nodes=[str(n) for n in nodes])
                
                record = result.single()
                edge_count = record["edge_count"] if record else 0
                
                # Максимальное количество возможных связей
                max_edges = node_count * (node_count - 1) / 2
                
                if max_edges == 0:
                    return 0.0
                
                density = (2 * edge_count) / (node_count * (node_count - 1))
                return min(1.0, density)
        except Exception as e:
            logger.error(f"Failed to calculate density: {e}")
            return 0.0
    
    def calculate_risk(self, community: Dict[str, Any]) -> float:
        """
        Рассчитать risk score для сообщества
        
        Args:
            community: Данные сообщества
        
        Returns:
            Risk score [0.0, 1.0]
        """
        density = self.calculate_density(community)
        size = community.get("size", 0)
        
        # Risk = density * size_factor
        size_factor = min(1.0, size / 10.0)  # Нормализуем размер
        
        risk = density * size_factor
        return risk
    
    def predict_fraud_ring(self) -> List[Dict[str, Any]]:
        """
        Предсказать fraud rings
        
        Returns:
            Список fraud rings
        """
        communities = self.detect_communities()
        fraud_rings = []
        
        for community in communities:
            density = self.calculate_density(community)
            
            if community["size"] >= self.min_community_size and density >= self.density_threshold:
                risk_score = self.calculate_risk(community)
                
                fraud_ring = {
                    "members": community["nodes"],
                    "size": community["size"],
                    "density": density,
                    "risk_score": risk_score,
                    "community_id": community.get("community_id")
                }
                
                fraud_rings.append(fraud_ring)
        
        logger.info(f"Detected {len(fraud_rings)} fraud rings")
        return fraud_rings
