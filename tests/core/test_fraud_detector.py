"""
Тесты для Rule-based Fraud Detector
"""

import pytest
from datetime import datetime, timedelta
from src.core.fraud_detector_simple import RuleBasedFraudDetector


class TestRuleBasedFraudDetector:
    """Тесты для RuleBasedFraudDetector класса"""
    
    def test_init(self):
        """Тест инициализации"""
        detector = RuleBasedFraudDetector()
        assert detector.suspicious_threshold['max_links_per_client'] == 3
        assert detector.suspicious_threshold['min_ring_size'] == 3
        assert detector.suspicious_threshold['max_clients_per_phone'] == 5
    
    def test_init_custom_thresholds(self):
        """Тест инициализации с кастомными порогами"""
        custom_thresholds = {
            'max_links_per_client': 5,
            'min_ring_size': 4,
            'max_clients_per_phone': 10
        }
        detector = RuleBasedFraudDetector(suspicious_threshold=custom_thresholds)
        assert detector.suspicious_threshold == custom_thresholds
    
    def test_detect_fraud_patterns_no_driver(self):
        """Тест детекции без Neo4j driver (должен вернуть пустой список)"""
        detector = RuleBasedFraudDetector(neo4j_driver=None)
        results = detector.detect_fraud_patterns(time_window_days=30)
        
        # Без driver должен вернуть пустой список
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_generate_summary_empty(self):
        """Тест генерации сводки для пустых результатов"""
        detector = RuleBasedFraudDetector()
        summary = detector._generate_summary([])
        
        assert summary['total_alerts'] == 0
        assert summary['by_type'] == {}
        assert summary['by_risk_level']['critical'] == 0
        assert summary['by_risk_level']['high'] == 0
        assert summary['by_risk_level']['medium'] == 0
    
    def test_generate_summary_with_alerts(self):
        """Тест генерации сводки с алертами"""
        detector = RuleBasedFraudDetector()
        
        alerts = [
            {
                'type': 'high_link_count',
                'risk_level': 'high',
                'client_id': 'CLIENT-001'
            },
            {
                'type': 'fraud_ring',
                'risk_level': 'critical',
                'ring_id': 'RING-001'
            },
            {
                'type': 'shared_phone',
                'risk_level': 'high',
                'phone': '+77001234567'
            }
        ]
        
        summary = detector._generate_summary(alerts)
        
        assert summary['total_alerts'] == 3
        assert summary['by_type']['high_link_count'] == 1
        assert summary['by_type']['fraud_ring'] == 1
        assert summary['by_type']['shared_phone'] == 1
        assert summary['by_risk_level']['critical'] == 1
        assert summary['by_risk_level']['high'] == 2
