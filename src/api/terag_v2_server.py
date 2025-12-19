"""
TERAG v2.0 FastAPI Server
Минимальный FastAPI сервер для контрактных тестов
"""
import logging
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Создаём FastAPI приложение
app = FastAPI(
    title="TERAG v2.0 API",
    version="2.0.0",
    description="Adaptive Agentic RAG v2.0 with LangGraph"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handler middleware для унификации формата ошибок
try:
    from src.api.middleware.error_handler import error_handler_middleware
    app.middleware("http")(error_handler_middleware)
    logger.info("[TERAG v2.0] Error handler middleware registered")
except ImportError:
    logger.warning("[TERAG v2.0] Error handler middleware not available")

# Exception handler для RequestValidationError
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации в едином формате"""
    request_id = getattr(request.state, 'request_id', None) or str(uuid.uuid4())
    request_timestamp = datetime.now(timezone.utc).isoformat()
    
    error_detail = {
        "error": f"Validation error: {str(exc)}",
        "error_code": "VALIDATION_ERROR",
        "request_id": request_id,
        "timestamp": request_timestamp,
        "details": exc.errors() if hasattr(exc, 'errors') else []
    }
    
    logger.warning(f"[TERAG API] Validation error: request_id={request_id}, error={exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_detail
    )

# Health endpoints
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "TERAG v2.0 API"}

@app.get("/api/health")
async def api_health():
    """API health check endpoint"""
    try:
        from src.core.health import get_health
        return get_health()
    except ImportError:
        from datetime import datetime, timezone
        return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/v2/health")
async def api_v2_health():
    """TERAG v2.0 health check endpoint"""
    try:
        # Проверяем доступность компонентов
        neo4j_connected = False
        langgraph_available = False
        llm_client_available = False
        
        try:
            from src.graph.schema_manager_v2 import SchemaManagerV2
            neo4j_connected = True
        except ImportError:
            pass
        
        try:
            from src.langgraph.graph_builder import build_terag_graph
            langgraph_available = True
        except ImportError:
            pass
        
        try:
            from src.llm.ollama_client import create_llm_client
            llm_client_available = True
        except ImportError:
            pass
        
        from datetime import datetime, timezone
        return {
            "status": "ok" if neo4j_connected else "degraded",
            "neo4j_connected": neo4j_connected,
            "langgraph_available": langgraph_available,
            "llm_client_available": llm_client_available,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        from datetime import datetime, timezone
        return {
            "status": "error",
            "neo4j_connected": False,
            "langgraph_available": False,
            "llm_client_available": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": str(e)
        }

@app.get("/api/metrics")
async def api_metrics():
    """AI-REPS metrics endpoint (dual-format: snake_case + UPPERCASE)"""
    try:
        from src.core.metrics import get_metrics_snapshot
        return get_metrics_snapshot()
    except ImportError:
        # Fallback для тестов (dual-format)
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).isoformat()
        return {
            # Канонические поля (snake_case)
            "rss": 0.0,
            "cos": 0.0,
            "faith": 0.0,
            "growth": 0.0,
            "resonance": 0.0,
            "confidence": 0.0,
            "timestamp": timestamp,
            # Legacy поля (UPPERCASE)
            "RSS": 0.0,
            "COS": 0.0,
            "FAITH": 0.0,
            "Growth": 0.0,
            "Resonance": 0.0
        }

# Импорт роутов (если доступны)
try:
    from src.api.routes.terag_v2 import router as terag_v2_router
    app.include_router(terag_v2_router)
    logger.info("[TERAG v2.0] Router registered")
except ImportError as e:
    logger.warning(f"[TERAG v2.0] Router not available: {e}")
    # Создаём минимальную заглушку для /api/v2/query
    from fastapi import HTTPException, Body
    from pydantic import BaseModel, Field
    from datetime import datetime, timezone
    import uuid
    
    class QueryRequest(BaseModel):
        query: str = Field(..., description="Текстовый запрос")
        max_attempts: int = Field(2, description="Максимальное количество попыток")
    
    @app.post("/api/v2/query")
    async def query_terag_v2(request: QueryRequest = Body(...)):
        """Заглушка для /api/v2/query endpoint (для контрактных тестов)"""
        request_id = str(uuid.uuid4())
        request_timestamp = datetime.now(timezone.utc).isoformat()
        
        # Возвращаем структурированный ответ согласно контракту
        return {
            "answer": "TERAG v2.0 не инициализирован (заглушка для тестов)",
            "query": request.query,
            "attempts": 1,
            "max_attempts": request.max_attempts,
            "used_strategies": [],
            "decision": "accept",
            "quality_score": 0.0,
            "rss_score": 0.0,
            "rssscore": 0.0,
            "last_critique": None,
            "retrieval_results_count": 0,
            "trace": [],
            "metadata": {
                "request_id": request_id,
                "timestamp": request_timestamp,
                "trace_id": request_id,
                "status": "completed",
                "errors": []
            },
            "timestamp": request_timestamp
        }
