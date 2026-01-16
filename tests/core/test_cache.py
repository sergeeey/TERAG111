"""
Тесты для системы кэширования
"""
import pytest
import time
from unittest.mock import Mock, patch
from src.core.cache import Cache, get_cache


@pytest.fixture
def cache():
    """Создать кэш для тестов (in-memory)"""
    return Cache(default_ttl=60)


@pytest.fixture
def redis_cache():
    """Создать Redis кэш (если доступен)"""
    try:
        cache = Cache(redis_url="redis://localhost:6379/1", default_ttl=60)
        # Проверяем подключение
        cache.redis_client.ping()
        return cache
    except Exception:
        pytest.skip("Redis not available")


def test_cache_initialization(cache):
    """Тест инициализации кэша"""
    assert cache is not None
    assert cache.default_ttl == 60
    assert cache.redis_client is None  # In-memory mode


def test_cache_set_get(cache):
    """Тест установки и получения значения"""
    cache.set("test_key", {"data": "test"}, ttl=10)
    value = cache.get("test_key")
    
    assert value is not None
    assert value["data"] == "test"


def test_cache_expiration(cache):
    """Тест истечения срока действия кэша"""
    cache.set("test_key", "value", ttl=1)
    
    # Значение должно быть доступно
    assert cache.get("test_key") == "value"
    
    # Ждем истечения
    time.sleep(2)
    
    # Значение должно быть удалено
    assert cache.get("test_key") is None


def test_cache_delete(cache):
    """Тест удаления ключа"""
    cache.set("test_key", "value")
    assert cache.get("test_key") == "value"
    
    cache.delete("test_key")
    assert cache.get("test_key") is None


def test_cache_clear(cache):
    """Тест очистки кэша"""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    assert len(cache.memory_cache) == 2
    
    count = cache.clear()
    assert count == 2
    assert len(cache.memory_cache) == 0


def test_cache_make_key(cache):
    """Тест создания ключа кэша"""
    key1 = cache._make_key("prefix", "arg1", kwarg1="value1")
    key2 = cache._make_key("prefix", "arg1", kwarg1="value1")
    key3 = cache._make_key("prefix", "arg2", kwarg1="value1")
    
    # Одинаковые аргументы должны давать одинаковый ключ
    assert key1 == key2
    
    # Разные аргументы должны давать разные ключи
    assert key1 != key3


def test_cache_decorator_sync(cache):
    """Тест декоратора кэша для синхронной функции"""
    call_count = 0
    
    @cache.cached(prefix="test", ttl=10)
    def expensive_function(x, y):
        nonlocal call_count
        call_count += 1
        return x + y
    
    # Первый вызов - функция выполняется
    result1 = expensive_function(1, 2)
    assert result1 == 3
    assert call_count == 1
    
    # Второй вызов - из кэша
    result2 = expensive_function(1, 2)
    assert result2 == 3
    assert call_count == 1  # Функция не вызывалась


@pytest.mark.asyncio
async def test_cache_decorator_async(cache):
    """Тест декоратора кэша для асинхронной функции"""
    call_count = 0
    
    @cache.cached(prefix="test", ttl=10)
    async def expensive_function(x, y):
        nonlocal call_count
        call_count += 1
        return x + y
    
    # Первый вызов - функция выполняется
    result1 = await expensive_function(1, 2)
    assert result1 == 3
    assert call_count == 1
    
    # Второй вызов - из кэша
    result2 = await expensive_function(1, 2)
    assert result2 == 3
    assert call_count == 1  # Функция не вызывалась


def test_get_cache_singleton():
    """Тест singleton паттерна для кэша"""
    cache1 = get_cache()
    cache2 = get_cache()
    
    assert cache1 is cache2


@pytest.mark.skipif(True, reason="Requires Redis")
def test_redis_cache(redis_cache):
    """Тест Redis кэша (если доступен)"""
    redis_cache.set("test_key", {"data": "test"})
    value = redis_cache.get("test_key")
    
    assert value is not None
    assert value["data"] == "test"









