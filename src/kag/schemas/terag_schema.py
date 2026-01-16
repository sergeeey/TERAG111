#!/usr/bin/env python3
"""
TERAG Schema - схема OpenSPG для проекта TERAG
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class EntityType(Enum):
    """Типы сущностей в схеме TERAG"""
    CONCEPT = "Concept"
    AGENT = "Agent"
    PROCESS = "Process"
    DECISION = "Decision"
    EVIDENCE = "Evidence"
    CODE = "Code"
    FUNCTION = "Function"
    CLASS = "Class"
    VARIABLE = "Variable"
    INTERFACE = "Interface"
    DOCUMENT = "Document"
    USER = "User"
    SESSION = "Session"

class RelationType(Enum):
    """Типы отношений в схеме TERAG"""
    # Технические отношения
    IMPLEMENTS = "implements"
    EXTENDS = "extends"
    USES = "uses"
    CALLS = "calls"
    DEFINES = "defines"
    DEPENDS_ON = "depends_on"
    CONTAINS = "contains"
    
    # Логические отношения
    CAUSES = "causes"
    INFLUENCES = "influences"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    PRECEDES = "precedes"
    
    # Временные отношения
    HAPPENS_AT = "happens_at"
    STARTS = "starts"
    ENDS = "ends"
    DURATION = "duration"
    
    # Пользовательские отношения
    CREATES = "creates"
    MODIFIES = "modifies"
    DELETES = "deletes"
    VIEWS = "views"
    SEARCHES = "searches"

@dataclass
class EntityDefinition:
    """Определение сущности"""
    name: str
    type: EntityType
    properties: Dict[str, str]
    constraints: List[str]
    description: str

@dataclass
class RelationDefinition:
    """Определение отношения"""
    name: str
    type: RelationType
    source_entity: EntityType
    target_entity: EntityType
    properties: Dict[str, str]
    constraints: List[str]
    description: str

class TERAGSchema:
    """Схема OpenSPG для проекта TERAG"""
    
    def __init__(self):
        self.entities = self._define_entities()
        self.relations = self._define_relations()
        self.constraints = self._define_constraints()
    
    def _define_entities(self) -> List[EntityDefinition]:
        """Определение сущностей схемы"""
        return [
            EntityDefinition(
                name="Concept",
                type=EntityType.CONCEPT,
                properties={
                    "id": "string",
                    "name": "string",
                    "description": "string",
                    "category": "string",
                    "confidence": "float",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                },
                constraints=[
                    "id IS UNIQUE",
                    "name IS NOT NULL",
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Абстрактная концепция или идея"
            ),
            
            EntityDefinition(
                name="Agent",
                type=EntityType.AGENT,
                properties={
                    "id": "string",
                    "name": "string",
                    "type": "string",
                    "capabilities": "array<string>",
                    "status": "string",
                    "created_at": "timestamp"
                },
                constraints=[
                    "id IS UNIQUE",
                    "name IS NOT NULL",
                    "type IN ['user', 'system', 'ai']"
                ],
                description="Агент (пользователь, система или ИИ)"
            ),
            
            EntityDefinition(
                name="Process",
                type=EntityType.PROCESS,
                properties={
                    "id": "string",
                    "name": "string",
                    "type": "string",
                    "status": "string",
                    "start_time": "timestamp",
                    "end_time": "timestamp",
                    "parameters": "json"
                },
                constraints=[
                    "id IS UNIQUE",
                    "name IS NOT NULL",
                    "status IN ['running', 'completed', 'failed', 'cancelled']"
                ],
                description="Процесс или операция"
            ),
            
            EntityDefinition(
                name="Decision",
                type=EntityType.DECISION,
                properties={
                    "id": "string",
                    "description": "string",
                    "reasoning": "string",
                    "confidence": "float",
                    "alternatives": "array<string>",
                    "created_at": "timestamp",
                    "agent_id": "string"
                },
                constraints=[
                    "id IS UNIQUE",
                    "description IS NOT NULL",
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Принятое решение с обоснованием"
            ),
            
            EntityDefinition(
                name="Evidence",
                type=EntityType.EVIDENCE,
                properties={
                    "id": "string",
                    "content": "string",
                    "source": "string",
                    "type": "string",
                    "reliability": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "id IS UNIQUE",
                    "content IS NOT NULL",
                    "reliability >= 0 AND reliability <= 1"
                ],
                description="Доказательство или источник информации"
            ),
            
            EntityDefinition(
                name="Code",
                type=EntityType.CODE,
                properties={
                    "id": "string",
                    "name": "string",
                    "language": "string",
                    "content": "string",
                    "file_path": "string",
                    "line_start": "integer",
                    "line_end": "integer",
                    "created_at": "timestamp"
                },
                constraints=[
                    "id IS UNIQUE",
                    "name IS NOT NULL",
                    "language IS NOT NULL"
                ],
                description="Фрагмент кода"
            ),
            
            EntityDefinition(
                name="Function",
                type=EntityType.FUNCTION,
                properties={
                    "id": "string",
                    "name": "string",
                    "signature": "string",
                    "parameters": "array<string>",
                    "return_type": "string",
                    "description": "string",
                    "code_id": "string"
                },
                constraints=[
                    "id IS UNIQUE",
                    "name IS NOT NULL",
                    "signature IS NOT NULL"
                ],
                description="Функция или метод"
            ),
            
            EntityDefinition(
                name="Class",
                type=EntityType.CLASS,
                properties={
                    "id": "string",
                    "name": "string",
                    "package": "string",
                    "superclass": "string",
                    "interfaces": "array<string>",
                    "description": "string",
                    "code_id": "string"
                },
                constraints=[
                    "id IS UNIQUE",
                    "name IS NOT NULL"
                ],
                description="Класс или интерфейс"
            ),
            
            EntityDefinition(
                name="Variable",
                type=EntityType.VARIABLE,
                properties={
                    "id": "string",
                    "name": "string",
                    "type": "string",
                    "scope": "string",
                    "value": "string",
                    "description": "string",
                    "code_id": "string"
                },
                constraints=[
                    "id IS UNIQUE",
                    "name IS NOT NULL",
                    "type IS NOT NULL"
                ],
                description="Переменная или константа"
            ),
            
            EntityDefinition(
                name="Interface",
                type=EntityType.INTERFACE,
                properties={
                    "id": "string",
                    "name": "string",
                    "methods": "array<string>",
                    "properties": "array<string>",
                    "description": "string",
                    "code_id": "string"
                },
                constraints=[
                    "id IS UNIQUE",
                    "name IS NOT NULL"
                ],
                description="Интерфейс или протокол"
            ),
            
            EntityDefinition(
                name="Document",
                type=EntityType.DOCUMENT,
                properties={
                    "id": "string",
                    "title": "string",
                    "content": "string",
                    "type": "string",
                    "file_path": "string",
                    "created_at": "timestamp",
                    "updated_at": "timestamp"
                },
                constraints=[
                    "id IS UNIQUE",
                    "title IS NOT NULL",
                    "type IN ['pdf', 'markdown', 'text', 'code']"
                ],
                description="Документ или файл"
            ),
            
            EntityDefinition(
                name="User",
                type=EntityType.USER,
                properties={
                    "id": "string",
                    "username": "string",
                    "email": "string",
                    "role": "string",
                    "preferences": "json",
                    "created_at": "timestamp"
                },
                constraints=[
                    "id IS UNIQUE",
                    "username IS NOT NULL",
                    "email IS NOT NULL"
                ],
                description="Пользователь системы"
            ),
            
            EntityDefinition(
                name="Session",
                type=EntityType.SESSION,
                properties={
                    "id": "string",
                    "user_id": "string",
                    "start_time": "timestamp",
                    "end_time": "timestamp",
                    "status": "string",
                    "metadata": "json"
                },
                constraints=[
                    "id IS UNIQUE",
                    "user_id IS NOT NULL",
                    "status IN ['active', 'inactive', 'expired']"
                ],
                description="Сессия пользователя"
            )
        ]
    
    def _define_relations(self) -> List[RelationDefinition]:
        """Определение отношений схемы"""
        return [
            # Технические отношения
            RelationDefinition(
                name="implements",
                type=RelationType.IMPLEMENTS,
                source_entity=EntityType.CLASS,
                target_entity=EntityType.INTERFACE,
                properties={
                    "confidence": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Класс реализует интерфейс"
            ),
            
            RelationDefinition(
                name="extends",
                type=RelationType.EXTENDS,
                source_entity=EntityType.CLASS,
                target_entity=EntityType.CLASS,
                properties={
                    "confidence": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Класс наследует от другого класса"
            ),
            
            RelationDefinition(
                name="uses",
                type=RelationType.USES,
                source_entity=EntityType.FUNCTION,
                target_entity=EntityType.FUNCTION,
                properties={
                    "confidence": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Функция использует другую функцию"
            ),
            
            RelationDefinition(
                name="calls",
                type=RelationType.CALLS,
                source_entity=EntityType.FUNCTION,
                target_entity=EntityType.FUNCTION,
                properties={
                    "confidence": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Функция вызывает другую функцию"
            ),
            
            RelationDefinition(
                name="defines",
                type=RelationType.DEFINES,
                source_entity=EntityType.CLASS,
                target_entity=EntityType.FUNCTION,
                properties={
                    "confidence": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Класс определяет функцию"
            ),
            
            RelationDefinition(
                name="depends_on",
                type=RelationType.DEPENDS_ON,
                source_entity=EntityType.CODE,
                target_entity=EntityType.CODE,
                properties={
                    "confidence": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Код зависит от другого кода"
            ),
            
            RelationDefinition(
                name="contains",
                type=RelationType.CONTAINS,
                source_entity=EntityType.CLASS,
                target_entity=EntityType.VARIABLE,
                properties={
                    "confidence": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Класс содержит переменную"
            ),
            
            # Логические отношения
            RelationDefinition(
                name="causes",
                type=RelationType.CAUSES,
                source_entity=EntityType.CONCEPT,
                target_entity=EntityType.CONCEPT,
                properties={
                    "confidence": "float",
                    "evidence_id": "string",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Концепция вызывает другую концепцию"
            ),
            
            RelationDefinition(
                name="influences",
                type=RelationType.INFLUENCES,
                source_entity=EntityType.CONCEPT,
                target_entity=EntityType.CONCEPT,
                properties={
                    "confidence": "float",
                    "strength": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1",
                    "strength >= 0 AND strength <= 1"
                ],
                description="Концепция влияет на другую концепцию"
            ),
            
            RelationDefinition(
                name="supports",
                type=RelationType.SUPPORTS,
                source_entity=EntityType.EVIDENCE,
                target_entity=EntityType.CONCEPT,
                properties={
                    "confidence": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Доказательство поддерживает концепцию"
            ),
            
            RelationDefinition(
                name="contradicts",
                type=RelationType.CONTRADICTS,
                source_entity=EntityType.EVIDENCE,
                target_entity=EntityType.CONCEPT,
                properties={
                    "confidence": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Доказательство противоречит концепции"
            ),
            
            RelationDefinition(
                name="precedes",
                type=RelationType.PRECEDES,
                source_entity=EntityType.PROCESS,
                target_entity=EntityType.PROCESS,
                properties={
                    "confidence": "float",
                    "created_at": "timestamp"
                },
                constraints=[
                    "confidence >= 0 AND confidence <= 1"
                ],
                description="Процесс предшествует другому процессу"
            ),
            
            # Пользовательские отношения
            RelationDefinition(
                name="creates",
                type=RelationType.CREATES,
                source_entity=EntityType.USER,
                target_entity=EntityType.DOCUMENT,
                properties={
                    "created_at": "timestamp"
                },
                constraints=[],
                description="Пользователь создает документ"
            ),
            
            RelationDefinition(
                name="modifies",
                type=RelationType.MODIFIES,
                source_entity=EntityType.USER,
                target_entity=EntityType.DOCUMENT,
                properties={
                    "created_at": "timestamp"
                },
                constraints=[],
                description="Пользователь изменяет документ"
            ),
            
            RelationDefinition(
                name="views",
                type=RelationType.VIEWS,
                source_entity=EntityType.USER,
                target_entity=EntityType.DOCUMENT,
                properties={
                    "created_at": "timestamp"
                },
                constraints=[],
                description="Пользователь просматривает документ"
            ),
            
            RelationDefinition(
                name="searches",
                type=RelationType.SEARCHES,
                source_entity=EntityType.USER,
                target_entity=EntityType.CONCEPT,
                properties={
                    "query": "string",
                    "created_at": "timestamp"
                },
                constraints=[],
                description="Пользователь ищет концепцию"
            )
        ]
    
    def _define_constraints(self) -> List[str]:
        """Определение глобальных ограничений схемы"""
        return [
            "temporal_consistency: Временные отношения должны быть логически последовательными",
            "logical_consistency: Логические отношения не должны противоречить друг другу",
            "evidence_requirement: Критические утверждения должны иметь доказательства",
            "confidence_threshold: Confidence должен быть >= 0.5 для production",
            "uniqueness: Все сущности должны иметь уникальные идентификаторы",
            "referential_integrity: Ссылки на сущности должны быть валидными"
        ]
    
    def get_schema_dict(self) -> Dict[str, Any]:
        """Получение схемы в виде словаря для OpenSPG"""
        return {
            "entities": [
                {
                    "name": entity.name,
                    "type": entity.type.value,
                    "properties": entity.properties,
                    "constraints": entity.constraints,
                    "description": entity.description
                }
                for entity in self.entities
            ],
            "relations": [
                {
                    "name": relation.name,
                    "type": relation.type.value,
                    "source_entity": relation.source_entity.value,
                    "target_entity": relation.target_entity.value,
                    "properties": relation.properties,
                    "constraints": relation.constraints,
                    "description": relation.description
                }
                for relation in self.relations
            ],
            "constraints": self.constraints
        }
    
    def validate_entity(self, entity_type: str, properties: Dict[str, Any]) -> bool:
        """Валидация сущности по схеме"""
        entity_def = next(
            (e for e in self.entities if e.name == entity_type), 
            None
        )
        
        if not entity_def:
            return False
        
        # Проверка обязательных свойств
        for prop, prop_type in entity_def.properties.items():
            if prop not in properties:
                return False
        
        # Проверка ограничений
        for constraint in entity_def.constraints:
            if not self._check_constraint(constraint, properties):
                return False
        
        return True
    
    def validate_relation(self, relation_type: str, properties: Dict[str, Any]) -> bool:
        """Валидация отношения по схеме"""
        relation_def = next(
            (r for r in self.relations if r.name == relation_type), 
            None
        )
        
        if not relation_def:
            return False
        
        # Проверка обязательных свойств
        for prop, prop_type in relation_def.properties.items():
            if prop not in properties:
                return False
        
        # Проверка ограничений
        for constraint in relation_def.constraints:
            if not self._check_constraint(constraint, properties):
                return False
        
        return True
    
    def _check_constraint(self, constraint: str, properties: Dict[str, Any]) -> bool:
        """Проверка ограничения"""
        # Простая проверка ограничений
        # В реальной реализации здесь должна быть более сложная логика
        
        if "IS NOT NULL" in constraint:
            field = constraint.split()[0]
            return field in properties and properties[field] is not None
        
        if "IS UNIQUE" in constraint:
            # Проверка уникальности должна быть на уровне базы данных
            return True
        
        if ">=" in constraint and "<=" in constraint:
            # Проверка диапазона значений
            field = constraint.split()[0]
            if field in properties:
                value = properties[field]
                if isinstance(value, (int, float)):
                    min_val = float(constraint.split(">=")[1].split()[0])
                    max_val = float(constraint.split("<=")[1].split()[0])
                    return min_val <= value <= max_val
        
        return True

# Создание глобального экземпляра схемы
TERAG_SCHEMA = TERAGSchema()

# Экспорт для использования в других модулях
__all__ = ['TERAG_SCHEMA', 'EntityType', 'RelationType', 'EntityDefinition', 'RelationDefinition']





































