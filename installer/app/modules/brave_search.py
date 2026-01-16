"""
Brave Search API Module
Интеграция с Brave Search API для OSINT-поиска
"""

import requests
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BraveSearchClient:
    """Клиент для работы с Brave Search API"""
    
    BASE_URL = "https://api.search.brave.com/res/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация клиента Brave Search
        
        Args:
            api_key: API ключ Brave Search (или из переменной окружения BRAVE_API_KEY)
        """
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            logger.warning("Brave API key not provided. Set BRAVE_API_KEY environment variable.")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        })
    
    def search(self, query: str, count: int = 10, language: str = "en", 
              safe_search: str = "moderate", **kwargs) -> Dict[str, Any]:
        """
        Выполнить поисковый запрос
        
        Args:
            query: Поисковый запрос
            count: Количество результатов (макс 20)
            language: Язык результатов (en, ru, и т.д.)
            safe_search: Уровень безопасного поиска (off, moderate, strict)
            **kwargs: Дополнительные параметры API
            
        Returns:
            Словарь с результатами поиска
        """
        if not self.api_key:
            logger.error("Brave API key not configured")
            return {"error": "API key not configured", "results": []}
        
        try:
            params = {
                "q": query,
                "count": min(count, 20),
                "search_lang": language,
                "safesearch": safe_search,
                **kwargs
            }
            
            # Используем безопасный запрос с проверкой SAFE_MODE
            try:
                from modules.safe_request import safe_request
                response, error = safe_request("GET", f"{self.BASE_URL}/web/search", 
                                               params=params, timeout=10, 
                                               headers=self.session.headers)
                if error:
                    logger.warning(f"Brave search blocked by SAFE_MODE: {error}")
                    return {"error": error, "results": [], "safe_mode": True}
                if not response:
                    return {"error": "Request failed", "results": []}
            except ImportError:
                # Fallback: обычный запрос если safe_request недоступен
                response = self.session.get(f"{self.BASE_URL}/web/search", params=params, timeout=10)
            
            response.raise_for_status()
            data = response.json()
            
            # Нормализация результатов
            results = []
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                    "age": item.get("age", ""),
                    "meta_url": item.get("meta_url", {}),
                    "query": query,
                    "extracted_at": datetime.now().isoformat()
                })
            
            logger.info(f"Brave search: '{query}' → {len(results)} results")
            return {
                "query": query,
                "results": results,
                "total_results": len(results),
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Brave search error: {e}")
            return {"error": str(e), "results": []}
        except Exception as e:
            logger.error(f"Unexpected error in Brave search: {e}")
            return {"error": str(e), "results": []}
    
    def search_multiple(self, queries: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Выполнить несколько поисковых запросов
        
        Args:
            queries: Список запросов
            **kwargs: Параметры для каждого запроса
            
        Returns:
            Список результатов для каждого запроса
        """
        all_results = []
        for query in queries:
            result = self.search(query, **kwargs)
            all_results.append(result)
            # Небольшая задержка между запросами
            import time
            time.sleep(0.5)
        
        return all_results
    
    def generate_search_queries(self, topics: List[str], max_queries: int = 10) -> List[str]:
        """
        Генерировать поисковые запросы на основе тем
        
        Args:
            topics: Список тем
            max_queries: Максимальное количество запросов
            
        Returns:
            Список сгенерированных запросов
        """
        queries = []
        
        # Базовые паттерны запросов
        patterns = [
            "{topic}",
            "{topic} methodology",
            "{topic} best practices",
            "{topic} implementation",
            "{topic} research",
            "latest {topic}",
            "{topic} 2025"
        ]
        
        for topic in topics[:max_queries]:
            for pattern in patterns:
                if len(queries) >= max_queries:
                    break
                query = pattern.format(topic=topic)
                if query not in queries:
                    queries.append(query)
        
        return queries[:max_queries]

