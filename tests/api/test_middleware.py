"""
Тесты для API middleware (безопасность, rate limiting)
"""
import pytest
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.middleware.security import SecurityHeadersMiddleware, RateLimitMiddleware


@pytest.fixture
def app():
    """Создать тестовое приложение"""
    app = FastAPI()
    
    # Добавляем middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=10,  # Низкий лимит для тестов
        requests_per_hour=100,
        burst_size=3
    )
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    @app.get("/api/health")
    def health():
        return {"status": "ok"}
    
    return app


@pytest.fixture
def client(app):
    """Создать тестового клиента"""
    return TestClient(app)


def test_security_headers(client):
    """Тест security headers"""
    response = client.get("/test")
    
    assert response.status_code == 200
    assert "Content-Security-Policy" in response.headers
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "X-XSS-Protection" in response.headers
    assert "Referrer-Policy" in response.headers


def test_rate_limit_success(client):
    """Тест успешных запросов в пределах лимита"""
    # Делаем несколько запросов
    for i in range(5):
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-RateLimit-Limit-Minute" in response.headers
        assert "X-RateLimit-Remaining-Minute" in response.headers


def test_rate_limit_exceeded(client):
    """Тест превышения rate limit"""
    # Делаем запросы до превышения лимита
    for i in range(11):  # Превышаем лимит в 10 запросов/минуту
        response = client.get("/test")
        if i < 10:
            assert response.status_code == 200
        else:
            # 11-й запрос должен быть заблокирован
            assert response.status_code == 429
            assert "Rate limit exceeded" in response.json()["error"]
            assert "Retry-After" in response.headers


def test_rate_limit_burst(client):
    """Тест burst limit"""
    # Делаем быстрые запросы (burst)
    responses = []
    for i in range(5):
        responses.append(client.get("/test"))
        time.sleep(0.1)  # Небольшая задержка
    
    # Первые 3 должны пройти (burst_size=3)
    # Остальные могут быть заблокированы
    success_count = sum(1 for r in responses if r.status_code == 200)
    assert success_count >= 3


def test_rate_limit_health_endpoint(client):
    """Тест что health endpoint не ограничен rate limit"""
    # Health endpoint должен пропускаться без ограничений
    for i in range(20):
        response = client.get("/api/health")
        assert response.status_code == 200


def test_rate_limit_headers(client):
    """Тест заголовков rate limit"""
    response = client.get("/test")
    
    assert "X-RateLimit-Limit-Minute" in response.headers
    assert "X-RateLimit-Remaining-Minute" in response.headers
    assert "X-RateLimit-Limit-Hour" in response.headers
    assert "X-RateLimit-Remaining-Hour" in response.headers
    
    # Проверяем значения
    limit_minute = int(response.headers["X-RateLimit-Limit-Minute"])
    remaining_minute = int(response.headers["X-RateLimit-Remaining-Minute"])
    
    assert limit_minute == 10
    assert 0 <= remaining_minute <= limit_minute









