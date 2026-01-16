"""
Bright Data Extraction Module
Извлечение контента через Bright Data MCP или прямые запросы
"""

import os
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class BrightDataExtractor:
    """Клиент для извлечения контента через Bright Data"""
    
    def __init__(self, mcp_server: Optional[str] = None, api_key: Optional[str] = None):
        """
        Инициализация экстрактора Bright Data
        
        Args:
            mcp_server: Имя MCP сервера (если используется MCP)
            api_key: API ключ Bright Data (если используется прямой API)
        """
        self.mcp_server = mcp_server or os.getenv("BRIGHT_DATA_MCP_SERVER", "bright_data")
        self.api_key = api_key or os.getenv("BRIGHT_DATA_API_KEY")
        self.timeout = 30
        self.retry_attempts = 3
    
    def scrape_as_markdown(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Извлечь контент страницы в формате Markdown
        
        Args:
            url: URL страницы для извлечения
            **kwargs: Дополнительные параметры
            
        Returns:
            Словарь с извлечённым контентом
        """
        try:
            # Если используется MCP, вызываем через MCP протокол
            if self.mcp_server:
                return self._scrape_via_mcp(url, **kwargs)
            else:
                # Прямой запрос (требует настройки Bright Data прокси)
                return self._scrape_direct(url, **kwargs)
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "content": "",
                "extracted_at": datetime.now().isoformat()
            }
    
    def _scrape_via_mcp(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Извлечение через MCP сервер
        
        Args:
            url: URL для извлечения
            **kwargs: Дополнительные параметры
            
        Returns:
            Результат извлечения
        """
        # TODO: Реализовать вызов MCP сервера
        # Это требует интеграции с MCP протоколом
        logger.warning("MCP scraping not yet implemented, using fallback")
        return self._scrape_fallback(url)
    
    def _scrape_direct(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Прямое извлечение через Bright Data API
        
        Args:
            url: URL для извлечения
            **kwargs: Дополнительные параметры
            
        Returns:
            Результат извлечения
        """
        # TODO: Реализовать прямой запрос к Bright Data API
        # Требует настройки прокси и аутентификации
        logger.warning("Direct Bright Data API not yet configured, using fallback")
        return self._scrape_fallback(url)
    
    def _scrape_fallback(self, url: str) -> Dict[str, Any]:
        """
        Fallback метод: простое извлечение через requests
        
        Args:
            url: URL для извлечения
            
        Returns:
            Базовый результат извлечения
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            # Используем безопасный запрос с проверкой SAFE_MODE
            try:
                from modules.safe_request import safe_request
                response, error = safe_request("GET", url, headers=headers, timeout=self.timeout)
                if error:
                    logger.warning(f"Bright extraction blocked by SAFE_MODE: {error}")
                    return {
                        "url": url,
                        "error": error,
                        "content": "",
                        "extracted_at": datetime.now().isoformat(),
                        "safe_mode": True
                    }
                if not response:
                    raise Exception("Request failed")
            except ImportError:
                # Fallback: обычный запрос если safe_request недоступен
                response = requests.get(url, headers=headers, timeout=self.timeout)
            
            response.raise_for_status()
            
            # Простое извлечение текста (можно улучшить с помощью BeautifulSoup)
            content = response.text[:50000]  # Ограничение размера
            
            return {
                "url": url,
                "content": content,
                "content_type": response.headers.get("Content-Type", "text/html"),
                "status_code": response.status_code,
                "extracted_at": datetime.now().isoformat(),
                "method": "fallback"
            }
        except Exception as e:
            logger.error(f"Fallback scraping failed for {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "content": "",
                "extracted_at": datetime.now().isoformat()
            }
    
    def extract_multiple(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Извлечь контент из нескольких URL
        
        Args:
            urls: Список URL для извлечения
            **kwargs: Дополнительные параметры
            
        Returns:
            Список результатов извлечения
        """
        results = []
        for url in urls:
            result = self.scrape_as_markdown(url, **kwargs)
            results.append(result)
            # Небольшая задержка между запросами
            import time
            time.sleep(1)
        
        return results
    
    def extract_entities_from_content(self, content: str) -> List[Dict[str, Any]]:
        """
        Извлечь сущности из контента (базовая реализация)
        
        Args:
            content: Текст для анализа
            
        Returns:
            Список извлечённых сущностей
        """
        # TODO: Интегрировать с LLM для извлечения сущностей
        # Пока возвращаем базовую структуру
        entities = []
        
        # Простое извлечение (можно улучшить)
        import re
        # Ищем упоминания организаций, людей, технологий
        patterns = {
            "organization": r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company)\b',
            "technology": r'\b(?:AI|ML|LLM|API|REST|GraphQL|Neo4j|Python|JavaScript)\b',
            "person": r'\b(?:Dr\.|Mr\.|Ms\.|Mrs\.)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, content)
            for match in matches:
                entities.append({
                    "text": match,
                    "type": entity_type,
                    "confidence": 0.6  # Базовая уверенность
                })
        
        return entities

