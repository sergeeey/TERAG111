"""
LangGraph Serializer для TERAG
Сериализация состояния LangGraph в ReasonGraph JSON
"""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

from .langgraph_core import TERAGState

# Порог confidence согласно стандартам TERAG
CONFIDENCE_THRESHOLD = 0.6


class LangGraphSerializer:
    """
    Сериализатор для преобразования TERAGState в ReasonGraph JSON
    
    Функции:
    1. Сериализация состояния в формат ReasonGraph
    2. Генерация позиций узлов для 3D визуализации
    3. Создание временной линии reasoning
    """
    
    # Позиции узлов в 3D пространстве
    NODE_POSITIONS = {
        "guardrail": {"x": 0, "y": 2, "z": 0},
        "planner": {"x": -2, "y": 1, "z": 0},
        "solver": {"x": 0, "y": 0, "z": 0},
        "verifier": {"x": 2, "y": -1, "z": 0},
        "ethical": {"x": 0, "y": -2, "z": 0},
        "reject": {"x": -4, "y": 0, "z": 0}
    }
    
    def __init__(self):
        """Инициализация сериализатора"""
        logger.info("LangGraphSerializer initialized")
    
    def serialize(
        self,
        state: TERAGState,
        include_scratchpad: bool = True,
        trace_id: Optional[str] = None,
        mlflow_tracer=None,
        langsmith_tracer=None
    ) -> Dict[str, Any]:
        """
        Сериализовать TERAGState в ReasonGraph JSON
        
        Args:
            state: Состояние LangGraph
            include_scratchpad: Включить scratchpad
            trace_id: ID трассировки для логирования
            mlflow_tracer: MLflow tracer для observability
            langsmith_tracer: LangSmith tracer для observability
        
        Returns:
            ReasonGraph JSON
        """
        trace_id = trace_id or state.get("metadata", {}).get("trace_id", "unknown")
        
        logger.info(
            "Serializing TERAGState to ReasonGraph",
            extra={
                "trace_id": trace_id,
                "query": state.get("query", "")[:100],
                "num_steps": len(state.get("reasoning_steps", []))
            }
        )
        
        # Создаем узлы
        nodes = self._create_nodes(state, trace_id)
        
        # Создаем связи
        edges = self._create_edges(state, nodes, trace_id)
        
        # Метаданные
        metadata = self._create_metadata(state, trace_id)
        
        # Временная линия
        timeline = self._create_timeline(state, trace_id)
        
        result = {
            "nodes": nodes,
            "edges": edges,
            "metadata": metadata,
            "timeline": timeline
        }
        
        # Добавляем scratchpad если нужно
        if include_scratchpad:
            result["scratchpad"] = state.get("scratchpad", [])
        
        # Логирование в MLflow
        if mlflow_tracer:
            try:
                mlflow_tracer.log_reason_graph(result)
            except Exception as e:
                logger.warning(f"Failed to log to MLflow: {e}", extra={"trace_id": trace_id})
        
        # Логирование в LangSmith
        if langsmith_tracer:
            try:
                langsmith_tracer.log_reason_graph(result)
            except Exception as e:
                logger.warning(f"Failed to log to LangSmith: {e}", extra={"trace_id": trace_id})
        
        return result
    
    def _create_nodes(self, state: TERAGState, trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Создать узлы из состояния"""
        nodes = []
        reasoning_steps = state.get("reasoning_steps", [])
        current_step = state.get("current_step", "start")
        trace_id = trace_id or state.get("metadata", {}).get("trace_id", "unknown")
        
        # Узел Guardrail
        guardrail_result = state.get("guardrail_result")
        if guardrail_result is not None:
            nodes.append({
                "id": "node_guardrail",
                "type": "guardrail",
                "label": "Guardrail",
                "status": "completed" if guardrail_result.get("safe", True) else "failed",
                "confidence": guardrail_result.get("confidence", 1.0),
                "timestamp": state.get("metadata", {}).get("timestamp", ""),
                "data": guardrail_result,
                "position": self.NODE_POSITIONS["guardrail"]
            })
        
        # Узлы из reasoning_steps
        for i, step in enumerate(reasoning_steps):
            step_name = step.get("step", "unknown")
            step_id = f"node_{i}_{step_name}"
            
            # Определяем статус
            status = "active" if step_name == current_step else "completed"
            
            # Извлекаем confidence из результата
            result = step.get("result", {})
            confidence = result.get("confidence", state.get("confidence", 0.0))
            
            # Валидация confidence согласно стандартам TERAG
            if confidence < CONFIDENCE_THRESHOLD:
                logger.warning(
                    f"Low confidence node detected: {step_name} (confidence: {confidence:.2f} < {CONFIDENCE_THRESHOLD})",
                    extra={
                        "confidence": confidence,
                        "threshold": CONFIDENCE_THRESHOLD,
                        "step": step_name,
                        "trace_id": trace_id
                    }
                )
                # Помечаем как questionable
                if status == "completed":
                    status = "questionable"
            
            node = {
                "id": step_id,
                "type": step_name,
                "label": step_name.capitalize(),
                "status": status,
                "confidence": confidence,
                "timestamp": step.get("timestamp", ""),
                "data": result,
                "position": self.NODE_POSITIONS.get(step_name, {"x": 0, "y": 0, "z": 0})
            }
            
            nodes.append(node)
        
        # Узел Ethical (если есть)
        ethical_evaluation = state.get("ethical_evaluation")
        if ethical_evaluation:
            nodes.append({
                "id": "node_ethical",
                "type": "ethical",
                "label": "Ethical Evaluation",
                "status": "completed",
                "confidence": state.get("ethical_score", 1.0),
                "timestamp": datetime.utcnow().isoformat(),
                "data": ethical_evaluation,
                "position": self.NODE_POSITIONS["ethical"]
            })
        
        # Узел Reject (если запрос отклонен)
        if not guardrail_result or not guardrail_result.get("safe", True):
            nodes.append({
                "id": "node_reject",
                "type": "reject",
                "label": "Rejected",
                "status": "completed",
                "confidence": 0.0,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"reason": guardrail_result.get("reason", "unsafe") if guardrail_result else "unknown"},
                "position": self.NODE_POSITIONS["reject"]
            })
        
        return nodes
    
    def _create_edges(self, state: TERAGState, nodes: List[Dict[str, Any]], trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Создать связи между узлами"""
        edges = []
        reasoning_steps = state.get("reasoning_steps", [])
        guardrail_result = state.get("guardrail_result")
        trace_id = trace_id or state.get("metadata", {}).get("trace_id", "unknown")
        
        # Связь от Guardrail
        if guardrail_result:
            guardrail_node = next((n for n in nodes if n["type"] == "guardrail"), None)
            if guardrail_node:
                if guardrail_result.get("safe", True):
                    # Связь к первому reasoning узлу
                    if reasoning_steps:
                        first_step = reasoning_steps[0]
                        first_node = next((n for n in nodes if n["id"].endswith(f"_{first_step.get('step')}")), None)
                        if first_node:
                            edges.append({
                                "id": "edge_guardrail_start",
                                "source": guardrail_node["id"],
                                "target": first_node["id"],
                                "type": "guardrail_check",
                                "confidence": guardrail_result.get("confidence", 1.0),
                                "data_flow": {"status": "approved"}
                            })
                else:
                    # Связь к Reject
                    reject_node = next((n for n in nodes if n["type"] == "reject"), None)
                    if reject_node:
                        edges.append({
                            "id": "edge_guardrail_reject",
                            "source": guardrail_node["id"],
                            "target": reject_node["id"],
                            "type": "reject",
                            "confidence": 0.0,
                            "data_flow": {"reason": guardrail_result.get("reason", "unsafe")}
                        })
        
        # Связи между reasoning шагами
        for i in range(len(reasoning_steps) - 1):
            current_step = reasoning_steps[i]
            next_step = reasoning_steps[i + 1]
            
            current_node = next((n for n in nodes if n["id"].endswith(f"_{current_step.get('step')}")), None)
            next_node = next((n for n in nodes if n["id"].endswith(f"_{next_step.get('step')}")), None)
            
            if current_node and next_node:
                edges.append({
                    "id": f"edge_{i}_{i+1}",
                    "source": current_node["id"],
                    "target": next_node["id"],
                    "type": "reasoning_flow",
                    "confidence": state.get("confidence", 0.5),
                    "data_flow": {
                        "from": current_step.get("step"),
                        "to": next_step.get("step")
                    }
                })
        
        return edges
    
    def _create_metadata(self, state: TERAGState, trace_id: Optional[str] = None) -> Dict[str, Any]:
        """Создать метаданные"""
        metadata = state.get("metadata", {})
        return {
            "query": state.get("query", ""),
            "final_answer": state.get("final_answer", ""),
            "confidence": state.get("confidence", 0.0),
            "ethical_score": state.get("ethical_score", 1.0),
            "alignment_status": state.get("alignment_status", "ethical"),
            "secure_reasoning_index": state.get("secure_reasoning_index", 1.0),
            "timestamp": metadata.get("timestamp", datetime.utcnow().isoformat()),
            "version": metadata.get("version", "2.1.0"),
            "trace_id": trace_id or metadata.get("trace_id")
        }
    
    def _create_timeline(self, state: TERAGState, trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Создать временную линию"""
        timeline = []
        reasoning_steps = state.get("reasoning_steps", [])
        trace_id = trace_id or state.get("metadata", {}).get("trace_id", "unknown")
        
        for i, step in enumerate(reasoning_steps):
            timestamp_str = step.get("timestamp", "")
            
            # Вычисляем длительность (упрощенно)
            duration = 0.5  # По умолчанию 0.5 секунды
            
            timeline.append({
                "step": step.get("step", "unknown"),
                "timestamp": timestamp_str,
                "duration": duration,
                "trace_id": trace_id
            })
        
        return timeline
    
    def to_json(self, state: TERAGState, indent: int = 2) -> str:
        """
        Преобразовать состояние в JSON строку
        
        Args:
            state: Состояние LangGraph
            indent: Отступ для форматирования
        
        Returns:
            JSON строка
        """
        reason_graph = self.serialize(state)
        return json.dumps(reason_graph, indent=indent, ensure_ascii=False)


