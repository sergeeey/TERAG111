#!/usr/bin/env python3
"""
TERAG Configuration Module
Централизованное управление конфигурацией и безопасными режимами
"""

import os
from typing import Optional, Dict, Any, Tuple
from pathlib import Path


class SafeConfig:
    """Безопасная конфигурация TERAG с защитными механизмами"""
    
    def __init__(self):
        """Инициализация конфигурации с проверкой безопасного режима"""
        self._load_config()
        self._validate_safe_mode()
    
    def _load_config(self):
        """Загрузка конфигурации из переменных окружения"""
        # Безопасный режим по умолчанию включен
        self.safe_mode = os.getenv("SAFE_MODE", "true").lower() in ("true", "1", "yes")
        
        # Ограничения для внешних запросов
        self.max_external_requests_per_minute = int(os.getenv("MAX_EXTERNAL_REQUESTS_PER_MINUTE", "10"))
        self.max_external_requests_per_hour = int(os.getenv("MAX_EXTERNAL_REQUESTS_PER_HOUR", "100"))
        
        # Разрешенные домены для внешних запросов (whitelist)
        self.allowed_domains = os.getenv(
            "ALLOWED_EXTERNAL_DOMAINS", 
            "api.search.brave.com,localhost,127.0.0.1"
        ).split(",")
        
        # Симуляция внешних запросов (только localhost)
        self.simulate_external = os.getenv("SIMULATE_EXTERNAL", "false").lower() in ("true", "1", "yes")
        
        # Логирование всех внешних запросов
        self.log_external_requests = os.getenv("LOG_EXTERNAL_REQUESTS", "true").lower() in ("true", "1", "yes")
    
    def _validate_safe_mode(self):
        """Валидация безопасного режима"""
        if self.safe_mode:
            # В безопасном режиме разрешаем только localhost
            if "localhost" not in self.allowed_domains:
                self.allowed_domains.append("localhost")
            if "127.0.0.1" not in self.allowed_domains:
                self.allowed_domains.append("127.0.0.1")
    
    def is_external_request_allowed(self, url: str) -> Tuple[bool, str]:
        """
        Проверка разрешения внешнего запроса
        
        Args:
            url: URL для проверки
            
        Returns:
            tuple: (разрешен, причина)
        """
        if not self.safe_mode:
            return True, "Safe mode disabled"
        
        # Парсим домен из URL
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.hostname or ""
        except Exception:
            return False, "Invalid URL format"
        
        # Проверка whitelist
        if domain and domain not in self.allowed_domains:
            # Проверка на localhost варианты
            if domain in ("localhost", "127.0.0.1", "0.0.0.0") or domain.startswith("localhost:"):
                return True, "Localhost allowed"
            return False, f"Domain {domain} not in allowed list (SAFE_MODE enabled)"
        
        return True, "Domain allowed"
    
    def should_simulate_external(self, url: str) -> bool:
        """
        Проверка необходимости симуляции внешнего запроса
        
        Args:
            url: URL для проверки
            
        Returns:
            True если нужно симулировать
        """
        if not self.simulate_external:
            return False
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.hostname or ""
            
            # Симулируем только внешние запросы (не localhost)
            if domain and domain not in ("localhost", "127.0.0.1", "0.0.0.0"):
                return True
        except Exception:
            pass
        
        return False
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Получить конфигурацию в виде словаря"""
        return {
            "safe_mode": self.safe_mode,
            "max_external_requests_per_minute": self.max_external_requests_per_minute,
            "max_external_requests_per_hour": self.max_external_requests_per_hour,
            "allowed_domains": self.allowed_domains,
            "simulate_external": self.simulate_external,
            "log_external_requests": self.log_external_requests
        }


# Глобальный экземпляр конфигурации
_config_instance: Optional[SafeConfig] = None


def get_config() -> SafeConfig:
    """Получить глобальный экземпляр конфигурации"""
    global _config_instance
    if _config_instance is None:
        _config_instance = SafeConfig()
    return _config_instance


def reset_config():
    """Сбросить конфигурацию (для тестов)"""
    global _config_instance
    _config_instance = None

