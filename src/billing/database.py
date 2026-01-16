"""
MongoDB подключение и коллекции для биллинга
"""

import os
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

logger = logging.getLogger(__name__)


class BillingDatabase:
    """Класс для работы с MongoDB для биллинга"""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Инициализация подключения к MongoDB
        
        Args:
            connection_string: MongoDB connection string (или из переменной окружения)
        """
        self.connection_string = connection_string or os.getenv(
            "MONGODB_URI",
            "mongodb://localhost:27017/"
        )
        self.database_name = os.getenv("MONGODB_DATABASE", "terag_billing")
        
        try:
            self.client = MongoClient(self.connection_string)
            self.db: Database = self.client[self.database_name]
            # Проверяем подключение
            self.client.admin.command('ping')
            logger.info(f"MongoDB connected: {self.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @property
    def usage_collection(self) -> Collection:
        """Коллекция для учета использования"""
        return self.db.usage_meters
    
    @property
    def clients_collection(self) -> Collection:
        """Коллекция клиентов"""
        return self.db.clients
    
    @property
    def invoices_collection(self) -> Collection:
        """Коллекция инвойсов"""
        return self.db.invoices
    
    @property
    def payments_collection(self) -> Collection:
        """Коллекция платежей"""
        return self.db.payments
    
    @property
    def api_keys_collection(self) -> Collection:
        """Коллекция API ключей (для биллинга)"""
        return self.db.api_keys
    
    def create_indexes(self):
        """Создание индексов для оптимизации запросов"""
        try:
            # Индексы для usage_meters
            self.usage_collection.create_index([("client_id", 1), ("timestamp", -1)])
            self.usage_collection.create_index([("timestamp", -1)])
            self.usage_collection.create_index([("api_key_id", 1)])
            
            # Индексы для clients
            self.clients_collection.create_index([("client_id", 1)], unique=True)
            self.clients_collection.create_index([("email", 1)], unique=True)
            
            # Индексы для invoices
            self.invoices_collection.create_index([("client_id", 1), ("period_end", -1)])
            self.invoices_collection.create_index([("status", 1)])
            self.invoices_collection.create_index([("invoice_id", 1)], unique=True)
            
            # Индексы для payments
            self.payments_collection.create_index([("invoice_id", 1)])
            self.payments_collection.create_index([("transaction_id", 1)], unique=True, sparse=True)
            self.payments_collection.create_index([("status", 1)])
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def close(self):
        """Закрыть подключение"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Глобальный экземпляр (singleton)
_billing_db: Optional[BillingDatabase] = None


def get_billing_db() -> BillingDatabase:
    """Получить глобальный экземпляр BillingDatabase"""
    global _billing_db
    if _billing_db is None:
        _billing_db = BillingDatabase()
        _billing_db.create_indexes()
    return _billing_db
