"""
API Key Authentication для TERAG
"""

import os
import logging
import uuid
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from src.security.roles import Role, APIKey
from src.billing.database import get_billing_db

logger = logging.getLogger(__name__)


class TeragAuth:
    """Класс для управления API ключами и аутентификации"""
    
    def __init__(self):
        """Инициализация TeragAuth"""
        self.db = get_billing_db()
        logger.info("TeragAuth initialized")
    
    def create_key(
        self,
        client_id: str,
        role: Role,
        expires_days: int = 365
    ) -> APIKey:
        """
        Создать новый API ключ
        
        Args:
            client_id: ID клиента
            role: Роль (ADMIN, ANALYST, CLIENT)
            expires_days: Срок действия в днях (по умолчанию 1 год)
        
        Returns:
            APIKey объект
        """
        # Генерируем ключ
        timestamp = int(datetime.utcnow().timestamp())
        random_part = uuid.uuid4().hex[:16]
        key_value = f"sk_terag_prod_{timestamp}_{random_part}"
        
        # Хешируем для хранения
        key_hash = bcrypt.hashpw(key_value.encode(), bcrypt.gensalt()).decode()
        
        # Создаем APIKey объект
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(days=expires_days)
        
        api_key = APIKey(
            key=key_value,  # Возвращаем оригинальный ключ (только один раз!)
            role=role,
            client_id=client_id,
            created_at=created_at,
            expires_at=expires_at,
            is_active=True
        )
        
        # Сохраняем в MongoDB (с хешем, не оригинальным ключом)
        key_doc = {
            "key_hash": key_hash,
            "role": role.value,
            "client_id": client_id,
            "created_at": created_at,
            "expires_at": expires_at,
            "is_active": True,
            "last_used_at": None,
            "usage_count": 0
        }
        
        try:
            self.db.api_keys_collection.insert_one(key_doc)
            logger.info(f"API key created for client {client_id} with role {role.value}")
        except Exception as e:
            logger.error(f"Failed to create API key: {e}")
            raise
        
        return api_key
    
    def verify_key(self, key: str) -> Optional[APIKey]:
        """
        Проверить и верифицировать API ключ
        
        Args:
            key: API ключ для проверки
        
        Returns:
            APIKey объект если валиден, None если невалиден
        """
        # Получаем все ключи из БД
        all_keys = list(self.db.api_keys_collection.find({"is_active": True}))
        
        # Проверяем каждый ключ
        for key_doc in all_keys:
            key_hash = key_doc.get("key_hash")
            if not key_hash:
                continue
            
            # Проверяем хеш
            try:
                if bcrypt.checkpw(key.encode(), key_hash.encode()):
                    # Ключ найден - обновляем статистику
                    self._update_key_usage(key_doc["_id"])
                    
                    # Создаем APIKey объект
                    api_key = APIKey(
                        key=key,  # Возвращаем оригинальный ключ
                        role=Role(key_doc["role"]),
                        client_id=key_doc["client_id"],
                        created_at=key_doc["created_at"],
                        expires_at=key_doc["expires_at"],
                        is_active=key_doc["is_active"],
                        last_used_at=key_doc.get("last_used_at"),
                        usage_count=key_doc.get("usage_count", 0)
                    )
                    
                    # Проверяем валидность
                    if api_key.is_valid():
                        return api_key
                    else:
                        logger.warning(f"API key expired or inactive: {key[:20]}...")
                        return None
            except Exception as e:
                logger.debug(f"Failed to verify key hash: {e}")
                continue
        
        logger.warning(f"API key not found: {key[:20]}...")
        return None
    
    def _update_key_usage(self, key_id):
        """Обновить статистику использования ключа"""
        try:
            self.db.api_keys_collection.update_one(
                {"_id": key_id},
                {
                    "$set": {"last_used_at": datetime.utcnow()},
                    "$inc": {"usage_count": 1}
                }
            )
        except Exception as e:
            logger.warning(f"Failed to update key usage: {e}")
    
    def revoke_key(self, key: str) -> bool:
        """
        Отозвать API ключ
        
        Args:
            key: API ключ для отзыва
        
        Returns:
            True если успешно отозван
        """
        # Находим ключ
        all_keys = list(self.db.api_keys_collection.find({"is_active": True}))
        
        for key_doc in all_keys:
            key_hash = key_doc.get("key_hash")
            if key_hash:
                try:
                    if bcrypt.checkpw(key.encode(), key_hash.encode()):
                        # Деактивируем ключ
                        self.db.api_keys_collection.update_one(
                            {"_id": key_doc["_id"]},
                            {"$set": {"is_active": False}}
                        )
                        logger.info(f"API key revoked: {key[:20]}...")
                        return True
                except Exception:
                    continue
        
        return False
    
    def get_client_keys(self, client_id: str) -> list:
        """
        Получить все ключи клиента
        
        Args:
            client_id: ID клиента
        
        Returns:
            Список ключей (без хешей, только метаданные)
        """
        keys = list(
            self.db.api_keys_collection.find({
                "client_id": client_id,
                "is_active": True
            })
        )
        
        # Удаляем хеши из результата
        for key in keys:
            key.pop("key_hash", None)
            key.pop("_id", None)
        
        return keys
