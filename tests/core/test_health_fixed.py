"""
Тесты для модуля health.py
Проверка здоровья системы TERAG
Исправленная версия с правильными импортами
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Прямой импорт модуля
import importlib.util
health_spec = importlib.util.spec_from_file_location("health", project_root / "src" / "core" / "health.py")
health_module = importlib.util.module_from_spec(health_spec)
health_spec.loader.exec_module(health_module)
get_health = health_module.get_health

metrics_spec = importlib.util.spec_from_file_location("metrics", project_root / "src" / "core" / "metrics.py")
metrics_module = importlib.util.module_from_spec(metrics_spec)
metrics_spec.loader.exec_module(metrics_module)
get_metrics_snapshot = metrics_module.get_metrics_snapshot


class TestGetHealth:
    """Тесты для функции get_health()"""
    
    def test_health_ok_status(self):
        """Тест: статус 'ok' при нормальном Resonance"""
        with patch.object(health_module, 'get_metrics_snapshot') as mock_metrics:
            mock_metrics.return_value = {
                'Resonance': 0.95,  # Высокий Resonance = низкий drift
                'RSS': 0.88,
                'COS': 0.86,
                'FAITH': 0.89
            }
            
            result = get_health()
            
            assert result['status'] == 'ok'
            assert result['heartbeat'] is True
            assert 'resonance_phase_drift' in result
            assert result['resonance_phase_drift'] < 0.2
    
    def test_health_warning_status(self):
        """Тест: статус 'warning' при среднем drift"""
        with patch.object(health_module, 'get_metrics_snapshot') as mock_metrics:
            mock_metrics.return_value = {
                'Resonance': 0.75,  # Средний Resonance = средний drift
                'RSS': 0.88,
                'COS': 0.86,
                'FAITH': 0.89
            }
            
            result = get_health()
            
            assert result['status'] == 'warning'
            assert result['heartbeat'] is True
            assert 0.2 < result['resonance_phase_drift'] <= 0.35
    
    def test_health_critical_status(self):
        """Тест: статус 'critical' при высоком drift"""
        with patch.object(health_module, 'get_metrics_snapshot') as mock_metrics:
            mock_metrics.return_value = {
                'Resonance': 0.60,  # Низкий Resonance = высокий drift
                'RSS': 0.88,
                'COS': 0.86,
                'FAITH': 0.89
            }
            
            result = get_health()
            
            assert result['status'] == 'critical'
            assert result['heartbeat'] is True
            assert result['resonance_phase_drift'] > 0.35
    
    def test_health_returns_dict(self):
        """Тест: функция возвращает словарь с правильными ключами"""
        with patch.object(health_module, 'get_metrics_snapshot') as mock_metrics:
            mock_metrics.return_value = {
                'Resonance': 0.90,
                'RSS': 0.88,
                'COS': 0.86,
                'FAITH': 0.89
            }
            
            result = get_health()
            
            assert isinstance(result, dict)
            assert 'status' in result
            assert 'heartbeat' in result
            assert 'resonance_phase_drift' in result
    
    def test_health_drift_calculation(self):
        """Тест: правильный расчет drift"""
        with patch.object(health_module, 'get_metrics_snapshot') as mock_metrics:
            mock_metrics.return_value = {
                'Resonance': 0.80,  # drift = 1.0 - 0.80 = 0.20
                'RSS': 0.88,
                'COS': 0.86,
                'FAITH': 0.89
            }
            
            result = get_health()
            
            expected_drift = round(1.0 - 0.80, 3)
            assert result['resonance_phase_drift'] == expected_drift
    
    def test_health_integration_with_metrics(self):
        """Тест: интеграция с реальным get_metrics_snapshot"""
        # Используем реальную функцию metrics (может быть симуляция)
        result = get_health()
        
        assert isinstance(result, dict)
        assert 'status' in result
        assert result['status'] in ['ok', 'warning', 'critical']
        assert result['heartbeat'] is True
