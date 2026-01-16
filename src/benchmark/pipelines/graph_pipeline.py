"""
Graph-RAG Pipeline
RAG с графовым поиском через Neo4j
"""
import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j not available")

try:
    from haystack.dataclasses import Document
    HAYSTACK_AVAILABLE = True
except ImportError:
    HAYSTACK_AVAILABLE = False
    logger.warning("Haystack not available")


class GraphRAGPipeline:
    """
    Graph-RAG Pipeline с использованием Neo4j
    """
    
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password",
        database: str = "neo4j",
        max_hops: int = 3,
        top_k: int = 5
    ):
        """
        Инициализация Graph-RAG pipeline
        
        Args:
            uri: URI Neo4j
            user: Имя пользователя
            password: Пароль
            database: Имя базы данных
            max_hops: Максимальная глубина поиска
            top_k: Количество результатов
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not installed")
        
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        self.max_hops = max_hops
        self.top_k = top_k
        
        logger.info(f"GraphRAGPipeline initialized: {uri}/{database}")
    
    def extract_concepts(self, query: str) -> List[str]:
        """
        Извлечь концепты из запроса
        
        Args:
            query: Запрос пользователя
        
        Returns:
            Список концептов
        """
        # Простое извлечение: слова с заглавной буквы и ключевые слова
        words = re.findall(r'\b[A-Z][a-z]+\b|\b\w{4,}\b', query)
        # Убираем стоп-слова
        stop_words = {"что", "как", "где", "когда", "почему", "который", "которые"}
        concepts = [w for w in words if w.lower() not in stop_words]
        return concepts[:5]  # Ограничиваем количество
    
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Извлечь релевантные данные из графа
        
        Args:
            query: Запрос пользователя
        
        Returns:
            Список извлеченных данных
        """
        concepts = self.extract_concepts(query)
        
        if not concepts:
            return []
        
        results = []
        
        with self.driver.session(database=self.database) as session:
            for concept in concepts:
                # Поиск связанных концептов
                query_cypher = """
                    MATCH path = (start:Concept {name: $concept})-[*1..3]-(related:Concept)
                    RETURN DISTINCT related.name as name, 
                           [r IN relationships(path) | type(r)] as relationships,
                           length(path) as depth
                    ORDER BY depth
                    LIMIT $top_k
                """
                
                result = session.run(
                    query_cypher,
                    concept=concept,
                    top_k=self.top_k
                )
                
                for record in result:
                    results.append({
                        "concept": record["name"],
                        "relationships": record["relationships"],
                        "depth": record["depth"]
                    })
        
        return results[:self.top_k]
    
    def format_context(self, graph_results: List[Dict[str, Any]]) -> str:
        """
        Форматировать результаты графа в контекст
        
        Args:
            graph_results: Результаты из графа
        
        Returns:
            Отформатированный контекст
        """
        if not graph_results:
            return ""
        
        context_parts = []
        for result in graph_results:
            concept = result["concept"]
            rels = ", ".join(result["relationships"])
            context_parts.append(f"{concept} связан через: {rels}")
        
        return ". ".join(context_parts)
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Выполнить полный pipeline
        
        Args:
            query: Запрос пользователя
        
        Returns:
            Результат с ответом и контекстом
        """
        # Извлечение из графа
        graph_results = self.retrieve(query)
        
        # Форматирование контекста
        context = self.format_context(graph_results)
        
        # Простой ответ на основе контекста
        if context:
            answer = f"На основе графа знаний: {context[:500]}"
        else:
            answer = "Не найдено релевантной информации в графе знаний."
        
        return {
            "answer": answer,
            "context": [context] if context else [],
            "graph_results": graph_results,
            "score": 0.8 if graph_results else 0.3,
            "pipeline": "graph_rag"
        }
    
    def close(self):
        """Закрыть соединение"""
        if self.driver:
            self.driver.close()









