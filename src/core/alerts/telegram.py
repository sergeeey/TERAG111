"""
Telegram Alert Service для критических уведомлений
"""

import os
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

try:
    from src.integration.telegram_service import bot, TELEGRAM_CHAT_ID
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("Telegram service not available")


class TelegramAlertService:
    """Сервис для отправки критических alerts в Telegram"""
    
    def __init__(self, chat_id: Optional[str] = None):
        """
        Инициализация Telegram Alert Service
        
        Args:
            chat_id: Telegram chat ID (или из переменной окружения)
        """
        if not TELEGRAM_AVAILABLE:
            logger.warning("Telegram service not available - alerts will not be sent")
            self.enabled = False
            return
        
        self.chat_id = chat_id or TELEGRAM_CHAT_ID or os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.chat_id)
        
        if not self.enabled:
            logger.warning("TELEGRAM_CHAT_ID not set - alerts will not be sent")
    
    def send_critical_alert(self, message: str) -> bool:
        """
        Отправить критическое уведомление в Telegram
        
        Args:
            message: Текст сообщения
        
        Returns:
            True если отправлено успешно
        """
        if not self.enabled:
            return False
        
        try:
            # Используем существующий bot из telegram_service
            if TELEGRAM_AVAILABLE and bot:
                # Отправляем синхронно (или через asyncio если нужно)
                loop = None
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if loop.is_running():
                    # Если loop уже запущен, создаем task
                    asyncio.create_task(self._send_async(message))
                else:
                    # Если loop не запущен, запускаем
                    loop.run_until_complete(self._send_async(message))
                
                logger.info(f"Critical alert sent to Telegram: {message[:100]}")
                return True
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    async def _send_async(self, message: str):
        """Асинхронная отправка сообщения"""
        try:
            if bot and self.chat_id:
                await bot.send_message(
                    self.chat_id,
                    f"🚨 TERAG Critical Alert\n\n{message}",
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Failed to send async Telegram alert: {e}")
