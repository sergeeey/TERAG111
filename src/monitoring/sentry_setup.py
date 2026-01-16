"""
Настройка Sentry для мониторинга ошибок TERAG
"""

import os
import logging

logger = logging.getLogger(__name__)

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logger.warning("sentry-sdk not installed. Install it with: pip install sentry-sdk")


def init_sentry():
    """
    Инициализация Sentry для мониторинга ошибок
    
    Returns:
        True если Sentry инициализирован, False если нет
    """
    if not SENTRY_AVAILABLE:
        logger.warning("Sentry SDK not available. Error tracking disabled.")
        return False
    
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        logger.warning("SENTRY_DSN not set. Error tracking disabled.")
        return False
    
    try:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FastApiIntegration(),
                LoggingIntegration(
                    level=logging.INFO,        # Capture info and above
                    event_level=logging.ERROR  # Send errors as events
                ),
            ],
            traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
            profiles_sample_rate=0.1,  # 10% of transactions for profiling
            environment=os.getenv("ENVIRONMENT", "production"),
            release=os.getenv("RELEASE_VERSION", "unknown"),
        )
        logger.info("✅ Sentry initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False
