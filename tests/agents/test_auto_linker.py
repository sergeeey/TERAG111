"""
Тесты для Auto Linker MVP
"""

import pytest
from src.agents.auto_linker import AutoLinkerMVP


class TestAutoLinkerMVP:
    """Тесты для AutoLinkerMVP класса"""
    
    def test_init(self):
        """Тест инициализации"""
        linker = AutoLinkerMVP(min_confidence=0.85)
        assert linker.min_confidence == 0.85
        assert linker.driver is None
    
    def test_fio_similarity_exact_match(self):
        """Тест точного совпадения ФИО"""
        linker = AutoLinkerMVP()
        
        score = linker._calculate_fio_similarity(
            "Иванов Иван Иванович",
            "Иванов Иван Иванович"
        )
        assert score >= 0.99  # Почти точное совпадение
    
    def test_fio_similarity_similar(self):
        """Тест похожих ФИО"""
        linker = AutoLinkerMVP()
        
        score = linker._calculate_fio_similarity(
            "Иванов Иван Иванович",
            "Иванов И.И."
        )
        assert score > 0.5  # Должна быть некоторая схожесть
    
    def test_fio_similarity_different(self):
        """Тест разных ФИО"""
        linker = AutoLinkerMVP()
        
        score = linker._calculate_fio_similarity(
            "Иванов Иван Иванович",
            "Петров Петр Петрович"
        )
        assert score < 0.5  # Должна быть низкая схожесть
    
    def test_phone_similarity_exact_match(self):
        """Тест точного совпадения телефона"""
        linker = AutoLinkerMVP()
        
        score = linker._calculate_phone_similarity(
            "+77001234567",
            "+77001234567"
        )
        assert score == 1.0
    
    def test_phone_similarity_last_4_digits(self):
        """Тест совпадения последних 4 цифр"""
        linker = AutoLinkerMVP()
        
        score = linker._calculate_phone_similarity(
            "+77001234567",
            "+77771234567"
        )
        assert score == 1.0  # Последние 4 цифры совпадают
    
    def test_phone_similarity_different(self):
        """Тест разных телефонов"""
        linker = AutoLinkerMVP()
        
        score = linker._calculate_phone_similarity(
            "+77001234567",
            "+77009876543"
        )
        assert score == 0.0  # Последние 4 цифры не совпадают
    
    def test_find_similar_clients_exact_match(self):
        """Тест поиска точно совпадающих клиентов"""
        linker = AutoLinkerMVP(min_confidence=0.85)
        
        clients = [
            {"id": "CLIENT-001", "full_name": "Иванов Иван Иванович", "phone": "+77001234567"},
            {"id": "CLIENT-002", "full_name": "Иванов Иван Иванович", "phone": "+77001234567"},
        ]
        
        results = linker.find_similar_clients(clients)
        
        assert len(results) == 1
        assert results[0]["client1_id"] == "CLIENT-001"
        assert results[0]["client2_id"] == "CLIENT-002"
        assert results[0]["confidence"] >= 0.85
    
    def test_find_similar_clients_phone_match(self):
        """Тест поиска по телефону"""
        linker = AutoLinkerMVP(min_confidence=0.85)
        
        clients = [
            {"id": "CLIENT-001", "full_name": "Иванов Иван", "phone": "+77001234567"},
            {"id": "CLIENT-002", "full_name": "Петров Петр", "phone": "+77771234567"},
        ]
        
        results = linker.find_similar_clients(clients)
        
        # Должна быть найдена пара по телефону (последние 4 цифры совпадают)
        assert len(results) >= 1
        assert results[0]["match_reason"] == "phone"
    
    def test_find_similar_clients_no_match(self):
        """Тест отсутствия совпадений"""
        linker = AutoLinkerMVP(min_confidence=0.9)
        
        clients = [
            {"id": "CLIENT-001", "full_name": "Иванов Иван Иванович", "phone": "+77001234567"},
            {"id": "CLIENT-002", "full_name": "Петров Петр Петрович", "phone": "+77009876543"},
        ]
        
        results = linker.find_similar_clients(clients)
        
        # Не должно быть совпадений при высоком пороге
        assert len(results) == 0
    
    def test_find_similar_clients_limit_50(self):
        """Тест ограничения на 50 клиентов"""
        linker = AutoLinkerMVP()
        
        # Создаем 60 клиентов
        clients = [
            {"id": f"CLIENT-{i:03d}", "full_name": f"Client {i}"}
            for i in range(60)
        ]
        
        results = linker.find_similar_clients(clients)
        
        # Должно обработать только первые 50
        # Проверяем, что не упало с ошибкой
        assert isinstance(results, list)
    
    def test_combined_confidence_with_phone(self):
        """Тест комбинированного confidence с телефоном"""
        linker = AutoLinkerMVP()
        
        # Высокий ФИО score + телефон = высокий combined
        combined = linker._calculate_combined_confidence(
            fio_score=0.8,
            phone_score=1.0
        )
        
        assert combined >= 0.8  # Должен быть высокий score
    
    def test_combined_confidence_no_phone(self):
        """Тест комбинированного confidence без телефона"""
        linker = AutoLinkerMVP()
        
        # Только ФИО
        combined = linker._calculate_combined_confidence(
            fio_score=0.9,
            phone_score=0.0
        )
        
        assert combined == 0.9  # Должен быть равен ФИО score
