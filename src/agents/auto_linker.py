"""
Auto Linker MVP - синхронный endpoint для связывания похожих клиентов
Использует rapidfuzz для быстрого fuzzy matching по ФИО и телефону
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    try:
        from Levenshtein import ratio as levenshtein_ratio
        RAPIDFUZZ_AVAILABLE = False
        logger.warning("rapidfuzz not available, using python-Levenshtein")
    except ImportError:
        RAPIDFUZZ_AVAILABLE = False
        logger.error("Neither rapidfuzz nor python-Levenshtein available")
        raise ImportError("Install rapidfuzz or python-Levenshtein for Auto Linker")


class AutoLinkerMVP:
    """
    Auto Linker MVP - упрощенная версия для быстрого связывания клиентов
    
    Алгоритм:
    1. Сравнивает клиентов только по ФИО и телефону
    2. Использует fuzzy matching для ФИО (rapidfuzz или Levenshtein)
    3. Точное совпадение последних 4 цифр телефона
    4. Комбинированный confidence score
    5. Создает связи в Neo4j при confidence >= min_confidence
    """
    
    def __init__(
        self,
        min_confidence: float = 0.85,
        neo4j_driver=None
    ):
        """
        Инициализация Auto Linker
        
        Args:
            min_confidence: Минимальный confidence для создания связи (0.0-1.0)
            neo4j_driver: Neo4j driver для создания связей (опционально)
        """
        self.min_confidence = min_confidence
        self.driver = neo4j_driver
        logger.info(f"AutoLinkerMVP initialized (min_confidence={min_confidence})")
    
    def _calculate_fio_similarity(self, fio1: str, fio2: str) -> float:
        """
        Вычислить similarity между двумя ФИО
        
        Args:
            fio1: Первое ФИО
            fio2: Второе ФИО
            
        Returns:
            Similarity score (0.0-1.0)
        """
        if not fio1 or not fio2:
            return 0.0
        
        # Нормализуем: lowercase, strip, убираем лишние пробелы
        fio1_normalized = " ".join(fio1.lower().strip().split())
        fio2_normalized = " ".join(fio2.lower().strip().split())
        
        if RAPIDFUZZ_AVAILABLE:
            # Используем rapidfuzz (быстрее)
            score = fuzz.ratio(fio1_normalized, fio2_normalized) / 100.0
        else:
            # Fallback на Levenshtein
            score = levenshtein_ratio(fio1_normalized, fio2_normalized)
        
        return score
    
    def _calculate_phone_similarity(self, phone1: Optional[str], phone2: Optional[str]) -> float:
        """
        Вычислить similarity между двумя телефонами
        
        Args:
            phone1: Первый телефон
            phone2: Второй телефон
            
        Returns:
            Similarity score (0.0-1.0)
        """
        if not phone1 or not phone2:
            return 0.0
        
        # Извлекаем последние 4 цифры
        digits1 = ''.join(filter(str.isdigit, phone1))[-4:]
        digits2 = ''.join(filter(str.isdigit, phone2))[-4:]
        
        if not digits1 or not digits2:
            return 0.0
        
        # Точное совпадение последних 4 цифр = 1.0, иначе 0.0
        return 1.0 if digits1 == digits2 else 0.0
    
    def _calculate_combined_confidence(
        self,
        fio_score: float,
        phone_score: float
    ) -> float:
        """
        Вычислить комбинированный confidence score
        
        Args:
            fio_score: ФИО similarity (0.0-1.0)
            phone_score: Телефон similarity (0.0-1.0)
            
        Returns:
            Combined confidence (0.0-1.0)
        """
        # Если есть совпадение телефона - это сильный сигнал
        if phone_score > 0.0:
            # Телефон дает 50% веса, ФИО - 50%
            combined = (fio_score * 0.5) + (phone_score * 0.5)
        else:
            # Только ФИО
            combined = fio_score
        
        return round(combined, 3)
    
    def find_similar_clients(
        self,
        clients_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Найти похожих клиентов среди списка
        
        Args:
            clients_data: Список клиентов с полями:
                - id: ID клиента
                - full_name: ФИО (обязательно)
                - phone: Телефон (опционально)
        
        Returns:
            Список найденных пар с confidence scores
        """
        if len(clients_data) > 50:
            logger.warning(f"Too many clients ({len(clients_data)}), limiting to 50")
            clients_data = clients_data[:50]
        
        results = []
        
        logger.info(f"Comparing {len(clients_data)} clients for similarities")
        
        for i in range(len(clients_data)):
            client1 = clients_data[i]
            
            # Валидация обязательных полей
            if 'id' not in client1 or 'full_name' not in client1:
                logger.warning(f"Client {i} missing required fields (id or full_name)")
                continue
            
            for j in range(i + 1, len(clients_data)):
                client2 = clients_data[j]
                
                # Валидация обязательных полей
                if 'id' not in client2 or 'full_name' not in client2:
                    continue
                
                # Сравнение ФИО
                fio_score = self._calculate_fio_similarity(
                    client1.get('full_name', ''),
                    client2.get('full_name', '')
                )
                
                # Сравнение телефона
                phone_score = self._calculate_phone_similarity(
                    client1.get('phone'),
                    client2.get('phone')
                )
                
                # Комбинированный confidence
                combined_score = self._calculate_combined_confidence(fio_score, phone_score)
                
                # Если confidence >= min_confidence, добавляем в результаты
                if combined_score >= self.min_confidence:
                    match_reason = 'phone' if phone_score > 0.0 else 'fio'
                    
                    result = {
                        'client1_id': client1['id'],
                        'client2_id': client2['id'],
                        'client1_name': client1.get('full_name', ''),
                        'client2_name': client2.get('full_name', ''),
                        'confidence': combined_score,
                        'fio_score': round(fio_score, 3),
                        'phone_score': round(phone_score, 3),
                        'match_reason': match_reason,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    results.append(result)
                    logger.debug(f"Found match: {client1['id']} <-> {client2['id']} (confidence={combined_score})")
        
        logger.info(f"Found {len(results)} similar client pairs")
        return results
    
    def create_links_in_neo4j(
        self,
        similar_pairs: List[Dict[str, Any]],
        relation_type: str = "RELATES_TO"
    ) -> int:
        """
        Создать связи в Neo4j для найденных пар
        
        Args:
            similar_pairs: Список пар от find_similar_clients()
            relation_type: Тип связи в Neo4j (по умолчанию RELATES_TO)
        
        Returns:
            Количество созданных связей
        """
        if not self.driver:
            logger.warning("Neo4j driver not available, skipping link creation")
            return 0
        
        created_count = 0
        
        try:
            with self.driver.session() as session:
                for pair in similar_pairs:
                    try:
                        # Создаем связь между клиентами
                        query = f"""
                        MATCH (c1:Client {{id: $client1_id}})
                        MATCH (c2:Client {{id: $client2_id}})
                        MERGE (c1)-[r:{relation_type} {{
                            confidence: $confidence,
                            match_reason: $match_reason,
                            created_at: datetime()
                        }}]-(c2)
                        RETURN r
                        """
                        
                        result = session.run(query, {
                            'client1_id': pair['client1_id'],
                            'client2_id': pair['client2_id'],
                            'confidence': pair['confidence'],
                            'match_reason': pair['match_reason']
                        })
                        
                        if result.single():
                            created_count += 1
                            logger.debug(f"Created link: {pair['client1_id']} <-> {pair['client2_id']}")
                    except Exception as e:
                        logger.warning(f"Failed to create link for {pair['client1_id']} <-> {pair['client2_id']}: {e}")
                        continue
            
            logger.info(f"Created {created_count} links in Neo4j")
        except Exception as e:
            logger.error(f"Failed to create links in Neo4j: {e}")
        
        return created_count
