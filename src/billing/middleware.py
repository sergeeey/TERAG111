"""
Billing middleware для автоматического трекинга запросов
"""

import logging
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.billing.core import BillingCore
from src.billing.models import QueryType

logger = logging.getLogger(__name__)


class BillingMiddleware(BaseHTTPMiddleware):
    """Middleware для автоматического трекинга использования API"""
    
    def __init__(
        self,
        app: ASGIApp,
        billing_core: BillingCore = None
    ):
        """
        Инициализация billing middleware
        
        Args:
            app: ASGI приложение
            billing_core: Экземпляр BillingCore (создается автоматически если не передан)
        """
        super().__init__(app)
        self.billing = billing_core or BillingCore()
        logger.info("BillingMiddleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Обработка запроса с трекингом использования
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
        
        Returns:
            HTTP ответ
        """
        # Пропускаем health check и metrics endpoints
        if request.url.path in ["/health", "/api/health", "/metrics/prometheus", "/"]:
            return await call_next(request)
        
        # Пропускаем billing endpoints (чтобы избежать рекурсии)
        if request.url.path.startswith("/api/v2/billing"):
            return await call_next(request)
        
        # Получаем client_id из заголовка или query параметра
        client_id = request.headers.get("X-Client-ID") or request.query_params.get("client_id")
        api_key_id = request.headers.get("X-API-Key-ID")
        
        # Если нет client_id, пропускаем трекинг
        if not client_id:
            return await call_next(request)
        
        # Определяем тип запроса по пути
        query_type = self._determine_query_type(request.url.path)
        
        # Засекаем время начала
        start_time = time.time()
        
        try:
            # Выполняем запрос
            response = await call_next(request)
            
            # Рассчитываем латентность
            latency_ms = (time.time() - start_time) * 1000
            
            # Пытаемся получить информацию о токенах из ответа (если есть)
            tokens_in = 0
            tokens_out = 0
            
            # Если ответ содержит JSON, пытаемся извлечь токены
            if response.headers.get("content-type", "").startswith("application/json"):
                try:
                    import json
                    body = b""
                    async for chunk in response.body_iterator:
                        body += chunk
                    
                    # Парсим JSON
                    data = json.loads(body.decode())
                    tokens_in = data.get("tokens_in", 0)
                    tokens_out = data.get("tokens_out", 0)
                    
                    # Создаем новый response с телом
                    from starlette.responses import Response as StarletteResponse
                    response = StarletteResponse(
                        content=body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.headers.get("content-type")
                    )
                except Exception:
                    pass  # Игнорируем ошибки парсинга
            
            # Записываем использование (асинхронно, не блокируем ответ)
            try:
                self.billing.record_usage(
                    client_id=client_id,
                    query_type=query_type,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    latency_ms=latency_ms,
                    api_key_id=api_key_id
                )
            except Exception as e:
                logger.warning(f"Failed to record usage: {e}")
                # Не прерываем запрос, если биллинг не работает
        
        except Exception as e:
            # В случае ошибки все равно записываем использование
            latency_ms = (time.time() - start_time) * 1000
            try:
                self.billing.record_usage(
                    client_id=client_id,
                    query_type=query_type,
                    tokens_in=0,
                    tokens_out=0,
                    latency_ms=latency_ms,
                    api_key_id=api_key_id
                )
            except Exception:
                pass
            raise
        
        return response
    
    def _determine_query_type(self, path: str) -> str:
        """
        Определить тип запроса по пути
        
        Args:
            path: URL путь
        
        Returns:
            Тип запроса (simple, fraud_ring, predictive)
        """
        # Простые запросы
        if "/api/query" in path or "/api/v2/query" in path:
            return "simple"
        
        # Fraud ring detection
        if "/fraud" in path or "/fraud_ring" in path:
            return "fraud_ring"
        
        # Predictive analytics
        if "/predict" in path or "/predictive" in path or "/analytics" in path:
            return "predictive"
        
        # По умолчанию - simple
        return "simple"
