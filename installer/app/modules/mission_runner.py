"""
Mission Runner Module
Основной движок для выполнения OSINT-миссий TERAG
"""

import yaml
import os
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import csv

from modules.brave_search import BraveSearchClient
from modules.bright_extractor import BrightDataExtractor
from modules.deepconf_validator import DeepConfValidator
from modules.llm_client import create_llm_client

logger = logging.getLogger(__name__)


class MissionRunner:
    """Движок для выполнения OSINT-миссий"""
    
    def __init__(self, mission_config_path: str, install_path: Optional[str] = None):
        """
        Инициализация движка миссии
        
        Args:
            mission_config_path: Путь к файлу конфигурации миссии (mission.yaml)
            install_path: Путь к установке TERAG (для данных)
        """
        self.install_path = install_path or os.getenv("TERAG_INSTALL_PATH", "E:\\TERAG")
        self.mission_config = self._load_mission_config(mission_config_path)
        self.data_path = Path(self.install_path) / "data"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Инициализация компонентов
        self.brave_client = None
        self.bright_extractor = None
        self.validator = None
        self.llm_client = None
        
        self._initialize_components()
    
    def _load_mission_config(self, config_path: str) -> Dict[str, Any]:
        """Загрузить конфигурацию миссии"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Mission config loaded: {config.get('mission', {}).get('name', 'Unknown')}")
            return config.get('mission', {})
        except Exception as e:
            logger.error(f"Failed to load mission config: {e}")
            return {}
    
    def _initialize_components(self):
        """Инициализировать компоненты миссии"""
        # Brave Search
        if self.mission_config.get('brave_search', {}).get('enabled', False):
            brave_config = self.mission_config.get('brave_search', {})
            api_key = os.getenv("BRAVE_API_KEY") or brave_config.get('api_key', '').replace('${BRAVE_API_KEY}', os.getenv("BRAVE_API_KEY", ""))
            self.brave_client = BraveSearchClient(api_key=api_key)
        
        # Bright Data
        if self.mission_config.get('bright_extraction', {}).get('enabled', False):
            bright_config = self.mission_config.get('bright_extraction', {})
            self.bright_extractor = BrightDataExtractor(
                mcp_server=bright_config.get('mcp_server'),
                api_key=os.getenv("BRIGHT_DATA_API_KEY")
            )
        
        # LLM Client
        self.llm_client = create_llm_client()
        
        # DeepConf Validator
        if self.mission_config.get('deepconf_validation', {}).get('enabled', False):
            validator_config = self.mission_config.get('deepconf_validation', {})
            self.validator = DeepConfValidator(
                llm_client=self.llm_client,
                confidence_threshold=validator_config.get('confidence_threshold', 0.7),
                pemm_enabled=validator_config.get('pemm_enabled', True)
            )
    
    def run_mission(self) -> Dict[str, Any]:
        """
        Запустить полный цикл миссии
        
        Returns:
            Результаты выполнения миссии
        """
        logger.info("=" * 60)
        logger.info(f"Starting mission: {self.mission_config.get('name', 'Unknown')}")
        logger.info("=" * 60)
        
        results = {
            "mission_name": self.mission_config.get('name', 'Unknown'),
            "started_at": datetime.now().isoformat(),
            "components": {},
            "summary": {}
        }
        
        try:
            # 1. Brave Search Sweep
            if 'brave_search' in self.mission_config.get('components', []):
                results['components']['brave_search'] = self._run_brave_search()
            
            # 2. Bright Extraction
            if 'bright_extraction' in self.mission_config.get('components', []):
                results['components']['bright_extraction'] = self._run_bright_extraction(
                    results['components'].get('brave_search', {}).get('urls', [])
                )
            
            # 3. DeepConf Validation
            if 'deepconf_validation' in self.mission_config.get('components', []):
                results['components']['validation'] = self._run_validation(
                    results['components'].get('bright_extraction', {}).get('facts', [])
                )
            
            # 4. Graph-RAG Update
            if 'graph_rag_update' in self.mission_config.get('components', []):
                results['components']['graph_update'] = self._update_graph(
                    results['components'].get('validation', {}).get('validated_facts', [])
                )
            
            # 5. Reasoning Phase
            if 'reasoning_phase' in self.mission_config.get('components', []):
                results['components']['reasoning'] = self._run_reasoning(
                    results['components'].get('graph_update', {})
                )
            
            # 6. Metrics Logging
            if 'metrics_logging' in self.mission_config.get('components', []):
                results['components']['metrics'] = self._log_metrics(results)
            
            # 7. Daily Report
            if 'daily_report' in self.mission_config.get('components', []):
                results['components']['report'] = self._generate_daily_report(results)
            
            results['completed_at'] = datetime.now().isoformat()
            results['status'] = 'completed'
            
            logger.info("=" * 60)
            logger.info("Mission completed successfully!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Mission failed: {e}", exc_info=True)
            results['status'] = 'failed'
            results['error'] = str(e)
        
        return results
    
    def _run_brave_search(self) -> Dict[str, Any]:
        """Выполнить поиск через Brave"""
        logger.info("[1/7] Running Brave Search...")
        
        if not self.brave_client:
            logger.warning("Brave client not initialized")
            return {"error": "Brave client not available"}
        
        topics = self.mission_config.get('topics', [])
        max_queries = self.mission_config.get('brave_search', {}).get('max_queries_per_day', 50)
        
        queries = self.brave_client.generate_search_queries(topics, max_queries)
        search_results = self.brave_client.search_multiple(queries)
        
        # Извлечение URL из результатов
        urls = []
        for result in search_results:
            for item in result.get('results', []):
                urls.append(item.get('url', ''))
        
        logger.info(f"Brave search: {len(search_results)} queries, {len(urls)} URLs found")
        
        return {
            "queries": queries,
            "search_results": search_results,
            "urls": urls,
            "total_urls": len(urls)
        }
    
    def _run_bright_extraction(self, urls: List[str]) -> Dict[str, Any]:
        """Извлечь контент через Bright Data"""
        logger.info("[2/7] Running Bright Extraction...")
        
        if not self.bright_extractor:
            logger.warning("Bright extractor not initialized")
            return {"error": "Bright extractor not available", "facts": []}
        
        if not urls:
            logger.warning("No URLs to extract")
            return {"urls": [], "facts": []}
        
        # Ограничение количества URL
        max_pages = self.mission_config.get('bright_extraction', {}).get('max_pages_per_day', 100)
        urls_to_extract = urls[:max_pages]
        
        extracted_content = self.bright_extractor.extract_multiple(urls_to_extract)
        
        # Извлечение фактов из контента (базовая реализация)
        facts = []
        for content_item in extracted_content:
            if content_item.get('content'):
                entities = self.bright_extractor.extract_entities_from_content(content_item['content'])
                for entity in entities:
                    facts.append({
                        "subject": entity.get('text', ''),
                        "predicate": "mentions",
                        "object": entity.get('type', ''),
                        "source_url": content_item.get('url', ''),
                        "confidence": entity.get('confidence', 0.6)
                    })
        
        logger.info(f"Bright extraction: {len(extracted_content)} pages, {len(facts)} facts extracted")
        
        return {
            "extracted_content": extracted_content,
            "facts": facts,
            "total_facts": len(facts)
        }
    
    def _run_validation(self, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Валидировать факты через DeepConf"""
        logger.info("[3/7] Running DeepConf Validation...")
        
        if not self.validator:
            logger.warning("Validator not initialized")
            return {"error": "Validator not available", "validated_facts": facts}
        
        validated_facts = self.validator.validate_batch(facts)
        
        # Фильтрация по порогу уверенности
        threshold = self.mission_config.get('deepconf_validation', {}).get('confidence_threshold', 0.7)
        high_confidence_facts = [f for f in validated_facts if f.get('confidence', 0.0) >= threshold]
        
        logger.info(f"Validation: {len(validated_facts)} facts validated, {len(high_confidence_facts)} above threshold")
        
        return {
            "validated_facts": validated_facts,
            "high_confidence_facts": high_confidence_facts,
            "total_validated": len(validated_facts),
            "above_threshold": len(high_confidence_facts)
        }
    
    def _update_graph(self, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Обновить граф знаний в Neo4j"""
        logger.info("[4/7] Updating Neo4j Graph...")
        
        # Инициализируем GraphUpdater если ещё не инициализирован
        if not hasattr(self, 'graph_updater') or not self.graph_updater:
            try:
                from installer.app.modules.graph_updater import GraphUpdater
                self.graph_updater = GraphUpdater()
            except Exception as e:
                logger.warning(f"Could not initialize GraphUpdater: {e}")
                self.graph_updater = None
        
        # Если GraphUpdater недоступен, сохраняем в JSON (fallback)
        if not self.graph_updater or not self.graph_updater.driver:
            logger.warning("GraphUpdater not available, saving to JSON only")
            graph_snapshot = {
                "nodes": [],
                "relationships": [],
                "timestamp": datetime.now().isoformat()
            }
            
            for fact in facts:
                graph_snapshot["nodes"].append({
                    "id": fact.get('subject', ''),
                    "type": "entity",
                    "properties": fact
                })
                graph_snapshot["relationships"].append({
                    "from": fact.get('subject', ''),
                    "to": fact.get('object', ''),
                    "type": fact.get('predicate', ''),
                    "properties": {"confidence": fact.get('confidence', 0.0)}
                })
            
            snapshot_path = self.data_path / "graph_snapshot.json"
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                json.dump(graph_snapshot, f, ensure_ascii=False, indent=2)
            
            return {
                "nodes_count": len(graph_snapshot['nodes']),
                "relationships_count": len(graph_snapshot['relationships']),
                "snapshot_path": str(snapshot_path),
                "method": "json_fallback"
            }
        
        # Реальная интеграция с Neo4j
        added_count = 0
        failed_count = 0
        
        for fact in facts:
            source = fact.get('source_url', fact.get('source', ''))
            confidence = fact.get('confidence', 0.7)
            
            # Преобразуем факт в формат для add_fact()
            fact_dict = {
                "subject": fact.get('subject', ''),
                "predicate": fact.get('predicate', 'RELATED_TO'),
                "object": fact.get('object', '')
            }
            
            if self.graph_updater.add_fact(fact_dict, source=source, confidence=confidence):
                added_count += 1
                
                # Отправляем уведомление в Telegram (если доступно)
                try:
                    from src.integration.telegram_service import send_fact_notification_sync
                    send_fact_notification_sync(fact_dict, source=source, confidence=confidence)
                except Exception as e:
                    logger.debug(f"Could not send Telegram notification: {e}")
            else:
                failed_count += 1
        
        logger.info(f"Graph update: {added_count} facts added, {failed_count} failed")
        
        # Получаем статистику графа
        try:
            with self.graph_updater.driver.session() as session:
                nodes_result = session.run("MATCH (n) RETURN count(n) as count")
                nodes_count = nodes_result.single()["count"]
                
                rels_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                rels_count = rels_result.single()["count"]
        except Exception as e:
            logger.warning(f"Could not get graph statistics: {e}")
            nodes_count = None
            rels_count = None
        
        return {
            "nodes_count": nodes_count,
            "relationships_count": rels_count,
            "facts_added": added_count,
            "facts_failed": failed_count,
            "method": "neo4j"
        }
    
    def _run_reasoning(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Фаза рассуждений и выводов"""
        logger.info("[5/7] Running Reasoning Phase...")
        
        if not self.llm_client:
            logger.warning("LLM client not available for reasoning")
            return {"error": "LLM client not available"}
        
        # Генерация инсайтов на основе графа
        reasoning_prompt = f"""Analyze the knowledge graph with {graph_data.get('nodes_count', 0)} nodes and {graph_data.get('relationships_count', 0)} relationships.
Generate:
1. Key insights
2. Anomalies or contradictions
3. Missing connections
4. Recommendations

Provide structured analysis."""
        
        try:
            response = self.llm_client.generate(
                prompt=reasoning_prompt,
                system_prompt="You are a knowledge graph analyst. Provide structured insights.",
                temperature=0.7,
                max_tokens=1000
            )
            
            insights = response.get('response', 'No insights generated')
            
            logger.info("Reasoning phase completed")
            
            return {
                "insights": insights,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Reasoning phase error: {e}")
            return {"error": str(e)}
    
    def _log_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Логировать метрики"""
        logger.info("[6/7] Logging Metrics...")
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "mission_name": results.get('mission_name', 'Unknown'),
            "facts_validated": results.get('components', {}).get('validation', {}).get('total_validated', 0),
            "high_confidence_facts": results.get('components', {}).get('validation', {}).get('above_threshold', 0),
            "graph_nodes": results.get('components', {}).get('graph_update', {}).get('nodes_count', 0),
            "graph_relationships": results.get('components', {}).get('graph_update', {}).get('relationships_count', 0)
        }
        
        # Сохранение метрик в JSONL
        log_path = self.data_path / "mission_log.jsonl"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(metrics, ensure_ascii=False) + '\n')
        
        logger.info("Metrics logged")
        
        return metrics
    
    def _generate_daily_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Сгенерировать ежедневный отчёт"""
        logger.info("[7/7] Generating Daily Report...")
        
        report_path = self.data_path / "daily_summary.md"
        
        report_content = f"""# TERAG Daily Mission Report

**Mission:** {results.get('mission_name', 'Unknown')}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** {results.get('status', 'unknown')}

## Summary

- **Brave Search:** {len(results.get('components', {}).get('brave_search', {}).get('urls', []))} URLs found
- **Bright Extraction:** {results.get('components', {}).get('bright_extraction', {}).get('total_facts', 0)} facts extracted
- **Validation:** {results.get('components', {}).get('validation', {}).get('above_threshold', 0)} high-confidence facts
- **Graph Update:** {results.get('components', {}).get('graph_update', {}).get('nodes_count', 0)} nodes, {results.get('components', {}).get('graph_update', {}).get('relationships_count', 0)} relationships

## Components Status

"""
        
        for component_name, component_data in results.get('components', {}).items():
            status = "✅" if not component_data.get('error') else "❌"
            report_content += f"- **{component_name}:** {status}\n"
        
        report_content += f"""
## Reasoning Insights

{results.get('components', {}).get('reasoning', {}).get('insights', 'No insights generated')}

---
*Generated by TERAG Mission Runner*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Daily report generated: {report_path}")
        
        return {
            "report_path": str(report_path),
            "generated_at": datetime.now().isoformat()
        }






