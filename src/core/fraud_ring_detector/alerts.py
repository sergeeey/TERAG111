"""
Alert Service для Fraud Ring Detector
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class FraudRingAlertService:
    """Сервис для отправки уведомлений о fraud rings"""
    
    def __init__(self):
        """Инициализация FraudRingAlertService"""
        logger.info("FraudRingAlertService initialized")
    
    def send_alert(self, fraud_ring: Dict[str, Any]) -> bool:
        """
        Отправить alert о fraud ring
        
        Args:
            fraud_ring: Данные fraud ring
        
        Returns:
            True если отправлено успешно
        """
        try:
            from src.integration.telegram_service import send_fact_notification_sync
            
            message = (
                f"🚨 Fraud Ring Detected!\n"
                f"Members: {fraud_ring['size']}\n"
                f"Density: {fraud_ring['density']:.2f}\n"
                f"Risk: {'HIGH' if fraud_ring['risk_score'] > 0.8 else 'MEDIUM'}\n"
                f"Community ID: {fraud_ring.get('community_id', 'N/A')}"
            )
            
            send_fact_notification_sync(
                {"message": message},
                "fraud_ring_detector",
                1.0
            )
            
            logger.info(f"Fraud ring alert sent: {fraud_ring['size']} members")
            return True
        except Exception as e:
            logger.error(f"Failed to send fraud ring alert: {e}")
            return False
