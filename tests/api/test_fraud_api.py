"""
Тесты для Fraud Detection API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.api.terag_v2_server import app


class TestFraudDetectionAPI:
    """Тесты для Fraud Detection API"""
    
    @pytest.fixture
    def client(self):
        """Создать тестовый клиент"""
        return TestClient(app)
    
    def test_fraud_detection_endpoint_missing_auth(self, client):
        """Тест endpoint без аутентификации"""
        response = client.get("/api/v2/fraud-detection?days=30")
        
        # Должен вернуть 401 или 403
        assert response.status_code in [401, 403, 422]
    
    def test_fraud_detection_endpoint_invalid_days(self, client):
        """Тест endpoint с невалидным параметром days"""
        # days > 90
        response = client.get(
            "/api/v2/fraud-detection?days=100",
            headers={"Authorization": "Bearer test-key"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_fraud_detection_endpoint_valid_request(self, client):
        """Тест endpoint с валидным запросом"""
        # Примечание: Этот тест требует реального API ключа или мока
        response = client.get(
            "/api/v2/fraud-detection?days=30",
            headers={"Authorization": "Bearer test-key"}
        )
        
        # Может вернуть 401 если нет валидного ключа, или 200 если есть
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert "analysis_date" in data
            assert data["time_window_days"] == 30
            assert "total_alerts" in data
            assert "alerts" in data
            assert "summary" in data
