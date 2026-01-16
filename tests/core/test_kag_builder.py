#!/usr/bin/env python3
"""
Тесты для kag_builder.py
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import sys

# Добавляем путь к src
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.kag_builder import extract_triplets_from_text, process_document, run_batch_processing


class TestExtractTriplets:
    """Тесты для функции extract_triplets_from_text"""
    
    def test_extract_triplets_russian(self):
        """Тест извлечения триплетов из русского текста"""
        text = "Иван работает программистом. Мария изучает Python."
        triplets = extract_triplets_from_text(text, "ru")
        
        assert len(triplets) > 0
        assert all(t["language"] == "ru" for t in triplets)
        assert all("subject" in t for t in triplets)
        assert all("predicate" in t for t in triplets)
        assert all("object" in t for t in triplets)
    
    def test_extract_triplets_english(self):
        """Тест извлечения триплетов из английского текста"""
        text = "John works as a programmer. Mary studies Python."
        triplets = extract_triplets_from_text(text, "en")
        
        assert len(triplets) > 0
        assert all(t["language"] == "en" for t in triplets)
    
    def test_extract_triplets_empty_text(self):
        """Тест с пустым текстом"""
        triplets = extract_triplets_from_text("", "ru")
        assert triplets == []
    
    def test_extract_triplets_short_text(self):
        """Тест с коротким текстом (менее 10 символов)"""
        triplets = extract_triplets_from_text("Hi", "ru")
        assert triplets == []


class TestProcessDocument:
    """Тесты для функции process_document"""
    
    def test_process_document_success(self):
        """Тест успешной обработки документа"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Создаем тестовый файл
            test_file = Path(tmpdir) / "test_doc.txt"
            test_file.write_text("Это тестовый документ для проверки обработки.", encoding="utf-8")
            
            # Мокаем OUTPUT_DIR
            with patch('src.core.kag_builder.OUTPUT_DIR', Path(tmpdir) / "graph_results"):
                Path(tmpdir / "graph_results").mkdir(exist_ok=True)
                
                process_document(test_file)
                
                # Проверяем, что файл результата создан
                result_file = Path(tmpdir) / "graph_results" / "test_doc_graph.json"
                assert result_file.exists()
                
                # Проверяем содержимое
                with open(result_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                
                assert "file" in result
                assert "triplets" in result
                assert "language" in result
    
    def test_process_document_nonexistent_file(self):
        """Тест обработки несуществующего файла"""
        nonexistent = Path("/nonexistent/file.txt")
        # Не должно вызывать исключение, только логировать ошибку
        process_document(nonexistent)


class TestBatchProcessing:
    """Тесты для функции run_batch_processing"""
    
    @patch('src.core.kag_builder.get_converted_files')
    @patch('src.core.kag_builder.process_document')
    def test_run_batch_processing_with_files(self, mock_process, mock_get_files):
        """Тест пакетной обработки с файлами"""
        # Мокаем список файлов
        mock_files = [
            Path("test1.txt"),
            Path("test2.txt")
        ]
        mock_get_files.return_value = mock_files
        
        run_batch_processing()
        
        # Проверяем, что process_document вызван для каждого файла
        assert mock_process.call_count == 2
    
    @patch('src.core.kag_builder.get_converted_files')
    def test_run_batch_processing_no_files(self, mock_get_files):
        """Тест пакетной обработки без файлов"""
        mock_get_files.return_value = []
        
        # Не должно вызывать исключение
        run_batch_processing()














