"""
Модуль агрегации результатов аудита
Собирает все результаты аудита в единый отчёт с общими метриками и рекомендациями
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import glob

class AuditAggregator:
    """Агрегатор результатов аудита"""
    
    def __init__(self, report_dir: str):
        self.report_dir = report_dir
        self.aggregated_results = {}
        
    def aggregate_all_results(self) -> Dict[str, Any]:
        """Агрегация всех результатов аудита"""
        try:
            # Сбор всех JSON отчётов
            json_files = glob.glob(os.path.join(self.report_dir, "**/*.json"), recursive=True)
            
            # Загрузка результатов
            results = {}
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    filename = os.path.basename(json_file).replace('.json', '')
                    results[filename] = data
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки {json_file}: {e}")
            
            # Агрегация по категориям
            aggregated = {
                "metadata": self._create_metadata(),
                "cognitive_audit": self._aggregate_cognitive_results(results),
                "observability_audit": self._aggregate_observability_results(results),
                "ethics_audit": self._aggregate_ethics_results(results),
                "governance_audit": self._aggregate_governance_results(results),
                "environment_audit": self._aggregate_environment_results(results),
                "architecture_audit": self._aggregate_architecture_results(results),
                "technical_audit": self._aggregate_technical_results(results),
                "overall_assessment": self._calculate_overall_assessment(results)
            }
            
            return aggregated
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "failed"
            }
    
    def _create_metadata(self) -> Dict[str, Any]:
        """Создание метаданных аудита"""
        return {
            "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            "audit_version": "1.2",
            "project_name": "TERAG-AI-REPS",
            "report_directory": self.report_dir,
            "aggregation_method": "weighted_average"
        }
    
    def _aggregate_cognitive_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Агрегация результатов когнитивного аудита"""
        cognitive_data = results.get('cognitive_metrics', {})
        
        if 'error' in cognitive_data:
            return {
                "status": "failed",
                "error": cognitive_data['error'],
                "score": 0.0
            }
        
        cognitive_scores = cognitive_data.get('cognitive_scores', {})
        current_metrics = cognitive_data.get('current_metrics', {})
        health_status = cognitive_data.get('health_status', {})
        
        return {
            "status": "completed",
            "overall_cognitive_health": cognitive_scores.get('overall_cognitive_health', 0.0),
            "stability_score": cognitive_scores.get('stability_score', 0.0),
            "coherence_score": cognitive_scores.get('coherence_score', 0.0),
            "current_metrics": current_metrics,
            "health_status": health_status.get('status', 'unknown'),
            "phase_drift": health_status.get('resonance_phase_drift', 0.0),
            "compliance": cognitive_data.get('compliance', {}),
            "recommendations": self._extract_cognitive_recommendations(cognitive_data)
        }
    
    def _aggregate_observability_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Агрегация результатов аудита наблюдаемости"""
        observability_data = results.get('observability', {})
        drift_data = results.get('drift_analysis', {})
        
        if 'error' in observability_data:
            return {
                "status": "failed",
                "error": observability_data['error'],
                "score": 0.0
            }
        
        return {
            "status": "completed",
            "observability_score": observability_data.get('observability_score', 0.0),
            "overall_drift_index": drift_data.get('overall_drift_index', 0.0),
            "drift_status": drift_data.get('drift_status', 'unknown'),
            "anomalies_count": len(drift_data.get('anomalies', [])),
            "trends": drift_data.get('trends', {}),
            "recommendations": self._extract_observability_recommendations(observability_data, drift_data)
        }
    
    def _aggregate_ethics_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Агрегация результатов этического аудита"""
        ethics_data = results.get('ethics_audit', {})
        
        if 'error' in ethics_data:
            return {
                "status": "failed",
                "error": ethics_data['error'],
                "score": 0.0
            }
        
        return {
            "status": "completed",
            "overall_ethical_score": ethics_data.get('overall_ethical_score', 0.0),
            "ethical_status": ethics_data.get('ethical_status', 'unknown'),
            "documentation_score": ethics_data.get('documentation_audit', {}).get('documentation_score', 0.0),
            "code_ethics_score": ethics_data.get('code_audit', {}).get('overall_code_ethics_score', 0.0),
            "privacy_score": self._calculate_privacy_score(ethics_data.get('privacy_audit', {})),
            "recommendations": ethics_data.get('recommendations', [])
        }
    
    def _aggregate_environment_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Агрегация результатов environment-аудита"""
        env_data = results.get('cursor_env', {})
        
        if 'error' in env_data:
            return {
                "status": "failed",
                "error": env_data['error'],
                "score": 0.0
            }
        
        return {
            "status": "completed",
            "environment_score": env_data.get('environment_score', 0.0),
            "environment_status": env_data.get('status', 'unknown'),
            "total_issues": env_data.get('total_issues', 0),
            "total_recommendations": env_data.get('total_recommendations', 0),
            "workspace_consistency": env_data.get('checks', {}).get('workspace_consistency', {}),
            "mcp_integrations": env_data.get('checks', {}).get('mcp_integrations', {}),
            "project_structure": env_data.get('checks', {}).get('project_structure', {}),
            "recommendations": env_data.get('all_recommendations', [])
        }
    
    def _aggregate_architecture_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Агрегация результатов архитектурного аудита"""
        arch_data = results.get('architecture_audit', {})
        
        if 'error' in arch_data:
            return {
                "status": "failed",
                "error": arch_data['error'],
                "score": 0.0
            }
        
        return {
            "status": "completed",
            "architecture_score": arch_data.get('architecture_score', 0.0),
            "sections_found": arch_data.get('sections_found', 0),
            "sections_expected": arch_data.get('sections_expected', 0),
            "total_modules": arch_data.get('total_modules', 0),
            "code_analysis": arch_data.get('code_analysis', {}),
            "component_coverage": arch_data.get('component_coverage', {}),
            "issues": arch_data.get('issues', []),
            "recommendations": arch_data.get('recommendations', [])
        }
    
    def _aggregate_governance_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Агрегация результатов управленческого аудита"""
        governance_data = results.get('governance_audit', {})
        
        if 'error' in governance_data:
            return {
                "status": "failed",
                "error": governance_data['error'],
                "score": 0.0
            }
        
        return {
            "status": "completed",
            "overall_governance_score": governance_data.get('overall_governance_score', 0.0),
            "governance_status": governance_data.get('governance_status', 'unknown'),
            "mission_alignment": governance_data.get('mission_audit', {}).get('alignment_score', 0.0),
            "policy_coverage": governance_data.get('policies_audit', {}).get('policy_coverage', 0.0),
            "compliance_score": governance_data.get('compliance_audit', {}).get('compliance_score', 0.0),
            "continuity_score": governance_data.get('continuity_audit', {}).get('continuity_score', 0.0),
            "recommendations": governance_data.get('recommendations', [])
        }
    
    def _aggregate_technical_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Агрегация технических результатов аудита"""
        technical_results = {
            "code_quality": self._analyze_code_quality(results),
            "security": self._analyze_security(results),
            "performance": self._analyze_performance(results),
            "coverage": self._analyze_coverage(results)
        }
        
        return technical_results
    
    def _analyze_code_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ качества кода"""
        pylint_data = results.get('pylint', {})
        flake8_data = results.get('flake8', {})
        
        return {
            "pylint_score": self._extract_pylint_score(pylint_data),
            "flake8_issues": self._count_flake8_issues(flake8_data),
            "overall_quality": "good" if self._extract_pylint_score(pylint_data) > 7.0 else "needs_improvement"
        }
    
    def _analyze_security(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ безопасности"""
        bandit_data = results.get('bandit', {})
        safety_data = results.get('safety', {})
        
        return {
            "bandit_issues": self._count_bandit_issues(bandit_data),
            "safety_issues": self._count_safety_issues(safety_data),
            "security_level": self._assess_security_level(bandit_data, safety_data)
        }
    
    def _analyze_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ производительности"""
        perf_data = results.get('performance', {})
        
        return {
            "benchmarks_available": len(perf_data) > 0,
            "performance_data": perf_data,
            "performance_level": "good" if len(perf_data) > 0 else "unknown"
        }
    
    def _analyze_coverage(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ покрытия кода"""
        coverage_data = results.get('coverage', {})
        
        return {
            "coverage_available": len(coverage_data) > 0,
            "coverage_data": coverage_data,
            "coverage_level": "good" if len(coverage_data) > 0 else "unknown"
        }
    
    def _calculate_overall_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Расчёт общей оценки системы"""
        # Веса для разных аспектов
        weights = {
            'cognitive': 0.2,
            'observability': 0.15,
            'ethics': 0.15,
            'governance': 0.15,
            'environment': 0.15,
            'architecture': 0.15,
            'technical': 0.05
        }
        
        # Сбор оценок
        scores = {}
        
        # Когнитивная оценка
        cognitive_data = results.get('cognitive_metrics', {})
        if 'error' not in cognitive_data:
            scores['cognitive'] = cognitive_data.get('cognitive_scores', {}).get('overall_cognitive_health', 0.0)
        else:
            scores['cognitive'] = 0.0
        
        # Оценка наблюдаемости
        observability_data = results.get('observability', {})
        if 'error' not in observability_data:
            scores['observability'] = observability_data.get('observability_score', 0.0)
        else:
            scores['observability'] = 0.0
        
        # Этическая оценка
        ethics_data = results.get('ethics_audit', {})
        if 'error' not in ethics_data:
            scores['ethics'] = ethics_data.get('overall_ethical_score', 0.0)
        else:
            scores['ethics'] = 0.0
        
        # Управленческая оценка
        governance_data = results.get('governance_audit', {})
        if 'error' not in governance_data:
            scores['governance'] = governance_data.get('overall_governance_score', 0.0)
        else:
            scores['governance'] = 0.0
        
        # Environment-оценка
        env_data = results.get('cursor_env', {})
        if 'error' not in env_data:
            scores['environment'] = env_data.get('environment_score', 0.0)
        else:
            scores['environment'] = 0.0
        
        # Архитектурная оценка
        arch_data = results.get('architecture_audit', {})
        if 'error' not in arch_data:
            scores['architecture'] = arch_data.get('architecture_score', 0.0)
        else:
            scores['architecture'] = 0.0
        
        # Техническая оценка (упрощённая)
        technical_score = 0.5  # Базовый балл
        if results.get('pylint'):
            technical_score += 0.2
        if results.get('bandit'):
            technical_score += 0.2
        if results.get('coverage'):
            technical_score += 0.1
        scores['technical'] = min(technical_score, 1.0)
        
        # Взвешенная сумма
        overall_score = sum(scores[aspect] * weights[aspect] for aspect in weights)
        
        # Классификация статуса
        if overall_score >= 0.8:
            status = "excellent"
            status_icon = "🟢"
        elif overall_score >= 0.6:
            status = "good"
            status_icon = "🟡"
        elif overall_score >= 0.4:
            status = "fair"
            status_icon = "🟠"
        else:
            status = "poor"
            status_icon = "🔴"
        
        return {
            "overall_score": overall_score,
            "status": status,
            "status_icon": status_icon,
            "component_scores": scores,
            "weights": weights,
            "recommendations": self._generate_overall_recommendations(scores, overall_score)
        }
    
    def _generate_overall_recommendations(self, scores: Dict[str, float], overall_score: float) -> List[str]:
        """Генерация общих рекомендаций"""
        recommendations = []
        
        # Рекомендации по компонентам с низкими оценками
        for component, score in scores.items():
            if score < 0.5:
                if component == 'cognitive':
                    recommendations.append("🧠 Улучшите когнитивную стабильность: оптимизируйте метрики RSS/COS/FAITH")
                elif component == 'observability':
                    recommendations.append("👁️ Улучшите наблюдаемость: добавьте мониторинг и логирование")
                elif component == 'ethics':
                    recommendations.append("⚖️ Улучшите этическое соответствие: добавьте политики и процедуры")
                elif component == 'governance':
                    recommendations.append("🏛️ Улучшите управление: определите роли и процессы")
                elif component == 'technical':
                    recommendations.append("🔧 Улучшите техническое качество: исправьте ошибки кода и безопасности")
        
        # Общие рекомендации
        if overall_score < 0.6:
            recommendations.append("🚨 Критический уровень: требуется комплексная реструктуризация системы")
        elif overall_score < 0.8:
            recommendations.append("⚠️ Умеренный уровень: продолжайте улучшения по всем направлениям")
        else:
            recommendations.append("✅ Отличный уровень: поддерживайте текущее качество и продолжайте мониторинг")
        
        return recommendations
    
    def _extract_cognitive_recommendations(self, cognitive_data: Dict) -> List[str]:
        """Извлечение рекомендаций из когнитивного аудита"""
        # Простые рекомендации на основе метрик
        recommendations = []
        
        current_metrics = cognitive_data.get('current_metrics', {})
        if current_metrics.get('RSS', 0) < 0.8:
            recommendations.append("📊 Улучшите RSS: оптимизируйте стабильность рассуждений")
        if current_metrics.get('Resonance', 0) < 0.85:
            recommendations.append("🔄 Улучшите Resonance: стабилизируйте фазовый резонанс")
        
        return recommendations
    
    def _extract_observability_recommendations(self, observability_data: Dict, drift_data: Dict) -> List[str]:
        """Извлечение рекомендаций из аудита наблюдаемости"""
        recommendations = []
        
        if observability_data.get('observability_score', 0) < 0.6:
            recommendations.append("👁️ Улучшите наблюдаемость системы")
        
        if drift_data.get('overall_drift_index', 0) > 0.3:
            recommendations.append("📈 Высокий дрейф: стабилизируйте поведение системы")
        
        return recommendations
    
    def _calculate_privacy_score(self, privacy_audit: Dict) -> float:
        """Расчёт оценки приватности"""
        if not privacy_audit:
            return 0.0
        
        scores = []
        
        # Оценка сбора данных
        data_collection = privacy_audit.get('data_collection', {})
        if data_collection.get('minimal_collection') and data_collection.get('purpose_limitation'):
            scores.append(0.8)
        else:
            scores.append(0.4)
        
        # Оценка хранения данных
        data_storage = privacy_audit.get('data_storage', {})
        if data_storage.get('local_storage') and data_storage.get('retention_policy'):
            scores.append(0.6)
        else:
            scores.append(0.3)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _extract_pylint_score(self, pylint_data: Dict) -> float:
        """Извлечение оценки Pylint"""
        if not pylint_data or not isinstance(pylint_data, list):
            return 0.0
        
        # Поиск оценки в данных Pylint
        for item in pylint_data:
            if isinstance(item, dict) and 'score' in item:
                return float(item['score'])
        
        return 0.0
    
    def _count_flake8_issues(self, flake8_data: Dict) -> int:
        """Подсчёт проблем Flake8"""
        if not flake8_data or not isinstance(flake8_data, list):
            return 0
        
        return len(flake8_data)
    
    def _count_bandit_issues(self, bandit_data: Dict) -> int:
        """Подсчёт проблем Bandit"""
        if not bandit_data or not isinstance(bandit_data, dict):
            return 0
        
        results = bandit_data.get('results', [])
        return len(results) if isinstance(results, list) else 0
    
    def _count_safety_issues(self, safety_data: Dict) -> int:
        """Подсчёт проблем Safety"""
        if not safety_data or not isinstance(safety_data, list):
            return 0
        
        return len(safety_data)
    
    def _assess_security_level(self, bandit_data: Dict, safety_data: Dict) -> str:
        """Оценка уровня безопасности"""
        bandit_issues = self._count_bandit_issues(bandit_data)
        safety_issues = self._count_safety_issues(safety_data)
        
        total_issues = bandit_issues + safety_issues
        
        if total_issues == 0:
            return "excellent"
        elif total_issues <= 5:
            return "good"
        elif total_issues <= 10:
            return "fair"
        else:
            return "poor"
    
    def generate_final_report(self, output_path: str = None) -> str:
        """Генерация финального отчёта"""
        aggregated = self.aggregate_all_results()
        
        if 'error' in aggregated:
            report = f"# ❌ Ошибка агрегации аудита\n\n{aggregated['error']}"
        else:
            overall = aggregated['overall_assessment']
            
            report = f"""# 🧭 Auditor CurSor v1.2 - Финальный отчёт аудита

**Проект:** TERAG AI-REPS  
**Время аудита:** {aggregated['metadata']['audit_timestamp']}  
**Общая оценка:** {overall['status_icon']} {overall['overall_score']:.3f} ({overall['status']})  

## 📊 Сводка по компонентам

### 🧠 Когнитивный аудит
- **Статус:** {'✅' if aggregated['cognitive_audit']['status'] == 'completed' else '❌'}
- **Общее здоровье:** {aggregated['cognitive_audit']['overall_cognitive_health']:.3f}
- **Стабильность:** {aggregated['cognitive_audit']['stability_score']:.3f}
- **Когерентность:** {aggregated['cognitive_audit']['coherence_score']:.3f}

### 👁️ Наблюдаемость
- **Статус:** {'✅' if aggregated['observability_audit']['status'] == 'completed' else '❌'}
- **Оценка наблюдаемости:** {aggregated['observability_audit']['observability_score']:.3f}
- **Индекс дрейфа:** {aggregated['observability_audit']['overall_drift_index']:.3f}
- **Аномалии:** {aggregated['observability_audit']['anomalies_count']}

### ⚖️ Этический аудит
- **Статус:** {'✅' if aggregated['ethics_audit']['status'] == 'completed' else '❌'}
- **Этическая оценка:** {aggregated['ethics_audit']['overall_ethical_score']:.3f}
- **Документация:** {aggregated['ethics_audit']['documentation_score']:.3f}
- **Код:** {aggregated['ethics_audit']['code_ethics_score']:.3f}

### 🏛️ Управленческий аудит
- **Статус:** {'✅' if aggregated['governance_audit']['status'] == 'completed' else '❌'}
- **Управленческая оценка:** {aggregated['governance_audit']['overall_governance_score']:.3f}
- **Выравнивание миссии:** {aggregated['governance_audit']['mission_alignment']:.3f}
- **Покрытие политик:** {aggregated['governance_audit']['policy_coverage']:.3f}

### 🔧 Environment-аудит
- **Статус:** {'✅' if aggregated['environment_audit']['status'] == 'completed' else '❌'}
- **Environment-оценка:** {aggregated['environment_audit']['environment_score']:.3f}
- **Проблемы окружения:** {aggregated['environment_audit']['total_issues']}
- **Рекомендаций:** {aggregated['environment_audit']['total_recommendations']}

### 🧩 Architecture-аудит
- **Статус:** {'✅' if aggregated['architecture_audit']['status'] == 'completed' else '❌'}
- **Architecture-оценка:** {aggregated['architecture_audit']['architecture_score']:.3f}
- **Секций найдено:** {aggregated['architecture_audit']['sections_found']}/{aggregated['architecture_audit']['sections_expected']}
- **Модулей проанализировано:** {aggregated['architecture_audit']['total_modules']}
- **Проблем архитектуры:** {len(aggregated['architecture_audit']['issues'])}

### 🔧 Технический аудит
- **Качество кода:** {aggregated['technical_audit']['code_quality']['overall_quality']}
- **Безопасность:** {aggregated['technical_audit']['security']['security_level']}
- **Производительность:** {aggregated['technical_audit']['performance']['performance_level']}
- **Покрытие:** {aggregated['technical_audit']['coverage']['coverage_level']}

## 🎯 Ключевые рекомендации

"""
            
            for i, rec in enumerate(overall['recommendations'], 1):
                report += f"{i}. {rec}\n"
            
            report += f"""

## 📈 Детальные оценки компонентов

"""
            
            for component, score in overall['component_scores'].items():
                icon = "🟢" if score >= 0.8 else "🟡" if score >= 0.6 else "🟠" if score >= 0.4 else "🔴"
                report += f"- {icon} **{component.title()}:** {score:.3f}\n"
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report

def main():
    """Основная функция для запуска агрегации"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Агрегация результатов аудита TERAG AI-REPS')
    parser.add_argument('report_dir', help='Директория с отчётами аудита')
    parser.add_argument('--output', '-o', help='Путь для сохранения финального отчёта')
    
    args = parser.parse_args()
    
    aggregator = AuditAggregator(args.report_dir)
    report = aggregator.generate_final_report(args.output)
    
    if not args.output:
        print(report)

if __name__ == "__main__":
    main()
