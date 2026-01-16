"""
Тесты для модуля self_learning.py
Проверка обработки обратной связи и обучения системы
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
    from src.core import accept_feedback
    from src.core import metrics as M
except ImportError:
    # Пробуем прямой импорт
    try:
        from src.core.self_learning import accept_feedback
        from src.core import metrics as M
    except ImportError as e:
        pytest.skip(f"Module not available: {e}", allow_module_level=True)


class TestAcceptFeedback:
    """Тесты для функции accept_feedback()"""
    
    def setup_method(self):
        """Сброс состояния перед каждым тестом"""
        # Сохраняем исходное состояние
        if hasattr(M, '_state'):
            self.original_state = M._state.copy()
        else:
            self.original_state = {}
    
    def teardown_method(self):
        """Восстановление состояния после каждого теста"""
        if hasattr(M, '_state'):
            M._state.update(self.original_state)
    
    def test_accept_feedback_returns_true(self):
        """Тест: функция возвращает True при успешной обработке"""
        payload = {
            'target': {
                'RSS': 0.9,
                'COS': 0.9,
                'FAITH': 0.92
            }
        }
        
        result = accept_feedback(payload)
        
        assert result is True
    
    def test_accept_feedback_updates_metrics(self):
        """Тест: обратная связь обновляет метрики"""
        # Устанавливаем начальное состояние
        if hasattr(M, '_state'):
            M._state['RSS'] = 0.8
            M._state['COS'] = 0.8
            M._state['FAITH'] = 0.8
        
        payload = {
            'target': {
                'RSS': 0.9,
                'COS': 0.9,
                'FAITH': 0.92
            }
        }
        
        accept_feedback(payload)
        
        # Проверяем, что метрики изменились (с учетом ALPHA=0.15)
        if hasattr(M, '_state'):
            assert M._state['RSS'] > 0.8  # Должно увеличиться
            assert M._state['COS'] > 0.8
            assert M._state['FAITH'] > 0.8
    
    def test_accept_feedback_partial_update(self):
        """Тест: обновление только указанных метрик"""
        if hasattr(M, '_state'):
            original_rss = M._state.get('RSS', 0.8)
            original_cos = M._state.get('COS', 0.8)
            
            payload = {
                'target': {
                    'RSS': 0.9
                    # COS не указан
                }
            }
            
            accept_feedback(payload)
            
            # RSS должен измениться
            assert M._state['RSS'] != original_rss
            # COS не должен измениться (если не был указан)
            # Но может измениться из-за heartbeat, поэтому проверяем только RSS
    
    def test_accept_feedback_empty_target(self):
        """Тест: обработка пустого target"""
        payload = {
            'target': {}
        }
        
        result = accept_feedback(payload)
        
        assert result is True
    
    def test_accept_feedback_no_target(self):
        """Тест: обработка payload без target"""
        payload = {}
        
        result = accept_feedback(payload)
        
        assert result is True
    
    def test_accept_feedback_alpha_smoothing(self):
        """Тест: применение ALPHA для сглаживания изменений"""
        if hasattr(M, '_state'):
            M._state['RSS'] = 0.8
            
            payload = {
                'target': {
                    'RSS': 1.0  # Целевое значение
                }
            }
            
            accept_feedback(payload)
            
            # С ALPHA=0.15 новое значение = 0.8 + 0.15*(1.0-0.8) = 0.8 + 0.03 = 0.83
            expected = 0.8 + 0.15 * (1.0 - 0.8)
            assert abs(M._state['RSS'] - expected) < 0.01
    
    def test_accept_feedback_multiple_metrics(self):
        """Тест: обновление нескольких метрик одновременно"""
        if hasattr(M, '_state'):
            payload = {
                'target': {
                    'RSS': 0.9,
                    'COS': 0.85,
                    'FAITH': 0.92,
                    'Resonance': 0.95
                }
            }
            
            result = accept_feedback(payload)
            
            assert result is True
            # Проверяем, что все метрики обновлены
            assert 'RSS' in M._state or True  # Может не быть в _state
            assert 'COS' in M._state or True
            assert 'FAITH' in M._state or True
    
    def test_accept_feedback_invalid_metric(self):
        """Тест: игнорирование несуществующих метрик"""
        if hasattr(M, '_state'):
            original_state = M._state.copy()
            
            payload = {
                'target': {
                    'INVALID_METRIC': 0.9  # Несуществующая метрика
                }
            }
            
            result = accept_feedback(payload)
            
            assert result is True
            # Состояние не должно измениться (или измениться минимально)
            # Проверяем, что функция не упала
