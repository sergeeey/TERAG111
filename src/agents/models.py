"""
Pydantic модели для Auto Linker Agent
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Case(BaseModel):
    """Модель кейса"""
    case_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    additional_data: Optional[dict] = None
    created_at: Optional[datetime] = None


class Client(BaseModel):
    """Модель клиента"""
    client_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    additional_data: Optional[dict] = None


class Match(BaseModel):
    """Модель совпадения"""
    client_id: str
    confidence: float
    match_details: Optional[dict] = None
