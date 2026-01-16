"""
Fraud Ring Detector module
"""

from src.core.fraud_ring_detector import FraudRingDetector
from src.core.fraud_ring_detector.alerts import FraudRingAlertService
from src.core.fraud_ring_detector.models import Community, FraudRing

__all__ = [
    "FraudRingDetector",
    "FraudRingAlertService",
    "Community",
    "FraudRing",
]
