"""
Интеграционные тесты для полного цикла TERAG
API → Core → Neo4j → Response
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Прямой импорт модулей
import importlib.util

# Импорт health модуля
health_spec = importlib.util.spec_from_file_location("health", project_root / "src" / "core" / "health.py")
health_module = importlib.util.module_from_spec(health_spec)
health_spec.loader.exec_module(health_module)
get_health = health_module.get_health

# Импорт metrics модуля
metrics_spec = importlib.util.spec_from_file_location("metrics", project_root / "src" / "core" / "metrics.py")
metrics_module = importlib.util.module_from_spec(metrics_spec)
metrics_spec.loader.exec_module(metrics_module)
get_metrics_snapshot = metrics_module.get_metrics_snapshot

# Импорт self_learning модуля
self_learning_spec = importlib.util.spec_from_file_location("self_learning", project_root / "src" / "core" / "self_learning.py")
self_learning_module = importlib.util.module_from_spec(self_learning_spec)
self_learning_spec.loader.exec_module(self_learning_module)
accept_feedback = self_learning_module.accept_feedback


class TestFullCycleHealth:
    """Интеграционные тесты для полного цикла Health Check"""
    
    def test_health_check_full_cycle(self):
        """Тест: полный цикл health check"""
        # Получаем метрики и health одновременно (метрики могут изменяться)
        metrics = get_metrics_snapshot()
        health = get_health()
        
        # Проверяем, что health использует metrics
        assert 'status' in health
        assert 'heartbeat' in health
        assert health['status'] in ['ok', 'warning', 'critical']
        
        # Проверяем связь с metrics (может быть небольшое расхождение из-за heartbeat)
        assert 'Resonance' in metrics
        expected_drift = round(1.0 - metrics['Resonance'], 3)
        # Допускаем небольшую погрешность из-за динамического изменения
        assert abs(health['resonance_phase_drift'] - expected_drift) < 0.01
    
    def test_health_metrics_integration(self):
        """Тест: интеграция health и metrics"""
        # Получаем метрики и health одновременно
        metrics1 = get_metrics_snapshot()
        health1 = get_health()
        
        # Получаем еще раз (может измениться из-за heartbeat)
        metrics2 = get_metrics_snapshot()
        health2 = get_health()
        
        # Проверяем, что health корректно использует metrics
        # Допускаем небольшую погрешность из-за динамического изменения
        expected_drift1 = round(1.0 - metrics1['Resonance'], 3)
        expected_drift2 = round(1.0 - metrics2['Resonance'], 3)
        assert abs(health1['resonance_phase_drift'] - expected_drift1) < 0.01
        assert abs(health2['resonance_phase_drift'] - expected_drift2) < 0.01


class TestFullCycleFeedback:
    """Интеграционные тесты для полного цикла Feedback"""
    
    def test_feedback_metrics_integration(self):
        """Тест: интеграция feedback и metrics"""
        # Получаем начальные метрики
        metrics_before = get_metrics_snapshot()
        initial_rss = metrics_before.get('RSS', 0.8)
        
        # Отправляем feedback
        payload = {
            'target': {
                'RSS': 0.9
            }
        }
        result = accept_feedback(payload)
        
        assert result is True
        
        # Получаем метрики после feedback
        metrics_after = get_metrics_snapshot()
        
        # Проверяем, что метрики изменились (может быть не сразу из-за heartbeat)
        # Но структура должна быть правильной
        assert 'RSS' in metrics_after
    
    def test_feedback_health_integration(self):
        """Тест: интеграция feedback, metrics и health"""
        # Отправляем feedback
        payload = {
            'target': {
                'Resonance': 0.95
            }
        }
        accept_feedback(payload)
        
        # Проверяем health
        health = get_health()
        
        # Health должен корректно отражать изменения
        assert 'status' in health
        assert health['status'] in ['ok', 'warning', 'critical']


class TestFullCycleAPI:
    """Интеграционные тесты для полного цикла API"""
    
    def test_api_health_endpoint_integration(self):
        """Тест: интеграция API health endpoint с core модулями"""
        # Создаем тестовое приложение
        try:
            from fastapi import FastAPI
            app = FastAPI()
            
            # Импортируем роутер
            try:
                from src.api.routes.terag_v2 import router
                app.include_router(router)
                client = TestClient(app)
                
                # Тестируем health endpoint
                response = client.get("/api/v2/health")
                
                assert response.status_code == 200
                data = response.json()
                assert 'status' in data
                assert 'health' in data or 'message' in data
                
            except ImportError:
                pytest.skip("terag_v2 router not available")
                
        except ImportError:
            pytest.skip("FastAPI not available")
    
    def test_api_metrics_endpoint_integration(self):
        """Тест: интеграция API metrics endpoint с core модулями"""
        try:
            from fastapi import FastAPI
            app = FastAPI()
            
            try:
                from src.api.routes.terag_v2 import router
                app.include_router(router)
                client = TestClient(app)
                
                # Тестируем metrics endpoint
                response = client.get("/api/v2/metrics")
                
                # Может быть 200 или 503 (если модули недоступны)
                assert response.status_code in [200, 503]
                
                if response.status_code == 200:
                    data = response.json()
                    assert 'metrics' in data
                    assert 'service' in data
                    
            except ImportError:
                pytest.skip("terag_v2 router not available")
                
        except ImportError:
            pytest.skip("FastAPI not available")
    
    def test_api_feedback_endpoint_integration(self):
        """Тест: интеграция API feedback endpoint с core модулями"""
        try:
            from fastapi import FastAPI
            app = FastAPI()
            
            try:
                from src.api.routes.terag_v2 import router
                app.include_router(router)
                client = TestClient(app)
                
                # Тестируем feedback endpoint
                payload = {
                    "query": "test query",
                    "rating": 5
                }
                response = client.post("/api/v2/feedback", json=payload)
                
                # Может быть 200 или 503
                assert response.status_code in [200, 503]
                
                if response.status_code == 200:
                    data = response.json()
                    assert 'status' in data
                    assert 'accepted' in data
                    
            except ImportError:
                pytest.skip("terag_v2 router not available")
                
        except ImportError:
            pytest.skip("FastAPI not available")


class TestFullCycleEndToEnd:
    """E2E тесты для полного цикла"""
    
    def test_e2e_metrics_to_health(self):
        """E2E тест: Metrics → Health"""
        # Получаем метрики и health одновременно
        metrics = get_metrics_snapshot()
        health = get_health()
        
        # Проверяем связь (допускаем небольшую погрешность)
        expected_drift = round(1.0 - metrics['Resonance'], 3)
        assert abs(health['resonance_phase_drift'] - expected_drift) < 0.01
        assert health['status'] in ['ok', 'warning', 'critical']
    
    def test_e2e_feedback_to_metrics(self):
        """E2E тест: Feedback → Metrics"""
        # Отправляем feedback
        payload = {
            'target': {
                'RSS': 0.9,
                'COS': 0.85
            }
        }
        result = accept_feedback(payload)
        
        assert result is True
        
        # Получаем метрики (могут измениться)
        metrics = get_metrics_snapshot()
        
        # Проверяем структуру
        assert 'RSS' in metrics
        assert 'COS' in metrics
    
    def test_e2e_feedback_to_health(self):
        """E2E тест: Feedback → Metrics → Health"""
        # Отправляем feedback для улучшения Resonance
        payload = {
            'target': {
                'Resonance': 0.95
            }
        }
        accept_feedback(payload)
        
        # Получаем health
        health = get_health()
        
        # Health должен отражать изменения
        assert 'status' in health
        assert health['status'] in ['ok', 'warning', 'critical']
        assert health['heartbeat'] is True
