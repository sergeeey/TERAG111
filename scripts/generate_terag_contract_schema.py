#!/usr/bin/env python3
"""
Генерация JSON Schema для TERAG API контракта.

Генерирует JSON Schema из OpenAPI схемы для использования в контрактных тестах.
Используется в CI для проверки соответствия API контракту.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Пути к файлам
PROJECT_ROOT = Path(__file__).parent.parent
OPENAPI_SCHEMA_PATH = PROJECT_ROOT / "docs" / "TERAG_API_OPENAPI_SCHEMA.json"
OUTPUT_SCHEMA_PATH = PROJECT_ROOT / "docs" / "TERAG_API_JSON_SCHEMA.json"


def extract_json_schema_from_openapi(openapi_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Извлечение JSON Schema из OpenAPI схемы."""
    
    # Извлекаем схемы компонентов
    components = openapi_schema.get("components", {}).get("schemas", {})
    
    # Создаем JSON Schema документ
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "TERAG API Contract Schema",
        "description": "JSON Schema для валидации TERAG API контракта (извлечено из OpenAPI)",
        "definitions": {}
    }
    
    # Копируем схемы компонентов в definitions
    for schema_name, schema_def in components.items():
        json_schema["definitions"][schema_name] = schema_def
    
    # Добавляем основные схемы для быстрого доступа
    if "QueryRequest" in components:
        json_schema["QueryRequest"] = {"$ref": "#/definitions/QueryRequest"}
    if "QueryResponse" in components:
        json_schema["QueryResponse"] = {"$ref": "#/definitions/QueryResponse"}
    if "MetricsResponse" in components:
        json_schema["MetricsResponse"] = {"$ref": "#/definitions/MetricsResponse"}
    if "ErrorResponse" in components:
        json_schema["ErrorResponse"] = {"$ref": "#/definitions/ErrorResponse"}
    
    return json_schema


def main():
    """Основная функция генерации."""
    print("🔧 Generating TERAG API Contract JSON Schema...")
    
    # Проверка существования OpenAPI схемы
    if not OPENAPI_SCHEMA_PATH.exists():
        print(f"❌ OpenAPI schema not found: {OPENAPI_SCHEMA_PATH}")
        return 1
    
    # Загрузка OpenAPI схемы
    try:
        with open(OPENAPI_SCHEMA_PATH, "r", encoding="utf-8") as f:
            openapi_schema = json.load(f)
        print(f"  ✓ Loaded OpenAPI schema from {OPENAPI_SCHEMA_PATH.name}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in OpenAPI schema: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error loading OpenAPI schema: {e}")
        return 1
    
    # Извлечение JSON Schema
    try:
        json_schema = extract_json_schema_from_openapi(openapi_schema)
        print("  ✓ Extracted JSON Schema from OpenAPI")
    except Exception as e:
        print(f"❌ Error extracting JSON Schema: {e}")
        return 1
    
    # Сохранение JSON Schema
    try:
        OUTPUT_SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_SCHEMA_PATH, "w", encoding="utf-8") as f:
            json.dump(json_schema, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Saved JSON Schema to {OUTPUT_SCHEMA_PATH.name}")
    except Exception as e:
        print(f"❌ Error saving JSON Schema: {e}")
        return 1
    
    print("\n✅ JSON Schema generated successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

