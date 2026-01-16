"""
Исключения для Circuit Breaker
"""


class CircuitBreakerOpenError(Exception):
    """Исключение при открытом Circuit Breaker"""
    pass


class CircuitBreakerError(Exception):
    """Базовое исключение Circuit Breaker"""
    pass
