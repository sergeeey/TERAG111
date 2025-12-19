#!/usr/bin/env python3
"""
Валидация TERAG API фикстур для контрактных тестов.

Проверяет соответствие примеров ответов (fixtures) OpenAPI схеме TERAG API.
Используется в CI для проверки контрактной совместимости.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Пути к файлам
PROJECT_ROOT = Path(__file__).parent.parent
SCHEMA_PATH = PROJECT_ROOT / "docs" / "TERAG_API_OPENAPI_SCHEMA.json"
FIXTURES_DIR = PROJECT_ROOT / "docs" / "contract_samples"

# Обязательные поля для QueryResponse
QUERY_RESPONSE_REQUIRED = {
    "answer", "query", "attempts", "max_attempts", "used_strategies",
    "decision", "rss_score", "rssscore", "retrieval_results_count",
    "trace", "metadata", "timestamp"
}

# Обязательные поля для MetricsResponse
METRICS_RESPONSE_REQUIRED = {
    "rss", "cos", "faith", "growth", "resonance", "confidence", "timestamp",
    "RSS", "COS", "FAITH", "Growth", "Resonance"
}

# Обязательные поля для ErrorResponse
ERROR_RESPONSE_REQUIRED = {
    "error", "error_code", "request_id", "timestamp"
}


def validate_query_response(fixture: Dict[str, Any]) -> List[str]:
    """Валидация QueryResponse фикстуры."""
    errors = []
    
    # Проверка обязательных полей
    missing_fields = QUERY_RESPONSE_REQUIRED - set(fixture.keys())
    if missing_fields:
        errors.append(f"Missing required fields: {missing_fields}")
    
    # Проверка dual-format (rss_score и rssscore должны совпадать)
    if "rss_score" in fixture and "rssscore" in fixture:
        if fixture["rss_score"] != fixture["rssscore"]:
            errors.append("rss_score and rssscore must be equal (dual-format)")
    
    # Проверка, что trace не null (может быть пустым списком)
    if "trace" in fixture and fixture["trace"] is None:
        errors.append("trace must not be null (can be empty list)")
    
    # Проверка, что metadata не null (может быть пустым объектом)
    if "metadata" in fixture and fixture["metadata"] is None:
        errors.append("metadata must not be null (can be empty object)")
    
    # Проверка metadata.request_id и metadata.timestamp
    if "metadata" in fixture and isinstance(fixture["metadata"], dict):
        if "request_id" not in fixture["metadata"]:
            errors.append("metadata.request_id is required")
        if "timestamp" not in fixture["metadata"]:
            errors.append("metadata.timestamp is required")
    
    # Проверка диапазонов для числовых полей
    for field in ["rss_score", "rssscore", "quality_score"]:
        if field in fixture and fixture[field] is not None:
            value = fixture[field]
            if not isinstance(value, (int, float)) or not (0 <= value <= 1):
                errors.append(f"{field} must be a number between 0 and 1")
    
    return errors


def validate_metrics_response(fixture: Dict[str, Any]) -> List[str]:
    """Валидация MetricsResponse фикстуры."""
    errors = []
    
    # Проверка обязательных полей
    missing_fields = METRICS_RESPONSE_REQUIRED - set(fixture.keys())
    if missing_fields:
        errors.append(f"Missing required fields: {missing_fields}")
    
    # Проверка dual-format (snake_case и UPPERCASE должны совпадать)
    dual_format_pairs = [
        ("rss", "RSS"),
        ("cos", "COS"),
        ("faith", "FAITH"),
        ("growth", "Growth"),
        ("resonance", "Resonance"),
    ]
    
    for snake_case, uppercase in dual_format_pairs:
        if snake_case in fixture and uppercase in fixture:
            if fixture[snake_case] != fixture[uppercase]:
                errors.append(f"{snake_case} and {uppercase} must be equal (dual-format)")
    
    # Проверка диапазонов для числовых полей (0..1)
    range_fields = ["rss", "RSS", "cos", "COS", "faith", "FAITH", "resonance", "Resonance", "confidence"]
    for field in range_fields:
        if field in fixture:
            value = fixture[field]
            if not isinstance(value, (int, float)) or not (0 <= value <= 1):
                errors.append(f"{field} must be a number between 0 and 1")
    
    return errors


def validate_error_response(fixture: Dict[str, Any]) -> List[str]:
    """Валидация ErrorResponse фикстуры."""
    errors = []
    
    # Проверка обязательных полей
    missing_fields = ERROR_RESPONSE_REQUIRED - set(fixture.keys())
    if missing_fields:
        errors.append(f"Missing required fields: {missing_fields}")
    
    # Проверка формата request_id (должен быть UUID-подобным)
    if "request_id" in fixture:
        request_id = fixture["request_id"]
        if not isinstance(request_id, str) or len(request_id) < 32:
            errors.append("request_id must be a valid UUID string")
    
    # Проверка формата timestamp (должен быть ISO-8601)
    if "timestamp" in fixture:
        timestamp = fixture["timestamp"]
        if not isinstance(timestamp, str) or "T" not in timestamp:
            errors.append("timestamp must be ISO-8601 format")
    
    return errors


def main():
    """Основная функция валидации."""
    print("🔍 Validating TERAG API fixtures...")
    
    all_errors = []
    
    # Валидация query_ok.json
    query_fixture_path = FIXTURES_DIR / "query_ok.json"
    if query_fixture_path.exists():
        print(f"  ✓ Validating {query_fixture_path.name}...")
        with open(query_fixture_path, "r", encoding="utf-8") as f:
            query_fixture = json.load(f)
        errors = validate_query_response(query_fixture)
        if errors:
            all_errors.append(f"{query_fixture_path.name}: {errors}")
        else:
            print(f"    ✅ {query_fixture_path.name} is valid")
    else:
        all_errors.append(f"Missing fixture: {query_fixture_path}")
    
    # Валидация metrics_ok.json
    metrics_fixture_path = FIXTURES_DIR / "metrics_ok.json"
    if metrics_fixture_path.exists():
        print(f"  ✓ Validating {metrics_fixture_path.name}...")
        with open(metrics_fixture_path, "r", encoding="utf-8") as f:
            metrics_fixture = json.load(f)
        errors = validate_metrics_response(metrics_fixture)
        if errors:
            all_errors.append(f"{metrics_fixture_path.name}: {errors}")
        else:
            print(f"    ✅ {metrics_fixture_path.name} is valid")
    else:
        all_errors.append(f"Missing fixture: {metrics_fixture_path}")
    
    # Валидация error_503.json
    error_fixture_path = FIXTURES_DIR / "error_503.json"
    if error_fixture_path.exists():
        print(f"  ✓ Validating {error_fixture_path.name}...")
        with open(error_fixture_path, "r", encoding="utf-8") as f:
            error_fixture = json.load(f)
        errors = validate_error_response(error_fixture)
        if errors:
            all_errors.append(f"{error_fixture_path.name}: {errors}")
        else:
            print(f"    ✅ {error_fixture_path.name} is valid")
    else:
        all_errors.append(f"Missing fixture: {error_fixture_path}")
    
    # Итоговый результат
    if all_errors:
        print("\n❌ Validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        return 1
    else:
        print("\n✅ All fixtures are valid!")
        return 0


if __name__ == "__main__":
    sys.exit(main())

