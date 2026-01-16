"""
Role-based Rate Limiter для TERAG API
"""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.security.roles import Role
from src.api.dependencies import verify_api_key

logger = logging.getLogger(__name__)


class RoleBasedRateLimiter(BaseHTTPMiddleware):
    """
    Rate Limiter на основе ролей
    
    Лимиты:
    - ADMIN: 200 req/min
    - ANALYST: 100 req/min
    - CLIENT: 50 req/min
    """
    
    def __init__(self, app):
        """
        Инициализация Role-based Rate Limiter
        
        Args:
            app: ASGI приложение
        """
        super().__init__(app)
        
        # Лимиты по ролям: (requests_per_minute, requests_per_hour)
        self.limits = {
            Role.ADMIN: (200, 3600),      # 200 per minute, 3600 per hour
            Role.ANALYST: (100, 1800),   # 100 per minute, 1800 per hour
            Role.CLIENT: (50, 900),      # 50 per minute, 900 per hour
        }
        
        # Хранилище для отслеживания запросов по API ключам
        # В production следует использовать Redis
        self._minute_requests: Dict[str, list] = defaultdict(list)
        self._hour_requests: Dict[str, list] = defaultdict(list)
        self._last_cleanup = time.time()
        
        logger.info("RoleBasedRateLimiter initialized")
    
    def _get_api_key_from_request(self, request: Request) -> Optional[str]:
        """
        Извлечь API ключ из запроса
        
        Args:
            request: HTTP запрос
        
        Returns:
            API ключ или None
        """
        # Проверяем Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Убираем "Bearer "
        
        # Проверяем X-API-Key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key
        
        return None
    
    def _get_role_from_api_key(self, api_key: str) -> Optional[Role]:
        """
        Получить роль из API ключа (без полной верификации)
        
        Args:
            api_key: API ключ
        
        Returns:
            Роль или None
        """
        try:
            from src.security.api_auth import TeragAuth
            auth = TeragAuth()
            api_key_obj = auth.verify_key(api_key)
            if api_key_obj:
                return api_key_obj.role
        except Exception:
            pass
        
        return None
    
    def _cleanup_old_requests(self):
        """Очистить старые записи"""
        current_time = time.time()
        if current_time - self._last_cleanup < 300:  # Каждые 5 минут
            return
        
        self._last_cleanup = current_time
        
        # Очистка минутных запросов
        minute_cutoff = current_time - 60
        for key in list(self._minute_requests.keys()):
            self._minute_requests[key] = [
                ts for ts in self._minute_requests[key] if ts > minute_cutoff
            ]
            if not self._minute_requests[key]:
                del self._minute_requests[key]
        
        # Очистка часовых запросов
        hour_cutoff = current_time - 3600
        for key in list(self._hour_requests.keys()):
            self._hour_requests[key] = [
                ts for ts in self._hour_requests[key] if ts > hour_cutoff
            ]
            if not self._hour_requests[key]:
                del self._hour_requests[key]
    
    def _check_rate_limit(self, api_key: str, role: Role) -> tuple[bool, Optional[str]]:
        """
        Проверить rate limit для API ключа
        
        Args:
            api_key: API ключ
            role: Роль пользователя
        
        Returns:
            (allowed, error_message)
        """
        current_time = time.time()
        
        # Очистка старых записей
        self._cleanup_old_requests()
        
        # Получаем лимиты для роли
        minute_limit, hour_limit = self.limits.get(role, (50, 900))  # Default: CLIENT limits
        
        # Проверка минутного лимита
        minute_requests = self._minute_requests[api_key]
        minute_requests = [ts for ts in minute_requests if ts > current_time - 60]
        if len(minute_requests) >= minute_limit:
            return False, f"Rate limit exceeded: {minute_limit} requests per minute"
        
        # Проверка часового лимита
        hour_requests = self._hour_requests[api_key]
        hour_requests = [ts for ts in hour_requests if ts > current_time - 3600]
        if len(hour_requests) >= hour_limit:
            return False, f"Rate limit exceeded: {hour_limit} requests per hour"
        
        # Запрос разрешен - добавляем timestamp
        self._minute_requests[api_key].append(current_time)
        self._hour_requests[api_key].append(current_time)
        
        return True, None
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработка запроса с rate limiting
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
        
        Returns:
            HTTP ответ
        """
        # Пропускаем health check и metrics endpoints
        if request.url.path in ["/health", "/api/health", "/metrics/prometheus", "/"]:
            return await call_next(request)
        
        # Пропускаем billing endpoints (они используют свою аутентификацию)
        if request.url.path.startswith("/api/v2/billing"):
            return await call_next(request)
        
        # Получаем API ключ
        api_key = self._get_api_key_from_request(request)
        
        if not api_key:
            # Если нет API ключа, пропускаем (может быть публичный endpoint)
            return await call_next(request)
        
        # Получаем роль
        role = self._get_role_from_api_key(api_key)
        
        if not role:
            # Если роль не найдена, пропускаем (будет обработано в verify_api_key)
            return await call_next(request)
        
        # Проверяем rate limit
        allowed, error_msg = self._check_rate_limit(api_key, role)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {role.value}: {error_msg}")
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
        minute_limit, hour_limit = self.limits.get(role, (50, 900))
        minute_count = len([ts for ts in self._minute_requests[api_key] if ts > time.time() - 60])
        hour_count = len([ts for ts in self._hour_requests[api_key] if ts > time.time() - 3600])
        
        response.headers["X-RateLimit-Limit-Minute"] = str(minute_limit)
        response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, minute_limit - minute_count))
        response.headers["X-RateLimit-Limit-Hour"] = str(hour_limit)
        response.headers["X-RateLimit-Remaining-Hour"] = str(max(0, hour_limit - hour_count))
        
        return response
