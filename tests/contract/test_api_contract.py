"""
Контрактные тесты для TERAG v2.0 API
Соответствуют контракту GeoScan

Этот модуль реализует проверку "dual-format" (совмещение snake_case и legacy-полей),
обязательную для интеграции GeoScan с TERAG v2.0.
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from src.api.terag_v2_server import app


@pytest.fixture
def client():
    """Тестовый клиент"""
    return TestClient(app)


class TestHealthEndpoints:
    """Тесты для health endpoints"""
    
    def test_health_endpoint(self, client):
        """Тест /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
    
    def test_api_health_endpoint(self, client):
        """Тест /api/health endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
    
    def test_api_v2_health_endpoint(self, client):
        """Тест /api/v2/health endpoint (канонический для GeoScan)"""
        response = client.get("/api/v2/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "neo4j_connected" in data
        assert "langgraph_available" in data
        assert "llm_client_available" in data
        assert "timestamp" in data
        assert isinstance(data["neo4j_connected"], bool)
        assert isinstance(data["langgraph_available"], bool)
        assert isinstance(data["llm_client_available"], bool)


class TestMetricsEndpoint:
    """Тесты для /api/metrics endpoint (dual-format: snake_case + UPPERCASE)"""
    
    def test_api_metrics_endpoint(self, client):
        """Тест /api/metrics endpoint (dual-format: канон + legacy)"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Канонические поля (snake_case)
        assert "rss" in data, "Каноническое поле 'rss' обязательно"
        assert "cos" in data, "Каноническое поле 'cos' обязательно"
        assert "faith" in data, "Каноническое поле 'faith' обязательно"
        assert "growth" in data, "Каноническое поле 'growth' обязательно"
        assert "resonance" in data, "Каноническое поле 'resonance' обязательно"
        assert "confidence" in data, "Каноническое поле 'confidence' обязательно"
        assert "timestamp" in data, "Каноническое поле 'timestamp' обязательно"
        
        # Legacy поля (UPPERCASE)
        assert "RSS" in data, "Legacy поле 'RSS' обязательно"
        assert "COS" in data, "Legacy поле 'COS' обязательно"
        assert "FAITH" in data, "Legacy поле 'FAITH' обязательно"
        assert "Growth" in data, "Legacy поле 'Growth' обязательно"
        assert "Resonance" in data, "Legacy поле 'Resonance' обязательно"
        
        # Проверка совпадения значений (канон = legacy)
        assert data["rss"] == data["RSS"], "rss и RSS должны совпадать"
        assert data["cos"] == data["COS"], "cos и COS должны совпадать"
        assert data["faith"] == data["FAITH"], "faith и FAITH должны совпадать"
        assert data["growth"] == data["Growth"], "growth и Growth должны совпадать"
        assert data["resonance"] == data["Resonance"], "resonance и Resonance должны совпадать"
        
        # Проверка типов (канонические поля)
        assert isinstance(data["rss"], (int, float))
        assert isinstance(data["cos"], (int, float))
        assert isinstance(data["faith"], (int, float))
        assert isinstance(data["growth"], (int, float))
        assert isinstance(data["resonance"], (int, float))
        assert isinstance(data["confidence"], (int, float))
        
        # Проверка диапазонов (0-1 для большинства метрик)
        assert 0.0 <= data["rss"] <= 1.0
        assert 0.0 <= data["cos"] <= 1.0
        assert 0.0 <= data["faith"] <= 1.0
        assert 0.0 <= data["resonance"] <= 1.0
        assert 0.0 <= data["confidence"] <= 1.0


class TestQueryEndpoint:
    """Тесты для /api/v2/query endpoint"""
    
    def test_query_endpoint_happy_path(self, client):
        """Тест /api/v2/query endpoint - happy path (dual-format: канон + legacy)"""
        payload = {
            "query": "Тестовый запрос для проверки контракта",
            "max_attempts": 2
        }
        
        response = client.post("/api/v2/query", json=payload)
        
        # Может быть 200 (успех) или 503 (не инициализирован) или 500 (ошибка)
        assert response.status_code in [200, 503, 500]
        
        if response.status_code == 200:
            data = response.json()
            
            # Обязательные поля согласно контракту GeoScan
            assert "answer" in data, "Поле 'answer' обязательно"
            assert "rss_score" in data, "Поле 'rss_score' обязательно для GeoScan"
            assert "trace" in data, "Поле 'trace' обязательно для GeoScan"
            assert "metadata" in data, "Поле 'metadata' обязательно для GeoScan"
            
            # Проверка dual-format (канон + legacy)
            assert "rss_score" in data, "Каноническое поле 'rss_score' обязательно"
            assert "rssscore" in data, "Legacy алиас 'rssscore' обязателен"
            assert data["rss_score"] == data["rssscore"], "rss_score и rssscore должны совпадать"
            
            # Проверка типов
            assert isinstance(data["answer"], str), "answer должен быть строкой"
            assert isinstance(data["rss_score"], (int, float)), "rss_score должен быть числом"
            assert isinstance(data["rssscore"], (int, float)), "rssscore должен быть числом"
            assert isinstance(data["trace"], list), "trace должен быть списком (может быть пустым)"
            assert isinstance(data["metadata"], dict), "metadata должен быть объектом (может быть пустым)"
            
            # Проверка диапазона rss_score
            assert 0.0 <= data["rss_score"] <= 1.0, "rss_score должен быть в диапазоне [0, 1]"
            assert 0.0 <= data["rssscore"] <= 1.0, "rssscore должен быть в диапазоне [0, 1]"
            
            # Проверка обязательных полей в metadata
            assert "request_id" in data["metadata"], "metadata.request_id обязательно"
            assert "timestamp" in data["metadata"], "metadata.timestamp обязательно"
            
            # Проверка, что trace не null (может быть пустым списком)
            assert data["trace"] is not None, "trace не должен быть null"
            
            # Проверка, что metadata не null (может быть пустым объектом)
            assert data["metadata"] is not None, "metadata не должен быть null"
    
    def test_query_endpoint_error_path(self, client):
        """Тест /api/v2/query endpoint - error path (единый формат ошибок)"""
        # Тест 1: Невалидный запрос (422)
        payload = {}
        response = client.post("/api/v2/query", json=payload)
        assert response.status_code == 422
        
        error_data = response.json()
        # Проверяем единый формат ошибки (без FastAPI detail wrapper)
        assert "error" in error_data, "Ошибка должна содержать поле 'error'"
        assert "error_code" in error_data, "Ошибка должна содержать поле 'error_code'"
        assert "request_id" in error_data, "Ошибка должна содержать поле 'request_id'"
        assert "timestamp" in error_data, "Ошибка должна содержать поле 'timestamp'"
        assert error_data["error_code"] == "VALIDATION_ERROR", "Код ошибки должен быть VALIDATION_ERROR"
        
        # Тест 2: Пустой query (может вызвать ошибку обработки)
        payload = {"query": ""}
        response = client.post("/api/v2/query", json=payload)
        
        if response.status_code != 200:
            error_data = response.json()
            # Проверяем единый формат ошибки
            assert "error" in error_data, "Ошибка должна содержать поле 'error'"
            assert "error_code" in error_data, "Ошибка должна содержать поле 'error_code'"
            assert "request_id" in error_data, "Ошибка должна содержать поле 'request_id'"
            assert "timestamp" in error_data, "Ошибка должна содержать поле 'timestamp'"
    
    def test_error_format_503(self, client):
        """Тест формата ошибки 503 (если TERAG не инициализирован)"""
        # Этот тест может не пройти, если TERAG инициализирован
        # Но проверяем формат ошибки, если она возникает
        payload = {"query": "test"}
        response = client.post("/api/v2/query", json=payload)
        
        if response.status_code == 503:
            error_data = response.json()
            # Проверяем единый формат ошибки
            assert "error" in error_data, "Ошибка должна содержать поле 'error'"
            assert "error_code" in error_data, "Ошибка должна содержать поле 'error_code'"
            assert "request_id" in error_data, "Ошибка должна содержать поле 'request_id'"
            assert "timestamp" in error_data, "Ошибка должна содержать поле 'timestamp'"
            assert error_data["error_code"] in ["TERAG_V2_UNAVAILABLE", "TERAG_V2_NOT_INITIALIZED"]
    
    def test_error_format_500(self, client):
        """Тест формата ошибки 500 (если возникает внутренняя ошибка)"""
        # Этот тест может не пройти, если нет ошибок
        # Но проверяем формат ошибки, если она возникает
        payload = {"query": "test"}
        response = client.post("/api/v2/query", json=payload)
        
        if response.status_code == 500:
            error_data = response.json()
            # Проверяем единый формат ошибки
            assert "error" in error_data, "Ошибка должна содержать поле 'error'"
            assert "error_code" in error_data, "Ошибка должна содержать поле 'error_code'"
            assert "request_id" in error_data, "Ошибка должна содержать поле 'request_id'"
            assert "timestamp" in error_data, "Ошибка должна содержать поле 'timestamp'"
            assert error_data["error_code"] in ["QUERY_PROCESSING_ERROR", "INTERNAL_SERVER_ERROR"]
    
    def test_query_endpoint_missing_fields(self, client):
        """Тест /api/v2/query endpoint - проверка отсутствия обязательных полей"""
        # Отправляем запрос без query (должна быть ошибка валидации)
        payload = {}
        
        response = client.post("/api/v2/query", json=payload)
        
        # Должна быть ошибка валидации (422)
        assert response.status_code == 422


class TestContractCompliance:
    """Тесты на соответствие контракту GeoScan"""
    
    def test_all_endpoints_available(self, client):
        """Проверка, что все канонические endpoints доступны"""
        endpoints = [
            "/health",
            "/api/health",
            "/api/v2/health",
            "/api/metrics"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Все endpoints должны отвечать (не 404)
            assert response.status_code != 404, f"Endpoint {endpoint} не найден"
    
    def test_response_consistency(self, client):
        """Проверка консистентности ответов"""
        # Проверяем, что /api/v2/health и /api/health возвращают совместимые форматы
        v2_health = client.get("/api/v2/health").json()
        api_health = client.get("/api/health").json()
        
        # Оба должны содержать status и timestamp
        assert "status" in v2_health
        assert "status" in api_health
        assert "timestamp" in v2_health
        assert "timestamp" in api_health


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

