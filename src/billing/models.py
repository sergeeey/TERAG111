"""
Pydantic модели для биллинга TERAG
"""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum


class QueryType(str, Enum):
    """Типы запросов для биллинга"""
    SIMPLE = "simple"
    FRAUD_RING = "fraud_ring"
    PREDICTIVE = "predictive"


class UsageMeter(BaseModel):
    """Модель для учета использования"""
    client_id: str = Field(..., description="ID клиента")
    query_type: Literal["simple", "fraud_ring", "predictive"] = Field(..., description="Тип запроса")
    tokens_in: int = Field(0, description="Входные токены")
    tokens_out: int = Field(0, description="Выходные токены")
    latency_ms: float = Field(0.0, description="Латентность в миллисекундах")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время запроса")
    cost_usd: float = Field(0.0, description="Стоимость в USD")
    api_key_id: Optional[str] = Field(None, description="ID API ключа, использованного для запроса")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Client(BaseModel):
    """Модель клиента"""
    client_id: str = Field(..., description="Уникальный ID клиента")
    name: str = Field(..., description="Название клиента")
    email: str = Field(..., description="Email для биллинга")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(True, description="Активен ли клиент")
    billing_tier: str = Field("standard", description="Тарифный план")
    currency: Literal["USD", "KZT"] = Field("USD", description="Валюта биллинга")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Invoice(BaseModel):
    """Модель инвойса"""
    invoice_id: str = Field(..., description="Уникальный ID инвойса")
    client_id: str = Field(..., description="ID клиента")
    period_start: datetime = Field(..., description="Начало периода")
    period_end: datetime = Field(..., description="Конец периода")
    total_amount: float = Field(0.0, description="Общая сумма")
    currency: str = Field("USD", description="Валюта")
    status: Literal["draft", "sent", "paid", "overdue"] = Field("draft", description="Статус")
    due_date: datetime = Field(..., description="Срок оплаты")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = Field(None, description="Дата оплаты")
    pdf_path: Optional[str] = Field(None, description="Путь к PDF файлу")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Payment(BaseModel):
    """Модель платежа"""
    payment_id: str = Field(..., description="Уникальный ID платежа")
    invoice_id: str = Field(..., description="ID инвойса")
    client_id: str = Field(..., description="ID клиента")
    amount: float = Field(..., description="Сумма платежа")
    currency: str = Field("USD", description="Валюта")
    payment_method: Literal["stripe", "kaspi", "bank_transfer"] = Field(..., description="Метод оплаты")
    status: Literal["pending", "completed", "failed", "refunded"] = Field("pending", description="Статус")
    transaction_id: Optional[str] = Field(None, description="ID транзакции в платежной системе")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Дата завершения")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
