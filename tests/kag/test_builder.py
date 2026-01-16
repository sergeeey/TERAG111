#!/usr/bin/env python3
"""
Тесты для KAG Builder
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from pathlib import Path

# Импорт модулей для тестирования
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.kag.builder import KAGBuilder, SPOTriplet, DocumentMetadata
from src.kag.extractors.spo_extractor import SPOExtractor, ExtractedTriplet, ExtractionMethod
from src.kag.schemas.terag_schema import TERAG_SCHEMA, EntityType, RelationType
from src.kag.storage.supabase_client import SupabaseClient, DocumentRecord

class TestKAGBuilder:
    """Тесты для KAGBuilder"""
    
    @pytest.fixture
    def builder(self):
        """Фикстура для KAGBuilder"""
        return KAGBuilder(
            openspg_url="http://localhost:8080",
            neo4j_url="bolt://localhost:7687",
            supabase_url="postgresql://postgres:password@localhost:5432/terag"
        )
    
    @pytest.fixture
    def sample_text(self):
        """Образец текста для тестирования"""
        return """
        The KAG Builder implements SPO extraction for knowledge graphs.
        It calls the LLM API to process documents and creates triplets.
        The system depends on OpenSPG for graph storage.
        """
    
    @pytest.fixture
    def sample_triplets(self):
        """Образец триплетов для тестирования"""
        return [
            SPOTriplet(
                subject="KAG Builder",
                predicate="implements",
                object="SPO extraction",
                confidence=0.9,
                source_chunk="chunk_0",
                source_document="test_doc",
                metadata={"type": "technical"}
            ),
            SPOTriplet(
                subject="KAG Builder",
                predicate="calls",
                object="LLM API",
                confidence=0.8,
                source_chunk="chunk_0",
                source_document="test_doc",
                metadata={"type": "technical"}
            )
        ]
    
    @pytest.mark.asyncio
    async def test_process_document_success(self, builder, sample_text):
        """Тест успешной обработки документа"""
        with patch.object(builder, '_load_document', return_value=sample_text), \
             patch.object(builder, '_chunk_document', return_value=[sample_text]), \
             patch.object(builder, 'extract_spo_triplets', return_value=[]), \
             patch.object(builder, '_validate_triplets', return_value=[]), \
             patch.object(builder, 'build_graph', return_value="test_graph_id"), \
             patch.object(builder, 'create_mutual_indexing', return_value={}), \
             patch.object(builder, '_save_metadata'):
            
            result = await builder.process_document("test.md", "markdown")
            
            assert result["success"] is True
            assert "document_id" in result
            assert "graph_id" in result
    
    @pytest.mark.asyncio
    async def test_process_document_error(self, builder):
        """Тест обработки ошибки при обработке документа"""
        with patch.object(builder, '_load_document', side_effect=Exception("File not found")):
            result = await builder.process_document("nonexistent.md", "markdown")
            
            assert result["success"] is False
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_extract_spo_triplets(self, builder, sample_text):
        """Тест извлечения SPO-триплетов"""
        with patch.object(builder, '_call_llm_api', return_value={
            "triplets": [
                {
                    "subject": "KAG Builder",
                    "predicate": "implements",
                    "object": "SPO extraction",
                    "confidence": 0.9,
                    "type": "technical"
                }
            ]
        }):
            triplets = await builder.extract_spo_triplets(sample_text, "chunk_0")
            
            assert len(triplets) == 1
            assert triplets[0].subject == "KAG Builder"
            assert triplets[0].predicate == "implements"
            assert triplets[0].object == "SPO extraction"
    
    @pytest.mark.asyncio
    async def test_build_graph_success(self, builder, sample_triplets):
        """Тест успешного построения графа"""
        with patch.object(builder.session, 'post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"graph_id": "test_graph"}
            mock_post.return_value.__aenter__.return_value = mock_response
            
            graph_id = await builder.build_graph(sample_triplets)
            
            assert graph_id == "test_graph"
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_build_graph_fallback(self, builder, sample_triplets):
        """Тест fallback на Neo4j при ошибке OpenSPG"""
        with patch.object(builder.session, 'post') as mock_post, \
             patch.object(builder, '_build_graph_neo4j', return_value="neo4j_graph"):
            
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_post.return_value.__aenter__.return_value = mock_response
            
            graph_id = await builder.build_graph(sample_triplets)
            
            assert graph_id == "neo4j_graph"
    
    @pytest.mark.asyncio
    async def test_create_mutual_indexing(self, builder, sample_triplets):
        """Тест создания mutual indexing"""
        chunks = ["chunk1", "chunk2"]
        
        with patch.object(builder, '_save_mutual_indexing'):
            result = await builder.create_mutual_indexing("test_graph", chunks, sample_triplets)
            
            assert "graph_id" in result
            assert "chunk_to_entities" in result
            assert "entity_to_chunks" in result
    
    def test_validate_triplets(self, builder, sample_triplets):
        """Тест валидации триплетов"""
        # Добавляем невалидный триплет
        invalid_triplet = SPOTriplet(
            subject="",  # Пустой субъект
            predicate="test",
            object="test",
            confidence=0.5,
            source_chunk="chunk_0",
            source_document="test_doc",
            metadata={}
        )
        
        all_triplets = sample_triplets + [invalid_triplet]
        validated = asyncio.run(builder._validate_triplets(all_triplets))
        
        assert len(validated) == len(sample_triplets)  # Невалидный исключен

class TestSPOExtractor:
    """Тесты для SPOExtractor"""
    
    @pytest.fixture
    def extractor(self):
        """Фикстура для SPOExtractor"""
        return SPOExtractor()
    
    @pytest.fixture
    def sample_text(self):
        """Образец текста для тестирования"""
        return """
        The KAG Builder implements SPO extraction for knowledge graphs.
        It calls the LLM API to process documents and creates triplets.
        The system depends on OpenSPG for graph storage.
        """
    
    def test_extract_with_regex(self, extractor, sample_text):
        """Тест извлечения с помощью regex"""
        triplets = extractor.extract_with_regex(sample_text)
        
        assert len(triplets) > 0
        assert all(isinstance(t, ExtractedTriplet) for t in triplets)
        assert all(t.method == ExtractionMethod.REGEX for t in triplets)
    
    def test_extract_with_llm(self, extractor, sample_text):
        """Тест извлечения с помощью LLM"""
        with patch.object(extractor, '_call_llm_stub', return_value={
            "triplets": [
                {
                    "subject": "KAG Builder",
                    "predicate": "implements",
                    "object": "SPO extraction",
                    "confidence": 0.9,
                    "type": "technical",
                    "context": "KAG Builder implements SPO extraction"
                }
            ]
        }):
            triplets = extractor.extract_with_llm(sample_text)
            
            assert len(triplets) == 1
            assert triplets[0].subject == "KAG Builder"
            assert triplets[0].method == ExtractionMethod.LLM
    
    def test_extract_hybrid(self, extractor, sample_text):
        """Тест гибридного извлечения"""
        with patch.object(extractor, '_call_llm_stub', return_value={
            "triplets": [
                {
                    "subject": "KAG Builder",
                    "predicate": "implements",
                    "object": "SPO extraction",
                    "confidence": 0.9,
                    "type": "technical",
                    "context": "KAG Builder implements SPO extraction"
                }
            ]
        }):
            triplets = extractor.extract_hybrid(sample_text)
            
            assert len(triplets) > 0
            assert all(isinstance(t, ExtractedTriplet) for t in triplets)
    
    def test_validate_triplets(self, extractor):
        """Тест валидации триплетов"""
        triplets = [
            ExtractedTriplet(
                subject="Valid Subject",
                predicate="valid_predicate",
                object="Valid Object",
                confidence=0.8,
                method=ExtractionMethod.REGEX,
                context="test context",
                position=(0, 10)
            ),
            ExtractedTriplet(
                subject="",  # Пустой субъект
                predicate="valid_predicate",
                object="Valid Object",
                confidence=0.8,
                method=ExtractionMethod.REGEX,
                context="test context",
                position=(0, 10)
            )
        ]
        
        validated = extractor.validate_triplets(triplets)
        
        assert len(validated) == 1  # Только валидный триплет
        assert validated[0].subject == "Valid Subject"
    
    def test_normalize_entities(self, extractor):
        """Тест нормализации сущностей"""
        triplets = [
            ExtractedTriplet(
                subject="  KAG BUILDER  ",
                predicate="IMPLEMENTS",
                object="spo extraction",
                confidence=0.8,
                method=ExtractionMethod.REGEX,
                context="test context",
                position=(0, 10)
            )
        ]
        
        normalized = extractor.normalize_entities(triplets)
        
        assert normalized[0].subject == "KAG Builder"
        assert normalized[0].predicate == "implements"
        assert normalized[0].object == "spo extraction"

class TestTERAGSchema:
    """Тесты для TERAGSchema"""
    
    def test_schema_creation(self):
        """Тест создания схемы"""
        schema = TERAG_SCHEMA
        
        assert len(schema.entities) > 0
        assert len(schema.relations) > 0
        assert len(schema.constraints) > 0
    
    def test_entity_validation(self):
        """Тест валидации сущности"""
        valid_entity = {
            "id": "test_entity",
            "name": "Test Entity",
            "description": "Test description",
            "category": "test",
            "confidence": 0.8,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        assert TERAG_SCHEMA.validate_entity("Concept", valid_entity) is True
    
    def test_entity_validation_invalid(self):
        """Тест валидации невалидной сущности"""
        invalid_entity = {
            "id": "test_entity",
            # Отсутствует обязательное поле name
            "confidence": 1.5  # Невалидное значение confidence
        }
        
        assert TERAG_SCHEMA.validate_entity("Concept", invalid_entity) is False
    
    def test_relation_validation(self):
        """Тест валидации отношения"""
        valid_relation = {
            "confidence": 0.8,
            "created_at": datetime.now()
        }
        
        assert TERAG_SCHEMA.validate_relation("implements", valid_relation) is True
    
    def test_schema_dict(self):
        """Тест получения схемы в виде словаря"""
        schema_dict = TERAG_SCHEMA.get_schema_dict()
        
        assert "entities" in schema_dict
        assert "relations" in schema_dict
        assert "constraints" in schema_dict
        assert len(schema_dict["entities"]) > 0
        assert len(schema_dict["relations"]) > 0

class TestSupabaseClient:
    """Тесты для SupabaseClient"""
    
    @pytest.fixture
    def client(self):
        """Фикстура для SupabaseClient"""
        return SupabaseClient(
            supabase_url="postgresql://postgres:password@localhost:5432/terag"
        )
    
    @pytest.fixture
    def sample_document(self):
        """Образец документа для тестирования"""
        return DocumentRecord(
            id="test_doc_1",
            title="Test Document",
            content_type="markdown",
            file_path="/path/to/test.md",
            created_at=datetime.now(),
            processed_at=datetime.now(),
            chunk_count=5,
            metadata={"author": "test", "version": "1.0"}
        )
    
    @pytest.mark.asyncio
    async def test_save_document(self, client, sample_document):
        """Тест сохранения документа"""
        with patch.object(client.connection, 'execute') as mock_execute:
            result = await client.save_document(sample_document)
            
            assert result is True
            mock_execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_document(self, client):
        """Тест получения документа"""
        mock_row = {
            'id': 'test_doc_1',
            'title': 'Test Document',
            'content_type': 'markdown',
            'file_path': '/path/to/test.md',
            'created_at': datetime.now(),
            'processed_at': datetime.now(),
            'chunk_count': 5,
            'metadata': '{"author": "test"}'
        }
        
        with patch.object(client.connection, 'fetchrow', return_value=mock_row):
            document = await client.get_document("test_doc_1")
            
            assert document is not None
            assert document.id == "test_doc_1"
            assert document.title == "Test Document"
    
    @pytest.mark.asyncio
    async def test_search_entities(self, client):
        """Тест поиска сущностей"""
        mock_rows = [
            {
                'id': 'entity_1',
                'name': 'KAG Builder',
                'type': 'Concept',
                'properties': '{}',
                'confidence': 0.9,
                'source_document': 'test_doc',
                'created_at': datetime.now()
            }
        ]
        
        with patch.object(client.connection, 'fetch', return_value=mock_rows):
            entities = await client.search_entities("KAG")
            
            assert len(entities) == 1
            assert entities[0].name == "KAG Builder"
    
    @pytest.mark.asyncio
    async def test_get_analytics(self, client):
        """Тест получения аналитики"""
        mock_analytics = {
            'total_documents': 10,
            'total_entities': 50,
            'total_triplets': 100
        }
        
        with patch.object(client.connection, 'fetchval', side_effect=[10, 50, 100]), \
             patch.object(client.connection, 'fetch', return_value=[]):
            
            analytics = await client.get_analytics()
            
            assert analytics['total_documents'] == 10
            assert analytics['total_entities'] == 50
            assert analytics['total_triplets'] == 100

# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v"])





































