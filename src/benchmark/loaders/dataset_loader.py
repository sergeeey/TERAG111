"""
Dataset Loader для TERAG Benchmark
Поддерживает MultiHop-QA и собственный корпус TERAG
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QAExample:
    """Структура примера вопрос-ответ"""
    question: str
    answer: str
    context: Optional[List[str]] = None
    ground_truth: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DatasetLoader:
    """
    Загрузчик датасетов для benchmark
    """
    
    def __init__(self, data_dir: str = "data/processed/"):
        """
        Инициализация загрузчика
        
        Args:
            data_dir: Директория с данными
        """
        self.data_dir = Path(data_dir)
        logger.info(f"DatasetLoader initialized with data_dir: {data_dir}")
    
    def load_multihop_qa(self, file_path: Optional[str] = None) -> List[QAExample]:
        """
        Загрузить MultiHop-QA датасет
        
        Args:
            file_path: Путь к файлу (опционально)
        
        Returns:
            Список примеров QA
        """
        if file_path:
            qa_file = Path(file_path)
        else:
            # Ищем стандартный файл
            qa_file = self.data_dir / "multihop_qa.json"
        
        if not qa_file.exists():
            logger.warning(f"MultiHop-QA file not found: {qa_file}")
            return []
        
        with open(qa_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        examples = []
        for item in data:
            example = QAExample(
                question=item.get("question", ""),
                answer=item.get("answer", ""),
                context=item.get("context", []),
                ground_truth=item.get("ground_truth", item.get("answer", "")),
                metadata=item.get("metadata", {})
            )
            examples.append(example)
        
        logger.info(f"Loaded {len(examples)} MultiHop-QA examples")
        return examples
    
    def load_terag_corpus(self) -> List[Dict[str, Any]]:
        """
        Загрузить собственный корпус TERAG из обработанных документов
        
        Returns:
            Список документов
        """
        documents = []
        
        # Ищем текстовые файлы в data/processed/
        processed_dir = self.data_dir / "converted"
        if not processed_dir.exists():
            logger.warning(f"Processed directory not found: {processed_dir}")
            return documents
        
        for txt_file in processed_dir.glob("*.txt"):
            try:
                content = txt_file.read_text(encoding='utf-8')
                documents.append({
                    "id": txt_file.stem,
                    "content": content,
                    "metadata": {
                        "source": str(txt_file),
                        "size": len(content)
                    }
                })
            except Exception as e:
                logger.error(f"Error loading {txt_file}: {e}")
        
        logger.info(f"Loaded {len(documents)} documents from TERAG corpus")
        return documents
    
    def generate_qa_from_corpus(
        self,
        documents: List[Dict[str, Any]],
        num_questions: int = 50
    ) -> List[QAExample]:
        """
        Генерировать вопросы-ответы из корпуса документов
        
        Args:
            documents: Список документов
            num_questions: Количество вопросов для генерации
        
        Returns:
            Список примеров QA
        """
        # TODO: Интегрировать LLM для генерации вопросов
        # Пока возвращаем пустой список
        logger.info(f"Generating {num_questions} QA examples from corpus")
        
        examples = []
        # Простая генерация на основе ключевых фраз
        for i, doc in enumerate(documents[:num_questions]):
            # Извлекаем первые предложения как вопросы
            content = doc["content"]
            sentences = content.split('.')[:3]
            
            if sentences:
                question = f"Что говорится о {sentences[0][:50]}?"
                answer = sentences[0] if len(sentences) > 0 else content[:200]
                
                example = QAExample(
                    question=question,
                    answer=answer,
                    context=[content[:500]],
                    ground_truth=answer,
                    metadata={"source": doc["id"]}
                )
                examples.append(example)
        
        logger.info(f"Generated {len(examples)} QA examples")
        return examples
    
    def load_benchmark_dataset(self) -> List[QAExample]:
        """
        Загрузить датасет для benchmark
        Пытается загрузить MultiHop-QA, если нет - генерирует из корпуса
        
        Returns:
            Список примеров QA
        """
        # Пытаемся загрузить MultiHop-QA
        examples = self.load_multihop_qa()
        
        if not examples:
            # Генерируем из корпуса TERAG
            logger.info("MultiHop-QA not found, generating from TERAG corpus")
            documents = self.load_terag_corpus()
            examples = self.generate_qa_from_corpus(documents, num_questions=50)
        
        return examples









