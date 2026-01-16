"""
Auditor CurSor v1.2 - AI-Audit Tools
Модули для когнитивного анализа и аудита AI-систем
"""

__version__ = "1.2.0"
__author__ = "Auditor CurSor Team"

from .cognitive import CognitiveAuditor
from .observability import ObservabilityAuditor
from .ethics import EthicsAuditor
from .governance import GovernanceAuditor
from .aggregate import AuditAggregator

__all__ = [
    "CognitiveAuditor",
    "ObservabilityAuditor", 
    "EthicsAuditor",
    "GovernanceAuditor",
    "AuditAggregator"
]



































