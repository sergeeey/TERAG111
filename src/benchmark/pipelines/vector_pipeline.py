"""
Vector-RAG Pipeline
Стандартный RAG с векторным поиском через ChromaDB
"""
import logging
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

try:
    from haystack import Pipeline
    from haystack.components.retrievers import InMemoryEmbeddingRetriever
    from haystack.components.readers import ExtractiveReader
    from haystack.dataclasses import Document
    HAYSTACK_AVAILABLE = True
except ImportError:
    HAYSTACK_AVAILABLE = False
    logger.warning("Haystack not available")


class VectorRAGPipeline:
    """
    Vector-RAG Pipeline с использованием ChromaDB
    """
    
    def __init__(
        self,
        collection_name: str = "terag_documents",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        top_k: int = 5,
        reader_model: str = "deepset/roberta-base-squad2"
    ):
        """
        Инициализация Vector-RAG pipeline
        
        Args:
            collection_name: Имя коллекции ChromaDB
            embedding_model: Модель для эмбеддингов
            top_k: Количество документов для извлечения
            reader_model: Модель для чтения
        """
        if not HAYSTACK_AVAILABLE:
            raise ImportError("Haystack not installed")
        
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        self.top_k = top_k
        
        # Инициализация ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name
        )
        
        # Инициализация embedding модели
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Создание pipeline
        self.pipeline = Pipeline()
        
        # Retriever (упрощенная версия через ChromaDB)
        # В production используйте Haystack ChromaDBRetriever
        
        # Reader
        try:
            self.reader = ExtractiveReader(model=reader_model)
        except:
            logger.warning(f"Could not load reader model {reader_model}, using fallback")
            self.reader = None
        
        logger.info(f"VectorRAGPipeline initialized: {collection_name}")
    
    def retrieve(self, query: str) -> List[Document]:
        """
        Извлечь релевантные документы
        
        Args:
            query: Запрос пользователя
        
        Returns:
            Список документов
        """
        # Генерируем эмбеддинг запроса
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Поиск в ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.top_k
        )
        
        # Преобразуем в Haystack Documents
        documents = []
        if results.get("documents") and results["documents"][0]:
            for i, doc_text in enumerate(results["documents"][0]):
                doc = Document(
                    content=doc_text,
                    meta=results.get("metadatas", [{}])[0][i] if results.get("metadatas") else {}
                )
                documents.append(doc)
        
        return documents
    
    def read(self, query: str, documents: List[Document]) -> Dict[str, Any]:
        """
        Извлечь ответ из документов
        
        Args:
            query: Запрос
            documents: Список документов
        
        Returns:
            Результат с ответом
        """
        if not self.reader:
            # Fallback: возвращаем первый документ
            if documents:
                return {
                    "answer": documents[0].content[:500],
                    "context": [doc.content for doc in documents],
                    "score": 0.8
                }
            return {"answer": "No answer found", "context": [], "score": 0.0}
        
        # Используем reader
        try:
            result = self.reader.run(query=query, documents=documents)
            return {
                "answer": result.get("answers", [{}])[0].get("answer", "") if result.get("answers") else "",
                "context": [doc.content for doc in documents],
                "score": result.get("answers", [{}])[0].get("score", 0.0) if result.get("answers") else 0.0
            }
        except Exception as e:
            logger.error(f"Error in reader: {e}")
            # Fallback
            if documents:
                return {
                    "answer": documents[0].content[:500],
                    "context": [doc.content for doc in documents],
                    "score": 0.8
                }
            return {"answer": "No answer found", "context": [], "score": 0.0}
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Выполнить полный pipeline
        
        Args:
            query: Запрос пользователя
        
        Returns:
            Результат с ответом и контекстом
        """
        # Извлечение
        documents = self.retrieve(query)
        
        # Чтение
        result = self.read(query, documents)
        
        return {
            "answer": result["answer"],
            "context": result["context"],
            "documents": [doc.content for doc in documents],
            "score": result["score"],
            "pipeline": "vector_rag"
        }









