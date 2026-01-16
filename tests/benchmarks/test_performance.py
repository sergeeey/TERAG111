#!/usr/bin/env python3
"""
Бенчмарки производительности для TERAG
"""
import pytest
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestKAGBuilderPerformance:
    """Бенчмарки для KAG Builder"""
    
    @pytest.mark.benchmark
    def test_extract_triplets_performance(self, benchmark):
        """Бенчмарк извлечения триплетов"""
        from src.core.kag_builder import extract_triplets_from_text
        
        text = "Это тестовый документ. " * 100  # 100 предложений
        
        result = benchmark(extract_triplets_from_text, text, "ru")
        
        assert len(result) > 0
        # Проверяем, что обработка заняла менее 1 секунды
        assert benchmark.stats['mean'] < 1.0


class TestMetricsPerformance:
    """Бенчмарки для метрик"""
    
    @pytest.mark.benchmark
    def test_get_metrics_snapshot_performance(self, benchmark):
        """Бенчмарк получения метрик"""
        from src.core.metrics import get_metrics_snapshot
        
        result = benchmark(get_metrics_snapshot)
        
        assert "RSS" in result
        # Проверяем, что получение метрик быстрое (< 10ms)
        assert benchmark.stats['mean'] < 0.01


class TestAPIPerformance:
    """Бенчмарки для API"""
    
    @pytest.mark.benchmark
    def test_api_response_time(self, benchmark):
        """Бенчмарк времени ответа API"""
        from fastapi.testclient import TestClient
        from src.api.server import app
        
        client = TestClient(app)
        
        def get_metrics():
            return client.get("/api/metrics")
        
        response = benchmark(get_metrics)
        
        assert response.status_code == 200
        # Проверяем, что ответ быстрый (< 100ms)
        assert benchmark.stats['mean'] < 0.1


class TestDocumentProcessingPerformance:
    """Бенчмарки обработки документов"""
    
    @pytest.mark.benchmark
    def test_language_detection_performance(self, benchmark):
        """Бенчмарк определения языка"""
        from src.core.doc_converter import detect_language
        
        text = "Это русский текст для проверки производительности определения языка. " * 10
        
        result = benchmark(detect_language, text)
        
        assert result in ["ru", "en", "unknown"]
        # Проверяем, что определение языка быстрое (< 100ms)
        assert benchmark.stats['mean'] < 0.1














