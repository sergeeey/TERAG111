"""
Тесты для линтинга промптов
"""
import pytest
import json
from pathlib import Path


def test_prompt_schema_validation():
    """Тест валидации схемы промпта"""
    schema_path = Path("configs/prompts/registry_schema.json")
    
    assert schema_path.exists(), "Schema file not found"
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    # Проверяем обязательные поля
    required_fields = schema.get("required", [])
    assert "name" in required_fields
    assert "content" in required_fields
    assert "version" in required_fields


def test_prompt_format():
    """Тест формата промпта"""
    # Пример валидного промпта
    valid_prompt = {
        "name": "test_prompt",
        "content": "This is a test prompt with {variable}",
        "version": "1.0.0",
        "description": "Test prompt",
        "variables": [
            {
                "name": "variable",
                "type": "string",
                "required": True
            }
        ],
        "tags": ["test"],
        "aliases": ["@latest"]
    }
    
    # Проверяем структуру
    assert "name" in valid_prompt
    assert "content" in valid_prompt
    assert "version" in valid_prompt
    assert len(valid_prompt["content"]) > 10


def test_prompt_variables():
    """Тест переменных в промпте"""
    prompt_content = "Hello {name}, you have {count} messages."
    
    # Извлекаем переменные
    import re
    variables = re.findall(r'\{(\w+)\}', prompt_content)
    
    assert "name" in variables
    assert "count" in variables


@pytest.mark.parametrize("prompt_name", [
    "planner_v1",
    "solver_base",
    "verifier_strict",
    "ethical_evaluator"
])
def test_prompt_name_format(prompt_name):
    """Тест формата имени промпта"""
    import re
    pattern = r'^[a-z0-9_]+$'
    assert re.match(pattern, prompt_name), f"Invalid prompt name format: {prompt_name}"









