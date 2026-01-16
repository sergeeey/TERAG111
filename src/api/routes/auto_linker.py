"""
API endpoints для Auto Linker MVP
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field, validator

from src.agents.auto_linker import AutoLinkerMVP
from src.api.dependencies import verify_api_key, APIKey

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["auto-linker"])


class ClientData(BaseModel):
    """Модель данных клиента для Auto Linker"""
    id: str = Field(..., description="Уникальный ID клиента")
    full_name: str = Field(..., description="ФИО клиента")
    phone: str = Field(None, description="Телефон клиента (опционально)")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "CLIENT-001",
                "full_name": "Иванов Иван Иванович",
                "phone": "+77001234567"
            }
        }


class AutoLinkRequest(BaseModel):
    """Запрос на связывание клиентов"""
    clients: List[ClientData] = Field(..., description="Список клиентов для проверки")
    min_confidence: float = Field(0.85, ge=0.0, le=1.0, description="Минимальный confidence для связи")
    create_links: bool = Field(False, description="Создать связи в Neo4j (требует driver)")
    
    @validator('clients')
    def validate_clients_count(cls, v):
        if len(v) > 50:
            raise ValueError("Maximum 50 clients per request")
        if len(v) < 2:
            raise ValueError("At least 2 clients required")
        return v


class AutoLinkResponse(BaseModel):
    """Ответ на запрос связывания"""
    status: str
    total_clients: int
    linked_pairs: List[Dict[str, Any]]
    total_links: int
    links_created_in_neo4j: int = 0


@router.post("/auto-link", response_model=AutoLinkResponse)
async def auto_link_clients(
    request: AutoLinkRequest = Body(...),
    api_key: APIKey = Depends(verify_api_key)
):
    """
    Найти похожих клиентов и опционально создать связи в Neo4j
    
    Args:
        request: Запрос с данными клиентов
        api_key: API ключ для аутентификации
    
    Returns:
        Результат связывания с найденными парами
    """
    try:
        # Получаем Neo4j driver если нужно создавать связи
        neo4j_driver = None
        if request.create_links:
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
                    logger.warning("Neo4j credentials not available, links will not be created")
            except Exception as e:
                logger.warning(f"Failed to initialize Neo4j driver: {e}")
        
        # Инициализируем Auto Linker
        linker = AutoLinkerMVP(
            min_confidence=request.min_confidence,
            neo4j_driver=neo4j_driver
        )
        
        # Преобразуем Pydantic модели в dict
        clients_data = [client.dict() for client in request.clients]
        
        # Находим похожих клиентов
        similar_pairs = linker.find_similar_clients(clients_data)
        
        # Создаем связи в Neo4j если запрошено
        links_created = 0
        if request.create_links and neo4j_driver:
            links_created = linker.create_links_in_neo4j(similar_pairs)
        
        # Закрываем driver если создавали
        if neo4j_driver:
            neo4j_driver.close()
        
        return AutoLinkResponse(
            status="success",
            total_clients=len(request.clients),
            linked_pairs=similar_pairs,
            total_links=len(similar_pairs),
            links_created_in_neo4j=links_created
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in auto_link_clients: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
