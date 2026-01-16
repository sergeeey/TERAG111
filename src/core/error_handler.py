"""
TeragErrorHandler - обработка ошибок с fallback на backup Neo4j
"""

import logging
import os
from contextlib import contextmanager
from typing import Optional, Dict, Any, Iterator
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase, Driver, Session
    from neo4j.exceptions import ServiceUnavailable, TransientError, DatabaseError
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j driver not available")


class Neo4jError(Exception):
    """Базовое исключение для ошибок Neo4j"""
    pass


class TeragErrorHandler:
    """
    Обработчик ошибок TERAG с автоматическим fallback на backup Neo4j
    """
    
    def __init__(
        self,
        primary_uri: Optional[str] = None,
        primary_user: Optional[str] = None,
        primary_password: Optional[str] = None,
        backup_uri: Optional[str] = None,
        backup_user: Optional[str] = None,
        backup_password: Optional[str] = None
    ):
        """
        Инициализация Error Handler
        
        Args:
            primary_uri: URI основного Neo4j (или из NEO4J_URI)
            primary_user: Пользователь основного Neo4j (или из NEO4J_USER)
            primary_password: Пароль основного Neo4j (или из NEO4J_PASSWORD)
            backup_uri: URI backup Neo4j (или из NEO4J_BACKUP_URI)
            backup_user: Пользователь backup Neo4j (или из NEO4J_BACKUP_USER)
            backup_password: Пароль backup Neo4j (или из NEO4J_BACKUP_PASSWORD)
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not installed")
        
        # Primary Neo4j
        self.primary_uri = primary_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.primary_user = primary_user or os.getenv("NEO4J_USER", "neo4j")
        self.primary_password = primary_password or os.getenv("NEO4J_PASSWORD", "password")
        
        # Backup Neo4j
        self.backup_uri = backup_uri or os.getenv("NEO4J_BACKUP_URI")
        self.backup_user = backup_user or os.getenv("NEO4J_BACKUP_USER", "neo4j")
        self.backup_password = backup_password or os.getenv("NEO4J_BACKUP_PASSWORD", "password")
        
        # Состояние
        self.primary_driver: Optional[Driver] = None
        self.backup_driver: Optional[Driver] = None
        self.current_driver: Optional[Driver] = None
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.using_backup = False
        
        # Инициализация драйверов
        self._init_primary()
        if self.backup_uri:
            self._init_backup()
        
        # Telegram alerts
        try:
            from src.core.alerts.telegram import TelegramAlertService
            self.alert_service = TelegramAlertService()
        except ImportError:
            # Fallback: используем telegram_service если alerts недоступен
            try:
                from src.integration.telegram_service import bot
                self.alert_service = bot  # Используем bot напрямую
                logger.info("Using telegram_service as fallback for alerts")
            except ImportError:
                logger.warning("TelegramAlertService and telegram_service not available")
                self.alert_service = None
        
        logger.info(f"TeragErrorHandler initialized (backup: {self.backup_uri is not None})")
    
    def _init_primary(self):
        """Инициализация primary Neo4j driver"""
        try:
            self.primary_driver = GraphDatabase.driver(
                self.primary_uri,
                auth=(self.primary_user, self.primary_password)
            )
            self.primary_driver.verify_connectivity()
            self.current_driver = self.primary_driver
            self.using_backup = False
            logger.info(f"Primary Neo4j connected: {self.primary_uri}")
        except Exception as e:
            logger.error(f"Failed to connect to primary Neo4j: {e}")
            self.primary_driver = None
    
    def _init_backup(self):
        """Инициализация backup Neo4j driver"""
        if not self.backup_uri:
            return
        
        try:
            self.backup_driver = GraphDatabase.driver(
                self.backup_uri,
                auth=(self.backup_user, self.backup_password)
            )
            self.backup_driver.verify_connectivity()
            logger.info(f"Backup Neo4j connected: {self.backup_uri}")
        except Exception as e:
            logger.warning(f"Failed to connect to backup Neo4j: {e}")
            self.backup_driver = None
    
    @contextmanager
    def handle_errors(self, context: Dict[str, Any]) -> Iterator[Session]:
        """
        Context manager для обработки ошибок Neo4j с автоматическим fallback
        
        Args:
            context: Контекст операции (для логирования)
        
        Yields:
            Neo4j Session
        
        Raises:
            Neo4jError: Если оба Neo4j недоступны
        """
        session = None
        try:
            # Пытаемся использовать текущий driver
            if not self.current_driver:
                if self.primary_driver:
                    self.current_driver = self.primary_driver
                elif self.backup_driver:
                    self.current_driver = self.backup_driver
                    self.using_backup = True
                else:
                    raise Neo4jError("No Neo4j drivers available")
            
            # Создаем session
            session = self.current_driver.session()
            yield session
            
            # Успешная операция - сбрасываем счетчик ошибок
            if self.using_backup:
                # Пытаемся вернуться на primary
                try:
                    if self.primary_driver:
                        self.primary_driver.verify_connectivity()
                        self.current_driver = self.primary_driver
                        self.using_backup = False
                        self.failure_count = 0
                        logger.info("Switched back to primary Neo4j")
                except Exception:
                    pass  # Primary все еще недоступен
            
            self.failure_count = 0
        
        except (ServiceUnavailable, TransientError, DatabaseError) as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            # Логируем ошибку
            error_info = {
                "error": str(e),
                "error_type": type(e).__name__,
                "context": context,
                "severity": "CRITICAL" if self.failure_count >= 3 else "WARNING",
                "failure_count": self.failure_count,
                "using_backup": self.using_backup
            }
            
            logger.error(f"Neo4j error: {error_info}")
            
            # Сохраняем в Neo4j (если доступен)
            self.log_to_neo4j(error_info)
            
            # Отправляем Telegram alert
            if self.alert_service:
                self.alert_service.send_critical_alert(
                    f"🔥 CRITICAL Neo4j Error: {str(e)}\n"
                    f"Context: {context}\n"
                    f"Failure count: {self.failure_count}"
                )
            
            # Пытаемся переключиться на backup
            if not self.using_backup and self.backup_driver:
                try:
                    self.switch_to_backup()
                    # Рекурсивно пытаемся выполнить операцию на backup
                    with self.handle_errors(context) as backup_session:
                        yield backup_session
                    return
                except Exception as backup_error:
                    logger.error(f"Backup Neo4j also failed: {backup_error}")
            
            # Если backup тоже не работает или его нет
            raise Neo4jError(f"Neo4j operation failed: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error in Neo4j operation: {e}")
            raise
        
        finally:
            if session:
                session.close()
    
    def switch_to_backup(self):
        """
        Переключиться на backup Neo4j
        """
        if not self.backup_driver:
            raise Neo4jError("Backup Neo4j not configured")
        
        try:
            self.backup_driver.verify_connectivity()
            self.current_driver = self.backup_driver
            self.using_backup = True
            logger.warning("Switched to backup Neo4j")
            
            # Отправляем alert
            if self.alert_service:
                self.alert_service.send_critical_alert(
                    "⚠️ Switched to backup Neo4j\n"
                    f"Primary: {self.primary_uri}\n"
                    f"Backup: {self.backup_uri}"
                )
        except Exception as e:
            logger.error(f"Failed to switch to backup: {e}")
            raise
    
    def log_to_neo4j(self, error_info: Dict[str, Any]):
        """
        Сохранить информацию об ошибке в Neo4j
        
        Args:
            error_info: Информация об ошибке
        """
        # Пытаемся сохранить в доступный Neo4j (primary или backup)
        target_driver = self.current_driver or self.primary_driver or self.backup_driver
        
        if not target_driver:
            logger.warning("Cannot log to Neo4j: no drivers available")
            return
        
        try:
            with target_driver.session() as session:
                session.run(
                    """
                    CREATE (e:ErrorLog {
                        error: $error,
                        error_type: $error_type,
                        severity: $severity,
                        failure_count: $failure_count,
                        timestamp: datetime(),
                        context: $context
                    })
                    """,
                    error=error_info.get("error"),
                    error_type=error_info.get("error_type"),
                    severity=error_info.get("severity"),
                    failure_count=error_info.get("failure_count"),
                    context=str(error_info.get("context", {}))
                )
        except Exception as e:
            logger.warning(f"Failed to log error to Neo4j: {e}")
    
    def close(self):
        """Закрыть все подключения"""
        if self.primary_driver:
            self.primary_driver.close()
        if self.backup_driver:
            self.backup_driver.close()
        logger.info("TeragErrorHandler closed")
