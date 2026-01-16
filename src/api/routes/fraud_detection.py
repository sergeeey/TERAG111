"""
API endpoints для Rule-based Fraud Detection
"""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from src.core.fraud_detector_simple import RuleBasedFraudDetector
from src.api.dependencies import verify_api_key, APIKey

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["fraud-detection"])


class FraudDetectionResponse(BaseModel):
    """Ответ на запрос fraud detection"""
    status: str
    analysis_date: str
    time_window_days: int
    total_alerts: int
    alerts: list
    summary: dict


@router.get("/fraud-detection", response_model=FraudDetectionResponse)
async def run_fraud_detection(
    days: int = Query(30, ge=1, le=90, description="Период анализа в днях"),
    api_key: APIKey = Depends(verify_api_key)
):
    """
    Запустить детекцию мошенничества по правилам
    
    Args:
        days: Период анализа в днях (1-90)
        api_key: API ключ для аутентификации
    
    Returns:
        Результаты детекции с найденными паттернами
    """
    try:
        # Получаем Neo4j driver
        neo4j_driver = None
        try:
            from neo4j import GraphDatabase
            import os
            
            neo4j_uri = os.getenv("NEO4J_URI")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD")
            
            if neo4j_uri and neo4j_password:
                neo4j_driver = GraphDatabase.driver(
                    neo4j_uri,
                    auth=(neo4j_user, neo4j_password)
                )
            else:
                logger.warning("Neo4j credentials not available, using mock data")
        except Exception as e:
            logger.warning(f"Failed to initialize Neo4j driver: {e}")
        
        # Инициализируем Fraud Detector
        detector = RuleBasedFraudDetector(neo4j_driver=neo4j_driver)
        
        # Запускаем детекцию
        results = detector.detect_fraud_patterns(time_window_days=days)
        
        # Генерируем сводку
        summary = detector._generate_summary(results)
        
        # Отправляем Telegram alerts для critical patterns
        try:
            from src.core.fraud_alerts import send_fraud_alerts_sync
            alerts_sent = send_fraud_alerts_sync(results, only_critical=True)
            logger.info(f"Sent {alerts_sent} critical fraud alerts to Telegram")
        except Exception as e:
            logger.warning(f"Failed to send fraud alerts: {e}")
        
        # Закрываем driver если создавали
        if neo4j_driver:
            neo4j_driver.close()
        
        return FraudDetectionResponse(
            status="success",
            analysis_date=datetime.utcnow().isoformat(),
            time_window_days=days,
            total_alerts=len(results),
            alerts=results,
            summary=summary
        )
    
    except Exception as e:
        logger.error(f"Error in run_fraud_detection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
