"""
Модели для Fraud Ring Detector
"""

from pydantic import BaseModel
from typing import List


class Community(BaseModel):
    """Модель сообщества"""
    community_id: str
    nodes: List[str]
    size: int


class FraudRing(BaseModel):
    """Модель fraud ring"""
    members: List[str]
    density: float
    risk_score: float
    community_id: str
