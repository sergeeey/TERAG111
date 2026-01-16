"""
Тесты для API routes terag_v2.py
Проверка эндпоинтов TERAG v2.0
"""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.api.routes.terag_v2 import router
except ImportError:
    # Если модуль не найден, пропускаем тесты
    pytest.skip("terag_v2 router not available", allow_module_level=True)


# Создаем тестовое приложение
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestTeragV2Root:
    """Тесты для корневого эндпоинта /api/v2/"""
    
    def test_root_endpoint(self):
        """Тест: корневой эндпоинт возвращает правильный ответ"""
        response = client.get("/api/v2/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "TERAG v2.0 API"
        assert data["version"] == "2.0"
        assert data["status"] == "ok"
        assert "timestamp" in data
    
    def test_root_endpoint_timestamp_format(self):
        """Тест: timestamp в правильном формате ISO"""
        response = client.get("/api/v2/")
        
        assert response.status_code == 200
        data = response.json()
        assert "T" in data["timestamp"]  # ISO format
        assert "Z" in data["timestamp"] or "+" in data["timestamp"]  # UTC


class TestTeragV2Health:
    """Тесты для эндпоинта /api/v2/health"""
    
    @patch('src.api.routes.terag_v2.get_health')
    def test_health_endpoint_success(self, mock_get_health):
        """Тест: health endpoint возвращает статус при доступных модулях"""
        mock_get_health.return_value = {
            "status": "healthy",
            "components": {
                "neo4j": {"status": "connected"},
                "openai": {"status": "configured"}
            }
        }
        
        response = client.get("/api/v2/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "TERAG v2.0"
        assert "health" in data
        assert "timestamp" in data
    
    @patch('src.api.routes.terag_v2.CORE_AVAILABLE', False)
    def test_health_endpoint_degraded(self):
        """Тест: health endpoint возвращает degraded при недоступных модулях"""
        response = client.get("/api/v2/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["service"] == "TERAG v2.0"
        assert "message" in data or "health" in data
    
    @patch('src.api.routes.terag_v2.get_health')
    def test_health_endpoint_error(self, mock_get_health):
        """Тест: обработка ошибок в health endpoint"""
        mock_get_health.side_effect = Exception("Test error")
        
        response = client.get("/api/v2/health")
        
        # Должен вернуть error статус
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error" or "error" in data


class TestTeragV2Metrics:
    """Тесты для эндпоинта /api/v2/metrics"""
    
    @patch('src.api.routes.terag_v2.get_metrics_snapshot')
    def test_metrics_endpoint_success(self, mock_get_metrics):
        """Тест: metrics endpoint возвращает метрики"""
        mock_get_metrics.return_value = {
            "rss_score": 0.88,
            "cos_score": 0.86,
            "faith_score": 0.89,
            "growth_rate": 0.002,
            "resonance": 0.92
        }
        
        response = client.get("/api/v2/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "TERAG v2.0"
        assert "metrics" in data
        assert "timestamp" in data
        assert data["metrics"]["rss_score"] == 0.88
    
    @patch('src.api.routes.terag_v2.CORE_AVAILABLE', False)
    def test_metrics_endpoint_unavailable(self):
        """Тест: metrics endpoint возвращает 503 при недоступных модулях"""
        response = client.get("/api/v2/metrics")
        
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
    
    @patch('src.api.routes.terag_v2.get_metrics_snapshot')
    def test_metrics_endpoint_error(self, mock_get_metrics):
        """Тест: обработка ошибок в metrics endpoint"""
        mock_get_metrics.side_effect = Exception("Test error")
        
        response = client.get("/api/v2/metrics")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestTeragV2Feedback:
    """Тесты для эндпоинта /api/v2/feedback"""
    
    @patch('src.api.routes.terag_v2.accept_feedback')
    def test_feedback_endpoint_success(self, mock_accept_feedback):
        """Тест: feedback endpoint принимает обратную связь"""
        mock_accept_feedback.return_value = True
        
        payload = {
            "query": "test query",
            "rating": 5,
            "comment": "Great result"
        }
        
        response = client.post("/api/v2/feedback", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "TERAG v2.0"
        assert data["accepted"] is True
        assert "timestamp" in data
    
    @patch('src.api.routes.terag_v2.CORE_AVAILABLE', False)
    def test_feedback_endpoint_unavailable(self):
        """Тест: feedback endpoint возвращает 503 при недоступных модулях"""
        payload = {"query": "test"}
        
        response = client.post("/api/v2/feedback", json=payload)
        
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
    
    @patch('src.api.routes.terag_v2.accept_feedback')
    def test_feedback_endpoint_error(self, mock_accept_feedback):
        """Тест: обработка ошибок в feedback endpoint"""
        mock_accept_feedback.side_effect = Exception("Test error")
        
        payload = {"query": "test"}
        
        response = client.post("/api/v2/feedback", json=payload)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestTeragV2Status:
    """Тесты для эндпоинта /api/v2/status"""
    
    def test_status_endpoint(self):
        """Тест: status endpoint возвращает общий статус"""
        response = client.get("/api/v2/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "TERAG v2.0"
        assert data["version"] == "2.0"
        assert "status" in data
        assert "core_modules_available" in data
        assert "timestamp" in data
    
    @patch('src.api.routes.terag_v2.CORE_AVAILABLE', True)
    def test_status_endpoint_operational(self):
        """Тест: status показывает operational при доступных модулях"""
        response = client.get("/api/v2/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["core_modules_available"] is True
    
    @patch('src.api.routes.terag_v2.CORE_AVAILABLE', False)
    def test_status_endpoint_degraded(self):
        """Тест: status показывает degraded при недоступных модулях"""
        response = client.get("/api/v2/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["core_modules_available"] is False
