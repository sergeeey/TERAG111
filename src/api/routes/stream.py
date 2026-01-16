"""
FastAPI SSE Stream для TERAG ReasonGraph
Потоковая передача состояния reasoning в реальном времени
"""
import logging
import json
import asyncio
from fastapi import APIRouter, Query, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from typing import Optional, Set, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from src.core.agents.langgraph_core import TERAGStateGraph, TERAGState
    from src.core.agents.langgraph_serializer import LangGraphSerializer
    from src.core.agents.langgraph_integration import get_terag_graph, TERAGLangGraphIntegration
    from src.core.exceptions import StreamError, GraphError, ValidationError
    from src.api.models.reasoning import ReasoningQuery
    from src.core.utils.logging import generate_trace_id
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    logger.warning(f"LangGraph components not available: {e}")


router = APIRouter(prefix="/api/stream", tags=["stream"])

# Глобальный сериализатор
_serializer = LangGraphSerializer() if LANGGRAPH_AVAILABLE else None

# Хранилище активных потоков (thread_id -> graph)
_active_streams: Dict[str, TERAGStateGraph] = {}


@router.get("/reasoning")
async def stream_reasoning(
    request: Request,
    query_params: ReasoningQuery = Depends(),
    graph: TERAGLangGraphIntegration = Depends(get_terag_graph)
):
    """
    SSE поток для передачи ReasonGraph в реальном времени
    
    Args:
        request: FastAPI Request для проверки разрыва соединения
        query_params: Валидированные параметры запроса
        graph: TERAG граф (dependency injection)
    
    Returns:
        SSE поток с обновлениями ReasonGraph
    """
    if not LANGGRAPH_AVAILABLE:
        raise HTTPException(status_code=503, detail="LangGraph not available")
    
    # Генерируем trace_id
    trace_id = generate_trace_id()
    
    # Валидация параметров через Pydantic
    try:
        query = query_params.query
        show = query_params.show
        thread_id = query_params.thread_id
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Парсим фильтр
    filter_nodes: Set[str] = set(show) if show else set()
    
    async def event_generator():
        """Генератор событий SSE"""
        try:
            # Получаем граф из dependency injection
            state_graph = graph.state_graph
            
            # Сохраняем thread_id
            if thread_id:
                _active_streams[thread_id] = state_graph
            
            # Запускаем reasoning с потоковой передачей
            config = {"configurable": {"thread_id": thread_id}} if thread_id else {}
            
            # Используем stream для получения промежуточных состояний
            initial_state: TERAGState = {
                "query": query,
                "scratchpad": [],
                "reasoning_steps": [],
                "current_step": "start",
                "guardrail_result": None,
                "ethical_evaluation": None,
                "ethical_score": 1.0,
                "alignment_status": "ethical",
                "secure_reasoning_index": 1.0,
                "final_answer": None,
                "confidence": 0.0,
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "2.1.0"
                }
            }
            
            # Отправляем начальное состояние
            reason_graph = _serializer.serialize(initial_state)
            reason_graph = _filter_nodes(reason_graph, filter_nodes)
            
            yield f"data: {json.dumps({'type': 'init', 'data': reason_graph})}\n\n"
            
            # Запускаем reasoning и отправляем обновления
            async for state_update in state_graph.app.astream(initial_state, config=config):
                # Проверяем, не закрыл ли клиент соединение
                if await request.is_disconnected():
                    logger.info(f"Client disconnected, stopping stream (trace_id: {trace_id})")
                    break
                
                # Сериализуем обновленное состояние
                current_state = state_update.get(list(state_update.keys())[0]) if state_update else initial_state
                reason_graph = _serializer.serialize(
                    current_state,
                    trace_id=trace_id,
                    mlflow_tracer=graph.mlflow_tracer if hasattr(graph, 'mlflow_tracer') else None,
                    langsmith_tracer=graph.langsmith_tracer if hasattr(graph, 'langsmith_tracer') else None
                )
                reason_graph = _filter_nodes(reason_graph, filter_nodes)
                
                # Отправляем обновление
                yield f"data: {json.dumps({'type': 'update', 'data': reason_graph})}\n\n"
                
                # Небольшая задержка для плавности
                await asyncio.sleep(0.1)
            
            # Отправляем финальное состояние (если соединение не разорвано)
            if not await request.is_disconnected():
                try:
                    final_state = await state_graph.app.ainvoke(initial_state, config=config)
                    final_reason_graph = _serializer.serialize(
                        final_state,
                        trace_id=trace_id,
                        mlflow_tracer=graph.mlflow_tracer if hasattr(graph, 'mlflow_tracer') else None,
                        langsmith_tracer=graph.langsmith_tracer if hasattr(graph, 'langsmith_tracer') else None
                    )
                    final_reason_graph = _filter_nodes(final_reason_graph, filter_nodes)
                    
                    yield f"data: {json.dumps({'type': 'complete', 'data': final_reason_graph})}\n\n"
                except GraphError as e:
                    logger.error(f"Graph error in final state: {e}", extra={"trace_id": trace_id})
                    yield f"data: {json.dumps({'type': 'error', 'code': 'GRAPH_ERROR', 'message': 'Graph unavailable', 'trace_id': trace_id})}\n\n"
            
        except GraphError as e:
            logger.error(f"Graph error: {e}", exc_info=True, extra={"trace_id": trace_id})
            yield f"data: {json.dumps({'type': 'error', 'code': 'GRAPH_ERROR', 'message': 'Graph unavailable', 'trace_id': trace_id})}\n\n"
        except StreamError as e:
            logger.warning(f"Stream error: {e}", extra={"trace_id": trace_id})
            yield f"data: {json.dumps({'type': 'error', 'code': 'STREAM_ERROR', 'message': str(e), 'trace_id': trace_id})}\n\n"
        except ValidationError as e:
            logger.warning(f"Validation error: {e}", extra={"trace_id": trace_id})
            yield f"data: {json.dumps({'type': 'error', 'code': 'VALIDATION_ERROR', 'message': str(e), 'trace_id': trace_id})}\n\n"
        except Exception as e:
            logger.critical(f"Unexpected error: {e}", exc_info=True, extra={"trace_id": trace_id})
            yield f"data: {json.dumps({'type': 'error', 'code': 'INTERNAL_ERROR', 'message': 'Internal server error', 'trace_id': trace_id})}\n\n"
        finally:
            # Cleanup: очищаем thread_id и закрываем соединения
            if thread_id and thread_id in _active_streams:
                del _active_streams[thread_id]
                logger.info(f"Stream cleanup completed for thread_id: {thread_id} (trace_id: {trace_id})")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


def _filter_nodes(reason_graph: Dict, filter_nodes: Set[str]) -> Dict:
    """Отфильтровать узлы по типу"""
    if not filter_nodes:
        return reason_graph
    
    filtered_nodes = [
        node for node in reason_graph.get("nodes", [])
        if node.get("type") in filter_nodes
    ]
    
    # Обновляем связи для отфильтрованных узлов
    filtered_node_ids = {node["id"] for node in filtered_nodes}
    filtered_edges = [
        edge for edge in reason_graph.get("edges", [])
        if edge.get("source") in filtered_node_ids and edge.get("target") in filtered_node_ids
    ]
    
    result = reason_graph.copy()
    result["nodes"] = filtered_nodes
    result["edges"] = filtered_edges
    
    return result


@router.get("/status")
def get_stream_status(thread_id: Optional[str] = Query(None)):
    """Получить статус активных потоков"""
    if thread_id:
        active = thread_id in _active_streams
        return {"thread_id": thread_id, "active": active}
    else:
        return {
            "active_streams": list(_active_streams.keys()),
            "count": len(_active_streams)
        }


