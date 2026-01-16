"""
Role definitions для TERAG API
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class Role(str, Enum):
    """Роли пользователей TERAG"""
    ADMIN = "admin"      # Полный доступ, 200 req/min
    ANALYST = "analyst"  # Read-only + queries, 100 req/min
    CLIENT = "client"    # API-only, 50 req/min


@dataclass
class APIKey:
    """Модель API ключа"""
    key: str
    role: Role
    client_id: str
    created_at: datetime
    expires_at: datetime
    is_active: bool = True
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    
    def is_expired(self) -> bool:
        """Проверить, истек ли ключ"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Проверить, валиден ли ключ"""
        return self.is_active and not self.is_expired()
