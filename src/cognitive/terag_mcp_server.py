"""
TERAG MCP Server v2.0
Model Context Protocol сервер для интеграции Cursor с TERAG
Предоставляет доступ к Graph-RAG reasoning, AI-REPS метрикам и статусу системы
"""
import json
import sys
import asyncio
import logging
import os
from typing import Any, Dict, Optional
import httpx

# Настройка логирования в stderr (stdout зарезервирован для MCP протокола)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Конфигурация API
TERAG_API_URL = os.getenv("TERAG_API_URL", "http://localhost:8001")
REQUEST_TIMEOUT = 30.0


async def call_terag_api(
    endpoint: str, 
    method: str = "GET", 
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Вызов TERAG API с обработкой ошибок.
    
    Args:
        endpoint: API эндпоинт (например, "/api/v2/health")
        method: HTTP метод (GET/POST)
        data: Данные для POST запроса
        params: Query параметры для GET запроса
    
    Returns:
        JSON ответ от API
    """
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            url = f"{TERAG_API_URL}{endpoint}"
            logger.info(f"Calling {method} {url}")
            
            if method == "GET":
                response = await client.get(url, params=params or {})
            elif method == "POST":
                response = await client.post(url, json=data or {})
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            result = response.json()
            logger.info(f"Success: {endpoint}")
            return result
            
    except httpx.ConnectError as e:
        logger.error(f"Connection error: {e}")
        return {
            "error": "Cannot connect to TERAG API",
            "details": str(e),
            "status": "connection_error",
            "hint": f"Ensure TERAG API is running at {TERAG_API_URL}"
        }
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error: {e}")
        return {
            "error": "Request timeout",
            "details": str(e),
            "status": "timeout_error",
            "hint": f"TERAG API did not respond within {REQUEST_TIMEOUT}s"
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e}")
        return {
            "error": f"HTTP {e.response.status_code}",
            "details": str(e),
            "status": "http_error",
            "response_body": e.response.text[:200] if e.response.text else ""
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "error": "Unexpected error",
            "details": str(e),
            "status": "unknown_error"
        }


def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обработка MCP запроса от Cursor.
    
    Поддерживаемые методы:
    - terag/health: Проверка здоровья системы
    - terag/metrics: AI-REPS метрики (RSS, COS, FAITH)
    - terag/reason: Выполнение reasoning запроса
    - terag/status: Общий статус системы
    - terag/feedback: Отправка обратной связи
    
    Args:
        request: JSON-RPC запрос от Cursor
    
    Returns:
        JSON-RPC ответ
    """
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id", 0)
    
    logger.info(f"Received MCP request: {method}")
    
    try:
        # Health Check - используем /api/v2/health или /api/health
        if method == "terag/health":
            # Пробуем сначала v2, потом fallback на v1
            result = asyncio.run(call_terag_api("/api/v2/health"))
            if result.get("status") == "connection_error":
                result = asyncio.run(call_terag_api("/api/health"))
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        # AI-REPS Metrics - используем /api/v2/metrics или /api/metrics
        elif method == "terag/metrics":
            result = asyncio.run(call_terag_api("/api/v2/metrics"))
            if result.get("status") == "connection_error":
                result = asyncio.run(call_terag_api("/api/metrics"))
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        # Reasoning - используем /api/query
        elif method == "terag/reason":
            query = params.get("query", "")
            context = params.get("context", {})
            
            if not query:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Missing required parameter: query"
                    }
                }
            
            # Используем GET /api/query?question=...
            result = asyncio.run(call_terag_api(
                "/api/query",
                method="GET",
                params={"question": query}
            ))
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        # Status - используем /api/v2/status
        elif method == "terag/status":
            result = asyncio.run(call_terag_api("/api/v2/status"))
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        # Feedback - используем /api/v2/feedback или /api/feedback
        elif method == "terag/feedback":
            payload = params.get("payload", {})
            
            if not payload:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Missing required parameter: payload"
                    }
                }
            
            result = asyncio.run(call_terag_api(
                "/api/v2/feedback",
                method="POST",
                data=payload
            ))
            
            # Fallback на v1 если v2 недоступен
            if result.get("status") == "connection_error":
                result = asyncio.run(call_terag_api(
                    "/api/feedback",
                    method="POST",
                    data=payload
                ))
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        # List Tools (для автоматического обнаружения)
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "terag/health",
                            "description": "Проверка здоровья TERAG системы (Neo4j, OpenAI, Memory Bank)",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "terag/metrics",
                            "description": "Получение AI-REPS метрик (RSS, COS, FAITH scores)",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "terag/reason",
                            "description": "Выполнение Graph-RAG reasoning запроса с контекстом",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Запрос для reasoning"
                                    },
                                    "context": {
                                        "type": "object",
                                        "description": "Контекст запроса (domain, parameters)"
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "terag/status",
                            "description": "Общий статус TERAG v2.0 (operational/degraded)",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "terag/feedback",
                            "description": "Отправка обратной связи для обучения системы",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "payload": {
                                        "type": "object",
                                        "description": "Данные обратной связи"
                                    }
                                },
                                "required": ["payload"]
                            }
                        }
                    ]
                }
            }
        
        # Неизвестный метод
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                    "data": {
                        "available_methods": [
                            "terag/health",
                            "terag/metrics",
                            "terag/reason",
                            "terag/status",
                            "terag/feedback"
                        ]
                    }
                }
            }
            
    except Exception as e:
        logger.error(f"Error handling request: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


def main():
    """
    Основной цикл MCP сервера.
    Читает JSON-RPC запросы из stdin и пишет ответы в stdout.
    """
    logger.info("=" * 60)
    logger.info("🚀 TERAG MCP Server v2.0 started")
    logger.info(f"API URL: {TERAG_API_URL}")
    logger.info(f"Timeout: {REQUEST_TIMEOUT}s")
    logger.info("=" * 60)
    
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = handle_request(request)
                
                # Вывод в stdout (MCP протокол)
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        logger.info("🛑 TERAG MCP Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
