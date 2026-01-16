#!/usr/bin/env python3
"""
Supabase Client - модуль для работы с Supabase в KAG системе
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import asyncpg

logger = logging.getLogger(__name__)

@dataclass
class DocumentRecord:
    """Запись документа в Supabase"""
    id: str
    title: str
    content_type: str
    file_path: str
    created_at: datetime
    processed_at: datetime
    chunk_count: int
    metadata: Dict[str, Any]

@dataclass
class EntityRecord:
    """Запись сущности в Supabase"""
    id: str
    name: str
    type: str
    properties: Dict[str, Any]
    confidence: float
    source_document: str
    created_at: datetime

@dataclass
class TripletRecord:
    """Запись триплета в Supabase"""
    id: str
    subject: str
    predicate: str
    object: str
    confidence: float
    source_document: str
    source_chunk: str
    metadata: Dict[str, Any]
    created_at: datetime

@dataclass
class MutualIndexingRecord:
    """Запись mutual indexing в Supabase"""
    id: str
    graph_id: str
    chunk_id: str
    entity_name: str
    entity_type: str
    relationship_type: str
    created_at: datetime

class SupabaseClient:
    """Клиент для работы с Supabase"""
    
    def __init__(self, supabase_url: str, supabase_key: str = None):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.connection = None
        
        # SQL для создания таблиц
        self.create_tables_sql = self._get_create_tables_sql()
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Подключение к Supabase"""
        try:
            # Парсинг URL для получения параметров подключения
            # postgresql://user:password@host:port/database
            if self.supabase_url.startswith('postgresql://'):
                self.connection = await asyncpg.connect(self.supabase_url)
                logger.info("Connected to Supabase PostgreSQL")
            else:
                raise ValueError("Invalid Supabase URL format")
        except Exception as e:
            logger.error(f"Error connecting to Supabase: {e}")
            raise
    
    async def disconnect(self):
        """Отключение от Supabase"""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from Supabase")
    
    async def initialize_schema(self):
        """Инициализация схемы базы данных"""
        try:
            await self.connection.execute(self.create_tables_sql)
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Error initializing schema: {e}")
            raise
    
    async def save_document(self, document: DocumentRecord) -> bool:
        """Сохранение документа"""
        try:
            query = """
                INSERT INTO documents (id, title, content_type, file_path, created_at, processed_at, chunk_count, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    content_type = EXCLUDED.content_type,
                    file_path = EXCLUDED.file_path,
                    processed_at = EXCLUDED.processed_at,
                    chunk_count = EXCLUDED.chunk_count,
                    metadata = EXCLUDED.metadata
            """
            
            await self.connection.execute(
                query,
                document.id,
                document.title,
                document.content_type,
                document.file_path,
                document.created_at,
                document.processed_at,
                document.chunk_count,
                json.dumps(document.metadata)
            )
            
            logger.info(f"Document {document.id} saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving document {document.id}: {e}")
            return False
    
    async def save_entity(self, entity: EntityRecord) -> bool:
        """Сохранение сущности"""
        try:
            query = """
                INSERT INTO entities (id, name, type, properties, confidence, source_document, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    type = EXCLUDED.type,
                    properties = EXCLUDED.properties,
                    confidence = EXCLUDED.confidence,
                    source_document = EXCLUDED.source_document
            """
            
            await self.connection.execute(
                query,
                entity.id,
                entity.name,
                entity.type,
                json.dumps(entity.properties),
                entity.confidence,
                entity.source_document,
                entity.created_at
            )
            
            logger.info(f"Entity {entity.id} saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving entity {entity.id}: {e}")
            return False
    
    async def save_triplet(self, triplet: TripletRecord) -> bool:
        """Сохранение триплета"""
        try:
            query = """
                INSERT INTO triplets (id, subject, predicate, object, confidence, source_document, source_chunk, metadata, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (id) DO UPDATE SET
                    subject = EXCLUDED.subject,
                    predicate = EXCLUDED.predicate,
                    object = EXCLUDED.object,
                    confidence = EXCLUDED.confidence,
                    source_document = EXCLUDED.source_document,
                    source_chunk = EXCLUDED.chunk,
                    metadata = EXCLUDED.metadata
            """
            
            await self.connection.execute(
                query,
                triplet.id,
                triplet.subject,
                triplet.predicate,
                triplet.object,
                triplet.confidence,
                triplet.source_document,
                triplet.source_chunk,
                json.dumps(triplet.metadata),
                triplet.created_at
            )
            
            logger.info(f"Triplet {triplet.id} saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving triplet {triplet.id}: {e}")
            return False
    
    async def save_mutual_indexing(self, indexing: MutualIndexingRecord) -> bool:
        """Сохранение mutual indexing"""
        try:
            query = """
                INSERT INTO mutual_indexing (id, graph_id, chunk_id, entity_name, entity_type, relationship_type, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (id) DO UPDATE SET
                    graph_id = EXCLUDED.graph_id,
                    chunk_id = EXCLUDED.chunk_id,
                    entity_name = EXCLUDED.entity_name,
                    entity_type = EXCLUDED.entity_type,
                    relationship_type = EXCLUDED.relationship_type
            """
            
            await self.connection.execute(
                query,
                indexing.id,
                indexing.graph_id,
                indexing.chunk_id,
                indexing.entity_name,
                indexing.entity_type,
                indexing.relationship_type,
                indexing.created_at
            )
            
            logger.info(f"Mutual indexing {indexing.id} saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving mutual indexing {indexing.id}: {e}")
            return False
    
    async def get_document(self, document_id: str) -> Optional[DocumentRecord]:
        """Получение документа по ID"""
        try:
            query = "SELECT * FROM documents WHERE id = $1"
            row = await self.connection.fetchrow(query, document_id)
            
            if row:
                return DocumentRecord(
                    id=row['id'],
                    title=row['title'],
                    content_type=row['content_type'],
                    file_path=row['file_path'],
                    created_at=row['created_at'],
                    processed_at=row['processed_at'],
                    chunk_count=row['chunk_count'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            return None
    
    async def get_entities_by_document(self, document_id: str) -> List[EntityRecord]:
        """Получение сущностей по документу"""
        try:
            query = "SELECT * FROM entities WHERE source_document = $1"
            rows = await self.connection.fetch(query, document_id)
            
            entities = []
            for row in rows:
                entities.append(EntityRecord(
                    id=row['id'],
                    name=row['name'],
                    type=row['type'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    confidence=row['confidence'],
                    source_document=row['source_document'],
                    created_at=row['created_at']
                ))
            
            return entities
            
        except Exception as e:
            logger.error(f"Error getting entities for document {document_id}: {e}")
            return []
    
    async def get_triplets_by_document(self, document_id: str) -> List[TripletRecord]:
        """Получение триплетов по документу"""
        try:
            query = "SELECT * FROM triplets WHERE source_document = $1"
            rows = await self.connection.fetch(query, document_id)
            
            triplets = []
            for row in rows:
                triplets.append(TripletRecord(
                    id=row['id'],
                    subject=row['subject'],
                    predicate=row['predicate'],
                    object=row['object'],
                    confidence=row['confidence'],
                    source_document=row['source_document'],
                    source_chunk=row['source_chunk'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {},
                    created_at=row['created_at']
                ))
            
            return triplets
            
        except Exception as e:
            logger.error(f"Error getting triplets for document {document_id}: {e}")
            return []
    
    async def get_mutual_indexing_by_graph(self, graph_id: str) -> List[MutualIndexingRecord]:
        """Получение mutual indexing по графу"""
        try:
            query = "SELECT * FROM mutual_indexing WHERE graph_id = $1"
            rows = await self.connection.fetch(query, graph_id)
            
            indexing = []
            for row in rows:
                indexing.append(MutualIndexingRecord(
                    id=row['id'],
                    graph_id=row['graph_id'],
                    chunk_id=row['chunk_id'],
                    entity_name=row['entity_name'],
                    entity_type=row['entity_type'],
                    relationship_type=row['relationship_type'],
                    created_at=row['created_at']
                ))
            
            return indexing
            
        except Exception as e:
            logger.error(f"Error getting mutual indexing for graph {graph_id}: {e}")
            return []
    
    async def search_entities(self, query: str, entity_type: str = None) -> List[EntityRecord]:
        """Поиск сущностей"""
        try:
            if entity_type:
                sql_query = "SELECT * FROM entities WHERE name ILIKE $1 AND type = $2"
                rows = await self.connection.fetch(sql_query, f"%{query}%", entity_type)
            else:
                sql_query = "SELECT * FROM entities WHERE name ILIKE $1"
                rows = await self.connection.fetch(sql_query, f"%{query}%")
            
            entities = []
            for row in rows:
                entities.append(EntityRecord(
                    id=row['id'],
                    name=row['name'],
                    type=row['type'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    confidence=row['confidence'],
                    source_document=row['source_document'],
                    created_at=row['created_at']
                ))
            
            return entities
            
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            return []
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Получение аналитики"""
        try:
            # Общая статистика
            total_documents = await self.connection.fetchval("SELECT COUNT(*) FROM documents")
            total_entities = await self.connection.fetchval("SELECT COUNT(*) FROM entities")
            total_triplets = await self.connection.fetchval("SELECT COUNT(*) FROM triplets")
            
            # Статистика по типам сущностей
            entity_types = await self.connection.fetch("""
                SELECT type, COUNT(*) as count 
                FROM entities 
                GROUP BY type 
                ORDER BY count DESC
            """)
            
            # Статистика по типам отношений
            relation_types = await self.connection.fetch("""
                SELECT predicate, COUNT(*) as count 
                FROM triplets 
                GROUP BY predicate 
                ORDER BY count DESC
            """)
            
            return {
                "total_documents": total_documents,
                "total_entities": total_entities,
                "total_triplets": total_triplets,
                "entity_types": [{"type": row['type'], "count": row['count']} for row in entity_types],
                "relation_types": [{"predicate": row['predicate'], "count": row['count']} for row in relation_types]
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}
    
    def _get_create_tables_sql(self) -> str:
        """SQL для создания таблиц"""
        return """
        -- Таблица документов
        CREATE TABLE IF NOT EXISTS documents (
            id VARCHAR PRIMARY KEY,
            title VARCHAR NOT NULL,
            content_type VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            created_at TIMESTAMP NOT NULL,
            processed_at TIMESTAMP NOT NULL,
            chunk_count INTEGER NOT NULL,
            metadata JSONB DEFAULT '{}'
        );
        
        -- Таблица сущностей
        CREATE TABLE IF NOT EXISTS entities (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            type VARCHAR NOT NULL,
            properties JSONB DEFAULT '{}',
            confidence FLOAT NOT NULL,
            source_document VARCHAR NOT NULL,
            created_at TIMESTAMP NOT NULL
        );
        
        -- Таблица триплетов
        CREATE TABLE IF NOT EXISTS triplets (
            id VARCHAR PRIMARY KEY,
            subject VARCHAR NOT NULL,
            predicate VARCHAR NOT NULL,
            object VARCHAR NOT NULL,
            confidence FLOAT NOT NULL,
            source_document VARCHAR NOT NULL,
            source_chunk VARCHAR NOT NULL,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP NOT NULL
        );
        
        -- Таблица mutual indexing
        CREATE TABLE IF NOT EXISTS mutual_indexing (
            id VARCHAR PRIMARY KEY,
            graph_id VARCHAR NOT NULL,
            chunk_id VARCHAR NOT NULL,
            entity_name VARCHAR NOT NULL,
            entity_type VARCHAR NOT NULL,
            relationship_type VARCHAR NOT NULL,
            created_at TIMESTAMP NOT NULL
        );
        
        -- Индексы для производительности
        CREATE INDEX IF NOT EXISTS idx_entities_document ON entities(source_document);
        CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
        CREATE INDEX IF NOT EXISTS idx_triplets_document ON triplets(source_document);
        CREATE INDEX IF NOT EXISTS idx_triplets_subject ON triplets(subject);
        CREATE INDEX IF NOT EXISTS idx_triplets_object ON triplets(object);
        CREATE INDEX IF NOT EXISTS idx_mutual_indexing_graph ON mutual_indexing(graph_id);
        CREATE INDEX IF NOT EXISTS idx_mutual_indexing_chunk ON mutual_indexing(chunk_id);
        """

# Пример использования
async def main():
    """Пример использования Supabase клиента"""
    client = SupabaseClient(
        supabase_url="postgresql://postgres:password@localhost:5432/terag"
    )
    
    async with client:
        # Инициализация схемы
        await client.initialize_schema()
        
        # Создание тестового документа
        document = DocumentRecord(
            id="test_doc_1",
            title="Test Document",
            content_type="markdown",
            file_path="/path/to/test.md",
            created_at=datetime.now(),
            processed_at=datetime.now(),
            chunk_count=5,
            metadata={"author": "test", "version": "1.0"}
        )
        
        # Сохранение документа
        success = await client.save_document(document)
        print(f"Document saved: {success}")
        
        # Получение аналитики
        analytics = await client.get_analytics()
        print(f"Analytics: {analytics}")

if __name__ == "__main__":
    asyncio.run(main())





































