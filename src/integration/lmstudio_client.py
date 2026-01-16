#!/usr/bin/env python3
"""
LM Studio Client для интеграции локального LLM inference-бэкенда с TERAG
Поддерживает async запросы через httpx и OpenAI-совместимый API
"""
import httpx
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class LMStudioError(Exception):
    """Базовое исключение для ошибок LM Studio"""
    pass


class ConnectionError(LMStudioError):
    """Ошибка подключения к LM Studio API"""
    pass


class TimeoutError(LMStudioError):
    """Ошибка таймаута при запросе к LM Studio"""
    pass


class InvalidResponseError(LMStudioError):
    """Ошибка невалидного ответа от LM Studio API"""
    pass


class LMStudioClient:
    """
    Асинхронный клиент для работы с LM Studio API
    
    LM Studio предоставляет OpenAI-совместимый API на http://localhost:1234/v1
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        default_model: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Инициализация LM Studio клиента
        
        Args:
            base_url: Базовый URL LM Studio API (по умолчанию http://localhost:1234/v1)
            default_model: Модель по умолчанию (если не указана, будет выбрана автоматически)
            timeout: Таймаут запросов в секундах
        """
        self.base_url = base_url.rstrip('/')
        self.default_model = default_model
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        
        logger.debug(f"LMStudioClient initialized: base_url={self.base_url}, model={self.default_model}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def connect(self):
        """Создать HTTP клиент"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            logger.debug("LM Studio HTTP client created")
    
    async def close(self):
        """Закрыть HTTP клиент"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.debug("LM Studio HTTP client closed")
    
    def _chatml_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Конвертирует ChatML формат в plain prompt
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            
        Returns:
            Plain text prompt
        """
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)
    
    async def list_models(self) -> List[str]:
        """
        Получить список доступных моделей
        
        Returns:
            Список названий моделей
            
        Raises:
            ConnectionError: Если не удалось подключиться к API
            InvalidResponseError: Если ответ API невалиден
        """
        await self.connect()
        
        start_time = time.time()
        
        try:
            logger.debug(f"Requesting models list from {self.base_url}/models")
            response = await self._client.get("/models")
            response.raise_for_status()
            
            data = response.json()
            latency = time.time() - start_time
            
            # OpenAI-совместимый формат: {"data": [{"id": "model1", ...}, ...]}
            if "data" in data:
                models = [model.get("id", model.get("name", "")) for model in data["data"]]
            else:
                # Альтернативный формат
                models = data.get("models", [])
                if isinstance(models, list) and models and isinstance(models[0], dict):
                    models = [m.get("id", m.get("name", "")) for m in models]
            
            models = [m for m in models if m]  # Фильтруем пустые
            
            logger.info(f"Retrieved {len(models)} models in {latency:.2f}s")
            logger.debug(f"Models: {models}")
            
            return models
            
        except httpx.ConnectError as e:
            latency = time.time() - start_time
            logger.error(f"Connection error after {latency:.2f}s: {e}")
            raise ConnectionError(f"Не удалось подключиться к LM Studio API: {e}")
        
        except httpx.TimeoutException as e:
            latency = time.time() - start_time
            logger.error(f"Timeout after {latency:.2f}s: {e}")
            raise TimeoutError(f"Таймаут запроса к LM Studio API: {e}")
        
        except httpx.HTTPStatusError as e:
            latency = time.time() - start_time
            logger.error(f"HTTP error {e.response.status_code} after {latency:.2f}s: {e}")
            raise InvalidResponseError(f"HTTP ошибка {e.response.status_code}: {e}")
        
        except Exception as e:
            latency = time.time() - start_time
            logger.error(f"Unexpected error after {latency:.2f}s: {e}", exc_info=True)
            raise InvalidResponseError(f"Неожиданная ошибка при получении списка моделей: {e}")
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        messages: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Генерация текста через LM Studio API
        
        Args:
            prompt: Текст промпта (используется если messages не указан)
            model: Название модели (если не указана, используется default_model или первая доступная)
            temperature: Температура генерации (0.0-2.0)
            max_tokens: Максимальное количество токенов
            messages: Список сообщений в ChatML формате (приоритет над prompt)
            **kwargs: Дополнительные параметры (top_p, frequency_penalty, etc.)
            
        Returns:
            Словарь с результатом:
            {
                "text": str,  # Сгенерированный текст
                "model": str,  # Использованная модель
                "latency": float,  # Время ответа в секундах
                "usage": dict,  # Статистика использования токенов
                "finish_reason": str  # Причина завершения
            }
            
        Raises:
            ConnectionError: Если не удалось подключиться к API
            TimeoutError: Если запрос превысил таймаут
            InvalidResponseError: Если ответ API невалиден
        """
        await self.connect()
        
        start_time = time.time()
        
        # Определяем модель
        selected_model = model or self.default_model
        if not selected_model:
            # Пытаемся получить первую доступную модель
            try:
                available_models = await self.list_models()
                if available_models:
                    selected_model = available_models[0]
                    logger.debug(f"Auto-selected model: {selected_model}")
                else:
                    raise InvalidResponseError("Нет доступных моделей в LM Studio")
            except Exception as e:
                logger.warning(f"Could not auto-select model: {e}")
                selected_model = "gpt-3.5-turbo"  # Fallback
        
        # Подготовка payload
        if messages:
            # Используем ChatML формат
            payload = {
                "model": selected_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
        else:
            # Используем plain prompt (конвертируем в ChatML для совместимости)
            payload = {
                "model": selected_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
        
        try:
            logger.debug(f"Generating with model={selected_model}, temperature={temperature}, max_tokens={max_tokens}")
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            latency = time.time() - start_time
            
            # Извлекаем текст ответа
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                text = choice.get("message", {}).get("content", "")
                finish_reason = choice.get("finish_reason", "stop")
            else:
                raise InvalidResponseError("Ответ не содержит choices")
            
            result = {
                "text": text,
                "model": selected_model,
                "latency": latency,
                "usage": data.get("usage", {}),
                "finish_reason": finish_reason,
                "raw_response": data  # Для отладки
            }
            
            logger.info(f"Generated {len(text)} chars in {latency:.2f}s using {selected_model}")
            logger.debug(f"Finish reason: {finish_reason}, Usage: {result['usage']}")
            
            return result
            
        except httpx.ConnectError as e:
            latency = time.time() - start_time
            logger.error(f"Connection error after {latency:.2f}s: {e}")
            raise ConnectionError(f"Не удалось подключиться к LM Studio API: {e}")
        
        except httpx.TimeoutException as e:
            latency = time.time() - start_time
            logger.error(f"Timeout after {latency:.2f}s: {e}")
            raise TimeoutError(f"Таймаут запроса к LM Studio API: {e}")
        
        except httpx.HTTPStatusError as e:
            latency = time.time() - start_time
            logger.error(f"HTTP error {e.response.status_code} after {latency:.2f}s: {e}")
            error_text = ""
            try:
                error_data = e.response.json()
                error_text = error_data.get("error", {}).get("message", str(e))
            except:
                error_text = str(e)
            raise InvalidResponseError(f"HTTP ошибка {e.response.status_code}: {error_text}")
        
        except Exception as e:
            latency = time.time() - start_time
            logger.error(f"Unexpected error after {latency:.2f}s: {e}", exc_info=True)
            raise InvalidResponseError(f"Неожиданная ошибка при генерации: {e}")
    
    async def health_check(self) -> bool:
        """
        Проверка доступности LM Studio API
        
        Returns:
            True если API доступен, False иначе
        """
        try:
            await self.connect()
            response = await self._client.get("/models", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Health check failed: {e}")
            return False


# Пример использования
async def example_usage():
    """Пример использования LMStudioClient"""
    async with LMStudioClient(base_url="http://localhost:1234/v1") as client:
        # Проверка доступности
        if await client.health_check():
            print("✅ LM Studio доступен")
        
        # Получение списка моделей
        models = await client.list_models()
        print(f"📋 Доступные модели: {models}")
        
        # Генерация текста
        result = await client.generate(
            prompt="Explain the concept of semantic graphs in AI.",
            temperature=0.7,
            max_tokens=256
        )
        print(f"📝 Ответ: {result['text']}")
        print(f"⏱️  Latency: {result['latency']:.2f}s")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())













