"""
Kaspi payment integration для TERAG
"""

import os
import logging
import httpx
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class KaspiPaymentProcessor:
    """Обработчик платежей через Kaspi API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None
    ):
        """
        Инициализация Kaspi processor
        
        Args:
            api_key: Kaspi API key (или из переменной окружения KASPI_API_KEY)
            api_url: Kaspi API URL (или из переменной окружения KASPI_API_URL)
        """
        self.api_key = api_key or os.getenv("KASPI_API_KEY")
        self.api_url = api_url or os.getenv("KASPI_API_URL", "https://api.kaspi.kz/v1")
        
        if not self.api_key:
            logger.warning("Kaspi API key not provided. Kaspi payments will not work.")
        
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        logger.info("KaspiPaymentProcessor initialized")
    
    async def create_payment(
        self,
        amount: float,
        currency: str = "KZT",
        invoice_id: str = "",
        client_id: str = ""
    ) -> Dict[str, Any]:
        """
        Создать платеж через Kaspi
        
        Args:
            amount: Сумма платежа
            currency: Валюта (KZT)
            invoice_id: ID инвойса
            client_id: ID клиента
        
        Returns:
            Информация о платеже
        """
        if not self.api_key:
            raise ValueError("Kaspi API key not configured")
        
        try:
            response = await self.client.post(
                "/payments/create",
                json={
                    "amount": amount,
                    "currency": currency,
                    "invoice_id": invoice_id,
                    "client_id": client_id,
                    "description": f"TERAG Invoice {invoice_id}"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Kaspi payment created: {data.get('payment_id')} for {amount} {currency}")
            return {
                "payment_id": data.get("payment_id"),
                "status": data.get("status", "pending"),
                "amount": amount,
                "currency": currency,
                "payment_url": data.get("payment_url")
            }
        except Exception as e:
            logger.error(f"Failed to create Kaspi payment: {e}")
            raise
    
    async def check_payment_status(
        self,
        payment_id: str
    ) -> Dict[str, Any]:
        """
        Проверить статус платежа
        
        Args:
            payment_id: ID платежа в Kaspi
        
        Returns:
            Статус платежа
        """
        if not self.api_key:
            raise ValueError("Kaspi API key not configured")
        
        try:
            response = await self.client.get(f"/payments/{payment_id}")
            response.raise_for_status()
            data = response.json()
            
            return {
                "payment_id": payment_id,
                "status": data.get("status"),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "paid_at": data.get("paid_at")
            }
        except Exception as e:
            logger.error(f"Failed to check payment status: {e}")
            raise
    
    async def close(self):
        """Закрыть HTTP клиент"""
        await self.client.aclose()
