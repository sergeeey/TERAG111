"""
TERAG LangGraph Core (T.R.A.C.)
State machine для трассируемого reasoning с полным аудитом
"""
import logging
import json
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime
from operator import add

logger = logging.getLogger(__name__)

try:
    from .mlflow_integration import MLflowTracer
    MLFLOW_TRACER_AVAILABLE = True
except ImportError:
    MLFLOW_TRACER_AVAILABLE = False
    MLflowTracer = None

try:
    from src.promptops.langsmith_integration import LangSmithTracer
    LANGSMITH_TRACER_AVAILABLE = True
except ImportError:
    LANGSMITH_TRACER_AVAILABLE = False
    LangSmithTracer = None

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph not available. Install with: pip install langgraph langgraph-checkpoint")


class TERAGState(TypedDict):
    """
    State для TERAG reasoning pipeline
    
    Содержит:
    - query: исходный запрос пользователя
    - scratchpad: рабочая память (Chain-of-Thought)
    - reasoning_steps: шаги рассуждения с трассировкой
    - current_step: текущий шаг
    - guardrail_result: результат проверки безопасности
    - ethical_evaluation: результат этической оценки (Phase 3)
    - ethical_score: этический score (0.0-1.0)
    - alignment_status: статус выравнивания (ethical/questionable/harmful)
    - secure_reasoning_index: индекс безопасного рассуждения (SRI)
    - final_answer: финальный ответ
    - metadata: метаданные для аудита
    """
    query: str
    scratchpad: Annotated[List[str], add]  # Накопительный список мыслей
    reasoning_steps: Annotated[List[Dict[str, Any]], add]  # Шаги рассуждения
    current_step: str
    guardrail_result: Optional[Dict[str, Any]]
    ethical_evaluation: Optional[Dict[str, Any]]  # Phase 3
    ethical_score: float  # Phase 3
    alignment_status: str  # Phase 3: "ethical" | "questionable" | "harmful"
    secure_reasoning_index: float  # Phase 3: SRI (0.0-1.0)
    final_answer: Optional[str]
    confidence: float
    metadata: Dict[str, Any]


class TERAGStateGraph:
    """
    TERAG State Graph - главный контур reasoning с полной трассировкой
    
    Архитектура:
    START → Guardrail → Planner → Solver → Verifier → END
                      ↓ (unsafe)
                   REJECT
    """
    
    def __init__(
        self,
        planner=None,
        solver=None,
        verifier=None,
        guardrail=None,
        ethical_node=None,  # Phase 3
        enable_checkpointing: bool = True,
        enable_mlflow: bool = True
    ):
        """
        Инициализация TERAG State Graph
        
        Args:
            planner: Planner агент
            solver: Solver агент (KAG Solver)
            verifier: Verifier агент
            guardrail: Guardrail агент для безопасности
            ethical_node: Ethical Evaluation Node (Phase 3)
            enable_checkpointing: Включить checkpointing для восстановления
            enable_mlflow: Включить MLflow трассировку
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph not installed. Install with: pip install langgraph langgraph-checkpoint")
        
        self.planner = planner
        self.solver = solver
        self.verifier = verifier
        self.guardrail = guardrail
        self.ethical_node = ethical_node  # Phase 3
        
        # MLflow tracer
        if enable_mlflow and MLFLOW_TRACER_AVAILABLE:
            self.mlflow_tracer = MLflowTracer()
        else:
            self.mlflow_tracer = None
        
        # LangSmith tracer (Phase 4)
        if LANGSMITH_TRACER_AVAILABLE:
            try:
                self.langsmith_tracer = LangSmithTracer(enable_tracing=True)
            except:
                self.langsmith_tracer = None
                logger.warning("LangSmith tracer not available")
        else:
            self.langsmith_tracer = None
        
        # Создаем граф
        self.graph = StateGraph(TERAGState)
        self._build_graph()
        
        # Checkpointing для восстановления состояния
        if enable_checkpointing:
            memory = MemorySaver()
            self.app = self.graph.compile(checkpointer=memory)
        else:
            self.app = self.graph.compile()
        
        logger.info("TERAGStateGraph initialized")
    
    def _build_graph(self):
        """Построить граф состояний"""
        # Добавляем узлы
        self.graph.add_node("guardrail", self._guardrail_node)
        self.graph.add_node("planner", self._planner_node)
        self.graph.add_node("solver", self._solver_node)
        self.graph.add_node("verifier", self._verifier_node)
        self.graph.add_node("ethical", self._ethical_node)  # Phase 3
        self.graph.add_node("reject", self._reject_node)
        
        # Определяем входную точку
        self.graph.set_entry_point("guardrail")
        
        # Добавляем переходы
        self.graph.add_conditional_edges(
            "guardrail",
            self._should_continue,
            {
                "continue": "planner",
                "reject": "reject"
            }
        )
        
        self.graph.add_edge("planner", "solver")
        self.graph.add_edge("solver", "verifier")
        self.graph.add_edge("verifier", "ethical")  # Phase 3: добавлен ethical node
        self.graph.add_edge("ethical", END)  # Phase 3
        self.graph.add_edge("reject", END)
    
    async def _guardrail_node(self, state: TERAGState) -> TERAGState:
        """
        Guardrail Node - проверка безопасности входных данных
        
        Args:
            state: Текущее состояние
        
        Returns:
            Обновленное состояние
        """
        logger.info("Guardrail: Checking input safety")
        
        if self.guardrail:
            try:
                result = await self.guardrail.check(state["query"])
                state["guardrail_result"] = result
            except Exception as e:
                logger.error(f"Error in guardrail: {e}")
                state["guardrail_result"] = {"safe": True, "confidence": 0.5, "error": str(e)}
        else:
            # Простая проверка если guardrail не настроен
            state["guardrail_result"] = {
                "safe": True,
                "confidence": 0.8,
                "reason": "Guardrail not configured, defaulting to safe"
            }
        
        state["current_step"] = "guardrail"
        state["scratchpad"].append(f"Guardrail check: {state['guardrail_result']['safe']}")
        
        return state
    
    def _should_continue(self, state: TERAGState) -> str:
        """
        Условный переход после Guardrail
        
        Args:
            state: Текущее состояние
        
        Returns:
            "continue" или "reject"
        """
        guardrail_result = state.get("guardrail_result", {})
        if guardrail_result.get("safe", True):
            return "continue"
        else:
            logger.warning(f"Input rejected by guardrail: {guardrail_result.get('reason', 'unsafe')}")
            return "reject"
    
    async def _planner_node(self, state: TERAGState) -> TERAGState:
        """
        Planner Node - планирование рассуждения
        
        Args:
            state: Текущее состояние
        
        Returns:
            Обновленное состояние
        """
        logger.info("Planner: Creating reasoning plan")
        
        if self.planner:
            try:
                plan = await self.planner.plan(state["query"])
                state["scratchpad"].append(f"Plan: {plan.get('steps', [])}")
                step_data = {
                    "step": "planner",
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": plan
                }
                state["reasoning_steps"].append(step_data)
                
                # LangSmith tracing (Phase 4)
                if self.langsmith_tracer:
                    mlflow_run_id = getattr(self.mlflow_tracer, 'current_run_id', None) if self.mlflow_tracer else None
                    self.langsmith_tracer.log_step(
                        step_name="planner",
                        inputs={"query": state["query"]},
                        outputs=plan,
                        mlflow_run_id=mlflow_run_id
                    )
            except Exception as e:
                logger.error(f"Error in planner: {e}")
                state["scratchpad"].append(f"Planner error: {str(e)}")
        else:
            # Простой план если planner не настроен
            state["scratchpad"].append("Simple plan: analyze query and generate answer")
        
        state["current_step"] = "planner"
        return state
    
    async def _solver_node(self, state: TERAGState) -> TERAGState:
        """
        Solver Node - решение задачи
        
        Args:
            state: Текущее состояние
        
        Returns:
            Обновленное состояние
        """
        logger.info("Solver: Solving query")
        
        if self.solver:
            try:
                # Используем scratchpad как контекст
                context = "\n".join(state["scratchpad"])
                result = await self.solver.reason(state["query"], context_data={"scratchpad": context})
                
                state["scratchpad"].append(f"Solution: {result.get('conclusion', '')[:200]}")
                state["reasoning_steps"].append({
                    "step": "solver",
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": result
                })
                state["confidence"] = result.get("confidence", 0.5)
            except Exception as e:
                logger.error(f"Error in solver: {e}")
                state["scratchpad"].append(f"Solver error: {str(e)}")
        else:
            state["scratchpad"].append("Solver not configured")
        
        state["current_step"] = "solver"
        return state
    
    async def _verifier_node(self, state: TERAGState) -> TERAGState:
        """
        Verifier Node - проверка результата
        
        Args:
            state: Текущее состояние
        
        Returns:
            Обновленное состояние
        """
        logger.info("Verifier: Verifying result")
        
        if self.verifier:
            try:
                # Проверяем последний шаг solver
                last_step = state["reasoning_steps"][-1] if state["reasoning_steps"] else {}
                reasoning = last_step.get("result", {})
                
                verified = await self.verifier.check(reasoning)
                
                state["scratchpad"].append(f"Verification: {verified.get('verified', False)}")
                state["reasoning_steps"].append({
                    "step": "verifier",
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": verified
                })
                
                # Извлекаем финальный ответ
                if verified.get("verified_reasoning"):
                    state["final_answer"] = verified["verified_reasoning"].get("conclusion", "")
                elif reasoning.get("conclusion"):
                    state["final_answer"] = reasoning["conclusion"]
            except Exception as e:
                logger.error(f"Error in verifier: {e}")
                state["scratchpad"].append(f"Verifier error: {str(e)}")
        else:
            # Если verifier не настроен, используем результат solver
            last_step = state["reasoning_steps"][-1] if state["reasoning_steps"] else {}
            state["final_answer"] = last_step.get("result", {}).get("conclusion", "No answer generated")
        
        state["current_step"] = "verifier"
        return state
    
    async def _ethical_node(self, state: TERAGState) -> TERAGState:
        """
        Ethical Evaluation Node - оценка этической состоятельности ответа (Phase 3)
        
        Args:
            state: Текущее состояние
        
        Returns:
            Обновленное состояние
        """
        logger.info("Ethical Node: Evaluating ethical alignment")
        
        if self.ethical_node:
            try:
                # Оцениваем финальный ответ
                answer = state.get("final_answer", "")
                evaluation = await self.ethical_node.evaluate_alignment(answer)
                
                state["ethical_evaluation"] = evaluation
                state["ethical_score"] = evaluation.get("ethical_score", 1.0)
                state["alignment_status"] = evaluation.get("alignment_status", "ethical")
                
                state["scratchpad"].append(f"Ethical evaluation: {state['alignment_status']} (score: {state['ethical_score']:.2f})")
                state["reasoning_steps"].append({
                    "step": "ethical",
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": evaluation
                })
                
                # Вычисляем Secure Reasoning Index (SRI)
                sri = self._calculate_sri(state)
                state["secure_reasoning_index"] = sri
                
            except Exception as e:
                logger.error(f"Error in ethical node: {e}")
                state["ethical_score"] = 0.5
                state["alignment_status"] = "questionable"
                state["secure_reasoning_index"] = 0.5
        else:
            # Если ethical node не настроен, используем значения по умолчанию
            state["ethical_score"] = 1.0
            state["alignment_status"] = "ethical"
            state["secure_reasoning_index"] = 0.8
            state["scratchpad"].append("Ethical node not configured, using defaults")
        
        state["current_step"] = "ethical"
        return state
    
    def _calculate_sri(self, state: TERAGState) -> float:
        """
        Вычислить Secure Reasoning Index (SRI)
        
        SRI = (guardrail_success * 0.4) + (ethical_score * 0.6)
        
        Args:
            state: Текущее состояние
        
        Returns:
            SRI (0.0-1.0)
        """
        # Guardrail success (1.0 если прошел, 0.0 если заблокирован)
        guardrail_result = state.get("guardrail_result", {})
        guardrail_success = 1.0 if guardrail_result.get("safe", True) else 0.0
        
        # Ethical score
        ethical_score = state.get("ethical_score", 1.0)
        
        # Вычисляем SRI
        sri = (guardrail_success * 0.4) + (ethical_score * 0.6)
        
        logger.info(f"SRI calculated: {sri:.2f} (guardrail: {guardrail_success:.2f}, ethical: {ethical_score:.2f})")
        
        return sri
    
    async def _reject_node(self, state: TERAGState) -> TERAGState:
        """
        Reject Node - обработка отклоненного запроса
        
        Args:
            state: Текущее состояние
        
        Returns:
            Обновленное состояние
        """
        logger.warning("Reject: Input rejected by guardrail")
        
        guardrail_result = state.get("guardrail_result", {})
        state["final_answer"] = f"Запрос отклонен по соображениям безопасности: {guardrail_result.get('reason', 'unsafe input')}"
        state["confidence"] = 0.0
        state["current_step"] = "reject"
        
        state["reasoning_steps"].append({
            "step": "reject",
            "timestamp": datetime.utcnow().isoformat(),
            "result": {
                "rejected": True,
                "reason": guardrail_result.get("reason", "unsafe")
            }
        })
        
        return state
    
    async def run(self, query: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Запустить reasoning pipeline
        
        Args:
            query: Запрос пользователя
            config: Конфигурация для выполнения
        
        Returns:
            Результат reasoning с полной трассировкой
        """
        logger.info(f"Starting TERAG reasoning for query: {query[:100]}")
        
        # Инициализируем состояние
        initial_state: TERAGState = {
            "query": query,
            "scratchpad": [],
            "reasoning_steps": [],
            "current_step": "start",
            "guardrail_result": None,
            "ethical_evaluation": None,  # Phase 3
            "ethical_score": 1.0,  # Phase 3
            "alignment_status": "ethical",  # Phase 3
            "secure_reasoning_index": 1.0,  # Phase 3
            "final_answer": None,
            "confidence": 0.0,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "version": "2.1.0"
            }
        }
        
        # Начинаем MLflow run
        if self.mlflow_tracer:
            self.mlflow_tracer.start_run(run_name=f"reasoning_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
            self.mlflow_tracer.log_params({"query": query[:100]})
        
        try:
            # Запускаем граф
            config = config or {}
            final_state = await self.app.ainvoke(initial_state, config=config)
            
            # Логируем шаги в MLflow
            if self.mlflow_tracer:
                for step in final_state.get("reasoning_steps", []):
                    self.mlflow_tracer.log_reasoning_step(
                        step.get("step", "unknown"),
                        step.get("result", {})
                    )
            
            # Сериализуем ReasonGraph
            from .langgraph_serializer import LangGraphSerializer
            serializer = LangGraphSerializer()
            reason_graph = serializer.serialize(final_state)
            
            # Логируем ReasonGraph
            if self.mlflow_tracer:
                self.mlflow_tracer.log_reason_graph(reason_graph)
                self.mlflow_tracer.log_metrics({
                    "confidence": final_state.get("confidence", 0.0),
                    "num_steps": len(final_state.get("reasoning_steps", [])),
                    "ethical_score": final_state.get("ethical_score", 1.0),  # Phase 3
                    "secure_reasoning_index": final_state.get("secure_reasoning_index", 1.0)  # Phase 3
                })
            
            result = {
                "query": query,
                "answer": final_state.get("final_answer", ""),
                "confidence": final_state.get("confidence", 0.0),
                "reason_graph": reason_graph,
                "scratchpad": final_state.get("scratchpad", []),
                "reasoning_steps": final_state.get("reasoning_steps", []),
                "ethical_evaluation": final_state.get("ethical_evaluation"),  # Phase 3
                "ethical_score": final_state.get("ethical_score", 1.0),  # Phase 3
                "alignment_status": final_state.get("alignment_status", "ethical"),  # Phase 3
                "secure_reasoning_index": final_state.get("secure_reasoning_index", 1.0),  # Phase 3
                "metadata": final_state.get("metadata", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"TERAG reasoning completed. Confidence: {result['confidence']:.2f}")
            
            return result
        
        finally:
            # Завершаем MLflow run
            if self.mlflow_tracer:
                self.mlflow_tracer.end_run()
    
    def serialize_reason_graph(self, state: TERAGState) -> Dict[str, Any]:
        """
        Сериализовать ReasonGraph в JSON формат
        
        Args:
            state: Финальное состояние
        
        Returns:
            ReasonGraph JSON
        """
        nodes = []
        edges = []
        
        # Создаем узлы из reasoning_steps
        for i, step in enumerate(state.get("reasoning_steps", [])):
            node_id = f"node_{i}_{step.get('step', 'unknown')}"
            nodes.append({
                "id": node_id,
                "label": step.get("step", "unknown"),
                "type": step.get("step", "unknown"),
                "timestamp": step.get("timestamp", ""),
                "data": step.get("result", {})
            })
            
            # Создаем связи
            if i > 0:
                prev_node_id = f"node_{i-1}_{state['reasoning_steps'][i-1].get('step', 'unknown')}"
                edges.append({
                    "id": f"edge_{i-1}_{i}",
                    "source": prev_node_id,
                    "target": node_id,
                    "type": "reasoning_flow"
                })
        
        # Добавляем guardrail узел если есть
        if state.get("guardrail_result"):
            nodes.insert(0, {
                "id": "node_guardrail",
                "label": "Guardrail",
                "type": "guardrail",
                "data": state["guardrail_result"]
            })
            if nodes:
                edges.insert(0, {
                    "id": "edge_guardrail_start",
                    "source": "node_guardrail",
                    "target": nodes[1]["id"] if len(nodes) > 1 else "node_0",
                    "type": "guardrail_check"
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "query": state.get("query", ""),
                "final_answer": state.get("final_answer", ""),
                "confidence": state.get("confidence", 0.0),
                "ethical_score": state.get("ethical_score", 1.0),  # Phase 3
                "alignment_status": state.get("alignment_status", "ethical"),  # Phase 3
                "secure_reasoning_index": state.get("secure_reasoning_index", 1.0),  # Phase 3
                "timestamp": state.get("metadata", {}).get("timestamp", "")
            }
        }
    
    def get_reason_graph_json(self, state: TERAGState) -> str:
        """
        Получить ReasonGraph в JSON строке
        
        Args:
            state: Состояние
        
        Returns:
            JSON строка
        """
        reason_graph = self.serialize_reason_graph(state)
        return json.dumps(reason_graph, indent=2, ensure_ascii=False)

