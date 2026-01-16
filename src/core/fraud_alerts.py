"""
Telegram alerts для fraud detection patterns
"""

import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Кэш для предотвращения дублирования алертов
_alert_cache = {}
_cache_ttl = timedelta(minutes=5)


def _get_alert_key(alert: Dict[str, Any]) -> str:
    """Генерировать уникальный ключ для алерта"""
    alert_type = alert.get('type', 'unknown')
    
    if alert_type == 'fraud_ring':
        return f"ring_{alert.get('ring_id', 'unknown')}"
    elif alert_type == 'high_link_count':
        return f"high_link_{alert.get('client_id', 'unknown')}"
    elif alert_type == 'shared_phone':
        return f"phone_{alert.get('phone', 'unknown')}"
    else:
        return f"{alert_type}_{datetime.utcnow().isoformat()}"


def _is_alert_cached(alert: Dict[str, Any]) -> bool:
    """Проверить, был ли уже отправлен этот алерт"""
    alert_key = _get_alert_key(alert)
    
    if alert_key in _alert_cache:
        cached_time = _alert_cache[alert_key]
        if datetime.utcnow() - cached_time < _cache_ttl:
            return True
    
    return False


def _cache_alert(alert: Dict[str, Any]):
    """Кэшировать отправленный алерт"""
    alert_key = _get_alert_key(alert)
    _alert_cache[alert_key] = datetime.utcnow()
    
    # Очистка старых записей (старше TTL)
    expired_keys = [
        key for key, time in _alert_cache.items()
        if datetime.utcnow() - time > _cache_ttl
    ]
    for key in expired_keys:
        del _alert_cache[key]


def format_fraud_alert(alert: Dict[str, Any]) -> str:
    """
    Форматировать fraud alert для Telegram
    
    Args:
        alert: Объект алерта от fraud detector
    
    Returns:
        Отформатированное сообщение
    """
    alert_type = alert.get('type', 'unknown')
    risk_level = alert.get('risk_level', 'medium')
    
    # Эмодзи по risk level
    emoji_map = {
        'critical': '🚨',
        'high': '⚠️',
        'medium': 'ℹ️'
    }
    emoji = emoji_map.get(risk_level, '📢')
    
    message_parts = [f"{emoji} *TERAG Fraud Alert*"]
    message_parts.append(f"Type: `{alert_type}`")
    message_parts.append(f"Risk: `{risk_level}`")
    
    if alert_type == 'fraud_ring':
        message_parts.append(f"Ring ID: `{alert.get('ring_id', 'N/A')}`")
        message_parts.append(f"Members: `{alert.get('member_count', 0)}`")
        message_parts.append(f"Density: `{alert.get('density', 0):.2f}`")
        if alert.get('member_ids'):
            member_ids = alert['member_ids'][:5]  # Показываем первые 5
            message_parts.append(f"Member IDs: `{', '.join(member_ids)}`")
            if len(alert['member_ids']) > 5:
                message_parts.append(f"... and {len(alert['member_ids']) - 5} more")
    
    elif alert_type == 'high_link_count':
        message_parts.append(f"Client ID: `{alert.get('client_id', 'N/A')}`")
        message_parts.append(f"Client Name: `{alert.get('client_name', 'Unknown')}`")
        message_parts.append(f"Link Count: `{alert.get('link_count', 0)}`")
        message_parts.append(f"Threshold: `{alert.get('threshold', 0)}`")
    
    elif alert_type == 'shared_phone':
        message_parts.append(f"Phone: `{alert.get('phone', 'N/A')}`")
        message_parts.append(f"Client Count: `{alert.get('client_count', 0)}`")
        message_parts.append(f"Threshold: `{alert.get('threshold', 0)}`")
        if alert.get('client_ids'):
            client_ids = alert['client_ids'][:5]  # Показываем первые 5
            message_parts.append(f"Client IDs: `{', '.join(client_ids)}`")
            if len(alert['client_ids']) > 5:
                message_parts.append(f"... and {len(alert['client_ids']) - 5} more")
    
    message_parts.append(f"Detected: `{alert.get('detected_at', datetime.utcnow().isoformat())}`")
    
    return "\n".join(message_parts)


async def send_fraud_alerts(
    alerts: List[Dict[str, Any]],
    only_critical: bool = True
) -> int:
    """
    Отправить fraud alerts в Telegram
    
    Args:
        alerts: Список алертов от fraud detector
        only_critical: Отправлять только critical alerts (по умолчанию True)
    
    Returns:
        Количество отправленных алертов
    """
    sent_count = 0
    
    try:
        from src.integration.telegram_service import bot, TELEGRAM_CHAT_ID
        
        if not bot or not TELEGRAM_CHAT_ID:
            logger.warning("Telegram bot or chat ID not configured")
            return 0
        
        for alert in alerts:
            # Фильтр по risk level
            if only_critical and alert.get('risk_level') != 'critical':
                continue
            
            # Проверка кэша (не отправлять дубликаты)
            if _is_alert_cached(alert):
                logger.debug(f"Alert already sent recently, skipping: {alert.get('type')}")
                continue
            
            # Форматируем сообщение
            message = format_fraud_alert(alert)
            
            # Отправляем в Telegram
            try:
                await bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=message,
                    parse_mode="Markdown"
                )
                
                _cache_alert(alert)
                sent_count += 1
                logger.info(f"Fraud alert sent to Telegram: {alert.get('type')}")
            except Exception as e:
                logger.error(f"Failed to send Telegram alert: {e}")
                continue
        
        logger.info(f"Sent {sent_count} fraud alerts to Telegram")
    except ImportError:
        logger.warning("Telegram service not available")
    except Exception as e:
        logger.error(f"Error sending fraud alerts: {e}")
    
    return sent_count


def send_fraud_alerts_sync(
    alerts: List[Dict[str, Any]],
    only_critical: bool = True
) -> int:
    """
    Синхронная версия send_fraud_alerts
    
    Args:
        alerts: Список алертов от fraud detector
        only_critical: Отправлять только critical alerts
    
    Returns:
        Количество отправленных алертов
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Если loop уже запущен, создаем task
            task = asyncio.create_task(send_fraud_alerts(alerts, only_critical))
            return 0  # Не ждем завершения
        else:
            # Если loop не запущен, запускаем
            return loop.run_until_complete(send_fraud_alerts(alerts, only_critical))
    except RuntimeError:
        # Нет event loop, создаем новый
        return asyncio.run(send_fraud_alerts(alerts, only_critical))
