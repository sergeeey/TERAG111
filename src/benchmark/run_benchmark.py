#!/usr/bin/env python3
"""
TERAG 2.1 Benchmark & Validation
Baseline Proof Cycle - главный скрипт запуска
"""
import argparse
import logging
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импорты компонентов
import os
from datetime import datetime

from src.benchmark.loaders.dataset_loader import DatasetLoader
from src.benchmark.loaders.neo4j_ingest import Neo4jIngester
from src.benchmark.loaders.chroma_ingest import ChromaIngester
from src.benchmark.pipelines.vector_pipeline import VectorRAGPipeline
from src.benchmark.pipelines.graph_pipeline import GraphRAGPipeline
from src.benchmark.pipelines.hybrid_pipeline import HybridRAGPipeline
from src.benchmark.eval.metrics import RAGAsEvaluator
from src.benchmark.eval.report_builder import BenchmarkReportBuilder

# MLflow интеграция
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not available")


def load_config(config_path: str) -> Dict[str, Any]:
    """Загрузить конфигурацию из YAML"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def setup_data_loaders(config: Dict[str, Any]) -> tuple:
    """Настроить загрузчики данных"""
    logger.info("Setting up data loaders...")
    
    # Dataset loader
    data_dir = config.get("data", {}).get("source", "data/processed/")
    dataset_loader = DatasetLoader(data_dir=data_dir)
    
    # Neo4j ingester
    neo4j_config = config.get("retriever", {})
    neo4j_ingester = None
    try:
        neo4j_ingester = Neo4jIngester(
            uri=neo4j_config.get("uri", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
            database=neo4j_config.get("database", "neo4j")
        )
        # Загружаем данные в Neo4j
        neo4j_ingester.ingest_from_graph_results()
    except Exception as e:
        logger.warning(f"Could not setup Neo4j ingester: {e}")
    
    # ChromaDB ingester
    vector_config = config.get("retriever", {})
    chroma_ingester = None
    try:
        chroma_ingester = ChromaIngester(
            collection_name=vector_config.get("collection_name", "terag_documents"),
            embedding_model=vector_config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        )
        # Загружаем данные в ChromaDB
        chroma_ingester.ingest_from_processed()
    except Exception as e:
        logger.warning(f"Could not setup ChromaDB ingester: {e}")
    
    return dataset_loader, neo4j_ingester, chroma_ingester


def create_pipeline(config: Dict[str, Any], pipeline_type: str) -> Any:
    """Создать pipeline по типу"""
    logger.info(f"Creating {pipeline_type} pipeline...")
    
    if pipeline_type == "vector":
        retriever_config = config.get("retriever", {})
        reader_config = config.get("reader", {})
        return VectorRAGPipeline(
            collection_name=retriever_config.get("collection_name", "terag_documents"),
            embedding_model=retriever_config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
            top_k=retriever_config.get("top_k", 5),
            reader_model=reader_config.get("model", "deepset/roberta-base-squad2")
        )
    
    elif pipeline_type == "graph":
        retriever_config = config.get("retriever", {})
        return GraphRAGPipeline(
            uri=retriever_config.get("uri", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
            database=retriever_config.get("database", "neo4j"),
            max_hops=retriever_config.get("max_hops", 3),
            top_k=retriever_config.get("top_k", 5)
        )
    
    elif pipeline_type == "hybrid":
        vector_config = config.get("vector_retriever", {})
        graph_config = config.get("graph_retriever", {})
        router_config = config.get("router", {})
        
        return HybridRAGPipeline(
            vector_config={
                "collection_name": vector_config.get("collection_name", "terag_documents"),
                "embedding_model": vector_config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
                "top_k": vector_config.get("top_k", 3)
            },
            graph_config={
                "uri": graph_config.get("uri", "bolt://localhost:7687"),
                "user": os.getenv("NEO4J_USER", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", "password"),
                "database": graph_config.get("database", "neo4j"),
                "max_hops": graph_config.get("max_hops", 3),
                "top_k": graph_config.get("top_k", 3)
            },
            fusion_strategy=config.get("fusion", {}).get("strategy", "reciprocal_rank_fusion"),
            confidence_threshold=router_config.get("confidence_threshold", 0.7)
        )
    
    else:
        raise ValueError(f"Unknown pipeline type: {pipeline_type}")


def run_benchmark(
    config_path: str,
    pipeline_type: str = "all",
    output_dir: str = "reports"
) -> Dict[str, Any]:
    """
    Запустить benchmark
    
    Args:
        config_path: Путь к конфигурации
        pipeline_type: Тип pipeline (vector, graph, hybrid, all)
        output_dir: Директория для отчетов
    
    Returns:
        Результаты benchmark
    """
    logger.info("=" * 60)
    logger.info("TERAG 2.1 Benchmark & Validation")
    logger.info("Baseline Proof Cycle")
    logger.info("=" * 60)
    
    # Загружаем конфигурацию
    config = load_config(config_path)
    pipeline_name = config.get("pipeline", {}).get("name", "unknown")
    
    # Настраиваем MLflow
    if MLFLOW_AVAILABLE:
        mlflow.set_experiment("TERAG_Benchmark")
        mlflow.start_run(run_name=f"{pipeline_name}_{pipeline_type}")
        mlflow.log_params(config)
    
    try:
        # Настраиваем загрузчики данных
        dataset_loader, neo4j_ingester, chroma_ingester = setup_data_loaders(config)
        
        # Загружаем датасет
        qa_examples = dataset_loader.load_benchmark_dataset()
        logger.info(f"Loaded {len(qa_examples)} QA examples")
        
        # Определяем какие pipeline запускать
        pipeline_types = []
        if pipeline_type == "all":
            pipeline_types = ["vector", "graph", "hybrid"]
        else:
            pipeline_types = [pipeline_type]
        
        all_results = []
        
        # Запускаем каждый pipeline
        for ptype in pipeline_types:
            logger.info(f"\n{'='*60}")
            logger.info(f"Running {ptype.upper()} pipeline")
            logger.info(f"{'='*60}")
            
            # Создаем pipeline
            pipeline = create_pipeline(config, ptype)
            
            # Оцениваем
            evaluator = RAGAsEvaluator()
            result = evaluator.evaluate_pipeline(pipeline, qa_examples)
            result["pipeline_name"] = ptype
            all_results.append(result)
            
            # Логируем в MLflow
            if MLFLOW_AVAILABLE:
                for metric_name, value in result["metrics"].items():
                    mlflow.log_metric(f"{ptype}_{metric_name}", value)
            
            # Создаем отчет
            report_builder = BenchmarkReportBuilder(output_dir=output_dir)
            target_scores = config.get("evaluation", {}).get("target_scores", {})
            report = report_builder.build_report(result, config, target_scores)
            report_path = report_builder.save_report(report)
            
            logger.info(f"Report saved: {report_path}")
            logger.info(f"Metrics: {result['metrics']}")
            
            # Закрываем pipeline
            if hasattr(pipeline, 'close'):
                pipeline.close()
        
        # Сравнительный отчет (если несколько pipeline)
        if len(all_results) > 1:
            report_builder = BenchmarkReportBuilder(output_dir=output_dir)
            comparison = report_builder.build_comparison_report(all_results)
            comparison_path = report_builder.save_report(
                comparison,
                filename="benchmark_comparison.json"
            )
            logger.info(f"Comparison report saved: {comparison_path}")
        
        return {
            "status": "success",
            "results": all_results,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in benchmark: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    
    finally:
        if MLFLOW_AVAILABLE:
            mlflow.end_run()


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="TERAG 2.1 Benchmark & Validation"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="src/benchmark/config/hybrid_rag.yml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--pipeline",
        type=str,
        choices=["vector", "graph", "hybrid", "all"],
        default="all",
        help="Pipeline type to run"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports",
        help="Output directory for reports"
    )
    
    args = parser.parse_args()
    
    # Проверяем существование конфигурации
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    # Запускаем benchmark
    result = run_benchmark(
        config_path=str(config_path),
        pipeline_type=args.pipeline,
        output_dir=args.output
    )
    
    if result["status"] == "error":
        logger.error(f"Benchmark failed: {result.get('error')}")
        sys.exit(1)
    
    logger.info("Benchmark completed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    main()

