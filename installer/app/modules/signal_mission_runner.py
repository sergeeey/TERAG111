"""
Signal Mission Runner
Специализированный runner для миссий обнаружения слабых сигналов
"""

import yaml
import os
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from modules.brave_search import BraveSearchClient
from modules.bright_extractor import BrightDataExtractor
from modules.deepconf_validator import DeepConfValidator
from modules.signal_discovery import SignalDiscovery
from modules.graph_updater import GraphUpdater
from modules.reflection import MissionReflection
from modules.llm_client import create_llm_client

logger = logging.getLogger(__name__)


class SignalMissionRunner:
    """Специализированный runner для миссий обнаружения сигналов"""
    
    def __init__(self, mission_config_path: str, install_path: Optional[str] = None):
        """
        Инициализация runner для сигналов
        
        Args:
            mission_config_path: Путь к конфигурации миссии
            install_path: Путь установки TERAG
        """
        self.install_path = install_path or os.getenv("TERAG_INSTALL_PATH", "E:\\TERAG")
        self.mission_config = self._load_mission_config(mission_config_path)
        self.data_path = Path(self.install_path) / "data"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Инициализация компонентов
        self.brave_client = None
        self.bright_extractor = None
        self.validator = None
        self.signal_discovery = None
        self.graph_updater = None
        self.reflection = None
        self.llm_client = None
        
        self._initialize_components()
    
    def _load_mission_config(self, config_path: str) -> Dict[str, Any]:
        """Загрузить конфигурацию миссии"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Signal mission config loaded: {config.get('mission', {}).get('name', 'Unknown')}")
            return config.get('mission', {})
        except Exception as e:
            logger.error(f"Failed to load mission config: {e}")
            return {}
    
    def _initialize_components(self):
        """Инициализировать компоненты"""
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
        
        # Signal Discovery
        if self.mission_config.get('signal_extraction', {}).get('enabled', False):
            signal_config = self.mission_config.get('signal_extraction', {})
            self.signal_discovery = SignalDiscovery(
                llm_client=self.llm_client,
                novelty_threshold=signal_config.get('novelty_threshold', 0.7),
                min_confidence=signal_config.get('min_confidence', 0.6)
            )
        
        # DeepConf Validator
        if self.mission_config.get('deepconf_validation', {}).get('enabled', False):
            validator_config = self.mission_config.get('deepconf_validation', {})
            self.validator = DeepConfValidator(
                llm_client=self.llm_client,
                confidence_threshold=validator_config.get('confidence_threshold', 0.65),
                pemm_enabled=validator_config.get('pemm_enabled', True)
            )
        
        # Graph Updater
        if self.mission_config.get('graph_rag', {}).get('enabled', False):
            graph_config = self.mission_config.get('graph_rag', {})
            self.graph_updater = GraphUpdater(
                uri=graph_config.get('neo4j_uri', os.getenv("NEO4J_URI", "bolt://neo4j:7687")),
                user=graph_config.get('neo4j_user', os.getenv("NEO4J_USER", "neo4j")),
                password=graph_config.get('neo4j_password', os.getenv("NEO4J_PASSWORD", "terag_local"))
            )
        
        # Reflection Module
        self.reflection = MissionReflection(llm_client=self.llm_client)
    
    def run_mission(self) -> Dict[str, Any]:
        """
        Запустить миссию обнаружения сигналов
        
        Returns:
            Результаты выполнения миссии
        """
        logger.info("=" * 60)
        logger.info(f"Starting Signal Discovery Mission: {self.mission_config.get('name', 'Unknown')}")
        logger.info("=" * 60)
        
        results = {
            "mission_name": self.mission_config.get('name', 'Unknown'),
            "mission_type": "signals",
            "started_at": datetime.now().isoformat(),
            "components": {},
            "discoveries": [],
            "summary": {}
        }
        
        try:
            # 1. Brave Search - поиск по темам
            logger.info("[1/8] Running Brave Search for signals...")
            search_results = self._run_brave_search()
            results['components']['brave_search'] = search_results
            
            # 2. Bright Extraction - извлечение контента
            logger.info("[2/8] Extracting content from URLs...")
            urls = search_results.get('urls', [])
            extraction_results = self._run_bright_extraction(urls)
            results['components']['bright_extraction'] = extraction_results
            
            # 3. Signal Extraction - извлечение новых концептов
            logger.info("[3/8] Extracting novel concepts and signals...")
            extracted_content = extraction_results.get('extracted_content', [])
            signal_results = self._run_signal_extraction(extracted_content)
            results['components']['signal_extraction'] = signal_results
            
            # 4. DeepConf Validation - валидация сигналов
            logger.info("[4/8] Validating signals with DeepConf...")
            discoveries = signal_results.get('discoveries', [])
            validation_results = self._run_validation(discoveries)
            results['components']['validation'] = validation_results
            
            # 5. Novelty Analysis - анализ новизны
            logger.info("[5/8] Analyzing novelty and trends...")
            validated_discoveries = validation_results.get('validated_discoveries', [])
            novelty_results = self._run_novelty_analysis(validated_discoveries)
            results['components']['novelty_analysis'] = novelty_results
            
            # 6. Graph Update - запись в Neo4j
            logger.info("[6/8] Updating knowledge graph...")
            graph_results = self._update_graph(validated_discoveries)
            results['components']['graph_update'] = graph_results
            
            # 7. Reasoning Phase - генерация инсайтов
            logger.info("[7/8] Running reasoning phase...")
            reasoning_results = self._run_reasoning(graph_results, validated_discoveries)
            results['components']['reasoning'] = reasoning_results
            
            # 8. Metrics & Report
            logger.info("[8/9] Logging metrics and generating report...")
            metrics_results = self._log_metrics(results)
            results['components']['metrics'] = metrics_results
            
            report_results = self._generate_discovery_report(results)
            results['components']['report'] = report_results
            
            # 9. Post-Mission Reflection
            logger.info("[9/9] Generating post-mission reflection...")
            reflection_results = self._run_reflection(validated_discoveries, results)
            results['components']['reflection'] = reflection_results
            
            results['discoveries'] = validated_discoveries
            results['completed_at'] = datetime.now().isoformat()
            results['status'] = 'completed'
            
            logger.info("=" * 60)
            logger.info("Signal Discovery Mission completed successfully!")
            logger.info(f"Total discoveries: {len(validated_discoveries)}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Mission failed: {e}", exc_info=True)
            results['status'] = 'failed'
            results['error'] = str(e)
        finally:
            if self.graph_updater:
                self.graph_updater.close()
        
        return results
    
    def _run_brave_search(self) -> Dict[str, Any]:
        """Выполнить поиск через Brave"""
        if not self.brave_client:
            return {"error": "Brave client not available", "urls": []}
        
        topics = self.mission_config.get('topics', [])
        max_queries = self.mission_config.get('brave_search', {}).get('max_queries_per_day', 100)
        
        queries = self.brave_client.generate_search_queries(topics, max_queries)
        search_results = self.brave_client.search_multiple(queries)
        
        # Фильтрация по годам и источникам
        filters = self.mission_config.get('search_filters', {})
        min_year = filters.get('min_year', 2024)
        
        urls = []
        for result in search_results:
            for item in result.get('results', []):
                url = item.get('url', '')
                # Фильтрация по источникам
                sources = filters.get('sources', [])
                if any(source in url for source in sources):
                    urls.append(url)
        
        logger.info(f"Brave search: {len(search_results)} queries, {len(urls)} filtered URLs")
        
        return {
            "queries": queries,
            "search_results": search_results,
            "urls": urls,
            "total_urls": len(urls)
        }
    
    def _run_bright_extraction(self, urls: List[str]) -> Dict[str, Any]:
        """Извлечь контент через Bright Data"""
        if not self.bright_extractor:
            return {"error": "Bright extractor not available", "extracted_content": []}
        
        max_pages = self.mission_config.get('bright_extraction', {}).get('max_pages_per_day', 200)
        urls_to_extract = urls[:max_pages]
        
        extracted_content = self.bright_extractor.extract_multiple(urls_to_extract)
        
        logger.info(f"Bright extraction: {len(extracted_content)} pages extracted")
        
        return {
            "extracted_content": extracted_content,
            "total_pages": len(extracted_content)
        }
    
    def _run_signal_extraction(self, extracted_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Извлечь сигналы и новые концепты"""
        if not self.signal_discovery:
            return {"error": "Signal discovery not available", "discoveries": []}
        
        all_discoveries = []
        
        for content_item in extracted_content:
            text = content_item.get('content', '')
            url = content_item.get('url', '')
            
            if text:
                # Извлечение концептов
                concepts = self.signal_discovery.extract_novel_concepts(
                    text, 
                    source_url=url,
                    metadata={
                        'content_type': content_item.get('content_type', ''),
                        'extracted_at': content_item.get('extracted_at', '')
                    }
                )
                
                all_discoveries.extend(concepts)
        
        # Обнаружение слабых сигналов
        existing_concepts = []
        if self.graph_updater:
            existing_concepts = self.graph_updater.get_existing_concepts()
        
        weak_signals = self.signal_discovery.detect_weak_signals(
            all_discoveries,
            existing_concepts=existing_concepts
        )
        
        logger.info(f"Signal extraction: {len(all_discoveries)} concepts, {len(weak_signals)} weak signals")
        
        return {
            "discoveries": all_discoveries,
            "weak_signals": weak_signals,
            "total_concepts": len(all_discoveries),
            "total_signals": len(weak_signals)
        }
    
    def _run_validation(self, discoveries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Валидировать открытия через DeepConf"""
        if not self.validator:
            return {"error": "Validator not available", "validated_discoveries": discoveries}
        
        # Преобразование в формат фактов для валидации
        facts = []
        for discovery in discoveries:
            facts.append({
                'subject': discovery.get('name', ''),
                'predicate': 'is_a',
                'object': discovery.get('type', 'concept'),
                'description': discovery.get('description', ''),
                'domain': discovery.get('domain', 'unknown')
            })
        
        validated_facts = self.validator.validate_batch(facts)
        
        # Объединение с оригинальными данными
        validated_discoveries = []
        for i, fact in enumerate(validated_facts):
            if i < len(discoveries):
                discovery = discoveries[i].copy()
                discovery['confidence_ratio'] = fact.get('confidence', 0.0)
                discovery['validated'] = fact.get('validated', False)
                discovery['validation_reasoning'] = fact.get('reasoning', '')
                validated_discoveries.append(discovery)
        
        # Фильтрация по порогу уверенности
        threshold = self.mission_config.get('deepconf_validation', {}).get('confidence_threshold', 0.65)
        high_confidence = [
            d for d in validated_discoveries 
            if d.get('confidence_ratio', 0.0) >= threshold
        ]
        
        logger.info(f"Validation: {len(validated_discoveries)} validated, {len(high_confidence)} above threshold")
        
        return {
            "validated_discoveries": validated_discoveries,
            "high_confidence_discoveries": high_confidence,
            "total_validated": len(validated_discoveries),
            "above_threshold": len(high_confidence)
        }
    
    def _run_novelty_analysis(self, discoveries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ новизны и трендов"""
        if not self.signal_discovery:
            return {"error": "Signal discovery not available"}
        
        trends = self.signal_discovery.analyze_trends(discoveries, time_period="weekly")
        
        # Сохранение индекса новизны
        novelty_index_path = self.data_path / "novelty_index.json"
        with open(novelty_index_path, 'w', encoding='utf-8') as f:
            json.dump(trends, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Novelty analysis: {trends.get('total_concepts', 0)} concepts analyzed")
        
        return trends
    
    def _update_graph(self, discoveries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Обновить граф знаний в Neo4j"""
        if not self.graph_updater:
            logger.warning("Graph updater not available, skipping graph update")
            return {"error": "Graph updater not available", "inserted": 0}
        
        stats = self.graph_updater.batch_insert_discoveries(discoveries)
        
        logger.info(f"Graph update: {stats['success']}/{stats['total']} discoveries inserted")
        
        return {
            "inserted": stats['success'],
            "failed": stats['failed'],
            "total": stats['total']
        }
    
    def _run_reasoning(self, graph_results: Dict[str, Any], 
                      discoveries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Фаза рассуждений"""
        if not self.llm_client:
            return {"error": "LLM client not available"}
        
        reasoning_prompt = f"""Analyze {len(discoveries)} new discoveries inserted into the knowledge graph.
Key discoveries:
{json.dumps([d.get('name', '') for d in discoveries[:10]], ensure_ascii=False, indent=2)}

Generate:
1. Key insights about emerging patterns
2. Potential applications or monetization opportunities
3. Anomalies or contradictions
4. Recommendations for further research

Provide structured analysis."""
        
        try:
            response = self.llm_client.generate(
                prompt=reasoning_prompt,
                system_prompt="You are a knowledge graph analyst specializing in weak signals and emerging concepts.",
                temperature=0.7,
                max_tokens=1500
            )
            
            insights = response.get('response', 'No insights generated')
            
            return {
                "insights": insights,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Reasoning phase error: {e}")
            return {"error": str(e)}
    
    def _log_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Логировать метрики"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "mission_name": results.get('mission_name', 'Unknown'),
            "discoveries_total": len(results.get('discoveries', [])),
            "weak_signals": results.get('components', {}).get('signal_extraction', {}).get('total_signals', 0),
            "validated_discoveries": results.get('components', {}).get('validation', {}).get('total_validated', 0),
            "graph_inserted": results.get('components', {}).get('graph_update', {}).get('inserted', 0)
        }
        
        # Сохранение в JSONL
        log_path = self.data_path / "signals_mission_log.jsonl"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(metrics, ensure_ascii=False) + '\n')
        
        return metrics
    
    def _generate_discovery_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Сгенерировать отчёт об открытиях"""
        report_path = self.data_path / "discoveries_report.md"
        
        discoveries = results.get('discoveries', [])
        weak_signals = results.get('components', {}).get('signal_extraction', {}).get('weak_signals', [])
        
        report_content = f"""# TERAG Discovery Report

**Mission:** {results.get('mission_name', 'Unknown')}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** {results.get('status', 'unknown')}

## Summary

- **Total Discoveries:** {len(discoveries)}
- **Weak Signals:** {len(weak_signals)}
- **Validated:** {results.get('components', {}).get('validation', {}).get('above_threshold', 0)}
- **Graph Inserted:** {results.get('components', {}).get('graph_update', {}).get('inserted', 0)}

## Top Discoveries

"""
        
        # Сортировка по novelty_index
        sorted_discoveries = sorted(
            discoveries,
            key=lambda x: x.get('novelty_index', 0.0),
            reverse=True
        )[:20]
        
        for i, discovery in enumerate(sorted_discoveries, 1):
            report_content += f"""
### {i}. {discovery.get('name', 'Unknown')}

- **Domain:** {discovery.get('domain', 'unknown')}
- **Type:** {discovery.get('type', 'concept')}
- **Novelty Index:** {discovery.get('novelty_index', 0.0):.2f}
- **Confidence:** {discovery.get('confidence_ratio', discovery.get('confidence', 0.0)):.2f}
- **Source:** {discovery.get('source_url', 'N/A')[:80]}

{discovery.get('description', 'No description')[:200]}

"""
        
        # Weak Signals
        if weak_signals:
            report_content += "\n## Weak Signals Detected\n\n"
            for signal in weak_signals[:10]:
                report_content += f"- **{signal.get('name', 'Unknown')}** (strength: {signal.get('signal_strength', 0.0):.2f})\n"
        
        # Reasoning Insights
        insights = results.get('components', {}).get('reasoning', {}).get('insights', '')
        if insights:
            report_content += f"\n## Reasoning Insights\n\n{insights}\n"
        
        report_content += "\n---\n*Generated by TERAG Signal Discovery Mission*\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Discovery report generated: {report_path}")
        
        return {
            "report_path": str(report_path),
            "generated_at": datetime.now().isoformat()
        }
    
    def _run_reflection(self, discoveries: List[Dict[str, Any]], 
                       results: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнить пост-миссионную рефлексию"""
        if not self.reflection:
            return {"error": "Reflection module not available"}
        
        reflection = self.reflection.generate_reflection(discoveries, results)
        
        # Сохранение отчёта рефлексии
        reflection_path = self.data_path / "daily_reflection.md"
        saved_path = self.reflection.save_reflection_report(reflection, str(reflection_path))
        
        logger.info(f"Reflection generated and saved: {saved_path}")
        
        return {
            "reflection": reflection,
            "report_path": saved_path,
            "generated_at": datetime.now().isoformat()
        }

