"""
Security Middleware для TERAG API
- CSP (Content Security Policy) headers
- Rate limiting
- Security headers
"""
import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware для добавления security headers
    Включает CSP, HSTS, X-Frame-Options и другие
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' http://localhost:* ws://localhost:*; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        
        # Security headers
        response.headers["Content-Security-Policy"] = csp_policy
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS (только для HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware
    Ограничивает количество запросов от одного IP
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        
        # Хранилище для отслеживания запросов
        # В production следует использовать Redis
        self._minute_requests: Dict[str, list] = defaultdict(list)
        self._hour_requests: Dict[str, list] = defaultdict(list)
        self._last_cleanup = time.time()
        
        logger.info(
            f"RateLimitMiddleware initialized: "
            f"{requests_per_minute}/min, {requests_per_hour}/hour, burst={burst_size}"
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Получить IP клиента"""
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self):
        """Очистить старые записи (каждые 5 минут)"""
        current_time = time.time()
        if current_time - self._last_cleanup < 300:  # 5 минут
            return
        
        self._last_cleanup = current_time
        
        # Очистка минутных запросов (старше 1 минуты)
        minute_cutoff = current_time - 60
        for ip in list(self._minute_requests.keys()):
            self._minute_requests[ip] = [
                ts for ts in self._minute_requests[ip] if ts > minute_cutoff
            ]
            if not self._minute_requests[ip]:
                del self._minute_requests[ip]
        
        # Очистка часовых запросов (старше 1 часа)
        hour_cutoff = current_time - 3600
        for ip in list(self._hour_requests.keys()):
            self._hour_requests[ip] = [
                ts for ts in self._hour_requests[ip] if ts > hour_cutoff
            ]
            if not self._hour_requests[ip]:
                del self._hour_requests[ip]
    
    def _check_rate_limit(self, ip: str) -> tuple:
        """
        Проверить rate limit для IP
        
        Returns:
            (allowed, error_message)
        """
        current_time = time.time()
        
        # Очистка старых записей
        self._cleanup_old_requests()
        
        # Проверка burst (быстрые запросы)
        minute_requests = self._minute_requests[ip]
        recent_requests = [ts for ts in minute_requests if ts > current_time - 1]
        if len(recent_requests) >= self.burst_size:
            return False, "Too many requests in short time (burst limit)"
        
        # Проверка лимита в минуту
        minute_requests = [ts for ts in minute_requests if ts > current_time - 60]
        if len(minute_requests) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
        
        # Проверка лимита в час
        hour_requests = self._hour_requests[ip]
        hour_requests = [ts for ts in hour_requests if ts > current_time - 3600]
        if len(hour_requests) >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"
        
        # Запрос разрешен - добавляем timestamp
        self._minute_requests[ip].append(current_time)
        self._hour_requests[ip].append(current_time)
        
        return True, None
    
    async def dispatch(self, request: Request, call_next):
        # Пропускаем health check и metrics endpoints
        if request.url.path in ["/api/health", "/metrics/prometheus", "/"]:
            return await call_next(request)
        
        # Получаем IP клиента
        client_ip = self._get_client_ip(request)
        
        # Проверяем rate limit
        allowed, error_msg = self._check_rate_limit(client_ip)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for IP {client_ip}: {error_msg}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": error_msg,
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Добавляем заголовки с информацией о лимитах
        minute_count = len([ts for ts in self._minute_requests[client_ip] if ts > time.time() - 60])
        hour_count = len([ts for ts in self._hour_requests[client_ip] if ts > time.time() - 3600])
        
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, self.requests_per_minute - minute_count))
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(max(0, self.requests_per_hour - hour_count))
        
        return response
