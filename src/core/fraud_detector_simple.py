"""
Rule-based Fraud Detection - упрощенная версия для MVP
Использует 3 простых правила для детекции мошенничества
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j not available")


class RuleBasedFraudDetector:
    """
    Rule-based Fraud Detector - детекция мошенничества по простым правилам
    
    Правила:
    1. Высокое количество связей: клиент с >3 связями за период = подозрительно
    2. Fraud rings: группа из 3+ клиентов, связанных между собой = fraud ring
    3. Общий телефон: один телефон у 5+ клиентов = подозрительно
    """
    
    def __init__(
        self,
        neo4j_driver=None,
        suspicious_threshold: Optional[Dict[str, int]] = None
    ):
        """
        Инициализация Fraud Detector
        
        Args:
            neo4j_driver: Neo4j driver (опционально)
            suspicious_threshold: Пороги для правил (по умолчанию стандартные)
        """
        self.driver = neo4j_driver
        
        self.suspicious_threshold = suspicious_threshold or {
            'max_links_per_client': 3,      # Максимум связей на клиента
            'min_ring_size': 3,              # Минимум клиентов в fraud ring
            'max_clients_per_phone': 5       # Максимум клиентов на телефон
        }
        
        logger.info(f"RuleBasedFraudDetector initialized (thresholds: {self.suspicious_threshold})")
    
    def _find_high_link_clients(
        self,
        since_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Найти клиентов с большим количеством связей
        
        Args:
            since_date: Дата начала периода анализа
        
        Returns:
            Список клиентов с количеством связей
        """
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return []
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (c:Client)-[r:RELATES_TO]-(connected:Client)
                WHERE r.created_at >= datetime($since_date)
                WITH c, count(r) as link_count
                WHERE link_count > 0
                RETURN c.id as client_id, c.name as client_name, link_count
                ORDER BY link_count DESC
                LIMIT 100
                """
                
                result = session.run(query, {
                    'since_date': since_date.isoformat()
                })
                
                clients = []
                for record in result:
                    clients.append({
                        'id': record['client_id'],
                        'name': record.get('client_name', 'Unknown'),
                        'link_count': record['link_count']
                    })
                
                return clients
        except Exception as e:
            logger.error(f"Error finding high link clients: {e}")
            return []
    
    def _find_fraud_rings(
        self,
        since_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Найти fraud rings (циклы в графе)
        
        Args:
            since_date: Дата начала периода анализа
        
        Returns:
            Список найденных fraud rings
        """
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return []
        
        try:
            with self.driver.session() as session:
                # Ищем циклы: клиенты, связанные между собой
                query = """
                MATCH path = (c1:Client)-[:RELATES_TO*2..4]-(c1)
                WHERE ALL(r in relationships(path) WHERE r.created_at >= datetime($since_date))
                WITH nodes(path) as ring_nodes, length(path) as path_length
                WHERE size(ring_nodes) >= $min_ring_size
                WITH ring_nodes, 
                     [n in ring_nodes | n.id] as member_ids,
                     size(ring_nodes) as ring_size
                RETURN DISTINCT member_ids, ring_size
                ORDER BY ring_size DESC
                LIMIT 50
                """
                
                result = session.run(query, {
                    'since_date': since_date.isoformat(),
                    'min_ring_size': self.suspicious_threshold['min_ring_size']
                })
                
                rings = []
                for idx, record in enumerate(result):
                    member_ids = record['member_ids']
                    ring_size = record['ring_size']
                    
                    # Вычисляем density (плотность связей)
                    # Упрощенная метрика: количество связей / возможное количество
                    density = 0.5  # Заглушка, в реальности нужно вычислять
                    
                    rings.append({
                        'id': f"RING-{idx+1}",
                        'members': member_ids,
                        'size': ring_size,
                        'density': density
                    })
                
                return rings
        except Exception as e:
            logger.error(f"Error finding fraud rings: {e}")
            return []
    
    def _find_phone_clusters(self) -> Dict[str, List[str]]:
        """
        Найти кластеры клиентов по телефону
        
        Returns:
            Словарь {phone: [client_ids]}
        """
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return {}
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (c:Client)
                WHERE c.phone IS NOT NULL AND c.phone <> ''
                WITH c.phone as phone, collect(c.id) as client_ids
                WHERE size(client_ids) > 1
                RETURN phone, client_ids
                ORDER BY size(client_ids) DESC
                """
                
                result = session.run(query)
                
                phone_clusters = {}
                for record in result:
                    phone = record['phone']
                    client_ids = record['client_ids']
                    phone_clusters[phone] = client_ids
                
                return phone_clusters
        except Exception as e:
            logger.error(f"Error finding phone clusters: {e}")
            return {}
    
    def detect_fraud_patterns(
        self,
        time_window_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Детекция паттернов мошенничества
        
        Args:
            time_window_days: Период анализа в днях
        
        Returns:
            Список найденных паттернов с risk_level
        """
        today = datetime.utcnow()
        since_date = today - timedelta(days=time_window_days)
        
        logger.info(f"Detecting fraud patterns for last {time_window_days} days")
        
        results = []
        
        # Правило 1: Клиенты с большим количеством связей
        high_link_clients = self._find_high_link_clients(since_date)
        for client in high_link_clients:
            if client['link_count'] > self.suspicious_threshold['max_links_per_client']:
                risk_level = 'critical' if client['link_count'] > 5 else 'high'
                
                results.append({
                    'type': 'high_link_count',
                    'client_id': client['id'],
                    'client_name': client.get('name', 'Unknown'),
                    'link_count': client['link_count'],
                    'threshold': self.suspicious_threshold['max_links_per_client'],
                    'risk_level': risk_level,
                    'detected_at': datetime.utcnow().isoformat()
                })
        
        # Правило 2: Fraud rings
        fraud_rings = self._find_fraud_rings(since_date)
        for ring in fraud_rings:
            if ring['size'] >= self.suspicious_threshold['min_ring_size']:
                results.append({
                    'type': 'fraud_ring',
                    'ring_id': ring['id'],
                    'member_count': ring['size'],
                    'member_ids': ring['members'],
                    'density': ring['density'],
                    'risk_level': 'critical',
                    'detected_at': datetime.utcnow().isoformat()
                })
        
        # Правило 3: Общий телефон у многих клиентов
        phone_clusters = self._find_phone_clusters()
        for phone, client_ids in phone_clusters.items():
            if len(client_ids) > self.suspicious_threshold['max_clients_per_phone']:
                results.append({
                    'type': 'shared_phone',
                    'phone': phone,
                    'client_count': len(client_ids),
                    'client_ids': client_ids,
                    'threshold': self.suspicious_threshold['max_clients_per_phone'],
                    'risk_level': 'high',
                    'detected_at': datetime.utcnow().isoformat()
                })
        
        logger.info(f"Detected {len(results)} fraud patterns")
        return results
    
    def _generate_summary(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Генерация сводки по результатам детекции
        
        Args:
            results: Список найденных паттернов
        
        Returns:
            Сводка с количеством по типам и risk levels
        """
        summary = {
            'total_alerts': len(results),
            'by_type': {},
            'by_risk_level': {
                'critical': 0,
                'high': 0,
                'medium': 0
            }
        }
        
        for result in results:
            # Подсчет по типам
            alert_type = result['type']
            summary['by_type'][alert_type] = summary['by_type'].get(alert_type, 0) + 1
            
            # Подсчет по risk levels
            risk_level = result.get('risk_level', 'medium')
            if risk_level in summary['by_risk_level']:
                summary['by_risk_level'][risk_level] += 1
        
        return summary
