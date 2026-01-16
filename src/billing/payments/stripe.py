"""
Stripe payment integration для TERAG
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logger.warning("Stripe library not installed. Install with: pip install stripe>=7.0.0")


class StripePaymentProcessor:
    """Обработчик платежей через Stripe"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация Stripe processor
        
        Args:
            api_key: Stripe API key (или из переменной окружения STRIPE_SECRET_KEY)
        """
        if not STRIPE_AVAILABLE:
            raise ImportError("Stripe library not installed")
        
        self.api_key = api_key or os.getenv("STRIPE_SECRET_KEY")
        if not self.api_key:
            raise ValueError("Stripe API key not provided")
        
        stripe.api_key = self.api_key
        logger.info("StripePaymentProcessor initialized")
    
    def create_payment_intent(
        self,
        amount: float,
        currency: str = "usd",
        invoice_id: str = "",
        client_id: str = ""
    ) -> Dict[str, Any]:
        """
        Создать payment intent в Stripe
        
        Args:
            amount: Сумма платежа
            currency: Валюта (usd, kzt)
            invoice_id: ID инвойса
            client_id: ID клиента
        
        Returns:
            Payment intent объект от Stripe
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe использует центы
                currency=currency.lower(),
                metadata={
                    "invoice_id": invoice_id,
                    "client_id": client_id,
                    "terag_service": "billing"
                }
            )
            logger.info(f"Payment intent created: {intent.id} for ${amount:.2f}")
            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": amount,
                "currency": currency
            }
        except Exception as e:
            logger.error(f"Failed to create payment intent: {e}")
            raise
    
    def confirm_payment(
        self,
        payment_intent_id: str
    ) -> Dict[str, Any]:
        """
        Подтвердить платеж
        
        Args:
            payment_intent_id: ID payment intent
        
        Returns:
            Статус платежа
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == "succeeded":
                return {
                    "status": "completed",
                    "transaction_id": intent.id,
                    "amount": intent.amount / 100.0,
                    "currency": intent.currency,
                    "paid_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": intent.status,
                    "transaction_id": intent.id
                }
        except Exception as e:
            logger.error(f"Failed to confirm payment: {e}")
            raise
    
    def handle_webhook(
        self,
        payload: bytes,
        signature: str
    ) -> Dict[str, Any]:
        """
        Обработать webhook от Stripe
        
        Args:
            payload: Тело запроса
            signature: Stripe signature header
        
        Returns:
            Обработанное событие
        """
        try:
            webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
            if not webhook_secret:
                raise ValueError("STRIPE_WEBHOOK_SECRET not set")
            
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            # Обрабатываем событие
            if event["type"] == "payment_intent.succeeded":
                payment_intent = event["data"]["object"]
                return {
                    "event_type": "payment_succeeded",
                    "payment_intent_id": payment_intent["id"],
                    "amount": payment_intent["amount"] / 100.0,
                    "metadata": payment_intent.get("metadata", {})
                }
            
            return {"event_type": event["type"], "processed": True}
        except Exception as e:
            logger.error(f"Failed to handle webhook: {e}")
            raise
