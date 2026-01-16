#!/usr/bin/env python3
"""
Тесты для ollama_client.py
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.ollama_client import query_ollama, list_available_models, query_with_context


class TestQueryOllama:
    """Тесты для функции query_ollama"""
    
    @patch('src.core.ollama_client.requests.post')
    def test_query_ollama_success(self, mock_post):
        """Тест успешного запроса к Ollama"""
        # Мокаем успешный ответ
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Test response"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        result = query_ollama("Test prompt", "test-model")
        
        assert result == "Test response"
        mock_post.assert_called_once()
    
    @patch('src.core.ollama_client.requests.post')
    def test_query_ollama_connection_error(self, mock_post):
        """Тест ошибки подключения"""
        from requests.exceptions import ConnectionError
        mock_post.side_effect = ConnectionError()
        
        result = query_ollama("Test prompt")
        
        assert "[Ошибка]" in result
        assert "Ollama" in result
    
    @patch('src.core.ollama_client.requests.post')
    def test_query_ollama_general_error(self, mock_post):
        """Тест общей ошибки"""
        mock_post.side_effect = Exception("Test error")
        
        result = query_ollama("Test prompt")
        
        assert "[Ошибка Ollama]" in result


class TestListAvailableModels:
    """Тесты для функции list_available_models"""
    
    @patch('src.core.ollama_client.requests.get')
    def test_list_available_models_success(self, mock_get):
        """Тест успешного получения списка моделей"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "models": [
                {"name": "model1"},
                {"name": "model2"}
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        models = list_available_models()
        
        assert len(models) == 2
        assert "model1" in models
        assert "model2" in models
    
    @patch('src.core.ollama_client.requests.get')
    def test_list_available_models_error(self, mock_get):
        """Тест ошибки при получении списка моделей"""
        mock_get.side_effect = Exception("Connection error")
        
        models = list_available_models()
        
        assert models == []


class TestQueryWithContext:
    """Тесты для функции query_with_context"""
    
    @patch('src.core.ollama_client.query_ollama')
    def test_query_with_context(self, mock_query):
        """Тест запроса с контекстом"""
        mock_query.return_value = "Answer with context"
        
        result = query_with_context("Question", "Context information", "test-model")
        
        assert result == "Answer with context"
        mock_query.assert_called_once()
        # Проверяем, что контекст включен в промпт
        call_args = mock_query.call_args[0][0]
        assert "Context information" in call_args
        assert "Question" in call_args














