"""
Circuit Breaker Middleware для FastAPI
"""

import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.circuit_breaker import CircuitBreakerOpenError, get_neo4j_circuit_breaker
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    """Middleware для применения Circuit Breaker к запросам"""
    
    def __init__(self, app: ASGIApp):
        """
        Инициализация Circuit Breaker middleware
        
        Args:
            app: ASGI приложение
        """
        super().__init__(app)
        self.breaker = get_neo4j_circuit_breaker()
        logger.info("CircuitBreakerMiddleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Обработка запроса с Circuit Breaker
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
        
        Returns:
            HTTP ответ
        """
        # Пропускаем health check и metrics endpoints
        if request.url.path in ["/health", "/api/health", "/metrics/prometheus", "/"]:
            return await call_next(request)
        
        # Применяем Circuit Breaker только к запросам, которые используют Neo4j
        neo4j_paths = ["/api/v2/query", "/api/query", "/api/graph", "/api/v2"]
        
        if any(request.url.path.startswith(path) for path in neo4j_paths):
            # Проверяем состояние Circuit Breaker перед выполнением
            if self.breaker.state.value == "OPEN":
                # Проверяем, можно ли перейти в HALF_OPEN
                if self.breaker.last_failure_time:
                    from datetime import datetime
                    elapsed = (datetime.utcnow() - self.breaker.last_failure_time).total_seconds()
                    if elapsed < self.breaker.timeout_seconds:
                        logger.warning(f"Circuit Breaker OPEN: {request.url.path}")
                        return JSONResponse(
                            status_code=503,
                            content={
                                "error": "Service temporarily unavailable",
                                "message": "Circuit Breaker is OPEN",
                                "retry_after": self.breaker.timeout_seconds
                            },
                            headers={"Retry-After": str(self.breaker.timeout_seconds)}
                        )
                    else:
                        # Переходим в HALF_OPEN
                        self.breaker.state = self.breaker.state.__class__("HALF_OPEN")
                        self.breaker.success_count = 0
            
            try:
                # Выполняем запрос и измеряем latency
                import time
                start_time = time.time()
                response = await call_next(request)
                latency_ms = (time.time() - start_time) * 1000
                
                # Обновляем Circuit Breaker
                if latency_ms > self.breaker.latency_threshold_ms:
                    self.breaker._on_latency_exceeded(latency_ms)
                else:
                    self.breaker._on_success()
                
                return response
            except Exception as e:
                self.breaker._on_failure()
                raise
                logger.warning(f"Circuit Breaker OPEN: {request.url.path}")
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": "Service temporarily unavailable",
                        "message": str(e),
                        "retry_after": self.breaker.timeout_seconds
                    },
                    headers={"Retry-After": str(self.breaker.timeout_seconds)}
                )
        
        # Для остальных запросов выполняем без Circuit Breaker
        return await call_next(request)
