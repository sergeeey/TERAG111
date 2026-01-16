"""
Neo4j Ingest для загрузки данных в граф знаний
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j not available")


class Neo4jIngester:
    """
    Загрузчик данных в Neo4j для Graph-RAG
    """
    
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password",
        database: str = "neo4j"
    ):
        """
        Инициализация загрузчика
        
        Args:
            uri: URI Neo4j
            user: Имя пользователя
            password: Пароль
            database: Имя базы данных
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not installed")
        
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        logger.info(f"Neo4jIngester initialized: {uri}/{database}")
    
    def create_indices(self):
        """Создать индексы для оптимизации запросов"""
        with self.driver.session(database=self.database) as session:
            # Индекс для концептов
            session.run("""
                CREATE INDEX IF NOT EXISTS FOR (c:Concept) ON (c.name)
            """)
            
            # Индекс для документов
            session.run("""
                CREATE INDEX IF NOT EXISTS FOR (d:Document) ON (d.id)
            """)
            
            # Индекс для доменов
            session.run("""
                CREATE INDEX IF NOT EXISTS FOR (c:Concept) ON (c.domain)
            """)
            
            logger.info("Neo4j indices created")
    
    def ingest_triplets(
        self,
        triplets: List[Dict[str, Any]],
        document_id: Optional[str] = None
    ):
        """
        Загрузить SPO-триплеты в Neo4j
        
        Args:
            triplets: Список триплетов
            document_id: ID документа (опционально)
        """
        with self.driver.session(database=self.database) as session:
            for triplet in triplets:
                subject = triplet.get("subject", "")
                predicate = triplet.get("predicate", "")
                obj = triplet.get("object", "")
                confidence = triplet.get("confidence", 0.5)
                
                # Создаем узлы и связи
                query = """
                    MERGE (s:Concept {name: $subject})
                    MERGE (o:Concept {name: $object})
                    MERGE (s)-[r:RELATES {type: $predicate, confidence: $confidence}]->(o)
                    SET s.domain = coalesce(s.domain, $domain)
                    SET o.domain = coalesce(o.domain, $domain)
                """
                
                session.run(
                    query,
                    subject=subject,
                    object=obj,
                    predicate=predicate,
                    confidence=confidence,
                    domain=triplet.get("domain", "general")
                )
            
            # Связываем с документом если указан
            if document_id:
                for triplet in triplets[:1]:  # Связываем через первый триплет
                    query = """
                        MATCH (d:Document {id: $doc_id})
                        MATCH (c:Concept {name: $subject})
                        MERGE (d)-[:CONTAINS]->(c)
                    """
                    session.run(
                        query,
                        doc_id=document_id,
                        subject=triplet.get("subject", "")
                    )
        
        logger.info(f"Ingested {len(triplets)} triplets into Neo4j")
    
    def ingest_from_graph_results(self, graph_results_dir: str = "data/graph_results/"):
        """
        Загрузить данные из graph_results в Neo4j
        
        Args:
            graph_results_dir: Директория с результатами графа
        """
        graph_dir = Path(graph_results_dir)
        if not graph_dir.exists():
            logger.warning(f"Graph results directory not found: {graph_dir}")
            return
        
        # Создаем индексы
        self.create_indices()
        
        # Загружаем все JSON файлы с графами
        for graph_file in graph_dir.glob("*_graph.json"):
            if graph_file.name == "processing_summary.json":
                continue
            
            try:
                with open(graph_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                triplets = data.get("triplets", [])
                document_id = graph_file.stem.replace("_graph", "")
                
                self.ingest_triplets(triplets, document_id=document_id)
                
            except Exception as e:
                logger.error(f"Error loading {graph_file}: {e}")
        
        logger.info("Finished ingesting graph results into Neo4j")
    
    def close(self):
        """Закрыть соединение"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")









