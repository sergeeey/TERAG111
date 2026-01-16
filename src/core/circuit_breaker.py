"""
Circuit Breaker для защиты от перегрузки Neo4j
"""

import logging
import time
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Состояния Circuit Breaker"""
    CLOSED = "CLOSED"      # Нормальная работа
    OPEN = "OPEN"          # Блокировка запросов
    HALF_OPEN = "HALF_OPEN"  # Тестовый режим


class CircuitBreakerOpenError(Exception):
    """Исключение при открытом Circuit Breaker"""
    pass


class CircuitBreaker:
    """
    Circuit Breaker для защиты от перегрузки
    
    Принцип работы:
    - CLOSED: Все запросы проходят
    - OPEN: Все запросы блокируются (после N ошибок или latency > threshold)
    - HALF_OPEN: Пробный запрос для проверки восстановления
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 30,
        latency_threshold_ms: float = 500.0,
        success_threshold: int = 2
    ):
        """
        Инициализация Circuit Breaker
        
        Args:
            failure_threshold: Количество ошибок для открытия circuit
            timeout_seconds: Время в OPEN состоянии перед переходом в HALF_OPEN
            latency_threshold_ms: Порог latency для открытия circuit (в миллисекундах)
            success_threshold: Количество успешных запросов в HALF_OPEN для закрытия circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.latency_threshold_ms = latency_threshold_ms
        self.success_threshold = success_threshold
        
        # Состояние
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        
        logger.info(
            f"CircuitBreaker initialized: "
            f"failure_threshold={failure_threshold}, "
            f"latency_threshold={latency_threshold_ms}ms"
        )
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Выполнить функцию через Circuit Breaker
        
        Args:
            func: Функция для выполнения
            *args: Аргументы функции
            **kwargs: Ключевые аргументы функции
        
        Returns:
            Результат выполнения функции
        
        Raises:
            CircuitBreakerOpenError: Если circuit открыт
        """
        # Проверяем состояние
        if self.state == CircuitState.OPEN:
            # Проверяем, прошло ли достаточно времени для перехода в HALF_OPEN
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    logger.info("Circuit Breaker: OPEN -> HALF_OPEN")
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit is OPEN. Retry after {self.timeout_seconds - int(elapsed)} seconds"
                    )
        
        # Выполняем функцию
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            
            # Рассчитываем latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Проверяем latency
            if latency_ms > self.latency_threshold_ms:
                self._on_latency_exceeded(latency_ms)
                # Не прерываем запрос, но логируем
            
            # Успешное выполнение
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Обработка успешного выполнения"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit Breaker: HALF_OPEN -> CLOSED (recovered)")
        else:
            # В CLOSED состоянии сбрасываем счетчик ошибок
            self.failure_count = 0
        
        self.last_success_time = datetime.utcnow()
    
    def _on_failure(self):
        """Обработка ошибки"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitState.HALF_OPEN:
            # В HALF_OPEN любая ошибка возвращает в OPEN
            self.state = CircuitState.OPEN
            self.success_count = 0
            logger.warning("Circuit Breaker: HALF_OPEN -> OPEN (test failed)")
        elif self.failure_count >= self.failure_threshold:
            # Превышен порог ошибок
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit Breaker: CLOSED -> OPEN "
                f"(failure_count={self.failure_count} >= {self.failure_threshold})"
            )
    
    def _on_latency_exceeded(self, latency_ms: float):
        """Обработка превышения latency"""
        if latency_ms > self.latency_threshold_ms:
            logger.warning(
                f"Circuit Breaker: Latency exceeded "
                f"({latency_ms:.2f}ms > {self.latency_threshold_ms}ms)"
            )
            
            # Если latency критически высокая, открываем circuit
            if latency_ms > self.latency_threshold_ms * 2:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    self.last_failure_time = datetime.utcnow()
                    logger.error(
                        f"Circuit Breaker: CLOSED -> OPEN "
                        f"(latency {latency_ms:.2f}ms too high)"
                    )
    
    def get_state(self) -> dict:
        """Получить текущее состояние"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None
        }
    
    def reset(self):
        """Сбросить circuit breaker в начальное состояние"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        logger.info("Circuit Breaker reset")


# Глобальный экземпляр для Neo4j операций
_neo4j_circuit_breaker: Optional[CircuitBreaker] = None


def get_neo4j_circuit_breaker() -> CircuitBreaker:
    """Получить глобальный Circuit Breaker для Neo4j"""
    global _neo4j_circuit_breaker
    if _neo4j_circuit_breaker is None:
        _neo4j_circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout_seconds=30,
            latency_threshold_ms=500.0
        )
    return _neo4j_circuit_breaker


def circuit_breaker(func: Callable) -> Callable:
    """
    Декоратор для применения Circuit Breaker к функции
    
    Usage:
        @circuit_breaker
        def my_neo4j_operation():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        breaker = get_neo4j_circuit_breaker()
        return breaker.call(func, *args, **kwargs)
    
    return wrapper
