"""
Hybrid GraphRAG Pipeline
Агентный router между Vector-RAG и Graph-RAG
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from src.integration.lmstudio_client import LMStudioClient
    LMSTUDIO_AVAILABLE = True
except ImportError:
    LMSTUDIO_AVAILABLE = False
    logger.warning("LMStudioClient not available")

from .vector_pipeline import VectorRAGPipeline
from .graph_pipeline import GraphRAGPipeline


class HybridRAGPipeline:
    """
    Hybrid GraphRAG Pipeline
    Комбинирует Vector-RAG и Graph-RAG через агентный router
    """
    
    def __init__(
        self,
        vector_config: Optional[Dict[str, Any]] = None,
        graph_config: Optional[Dict[str, Any]] = None,
        fusion_strategy: str = "reciprocal_rank_fusion",
        confidence_threshold: float = 0.7
    ):
        """
        Инициализация Hybrid-RAG pipeline
        
        Args:
            vector_config: Конфигурация для Vector-RAG
            graph_config: Конфигурация для Graph-RAG
            fusion_strategy: Стратегия объединения результатов
            confidence_threshold: Порог уверенности для router
        """
        # Инициализация компонентов
        vector_config = vector_config or {}
        graph_config = graph_config or {}
        
        self.vector_pipeline = VectorRAGPipeline(**vector_config)
        self.graph_pipeline = GraphRAGPipeline(**graph_config)
        self.fusion_strategy = fusion_strategy
        self.confidence_threshold = confidence_threshold
        
        # Router (LLM для выбора стратегии)
        if LMSTUDIO_AVAILABLE:
            try:
                self.router = LMStudioClient()
            except:
                self.router = None
                logger.warning("LMStudioClient not available, using simple router")
        else:
            self.router = None
        
        logger.info("HybridRAGPipeline initialized")
    
    def route_query(self, query: str) -> Dict[str, str]:
        """
        Определить стратегию поиска для запроса
        
        Args:
            query: Запрос пользователя
        
        Returns:
            Словарь с выбранной стратегией
        """
        if self.router:
            try:
                prompt = f"""Определи тип запроса и выбери стратегию поиска:
1. "vector" - для общих вопросов, фактов, определений
2. "graph" - для вопросов о связях, причинно-следственных цепочках
3. "hybrid" - для сложных вопросов, требующих комбинации

Запрос: {query}

Верни только одно слово: vector, graph или hybrid"""
                
                response = self.router.generate(prompt=prompt, temperature=0.1, max_tokens=10)
                strategy = response.get("text", "hybrid").strip().lower()
                
                if strategy not in ["vector", "graph", "hybrid"]:
                    strategy = "hybrid"
                
                return {"strategy": strategy, "confidence": 0.8}
            except Exception as e:
                logger.error(f"Error in router: {e}")
        
        # Простая эвристика
        graph_keywords = ["связь", "связан", "причина", "следствие", "влияет", "зависит"]
        if any(keyword in query.lower() for keyword in graph_keywords):
            return {"strategy": "graph", "confidence": 0.7}
        
        return {"strategy": "hybrid", "confidence": 0.6}
    
    def fuse_results(
        self,
        vector_result: Dict[str, Any],
        graph_result: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Объединить результаты Vector-RAG и Graph-RAG
        
        Args:
            vector_result: Результат Vector-RAG
            graph_result: Результат Graph-RAG
            weights: Веса для объединения
        
        Returns:
            Объединенный результат
        """
        weights = weights or {"vector": 0.4, "graph": 0.6}
        
        # Reciprocal Rank Fusion
        if self.fusion_strategy == "reciprocal_rank_fusion":
            # Простое объединение контекстов
            combined_context = vector_result.get("context", []) + graph_result.get("context", [])
            
            # Взвешенный ответ
            vector_answer = vector_result.get("answer", "")
            graph_answer = graph_result.get("answer", "")
            
            if vector_answer and graph_answer:
                combined_answer = f"{vector_answer}\n\n{graph_answer}"
            elif vector_answer:
                combined_answer = vector_answer
            elif graph_answer:
                combined_answer = graph_answer
            else:
                combined_answer = "Не найдено ответа."
            
            # Взвешенный score
            combined_score = (
                vector_result.get("score", 0.0) * weights["vector"] +
                graph_result.get("score", 0.0) * weights["graph"]
            )
            
            return {
                "answer": combined_answer,
                "context": combined_context,
                "score": combined_score,
                "vector_score": vector_result.get("score", 0.0),
                "graph_score": graph_result.get("score", 0.0),
                "pipeline": "hybrid_rag"
            }
        
        # Простое объединение по умолчанию
        return {
            "answer": vector_result.get("answer", "") or graph_result.get("answer", ""),
            "context": vector_result.get("context", []) + graph_result.get("context", []),
            "score": max(vector_result.get("score", 0.0), graph_result.get("score", 0.0)),
            "pipeline": "hybrid_rag"
        }
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Выполнить полный pipeline
        
        Args:
            query: Запрос пользователя
        
        Returns:
            Результат с ответом и контекстом
        """
        # Определяем стратегию
        routing = self.route_query(query)
        strategy = routing["strategy"]
        
        logger.info(f"Routing query to: {strategy}")
        
        if strategy == "vector":
            # Только Vector-RAG
            return self.vector_pipeline.run(query)
        
        elif strategy == "graph":
            # Только Graph-RAG
            return self.graph_pipeline.run(query)
        
        else:
            # Hybrid: объединяем оба
            vector_result = self.vector_pipeline.run(query)
            graph_result = self.graph_pipeline.run(query)
            
            return self.fuse_results(vector_result, graph_result)
    
    def close(self):
        """Закрыть соединения"""
        if hasattr(self.graph_pipeline, 'close'):
            self.graph_pipeline.close()









