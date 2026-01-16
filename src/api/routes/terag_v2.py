"""
TERAG v2.0 API Router
Основные эндпоинты для работы с TERAG v2.0
"""
import logging
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Импорты из core модулей
try:
    from src.core.metrics import get_metrics_snapshot
    from src.core.health import get_health
    from src.core.self_learning import accept_feedback
    CORE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Core modules not available: {e}")
    CORE_AVAILABLE = False

# Создаём роутер
router = APIRouter(prefix="/api/v2", tags=["terag-v2"])


@router.get("/")
def root():
    """Корневой эндпоинт TERAG v2.0"""
    return {
        "service": "TERAG v2.0 API",
        "version": "2.0",
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health")
def health_check():
    """Проверка здоровья системы TERAG v2.0"""
    if not CORE_AVAILABLE:
        return {
            "status": "degraded",
            "service": "TERAG v2.0",
            "message": "Core modules not available"
        }
    
    try:
        health = get_health()
        return {
            "status": "ok",
            "service": "TERAG v2.0",
            "health": health,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "error",
            "service": "TERAG v2.0",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/metrics")
def get_metrics():
    """Получение метрик AI-REPS для TERAG v2.0"""
    if not CORE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Core modules not available")
    
    try:
        metrics = get_metrics_snapshot()
        return {
            "service": "TERAG v2.0",
            "metrics": metrics,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.post("/feedback")
def submit_feedback(payload: Dict[str, Any] = Body(...)):
    """Отправка обратной связи для обучения системы"""
    if not CORE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Core modules not available")
    
    try:
        result = accept_feedback(payload)
        return {
            "status": "ok",
            "service": "TERAG v2.0",
            "accepted": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to accept feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to accept feedback: {str(e)}")


@router.get("/status")
def get_status():
    """Получение общего статуса TERAG v2.0"""
    return {
        "service": "TERAG v2.0",
        "version": "2.0",
        "status": "operational" if CORE_AVAILABLE else "degraded",
        "core_modules_available": CORE_AVAILABLE,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
