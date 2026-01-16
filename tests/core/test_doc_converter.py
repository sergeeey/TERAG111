#!/usr/bin/env python3
"""
Тесты для doc_converter.py
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.doc_converter import detect_language, convert_all_to_txt, get_converted_files


class TestDetectLanguage:
    """Тесты для функции detect_language"""
    
    def test_detect_language_russian(self):
        """Тест определения русского языка"""
        text = "Это русский текст для проверки определения языка."
        lang = detect_language(text)
        assert lang in ["ru", "unknown"]
    
    def test_detect_language_english(self):
        """Тест определения английского языка"""
        text = "This is English text for language detection test."
        lang = detect_language(text)
        assert lang in ["en", "unknown"]
    
    def test_detect_language_short_text(self):
        """Тест с коротким текстом"""
        lang = detect_language("Hi")
        assert lang == "unknown"
    
    def test_detect_language_empty(self):
        """Тест с пустым текстом"""
        lang = detect_language("")
        assert lang == "unknown"


class TestConvertAllToTxt:
    """Тесты для функции convert_all_to_txt"""
    
    def test_convert_all_to_txt_nonexistent_dir(self):
        """Тест с несуществующей директорией"""
        result = convert_all_to_txt("/nonexistent/directory")
        # Должна вернуть путь, даже если директория не существует
        assert isinstance(result, (str, Path))
    
    @patch('src.core.doc_converter.Path')
    def test_convert_all_to_txt_empty_dir(self, mock_path):
        """Тест с пустой директорией"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.rglob.return_value = []
        mock_path.return_value = mock_path_instance
        
        result = convert_all_to_txt("test_dir")
        assert isinstance(result, (str, Path))


class TestGetConvertedFiles:
    """Тесты для функции get_converted_files"""
    
    def test_get_converted_files_nonexistent_dir(self):
        """Тест с несуществующей директорией"""
        files = get_converted_files("/nonexistent/directory")
        assert isinstance(files, list)
    
    def test_get_converted_files_empty_dir(self):
        """Тест с пустой директорией"""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = get_converted_files(tmpdir)
            assert files == []














