#!/usr/bin/env python3
"""
KAG Builder - модуль для извлечения SPO-триплетов и построения графа знаний
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import asyncio
import aiohttp
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SPOTriplet:
    """SPO-триплет (Subject-Predicate-Object)"""
    subject: str
    predicate: str
    object: str
    confidence: float
    source_chunk: str
    source_document: str
    metadata: Dict[str, Any]

@dataclass
class DocumentMetadata:
    """Метаданные документа"""
    document_id: str
    title: str
    content_type: str
    file_path: str
    created_at: datetime
    processed_at: datetime
    chunk_count: int

class KAGBuilder:
    """Основной класс для построения графа знаний"""
    
    def __init__(self, openspg_url: str, neo4j_url: str, supabase_url: str):
        self.openspg_url = openspg_url
        self.neo4j_url = neo4j_url
        self.supabase_url = supabase_url
        self.session = None
        
        # Схема OpenSPG для TERAG
        self.terag_schema = {
            "entities": [
                "Concept", "Agent", "Process", "Decision", "Evidence",
                "Code", "Function", "Class", "Variable", "Interface"
            ],
            "relations": [
                "causes", "influences", "supports", "contradicts", "precedes",
                "implements", "extends", "uses", "calls", "defines"
            ],
            "constraints": [
                "temporal_consistency", "logical_consistency", "evidence_requirement"
            ]
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def process_document(self, doc_path: str, doc_type: str) -> Dict[str, Any]:
        """
        Обработка документа и извлечение SPO-триплетов
        
        Args:
            doc_path: Путь к документу
            doc_type: Тип документа (pdf, markdown, text)
            
        Returns:
            Словарь с результатами обработки
        """
        try:
            logger.info(f"Processing document: {doc_path}")
            
            # 1. Загрузка и предобработка документа
            content = await self._load_document(doc_path, doc_type)
            chunks = await self._chunk_document(content, doc_type)
            
            # 2. Извлечение SPO-триплетов
            triplets = []
            for i, chunk in enumerate(chunks):
                chunk_triplets = await self.extract_spo_triplets(
                    chunk, f"{doc_path}_chunk_{i}"
                )
                triplets.extend(chunk_triplets)
            
            # 3. Валидация триплетов
            validated_triplets = await self._validate_triplets(triplets)
            
            # 4. Построение графа
            graph_id = await self.build_graph(validated_triplets)
            
            # 5. Создание mutual indexing
            mutual_index = await self.create_mutual_indexing(
                graph_id, chunks, validated_triplets
            )
            
            # 6. Сохранение метаданных
            metadata = DocumentMetadata(
                document_id=Path(doc_path).stem,
                title=Path(doc_path).name,
                content_type=doc_type,
                file_path=doc_path,
                created_at=datetime.now(),
                processed_at=datetime.now(),
                chunk_count=len(chunks)
            )
            
            await self._save_metadata(metadata, mutual_index)
            
            return {
                "success": True,
                "document_id": metadata.document_id,
                "triplets_count": len(validated_triplets),
                "graph_id": graph_id,
                "chunks_count": len(chunks),
                "mutual_index": mutual_index
            }
            
        except Exception as e:
            logger.error(f"Error processing document {doc_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_id": Path(doc_path).stem
            }
    
    async def extract_spo_triplets(self, text: str, chunk_id: str) -> List[SPOTriplet]:
        """
        Извлечение SPO-триплетов из текста с помощью LLM
        
        Args:
            text: Текст для обработки
            chunk_id: Идентификатор чанка
            
        Returns:
            Список SPO-триплетов
        """
        try:
            # Промпт для извлечения SPO-триплетов
            prompt = f"""
            Извлеки SPO-триплеты (Subject-Predicate-Object) из следующего текста.
            Фокусируйся на технических концепциях, отношениях и зависимостях.
            
            Текст: {text}
            
            Верни результат в JSON формате:
            {{
                "triplets": [
                    {{
                        "subject": "субъект",
                        "predicate": "предикат", 
                        "object": "объект",
                        "confidence": 0.9,
                        "type": "technical|logical|temporal"
                    }}
                ]
            }}
            """
            
            # Здесь должен быть вызов LLM API
            # Пока используем заглушку
            triplets_data = await self._call_llm_api(prompt)
            
            # Парсинг результата
            triplets = []
            for triplet_data in triplets_data.get("triplets", []):
                triplet = SPOTriplet(
                    subject=triplet_data["subject"],
                    predicate=triplet_data["predicate"],
                    object=triplet_data["object"],
                    confidence=triplet_data.get("confidence", 0.8),
                    source_chunk=chunk_id,
                    source_document=chunk_id.split("_chunk_")[0],
                    metadata={
                        "type": triplet_data.get("type", "technical"),
                        "extracted_at": datetime.now().isoformat()
                    }
                )
                triplets.append(triplet)
            
            logger.info(f"Extracted {len(triplets)} triplets from chunk {chunk_id}")
            return triplets
            
        except Exception as e:
            logger.error(f"Error extracting triplets from chunk {chunk_id}: {e}")
            return []
    
    async def build_graph(self, triplets: List[SPOTriplet]) -> str:
        """
        Построение графа в OpenSPG
        
        Args:
            triplets: Список SPO-триплетов
            
        Returns:
            Идентификатор созданного графа
        """
        try:
            graph_id = f"terag_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Подготовка данных для OpenSPG
            graph_data = {
                "graph_id": graph_id,
                "schema": self.terag_schema,
                "triplets": [
                    {
                        "subject": t.subject,
                        "predicate": t.predicate,
                        "object": t.object,
                        "confidence": t.confidence,
                        "metadata": t.metadata
                    }
                    for t in triplets
                ]
            }
            
            # Отправка в OpenSPG
            async with self.session.post(
                f"{self.openspg_url}/api/graphs",
                json=graph_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Graph {graph_id} created successfully")
                    return graph_id
                else:
                    raise Exception(f"OpenSPG API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error building graph: {e}")
            # Fallback: сохранение в Neo4j
            return await self._build_graph_neo4j(triplets)
    
    async def create_mutual_indexing(
        self, 
        graph_id: str, 
        chunks: List[str], 
        triplets: List[SPOTriplet]
    ) -> Dict[str, Any]:
        """
        Создание взаимного индексирования узлов и чанков
        
        Args:
            graph_id: Идентификатор графа
            chunks: Список чанков текста
            triplets: Список триплетов
            
        Returns:
            Словарь с индексированием
        """
        try:
            mutual_index = {
                "graph_id": graph_id,
                "chunk_to_entities": {},
                "entity_to_chunks": {},
                "entity_relationships": {}
            }
            
            # Создание связей чанк -> сущности
            for i, chunk in enumerate(chunks):
                chunk_id = f"chunk_{i}"
                entities = []
                
                for triplet in triplets:
                    if triplet.source_chunk == chunk_id:
                        entities.extend([triplet.subject, triplet.object])
                
                mutual_index["chunk_to_entities"][chunk_id] = list(set(entities))
            
            # Создание связей сущность -> чанки
            for triplet in triplets:
                for entity in [triplet.subject, triplet.object]:
                    if entity not in mutual_index["entity_to_chunks"]:
                        mutual_index["entity_to_chunks"][entity] = []
                    mutual_index["entity_to_chunks"][entity].append(triplet.source_chunk)
            
            # Сохранение в Supabase
            await self._save_mutual_indexing(mutual_index)
            
            logger.info(f"Mutual indexing created for graph {graph_id}")
            return mutual_index
            
        except Exception as e:
            logger.error(f"Error creating mutual indexing: {e}")
            return {}
    
    async def _load_document(self, doc_path: str, doc_type: str) -> str:
        """Загрузка документа"""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading document {doc_path}: {e}")
            return ""
    
    async def _chunk_document(self, content: str, doc_type: str) -> List[str]:
        """Разбиение документа на чанки"""
        # Простое разбиение по абзацам
        chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
        return chunks
    
    async def _validate_triplets(self, triplets: List[SPOTriplet]) -> List[SPOTriplet]:
        """Валидация SPO-триплетов"""
        validated = []
        for triplet in triplets:
            # Проверка на пустые поля
            if triplet.subject and triplet.predicate and triplet.object:
                # Проверка confidence
                if 0 <= triplet.confidence <= 1:
                    validated.append(triplet)
        return validated
    
    async def _call_llm_api(self, prompt: str) -> Dict[str, Any]:
        """Вызов LLM API (заглушка)"""
        # Здесь должен быть реальный вызов LLM
        # Пока возвращаем заглушку
        return {
            "triplets": [
                {
                    "subject": "TERAG System",
                    "predicate": "implements",
                    "object": "KAG Architecture",
                    "confidence": 0.9,
                    "type": "technical"
                }
            ]
        }
    
    async def _build_graph_neo4j(self, triplets: List[SPOTriplet]) -> str:
        """Fallback: построение графа в Neo4j"""
        # Здесь должна быть интеграция с Neo4j
        logger.info("Using Neo4j fallback for graph building")
        return f"neo4j_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def _save_metadata(self, metadata: DocumentMetadata, mutual_index: Dict[str, Any]):
        """Сохранение метаданных в Supabase"""
        # Здесь должна быть интеграция с Supabase
        logger.info(f"Saving metadata for document {metadata.document_id}")
    
    async def _save_mutual_indexing(self, mutual_index: Dict[str, Any]):
        """Сохранение mutual indexing в Supabase"""
        # Здесь должна быть интеграция с Supabase
        logger.info(f"Saving mutual indexing for graph {mutual_index['graph_id']}")

# Пример использования
async def main():
    """Пример использования KAG Builder"""
    builder = KAGBuilder(
        openspg_url="http://localhost:8080",
        neo4j_url="bolt://localhost:7687",
        supabase_url="postgresql://postgres:password@localhost:5432/terag"
    )
    
    async with builder:
        result = await builder.process_document(
            "docs/architecture/kag-integration.md",
            "markdown"
        )
        print(f"Processing result: {result}")

if __name__ == "__main__":
    asyncio.run(main())





































