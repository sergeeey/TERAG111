"""
Post-Mission Reflection Module
Этап рефлексии после миссии для генерации осмысленных отчётов о найденных открытиях
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MissionReflection:
    """Класс для генерации рефлексивных отчётов после миссии"""
    
    def __init__(self, llm_client=None):
        """
        Инициализация модуля рефлексии
        
        Args:
            llm_client: Клиент LLM для генерации отчётов
        """
        self.llm_client = llm_client
    
    def generate_reflection(self, discoveries: List[Dict[str, Any]], 
                          mission_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Сгенерировать рефлексивный отчёт о миссии
        
        Args:
            discoveries: Список обнаруженных открытий
            mission_results: Результаты выполнения миссии
            
        Returns:
            Словарь с рефлексивным отчётом
        """
        logger.info("Generating post-mission reflection...")
        
        # Анализ открытий
        analysis = self._analyze_discoveries(discoveries)
        
        # Генерация текста рефлексии через LLM
        reflection_text = self._generate_reflection_text(discoveries, analysis, mission_results)
        
        # Выявление ключевых инсайтов
        key_insights = self._extract_key_insights(discoveries, analysis)
        
        # Рекомендации для следующих миссий
        recommendations = self._generate_recommendations(discoveries, analysis)
        
        reflection = {
            "generated_at": datetime.now().isoformat(),
            "mission_name": mission_results.get('mission_name', 'Unknown'),
            "total_discoveries": len(discoveries),
            "analysis": analysis,
            "reflection_text": reflection_text,
            "key_insights": key_insights,
            "recommendations": recommendations,
            "summary": self._generate_summary(discoveries, analysis)
        }
        
        logger.info("Reflection generated successfully")
        return reflection
    
    def _analyze_discoveries(self, discoveries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ открытий для выявления паттернов"""
        if not discoveries:
            return {
                "total": 0,
                "domains": {},
                "avg_novelty": 0.0,
                "avg_confidence": 0.0,
                "top_domains": [],
                "high_novelty_count": 0
            }
        
        # Статистика по доменам
        domain_stats = {}
        novelty_sum = 0.0
        confidence_sum = 0.0
        high_novelty_count = 0
        
        for discovery in discoveries:
            domain = discovery.get('domain', 'unknown')
            novelty = discovery.get('novelty_index', 0.0)
            confidence = discovery.get('confidence_ratio', discovery.get('confidence', 0.0))
            
            if domain not in domain_stats:
                domain_stats[domain] = {
                    'count': 0,
                    'novelty_sum': 0.0,
                    'confidence_sum': 0.0,
                    'high_novelty': 0
                }
            
            domain_stats[domain]['count'] += 1
            domain_stats[domain]['novelty_sum'] += novelty
            domain_stats[domain]['confidence_sum'] += confidence
            if novelty >= 0.8:
                domain_stats[domain]['high_novelty'] += 1
                high_novelty_count += 1
            
            novelty_sum += novelty
            confidence_sum += confidence
        
        # Вычисление средних
        total = len(discoveries)
        avg_novelty = novelty_sum / total if total > 0 else 0.0
        avg_confidence = confidence_sum / total if total > 0 else 0.0
        
        # Топ домены по количеству открытий
        top_domains = sorted(
            domain_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:5]
        
        return {
            "total": total,
            "domains": domain_stats,
            "avg_novelty": avg_novelty,
            "avg_confidence": avg_confidence,
            "top_domains": [d[0] for d in top_domains],
            "high_novelty_count": high_novelty_count,
            "high_novelty_percent": (high_novelty_count / total * 100) if total > 0 else 0.0
        }
    
    def _generate_reflection_text(self, discoveries: List[Dict[str, Any]], 
                                 analysis: Dict[str, Any],
                                 mission_results: Dict[str, Any]) -> str:
        """Генерировать текстовый отчёт рефлексии через LLM"""
        if not self.llm_client:
            return self._generate_simple_reflection(discoveries, analysis)
        
        try:
            # Подготовка данных для LLM
            top_discoveries = sorted(
                discoveries,
                key=lambda x: x.get('novelty_index', 0.0),
                reverse=True
            )[:10]
            
            discoveries_summary = []
            for d in top_discoveries:
                discoveries_summary.append({
                    "name": d.get('name', 'Unknown'),
                    "domain": d.get('domain', 'unknown'),
                    "novelty": d.get('novelty_index', 0.0),
                    "confidence": d.get('confidence_ratio', d.get('confidence', 0.0)),
                    "description": d.get('description', '')[:200]
                })
            
            system_prompt = """You are a cognitive knowledge analyst reflecting on discoveries made during an OSINT mission.
Your task is to generate a thoughtful, insightful reflection report that:
1. Summarizes what new knowledge was discovered
2. Identifies emerging patterns and trends
3. Highlights the most significant findings
4. Provides context about why these discoveries matter
5. Suggests potential implications

Write in a clear, analytical style. Focus on insights, not just facts."""
            
            prompt = f"""Generate a reflection report on discoveries made during a knowledge discovery mission.

Mission Results:
- Total discoveries: {analysis.get('total', 0)}
- Average novelty index: {analysis.get('avg_novelty', 0.0):.2f}
- Average confidence: {analysis.get('avg_confidence', 0.0):.2f}
- Top domains: {', '.join(analysis.get('top_domains', []))}
- High novelty discoveries: {analysis.get('high_novelty_count', 0)}

Top Discoveries:
{json.dumps(discoveries_summary, ensure_ascii=False, indent=2)}

Generate a comprehensive reflection report (300-500 words) covering:
1. What was discovered (summary)
2. Emerging patterns and trends
3. Most significant findings and why they matter
4. Potential implications and future directions

Return the reflection as a well-structured text."""
            
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            reflection_text = response.get('response', '')
            
            if not reflection_text or len(reflection_text) < 100:
                # Fallback к простой рефлексии
                return self._generate_simple_reflection(discoveries, analysis)
            
            return reflection_text
            
        except Exception as e:
            logger.warning(f"LLM reflection generation failed: {e}")
            return self._generate_simple_reflection(discoveries, analysis)
    
    def _generate_simple_reflection(self, discoveries: List[Dict[str, Any]],
                                   analysis: Dict[str, Any]) -> str:
        """Простая рефлексия без LLM"""
        reflection = f"""## Mission Reflection Summary

During this mission, {analysis.get('total', 0)} new discoveries were identified across {len(analysis.get('domains', {}))} domains.

### Key Statistics
- Average novelty index: {analysis.get('avg_novelty', 0.0):.2f}
- Average confidence: {analysis.get('avg_confidence', 0.0):.2f}
- High novelty discoveries: {analysis.get('high_novelty_count', 0)} ({analysis.get('high_novelty_percent', 0.0):.1f}%)

### Top Domains
"""
        for domain in analysis.get('top_domains', [])[:5]:
            domain_stats = analysis.get('domains', {}).get(domain, {})
            reflection += f"- **{domain}**: {domain_stats.get('count', 0)} discoveries\n"
        
        reflection += f"""
### Most Novel Discoveries

"""
        top_novel = sorted(
            discoveries,
            key=lambda x: x.get('novelty_index', 0.0),
            reverse=True
        )[:5]
        
        for i, d in enumerate(top_novel, 1):
            reflection += f"{i}. **{d.get('name', 'Unknown')}** (novelty: {d.get('novelty_index', 0.0):.2f}, domain: {d.get('domain', 'unknown')})\n"
        
        return reflection
    
    def _extract_key_insights(self, discoveries: List[Dict[str, Any]], 
                             analysis: Dict[str, Any]) -> List[str]:
        """Извлечь ключевые инсайты"""
        insights = []
        
        # Инсайт 1: Растущие домены
        top_domains = analysis.get('top_domains', [])
        if top_domains:
            insights.append(f"Emerging domain: {top_domains[0]} shows highest activity with {analysis.get('domains', {}).get(top_domains[0], {}).get('count', 0)} discoveries")
        
        # Инсайт 2: Высокая новизна
        high_novelty_pct = analysis.get('high_novelty_percent', 0.0)
        if high_novelty_pct > 30:
            insights.append(f"High novelty rate: {high_novelty_pct:.1f}% of discoveries have novelty index ≥ 0.8, indicating strong signal strength")
        
        # Инсайт 3: Средняя уверенность
        avg_confidence = analysis.get('avg_confidence', 0.0)
        if avg_confidence >= 0.7:
            insights.append(f"Strong validation: Average confidence {avg_confidence:.2f} indicates reliable discoveries")
        elif avg_confidence < 0.5:
            insights.append(f"Validation needed: Average confidence {avg_confidence:.2f} suggests need for additional verification")
        
        # Инсайт 4: Уникальные концепты
        unique_domains = len(analysis.get('domains', {}))
        if unique_domains > 5:
            insights.append(f"Diverse discovery: {unique_domains} different domains discovered, showing broad knowledge expansion")
        
        return insights
    
    def _generate_recommendations(self, discoveries: List[Dict[str, Any]],
                                 analysis: Dict[str, Any]) -> List[str]:
        """Сгенерировать рекомендации для следующих миссий"""
        recommendations = []
        
        # Рекомендация 1: Фокус на растущих доменах
        top_domains = analysis.get('top_domains', [])
        if top_domains:
            recommendations.append(f"Focus future missions on: {', '.join(top_domains[:3])} - these domains show highest discovery potential")
        
        # Рекомендация 2: Углубление в высокоуверенные открытия
        high_confidence_count = sum(
            1 for d in discoveries 
            if d.get('confidence_ratio', d.get('confidence', 0.0)) >= 0.8
        )
        if high_confidence_count > 0:
            recommendations.append(f"Deep dive recommended: {high_confidence_count} high-confidence discoveries warrant deeper investigation")
        
        # Рекомендация 3: Валидация низкоуверенных
        low_confidence_count = sum(
            1 for d in discoveries 
            if d.get('confidence_ratio', d.get('confidence', 0.0)) < 0.5
        )
        if low_confidence_count > 0:
            recommendations.append(f"Validation needed: {low_confidence_count} discoveries have low confidence and require cross-validation")
        
        # Рекомендация 4: Баланс доменов
        domain_counts = [stats.get('count', 0) for stats in analysis.get('domains', {}).values()]
        if domain_counts and max(domain_counts) / sum(domain_counts) > 0.5:
            recommendations.append("Diversify search topics: Current missions are too focused on one domain, consider broadening search scope")
        
        return recommendations
    
    def _generate_summary(self, discoveries: List[Dict[str, Any]], 
                         analysis: Dict[str, Any]) -> str:
        """Сгенерировать краткое резюме"""
        return f"""Mission completed successfully. Discovered {analysis.get('total', 0)} new concepts across {len(analysis.get('domains', {}))} domains. 
Average novelty: {analysis.get('avg_novelty', 0.0):.2f}, average confidence: {analysis.get('avg_confidence', 0.0):.2f}.
Top domains: {', '.join(analysis.get('top_domains', [])[:3])}."""
    
    def save_reflection_report(self, reflection: Dict[str, Any], output_path: str) -> str:
        """
        Сохранить отчёт рефлексии в файл
        
        Args:
            reflection: Словарь с рефлексией
            output_path: Путь для сохранения
            
        Returns:
            Путь к сохранённому файлу
        """
        from pathlib import Path
        
        report_path = Path(output_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_content = f"""# TERAG Mission Reflection Report

**Mission:** {reflection.get('mission_name', 'Unknown')}
**Generated:** {reflection.get('generated_at', 'Unknown')}
**Total Discoveries:** {reflection.get('total_discoveries', 0)}

## Executive Summary

{reflection.get('summary', 'No summary available')}

## Key Insights

"""
        for i, insight in enumerate(reflection.get('key_insights', []), 1):
            report_content += f"{i}. {insight}\n"
        
        report_content += f"""
## Reflection

{reflection.get('reflection_text', 'No reflection available')}

## Recommendations for Future Missions

"""
        for i, rec in enumerate(reflection.get('recommendations', []), 1):
            report_content += f"{i}. {rec}\n"
        
        report_content += f"""
## Analysis Details

- **Total Discoveries:** {reflection.get('analysis', {}).get('total', 0)}
- **Average Novelty Index:** {reflection.get('analysis', {}).get('avg_novelty', 0.0):.2f}
- **Average Confidence:** {reflection.get('analysis', {}).get('avg_confidence', 0.0):.2f}
- **High Novelty Discoveries:** {reflection.get('analysis', {}).get('high_novelty_count', 0)} ({reflection.get('analysis', {}).get('high_novelty_percent', 0.0):.1f}%)

### Domain Distribution

"""
        for domain, stats in reflection.get('analysis', {}).get('domains', {}).items():
            report_content += f"- **{domain}**: {stats.get('count', 0)} discoveries, avg novelty: {stats.get('novelty_sum', 0.0) / max(stats.get('count', 1), 1):.2f}\n"
        
        report_content += "\n---\n*Generated by TERAG Mission Reflection System*\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Reflection report saved: {report_path}")
        return str(report_path)


















