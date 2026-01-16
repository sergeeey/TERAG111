"""
Тесты для оценки промптов
"""
import pytest
from unittest.mock import Mock, patch


def test_prompt_loader_service():
    """Тест PromptLoaderService"""
    try:
        from src.promptops.loader_service import PromptLoaderService
        from src.promptops.mlflow_registry import PromptRegistryManager
        
        # Создаем мок registry
        mock_registry = Mock(spec=PromptRegistryManager)
        mock_registry.get_prompt = Mock(return_value={
            "name": "test",
            "content": "Test prompt",
            "version": "1.0.0"
        })
        
        # Создаем loader
        loader = PromptLoaderService(registry=mock_registry)
        
        # Тестируем загрузку
        prompt = loader.load_prompt("test", alias="@latest")
        
        assert prompt == "Test prompt"
    
    except ImportError:
        pytest.skip("PromptOps not available")


def test_prompt_with_variables():
    """Тест загрузки промпта с переменными"""
    try:
        from src.promptops.loader_service import PromptLoaderService
        from src.promptops.mlflow_registry import PromptRegistryManager
        
        mock_registry = Mock(spec=PromptRegistryManager)
        mock_registry.get_prompt = Mock(return_value={
            "name": "test",
            "content": "Hello {name}, you have {count} messages.",
            "version": "1.0.0"
        })
        
        loader = PromptLoaderService(registry=mock_registry)
        
        prompt = loader.load_prompt_with_variables(
            "test",
            variables={"name": "User", "count": 5}
        )
        
        assert "User" in prompt
        assert "5" in prompt
        assert "{name}" not in prompt
        assert "{count}" not in prompt
    
    except ImportError:
        pytest.skip("PromptOps not available")


def test_prompt_cache():
    """Тест кэширования промптов"""
    try:
        from src.promptops.loader_service import PromptLoaderService
        from src.promptops.mlflow_registry import PromptRegistryManager
        
        mock_registry = Mock(spec=PromptRegistryManager)
        mock_registry.get_prompt = Mock(return_value={
            "name": "test",
            "content": "Cached prompt",
            "version": "1.0.0"
        })
        
        loader = PromptLoaderService(registry=mock_registry, cache_ttl=60)
        
        # Первая загрузка
        prompt1 = loader.load_prompt("test", use_cache=True)
        
        # Вторая загрузка (должна быть из кэша)
        prompt2 = loader.load_prompt("test", use_cache=True)
        
        assert prompt1 == prompt2
        # Registry должен быть вызван только один раз
        assert mock_registry.get_prompt.call_count == 1
    
    except ImportError:
        pytest.skip("PromptOps not available")









