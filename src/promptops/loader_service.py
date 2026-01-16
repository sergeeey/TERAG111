"""
Dynamic Prompt Loader Service для TERAG
Сервис для динамической загрузки промптов из MLflow Registry
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from threading import Lock

logger = logging.getLogger(__name__)

try:
    from .mlflow_registry import PromptRegistryManager
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    logger.warning("PromptRegistryManager not available")

try:
    from src.core.cache import CacheManager, get_cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.warning("Cache not available")


class PromptLoaderService:
    """
    Сервис для динамической загрузки промптов
    
    Функции:
    1. Загрузка промптов из MLflow Registry
    2. Кэширование с TTL (60 минут)
    3. Обновление без перезапуска backend
    4. Поддержка алиасов (@latest, @staging, @production)
    """
    
    def __init__(
        self,
        registry: Optional[PromptRegistryManager] = None,
        cache_ttl: int = 3600  # 60 минут
    ):
        """
        Инициализация Prompt Loader Service
        
        Args:
            registry: PromptRegistryManager (создается автоматически если None)
            cache_ttl: TTL кэша в секундах
        """
        if not REGISTRY_AVAILABLE:
            raise ImportError("PromptRegistryManager not available")
        
        self.registry = registry or PromptRegistryManager()
        self.cache_ttl = cache_ttl
        
        # In-memory cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_lock = Lock()
        
        # Используем Redis cache если доступен
        if CACHE_AVAILABLE:
            try:
                self.redis_cache = get_cache()
            except:
                self.redis_cache = None
                logger.warning("Redis cache not available, using in-memory cache")
        else:
            self.redis_cache = None
        
        logger.info(f"PromptLoaderService initialized (cache_ttl: {cache_ttl}s)")
    
    def load_prompt(
        self,
        name: str,
        alias: str = "@latest",
        version: Optional[str] = None,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Загрузить промпт по имени и алиасу
        
        Args:
            name: Имя промпта
            alias: Алиас (@latest, @staging, @production)
            version: Конкретная версия (опционально)
            use_cache: Использовать кэш
        
        Returns:
            Содержимое промпта или None
        """
        cache_key = f"{name}:{alias}:{version or 'latest'}"
        
        # Проверяем кэш
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                logger.debug(f"Prompt loaded from cache: {name}")
                return cached
        
        # Загружаем из registry
        try:
            prompt_data = self.registry.get_prompt(name, alias=alias, version=version)
            
            if not prompt_data:
                logger.warning(f"Prompt not found: {name} (alias: {alias})")
                return None
            
            content = prompt_data.get("content", "")
            
            # Сохраняем в кэш
            if use_cache:
                self._save_to_cache(cache_key, content)
            
            logger.info(f"Prompt loaded: {name} v{prompt_data.get('version')} (alias: {alias})")
            return content
        
        except Exception as e:
            logger.error(f"Error loading prompt {name}: {e}")
            return None
    
    def load_prompt_with_variables(
        self,
        name: str,
        alias: str = "@latest",
        variables: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None
    ) -> Optional[str]:
        """
        Загрузить промпт и подставить переменные
        
        Args:
            name: Имя промпта
            alias: Алиас
            variables: Словарь переменных для подстановки
            version: Конкретная версия
        
        Returns:
            Промпт с подставленными переменными
        """
        prompt = self.load_prompt(name, alias=alias, version=version)
        
        if not prompt:
            return None
        
        if variables:
            # Простая подстановка переменных
            for key, value in variables.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))
                prompt = prompt.replace(f"${{{key}}}", str(value))
        
        return prompt
    
    def reload_prompt(self, name: str, alias: str = "@latest") -> bool:
        """
        Перезагрузить промпт (очистить кэш и загрузить заново)
        
        Args:
            name: Имя промпта
            alias: Алиас
        
        Returns:
            True если успешно
        """
        cache_key = f"{name}:{alias}:latest"
        
        # Очищаем кэш
        with self._cache_lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
            if cache_key in self._cache_timestamps:
                del self._cache_timestamps[cache_key]
        
        # Очищаем Redis cache
        if self.redis_cache:
            try:
                self.redis_cache.delete(cache_key)
            except:
                pass
        
        # Загружаем заново
        prompt = self.load_prompt(name, alias=alias, use_cache=False)
        
        return prompt is not None
    
    def _get_from_cache(self, key: str) -> Optional[str]:
        """Получить из кэша"""
        # Проверяем Redis
        if self.redis_cache:
            try:
                cached = self.redis_cache.get(key)
                if cached:
                    return cached
            except:
                pass
        
        # Проверяем in-memory cache
        with self._cache_lock:
            if key in self._cache:
                timestamp = self._cache_timestamps.get(key)
                if timestamp and (datetime.utcnow() - timestamp).total_seconds() < self.cache_ttl:
                    return self._cache[key]
                else:
                    # Истек TTL
                    del self._cache[key]
                    if key in self._cache_timestamps:
                        del self._cache_timestamps[key]
        
        return None
    
    def _save_to_cache(self, key: str, value: str):
        """Сохранить в кэш"""
        # Сохраняем в Redis
        if self.redis_cache:
            try:
                self.redis_cache.set(key, value, ttl=self.cache_ttl)
            except:
                pass
        
        # Сохраняем в in-memory cache
        with self._cache_lock:
            self._cache[key] = value
            self._cache_timestamps[key] = datetime.utcnow()









