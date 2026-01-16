"""
Fuzzy Matcher для поиска совпадений между кейсами и клиентами
"""

import logging
from typing import List, Dict, Any
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

try:
    from Levenshtein import distance as levenshtein_distance
    LEVENSHTEIN_AVAILABLE = True
except ImportError:
    LEVENSHTEIN_AVAILABLE = False
    logger.warning("python-Levenshtein not installed, using fallback")


class FuzzyMatcher:
    """
    Fuzzy matcher для поиска совпадений по ФИО, телефону, адресу
    """
    
    def __init__(self, threshold: float = 0.85):
        """
        Инициализация FuzzyMatcher
        
        Args:
            threshold: Порог confidence для совпадений (0.85)
        """
        self.threshold = threshold
        logger.info(f"FuzzyMatcher initialized (threshold={threshold})")
    
    def normalize_phone(self, phone: str) -> str:
        """
        Нормализовать телефонный номер
        
        Args:
            phone: Телефонный номер
        
        Returns:
            Нормализованный номер
        """
        if not phone:
            return ""
        
        # Удаляем все нецифровые символы
        normalized = "".join(filter(str.isdigit, phone))
        
        # Убираем префикс +7 или 8 для российских номеров
        if normalized.startswith("7") and len(normalized) == 11:
            normalized = normalized[1:]
        elif normalized.startswith("8") and len(normalized) == 11:
            normalized = normalized[1:]
        
        return normalized
    
    def calculate_fio_score(self, fio1: str, fio2: str) -> float:
        """
        Рассчитать score для ФИО
        
        Args:
            fio1: Первое ФИО
            fio2: Второе ФИО
        
        Returns:
            Score [0.0, 1.0]
        """
        if not fio1 or not fio2:
            return 0.0
        
        # Нормализуем (приводим к нижнему регистру, убираем лишние пробелы)
        fio1 = " ".join(fio1.lower().split())
        fio2 = " ".join(fio2.lower().split())
        
        if fio1 == fio2:
            return 1.0
        
        # Используем Levenshtein distance
        if LEVENSHTEIN_AVAILABLE:
            max_len = max(len(fio1), len(fio2))
            if max_len == 0:
                return 0.0
            distance = levenshtein_distance(fio1, fio2)
            return 1.0 - (distance / max_len)
        else:
            # Fallback на SequenceMatcher
            return SequenceMatcher(None, fio1, fio2).ratio()
    
    def calculate_phone_score(self, phone1: str, phone2: str) -> float:
        """
        Рассчитать score для телефона
        
        Args:
            phone1: Первый телефон
            phone2: Второй телефон
        
        Returns:
            Score [0.0, 1.0]
        """
        norm1 = self.normalize_phone(phone1)
        norm2 = self.normalize_phone(phone2)
        
        if not norm1 or not norm2:
            return 0.0
        
        if norm1 == norm2:
            return 1.0
        
        # Для телефонов точное совпадение важно
        # Частичное совпадение (последние 7 цифр) = 0.5
        if len(norm1) >= 7 and len(norm2) >= 7:
            if norm1[-7:] == norm2[-7:]:
                return 0.5
        
        return 0.0
    
    def calculate_address_score(self, addr1: str, addr2: str) -> float:
        """
        Рассчитать score для адреса
        
        Args:
            addr1: Первый адрес
            addr2: Второй адрес
        
        Returns:
            Score [0.0, 1.0]
        """
        if not addr1 or not addr2:
            return 0.0
        
        # Нормализуем
        addr1 = " ".join(addr1.lower().split())
        addr2 = " ".join(addr2.lower().split())
        
        if addr1 == addr2:
            return 1.0
        
        # Используем частичное совпадение слов
        words1 = set(addr1.split())
        words2 = set(addr2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def calculate_score(self, case: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        """
        Рассчитать общий score для совпадения
        
        Взвешенная сумма:
        - ФИО: 40%
        - Телефон: 30%
        - Адрес: 20%
        - Доп. данные: 10%
        
        Args:
            case: Данные кейса
            candidate: Данные кандидата (клиента)
        
        Returns:
            Общий score [0.0, 1.0]
        """
        fio_score = self.calculate_fio_score(
            case.get("name", ""),
            candidate.get("name", "")
        )
        
        phone_score = self.calculate_phone_score(
            case.get("phone", ""),
            candidate.get("phone", "")
        )
        
        address_score = self.calculate_address_score(
            case.get("address", ""),
            candidate.get("address", "")
        )
        
        # Дополнительные данные (простое сравнение)
        additional_score = 0.0
        if case.get("additional_data") and candidate.get("additional_data"):
            if case["additional_data"] == candidate["additional_data"]:
                additional_score = 1.0
        
        # Взвешенная сумма
        total_score = (
            0.4 * fio_score +
            0.3 * phone_score +
            0.2 * address_score +
            0.1 * additional_score
        )
        
        return total_score
    
    def match_clients(self, orphaned_case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Найти совпадения для orphaned case
        
        Args:
            orphaned_case: Данные кейса без связей
        
        Returns:
            Список совпадений с confidence scores
        """
        # В production это должно искать в Neo4j
        # Для MVP возвращаем пустой список (будет реализовано позже)
        matches = []
        
        # TODO: Реализовать поиск клиентов в Neo4j
        # Пример:
        # with driver.session() as session:
        #     result = session.run("MATCH (c:Client) RETURN c")
        #     for record in result:
        #         candidate = record["c"]
        #         score = self.calculate_score(orphaned_case, candidate)
        #         if score >= self.threshold:
        #             matches.append({
        #                 "client_id": candidate["id"],
        #                 "confidence": score,
        #                 "match_details": {...}
        #             })
        
        return matches
