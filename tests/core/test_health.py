"""
Тесты для модуля health.py
Проверка здоровья системы TERAG
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Импортируем через __init__.py
try:
    from src.core import get_health, get_metrics_snapshot
except ImportError:
    # Пробуем прямой импорт
    try:
        from src.core.health import get_health
        from src.core.metrics import get_metrics_snapshot
    except ImportError as e:
        pytest.skip(f"Module not available: {e}", allow_module_level=True)


class TestGetHealth:
    """Тесты для функции get_health()"""
    
    def test_health_ok_status(self):
        """Тест: статус 'ok' при нормальном Resonance"""
        with patch('src.core.health.get_metrics_snapshot') as mock_metrics:
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
        with patch('src.core.health.get_metrics_snapshot') as mock_metrics:
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
        with patch('src.core.health.get_metrics_snapshot') as mock_metrics:
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
        with patch('src.core.health.get_metrics_snapshot') as mock_metrics:
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
        with patch('src.core.health.get_metrics_snapshot') as mock_metrics:
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
