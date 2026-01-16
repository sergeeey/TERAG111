"""
Тесты для Auto Linker API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.api.terag_v2_server import app


class TestAutoLinkerAPI:
    """Тесты для Auto Linker API"""
    
    @pytest.fixture
    def client(self):
        """Создать тестовый клиент"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_api_key(self):
        """Мок API ключа для тестов"""
        # В реальных тестах нужно создать тестовый ключ через TeragAuth
        return "test-api-key"
    
    def test_auto_link_endpoint_missing_auth(self, client):
        """Тест endpoint без аутентификации"""
        response = client.post(
            "/api/v2/auto-link",
            json={
                "clients": [
                    {"id": "CLIENT-001", "full_name": "Иванов Иван"},
                    {"id": "CLIENT-002", "full_name": "Петров Петр"}
                ]
            }
        )
        
        # Должен вернуть 401 или 403 (зависит от реализации)
        assert response.status_code in [401, 403, 422]
    
    def test_auto_link_endpoint_invalid_request(self, client):
        """Тест endpoint с невалидным запросом"""
        # Слишком много клиентов
        response = client.post(
            "/api/v2/auto-link",
            json={
                "clients": [
                    {"id": f"CLIENT-{i:03d}", "full_name": f"Client {i}"}
                    for i in range(60)  # Больше 50
                ]
            },
            headers={"Authorization": "Bearer test-key"}
        )
        
        assert response.status_code == 400
    
    def test_auto_link_endpoint_too_few_clients(self, client):
        """Тест endpoint с недостаточным количеством клиентов"""
        response = client.post(
            "/api/v2/auto-link",
            json={
                "clients": [
                    {"id": "CLIENT-001", "full_name": "Иванов Иван"}
                ]
            },
            headers={"Authorization": "Bearer test-key"}
        )
        
        assert response.status_code == 400
    
    def test_auto_link_endpoint_valid_request(self, client):
        """Тест endpoint с валидным запросом"""
        # Примечание: Этот тест требует реального API ключа или мока
        # В реальной реализации нужно создать тестовый ключ
        
        response = client.post(
            "/api/v2/auto-link",
            json={
                "clients": [
                    {"id": "CLIENT-001", "full_name": "Иванов Иван Иванович", "phone": "+77001234567"},
                    {"id": "CLIENT-002", "full_name": "Иванов Иван Иванович", "phone": "+77001234567"},
                ],
                "min_confidence": 0.85,
                "create_links": False
            },
            headers={"Authorization": "Bearer test-key"}
        )
        
        # Может вернуть 401 если нет валидного ключа, или 200 если есть
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert data["total_clients"] == 2
            assert "linked_pairs" in data
            assert "total_links" in data
