"""
ChromaDB Ingest для загрузки векторных представлений
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB or sentence-transformers not available")


class ChromaIngester:
    """
    Загрузчик данных в ChromaDB для Vector-RAG
    """
    
    def __init__(
        self,
        collection_name: str = "terag_documents",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        persist_directory: str = "chroma_db"
    ):
        """
        Инициализация загрузчика
        
        Args:
            collection_name: Имя коллекции
            embedding_model: Модель для эмбеддингов
            persist_directory: Директория для сохранения
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB or sentence-transformers not installed")
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.embedding_model = SentenceTransformer(embedding_model)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"ChromaIngester initialized: {collection_name}")
    
    def ingest_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 100
    ):
        """
        Загрузить документы в ChromaDB
        
        Args:
            documents: Список документов с полями id, content, metadata
            batch_size: Размер батча для обработки
        """
        total = len(documents)
        logger.info(f"Ingesting {total} documents into ChromaDB")
        
        for i in range(0, total, batch_size):
            batch = documents[i:i + batch_size]
            
            ids = [doc["id"] for doc in batch]
            contents = [doc["content"] for doc in batch]
            metadatas = [doc.get("metadata", {}) for doc in batch]
            
            # Генерируем эмбеддинги
            embeddings = self.embedding_model.encode(contents).tolist()
            
            # Добавляем в коллекцию
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas
            )
            
            logger.info(f"Ingested batch {i//batch_size + 1}/{(total-1)//batch_size + 1}")
        
        logger.info(f"Finished ingesting {total} documents")
    
    def ingest_from_processed(self, processed_dir: str = "data/converted/"):
        """
        Загрузить документы из обработанной директории
        
        Args:
            processed_dir: Директория с обработанными документами
        """
        processed_path = Path(processed_dir)
        if not processed_path.exists():
            logger.warning(f"Processed directory not found: {processed_path}")
            return
        
        documents = []
        for txt_file in processed_path.glob("*.txt"):
            try:
                content = txt_file.read_text(encoding='utf-8')
                documents.append({
                    "id": txt_file.stem,
                    "content": content,
                    "metadata": {
                        "source": str(txt_file),
                        "size": len(content)
                    }
                })
            except Exception as e:
                logger.error(f"Error loading {txt_file}: {e}")
        
        if documents:
            self.ingest_documents(documents)
        else:
            logger.warning("No documents found to ingest")









