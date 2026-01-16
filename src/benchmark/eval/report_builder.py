"""
Report Builder для TERAG Benchmark
Генерирует отчеты с результатами оценки
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BenchmarkReportBuilder:
    """
    Построитель отчетов для benchmark
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Инициализация построителя
        
        Args:
            output_dir: Директория для сохранения отчетов
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"BenchmarkReportBuilder initialized: {output_dir}")
    
    def build_report(
        self,
        results: Dict[str, Any],
        config: Dict[str, Any],
        target_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Построить отчет
        
        Args:
            results: Результаты оценки
            config: Конфигурация pipeline
            target_scores: Целевые значения метрик
        
        Returns:
            Отчет
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "pipeline": config.get("pipeline", {}).get("name", "unknown"),
            "config": config,
            "results": results,
            "target_scores": target_scores,
            "summary": {}
        }
        
        # Анализ результатов
        metrics = results.get("metrics", {})
        summary = {}
        
        for metric_name, target_value in target_scores.items():
            actual_value = metrics.get(metric_name, 0.0)
            passed = actual_value >= target_value
            summary[metric_name] = {
                "target": target_value,
                "actual": actual_value,
                "passed": passed,
                "difference": actual_value - target_value
            }
        
        report["summary"] = summary
        
        # Общий статус
        all_passed = all(s["passed"] for s in summary.values())
        report["status"] = "PASSED" if all_passed else "FAILED"
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """
        Сохранить отчет в файл
        
        Args:
            report: Отчет
            filename: Имя файла (опционально)
        
        Returns:
            Путь к сохраненному файлу
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pipeline_name = report.get("pipeline", {}).get("name", "unknown")
            filename = f"benchmark_{pipeline_name}_{timestamp}.json"
        
        file_path = self.output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Report saved: {file_path}")
        return file_path
    
    def build_comparison_report(
        self,
        pipeline_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Построить сравнительный отчет для всех pipeline
        
        Args:
            pipeline_results: Список результатов для каждого pipeline
        
        Returns:
            Сравнительный отчет
        """
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "pipelines": [],
            "comparison": {}
        }
        
        # Собираем метрики для каждого pipeline
        for result in pipeline_results:
            pipeline_name = result.get("pipeline_name", "unknown")
            metrics = result.get("metrics", {})
            
            comparison["pipelines"].append({
                "name": pipeline_name,
                "metrics": metrics
            })
        
        # Сравнение метрик
        metric_names = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        comparison_metrics = {}
        
        for metric_name in metric_names:
            values = {}
            for result in pipeline_results:
                pipeline_name = result.get("pipeline_name", "unknown")
                metrics = result.get("metrics", {})
                values[pipeline_name] = metrics.get(metric_name, 0.0)
            
            # Находим лучший
            best_pipeline = max(values.items(), key=lambda x: x[1])
            
            comparison_metrics[metric_name] = {
                "values": values,
                "best": best_pipeline[0],
                "best_score": best_pipeline[1]
            }
        
        comparison["comparison"] = comparison_metrics
        
        return comparison

