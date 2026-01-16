"""
Multi-Agent System — система агентов для TERAG Evolution Loop

Агенты:
- Planner: Планирование рассуждений
- Researcher: Сбор данных из графа
- Verifier: Проверка достоверности
- Writer: Составление отчётов
- Critic: Критический анализ
- GuardrailNode: Защита от prompt injection
- TERAGStateGraph: LangGraph Core для трассировки
"""
from .planner import Planner
from .researcher import Researcher
from .verifier import Verifier
from .writer import Writer
from .critic import Critic

# LangGraph Core (TERAG 2.1)
try:
    from .guardrail_node import GuardrailNode
    from .langgraph_core import TERAGStateGraph, TERAGState
    from .langgraph_integration import TERAGLangGraphIntegration
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    GuardrailNode = None
    TERAGStateGraph = None
    TERAGState = None
    TERAGLangGraphIntegration = None

__all__ = ["Planner", "Researcher", "Verifier", "Writer", "Critic"]

if LANGGRAPH_AVAILABLE:
    __all__.extend(["GuardrailNode", "TERAGStateGraph", "TERAGState", "TERAGLangGraphIntegration"])

# Phase 3: Security Layer
try:
    from .ethical_node import EthicalEvaluationNode
    ETHICAL_NODE_AVAILABLE = True
except ImportError:
    ETHICAL_NODE_AVAILABLE = False
    EthicalEvaluationNode = None

if ETHICAL_NODE_AVAILABLE:
    __all__.append("EthicalEvaluationNode")





