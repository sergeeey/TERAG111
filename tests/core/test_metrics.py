#!/usr/bin/env python3
"""
Тесты для metrics.py
"""
import pytest
import os
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.metrics import get_metrics_snapshot, heartbeat


class TestGetMetricsSnapshot:
    """Тесты для функции get_metrics_snapshot"""
    
    def test_get_metrics_snapshot_structure(self):
        """Тест структуры возвращаемых метрик"""
        metrics = get_metrics_snapshot()
        
        # Проверяем наличие всех ключевых метрик
        assert "RSS" in metrics
        assert "COS" in metrics
        assert "FAITH" in metrics
        assert "Growth" in metrics
        assert "Resonance" in metrics
        assert "confidence" in metrics
        assert "timestamp" in metrics
    
    def test_get_metrics_snapshot_values_range(self):
        """Тест диапазона значений метрик"""
        metrics = get_metrics_snapshot()
        
        # Проверяем, что значения в разумных пределах
        assert 0.0 <= metrics["RSS"] <= 1.0
        assert 0.0 <= metrics["COS"] <= 1.0
        assert 0.0 <= metrics["FAITH"] <= 1.0
        assert 0.0 <= metrics["Resonance"] <= 1.0
        assert 0.0 <= metrics["confidence"] <= 1.0
    
    def test_get_metrics_snapshot_timestamp(self):
        """Тест формата timestamp"""
        metrics = get_metrics_snapshot()
        
        assert "timestamp" in metrics
        # Проверяем, что timestamp в формате ISO
        assert "T" in metrics["timestamp"] or "Z" in metrics["timestamp"]


class TestHeartbeat:
    """Тесты для функции heartbeat"""
    
    @patch('src.core.metrics.append_cycle')
    @patch('src.core.metrics.get_phase')
    @patch('src.core.metrics.update_phase')
    def test_heartbeat_calls(self, mock_update, mock_get, mock_append):
        """Тест вызовов функций в heartbeat"""
        mock_get.return_value = 0.5
        
        heartbeat()
        
        # Проверяем, что функции вызваны
        mock_get.assert_called()
        mock_update.assert_called()
        mock_append.assert_called()














