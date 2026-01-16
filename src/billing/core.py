"""
BillingCore - основная логика биллинга TERAG
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from src.billing.database import get_billing_db
from src.billing.models import UsageMeter, Invoice, Payment, Client, QueryType

logger = logging.getLogger(__name__)


# Тарифы согласно ТЗ
BILLING_TIERS = {
    "simple": 0.01,          # $0.01 per query
    "fraud_ring": 500.0,     # $500 per deep analysis
    "predictive": 5000.0,    # $5000 per report
}


class BillingCore:
    """Основной класс для биллинга"""
    
    def __init__(self):
        """Инициализация BillingCore"""
        self.db = get_billing_db()
        self.tiers = BILLING_TIERS
        logger.info("BillingCore initialized")
    
    def record_usage(
        self,
        client_id: str,
        query_type: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        latency_ms: float = 0.0,
        api_key_id: Optional[str] = None
    ) -> UsageMeter:
        """
        Записать использование в БД
        
        Args:
            client_id: ID клиента
            query_type: Тип запроса (simple, fraud_ring, predictive)
            tokens_in: Входные токены
            tokens_out: Выходные токены
            latency_ms: Латентность в миллисекундах
            api_key_id: ID API ключа
        
        Returns:
            UsageMeter объект
        """
        # Рассчитываем стоимость
        cost = self.calculate_cost(query_type, tokens_in, tokens_out)
        
        usage = UsageMeter(
            client_id=client_id,
            query_type=query_type,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            cost_usd=cost,
            api_key_id=api_key_id,
            timestamp=datetime.utcnow()
        )
        
        # Сохраняем в MongoDB
        try:
            self.db.usage_collection.insert_one(usage.model_dump())
            logger.debug(f"Usage recorded: {client_id} - {query_type} - ${cost:.2f}")
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
            raise
        
        return usage
    
    def calculate_cost(
        self,
        query_type: str,
        tokens_in: int = 0,
        tokens_out: int = 0
    ) -> float:
        """
        Рассчитать стоимость запроса
        
        Args:
            query_type: Тип запроса
            tokens_in: Входные токены
            tokens_out: Выходные токены
        
        Returns:
            Стоимость в USD
        """
        base_cost = self.tiers.get(query_type, self.tiers["simple"])
        
        # Для simple запросов - фиксированная цена
        if query_type == "simple":
            return base_cost
        
        # Для fraud_ring и predictive - базовая цена + токены (опционально)
        # Пока используем только базовую цену согласно ТЗ
        return base_cost
    
    def generate_invoice(
        self,
        client_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Invoice:
        """
        Сгенерировать инвойс за период
        
        Args:
            client_id: ID клиента
            period_start: Начало периода
            period_end: Конец периода
        
        Returns:
            Invoice объект
        """
        # Получаем все usage за период
        usage_records = list(
            self.db.usage_collection.find({
                "client_id": client_id,
                "timestamp": {
                    "$gte": period_start,
                    "$lte": period_end
                }
            })
        )
        
        # Рассчитываем общую сумму
        total_amount = sum(record.get("cost_usd", 0.0) for record in usage_records)
        
        # Получаем клиента для валюты
        client_doc = self.db.clients_collection.find_one({"client_id": client_id})
        currency = client_doc.get("currency", "USD") if client_doc else "USD"
        
        # Создаем инвойс
        invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        due_date = period_end + timedelta(days=30)  # 30 дней на оплату
        
        invoice = Invoice(
            invoice_id=invoice_id,
            client_id=client_id,
            period_start=period_start,
            period_end=period_end,
            total_amount=total_amount,
            currency=currency,
            status="draft",
            due_date=due_date,
            created_at=datetime.utcnow()
        )
        
        # Сохраняем в MongoDB
        try:
            self.db.invoices_collection.insert_one(invoice.model_dump())
            logger.info(f"Invoice generated: {invoice_id} for {client_id} - ${total_amount:.2f}")
        except Exception as e:
            logger.error(f"Failed to generate invoice: {e}")
            raise
        
        return invoice
    
    def create_client(
        self,
        name: str,
        email: str,
        billing_tier: str = "standard",
        currency: str = "USD"
    ) -> Client:
        """
        Создать нового клиента
        
        Args:
            name: Название клиента
            email: Email для биллинга
            billing_tier: Тарифный план
            currency: Валюта (USD или KZT)
        
        Returns:
            Client объект
        """
        client_id = f"CLIENT-{uuid.uuid4().hex[:8].upper()}"
        
        client = Client(
            client_id=client_id,
            name=name,
            email=email,
            billing_tier=billing_tier,
            currency=currency,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        # Сохраняем в MongoDB
        try:
            self.db.clients_collection.insert_one(client.model_dump())
            logger.info(f"Client created: {client_id} - {name}")
        except Exception as e:
            logger.error(f"Failed to create client: {e}")
            raise
        
        return client
    
    def get_client_usage(
        self,
        client_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить использование клиента за период
        
        Args:
            client_id: ID клиента
            start_date: Начало периода (опционально)
            end_date: Конец периода (опционально)
        
        Returns:
            Список записей использования
        """
        query = {"client_id": client_id}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        usage_records = list(
            self.db.usage_collection.find(query).sort("timestamp", -1)
        )
        
        return usage_records
    
    def get_client_invoices(
        self,
        client_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить инвойсы клиента
        
        Args:
            client_id: ID клиента
            status: Фильтр по статусу (опционально)
        
        Returns:
            Список инвойсов
        """
        query = {"client_id": client_id}
        if status:
            query["status"] = status
        
        invoices = list(
            self.db.invoices_collection.find(query).sort("created_at", -1)
        )
        
        return invoices
