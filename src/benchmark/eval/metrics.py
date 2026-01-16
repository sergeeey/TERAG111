"""
RAGAs Metrics обёртки для TERAG Benchmark
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    )
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    logger.warning("RAGAs not available")


class RAGAsEvaluator:
    """
    Оценщик метрик RAGAs для benchmark
    """
    
    def __init__(self):
        """Инициализация оценщика"""
        if not RAGAS_AVAILABLE:
            raise ImportError("RAGAs not installed. Install with: pip install ragas")
        
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
        
        logger.info("RAGAsEvaluator initialized")
    
    def evaluate(
        self,
        questions: List[str],
        answers: List[str],
        contexts: List[List[str]],
        ground_truths: List[str]
    ) -> Dict[str, float]:
        """
        Оценить результаты pipeline
        
        Args:
            questions: Список вопросов
            answers: Список ответов
            contexts: Список контекстов (каждый элемент - список строк)
            ground_truths: Список правильных ответов
        
        Returns:
            Словарь с метриками
        """
        # Преобразуем контексты в строки
        context_strings = ["\n".join(ctx) if isinstance(ctx, list) else ctx for ctx in contexts]
        
        # Создаем датасет
        dataset = Dataset.from_dict({
            "question": questions,
            "answer": answers,
            "contexts": context_strings,
            "ground_truth": ground_truths
        })
        
        # Оцениваем
        try:
            result = evaluate(
                dataset=dataset,
                metrics=self.metrics
            )
            
            # Извлекаем метрики
            metrics_dict = {}
            for metric_name in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
                if metric_name in result:
                    metrics_dict[metric_name] = float(result[metric_name])
                else:
                    metrics_dict[metric_name] = 0.0
            
            return metrics_dict
            
        except Exception as e:
            logger.error(f"Error in RAGAs evaluation: {e}")
            return {
                "faithfulness": 0.0,
                "answer_relevancy": 0.0,
                "context_precision": 0.0,
                "context_recall": 0.0,
                "error": str(e)
            }
    
    def evaluate_pipeline(
        self,
        pipeline,
        qa_examples: List[Any]
    ) -> Dict[str, Any]:
        """
        Оценить pipeline на датасете
        
        Args:
            pipeline: Pipeline для оценки
            qa_examples: Список примеров QA
        
        Returns:
            Результаты оценки
        """
        questions = []
        answers = []
        contexts = []
        ground_truths = []
        
        logger.info(f"Evaluating pipeline on {len(qa_examples)} examples")
        
        for i, example in enumerate(qa_examples):
            question = example.question if hasattr(example, 'question') else example.get("question", "")
            ground_truth = example.ground_truth if hasattr(example, 'ground_truth') else example.get("ground_truth", example.get("answer", ""))
            
            # Запускаем pipeline
            try:
                result = pipeline.run(question)
                answer = result.get("answer", "")
                context = result.get("context", [])
            except Exception as e:
                logger.error(f"Error running pipeline for question {i}: {e}")
                answer = ""
                context = []
            
            questions.append(question)
            answers.append(answer)
            contexts.append(context if isinstance(context, list) else [context])
            ground_truths.append(ground_truth)
        
        # Оцениваем
        metrics = self.evaluate(questions, answers, contexts, ground_truths)
        
        return {
            "metrics": metrics,
            "num_examples": len(qa_examples),
            "pipeline_name": getattr(pipeline, '__class__', {}).__name__ if hasattr(pipeline, '__class__') else "unknown"
        }









