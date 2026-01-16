"""
Кэширование для TERAG API
Поддержка in-memory и Redis кэша
"""
import json
import hashlib
import logging
from typing import Any, Optional
from datetime import timedelta
from functools import wraps

logger = logging.getLogger(__name__)

# Попытка импорта Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")


class Cache:
    """
    Универсальный кэш (Redis или in-memory)
    """
    
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
        """
        Инициализация кэша
        
        Args:
            redis_url: URL для Redis (например, redis://localhost:6379)
            default_ttl: Время жизни кэша по умолчанию (в секундах)
        """
        self.default_ttl = default_ttl
        self.redis_client = None
        self.memory_cache: dict = {}
        
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Проверка подключения
                self.redis_client.ping()
                logger.info(f"Redis cache initialized: {redis_url}")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}, using in-memory cache")
                self.redis_client = None
        else:
            logger.info("Using in-memory cache")
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Создать ключ кэша"""
        # Сериализуем аргументы
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получить значение из кэша
        
        Args:
            key: Ключ кэша
        
        Returns:
            Значение или None
        """
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                return None
        else:
            # In-memory cache
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                # Проверяем TTL
                if entry["expires_at"] > self._now():
                    return entry["value"]
                else:
                    # Удаляем истекший ключ
                    del self.memory_cache[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Установить значение в кэш
        
        Args:
            key: Ключ кэша
            value: Значение для кэширования
            ttl: Время жизни (в секундах), None = default_ttl
        
        Returns:
            True если успешно
        """
        ttl = ttl or self.default_ttl
        
        if self.redis_client:
            try:
                value_str = json.dumps(value)
                self.redis_client.setex(key, ttl, value_str)
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
                return False
        else:
            # In-memory cache
            self.memory_cache[key] = {
                "value": value,
                "expires_at": self._now() + ttl
            }
            return True
    
    def delete(self, key: str) -> bool:
        """
        Удалить ключ из кэша
        
        Args:
            key: Ключ для удаления
        
        Returns:
            True если успешно
        """
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
                return False
        else:
            if key in self.memory_cache:
                del self.memory_cache[key]
            return True
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Очистить кэш
        
        Args:
            pattern: Паттерн для удаления (только для Redis)
        
        Returns:
            Количество удаленных ключей
        """
        if self.redis_client:
            try:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        return self.redis_client.delete(*keys)
                else:
                    # Очистка всего кэша
                    return self.redis_client.flushdb()
            except Exception as e:
                logger.error(f"Redis clear error: {e}")
                return 0
        else:
            if pattern:
                # Простая фильтрация по префиксу
                keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(pattern)]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                return len(keys_to_delete)
            else:
                count = len(self.memory_cache)
                self.memory_cache.clear()
                return count
    
    def _now(self) -> int:
        """Получить текущее время (Unix timestamp)"""
        import time
        return int(time.time())
    
    def cached(self, prefix: str = "cache", ttl: Optional[int] = None):
        """
        Декоратор для кэширования результатов функции
        
        Args:
            prefix: Префикс для ключа кэша
            ttl: Время жизни кэша (в секундах)
        
        Usage:
            @cache.cached(prefix="api", ttl=300)
            def expensive_function(arg1, arg2):
                ...
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache_key = self._make_key(prefix, *args, **kwargs)
                
                # Пытаемся получить из кэша
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
                
                # Выполняем функцию
                logger.debug(f"Cache miss: {cache_key}")
                result = await func(*args, **kwargs)
                
                # Сохраняем в кэш
                self.set(cache_key, result, ttl=ttl)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = self._make_key(prefix, *args, **kwargs)
                
                # Пытаемся получить из кэша
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
                
                # Выполняем функцию
                logger.debug(f"Cache miss: {cache_key}")
                result = func(*args, **kwargs)
                
                # Сохраняем в кэш
                self.set(cache_key, result, ttl=ttl)
                
                return result
            
            # Определяем синхронная или асинхронная функция
            import inspect
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator


# Глобальный экземпляр кэша
_cache_instance: Optional[Cache] = None


def get_cache(redis_url: Optional[str] = None, default_ttl: int = 3600) -> Cache:
    """
    Получить глобальный экземпляр кэша (singleton)
    
    Args:
        redis_url: URL для Redis
        default_ttl: Время жизни по умолчанию
    
    Returns:
        Экземпляр Cache
    """
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = Cache(redis_url=redis_url, default_ttl=default_ttl)
    
    return _cache_instance
