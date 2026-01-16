"""
Safe Request Wrapper
Оборачивает HTTP-запросы с проверкой SAFE_MODE
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def safe_request(
    method: str,
    url: str,
    **kwargs
) -> Tuple[Optional[requests.Response], Optional[str]]:
    """
    Безопасный HTTP-запрос с проверкой SAFE_MODE
    
    Args:
        method: HTTP метод (GET, POST, etc.)
        url: URL для запроса
        **kwargs: Дополнительные параметры для requests
        
    Returns:
        tuple: (Response объект или None, сообщение об ошибке или None)
    """
    # Импортируем конфигурацию
    try:
        import sys
        from pathlib import Path
        
        # Добавляем путь к src/core для импорта config
        src_path = Path(__file__).parent.parent.parent.parent / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path.parent))
            from src.core.config import get_config
            config = get_config()
        else:
            # Fallback: используем переменные окружения напрямую
            config = None
    except Exception as e:
        logger.warning(f"Could not load SafeConfig: {e}, using environment variables")
        config = None
    
    # Проверка безопасного режима
    if config:
        allowed, reason = config.is_external_request_allowed(url)
        if not allowed:
            logger.warning(f"SAFE_MODE: Request to {url} blocked: {reason}")
            return None, f"SAFE_MODE: {reason}"
        
        # Проверка симуляции
        if config.should_simulate_external(url):
            logger.info(f"SAFE_MODE: Simulating request to {url}")
            # Возвращаем симулированный ответ
            return _simulate_response(url, method), None
        
        # Логирование запроса
        if config.log_external_requests:
            logger.info(f"SAFE_MODE: Allowed request to {url}")
    else:
        # Fallback проверка через переменные окружения
        safe_mode = os.getenv("SAFE_MODE", "true").lower() in ("true", "1", "yes")
        if safe_mode:
            # Простая проверка на localhost
            if "localhost" not in url and "127.0.0.1" not in url:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.hostname or ""
                allowed_domains = os.getenv(
                    "ALLOWED_EXTERNAL_DOMAINS",
                    "api.search.brave.com,localhost,127.0.0.1"
                ).split(",")
                
                if domain and domain not in allowed_domains:
                    logger.warning(f"SAFE_MODE: Domain {domain} not allowed")
                    return None, f"SAFE_MODE: Domain {domain} not in allowed list"
    
    # Выполняем запрос
    try:
        response = requests.request(method, url, **kwargs)
        return response, None
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None, str(e)


def _simulate_response(url: str, method: str) -> requests.Response:
    """Симуляция HTTP-ответа для тестирования"""
    # Создаем mock response
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self.url = url
            self.headers = {"Content-Type": "application/json"}
            self.text = '{"simulated": true, "url": "' + url + '", "method": "' + method + '"}'
            self.content = self.text.encode()
        
        def json(self):
            return {"simulated": True, "url": url, "method": method}
        
        def raise_for_status(self):
            pass
    
    return MockResponse()


















