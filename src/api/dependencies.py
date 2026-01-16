"""
FastAPI dependencies для TERAG
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.security.api_auth import TeragAuth
from src.security.roles import APIKey, Role

logger = logging.getLogger(__name__)

# Security scheme для API keys
security = HTTPBearer()


def get_auth() -> TeragAuth:
    """Dependency для получения TeragAuth"""
    return TeragAuth()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
    auth: TeragAuth = Depends(get_auth)
) -> APIKey:
    """
    FastAPI dependency для верификации API ключа
    
    Args:
        credentials: HTTP Authorization credentials
        auth: TeragAuth экземпляр
    
    Returns:
        APIKey объект
    
    Raises:
        HTTPException: Если ключ невалиден
    """
    api_key_value = credentials.credentials
    
    # Проверяем ключ
    api_key = auth.verify_key(api_key_value)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key is inactive"
        )
    
    return api_key


def require_role(allowed_roles: list[Role]) -> callable:
    """
    Dependency для проверки роли
    
    Args:
        allowed_roles: Список разрешенных ролей
    
    Returns:
        Dependency функция
    """
    async def role_checker(
        api_key: APIKey = Depends(verify_api_key)
    ) -> APIKey:
        if api_key.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {api_key.role.value} not allowed. Required: {[r.value for r in allowed_roles]}"
            )
        return api_key
    
    return role_checker


# Предопределенные dependencies для разных ролей
require_admin = require_role([Role.ADMIN])
require_analyst = require_role([Role.ADMIN, Role.ANALYST])
require_client = require_role([Role.ADMIN, Role.ANALYST, Role.CLIENT])
