"""
Модуль анализа наблюдаемости и дрейфа AI-систем
Отслеживает изменения в поведении системы и предупреждает о дрейфе
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from collections import deque

class ObservabilityAuditor:
    """Аудитор наблюдаемости и дрейфа системы"""
    
    def __init__(self, config_path: str = ".auditconfig.yaml"):
        self.config = self._load_config(config_path)
        self.drift_threshold = 0.1  # Порог для детекции дрейфа
        self.window_size = 50  # Размер окна для анализа
        
    def _load_config(self, config_path: str) -> Dict:
        """Загрузка конфигурации"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки конфигурации: {e}")
            return {}
    
    def analyze_drift(self, cycles: List[Dict]) -> Dict[str, Any]:
        """Анализ дрейфа в когнитивных циклах"""
        if not cycles:
            return {"error": "Нет данных для анализа дрейфа"}
        
        try:
            # Извлечение метрик
            metrics_data = self._extract_metrics(cycles)
            
            # Анализ дрейфа для каждой метрики
            drift_analysis = {}
            for metric, values in metrics_data.items():
                if len(values) < 2:
                    continue
                    
                drift_analysis[metric] = self._calculate_drift(values)
            
            # Общий индекс дрейфа
            overall_drift = self._calculate_overall_drift(drift_analysis)
            
            # Детекция аномалий
            anomalies = self._detect_anomalies(metrics_data)
            
            # Анализ трендов
            trends = self._analyze_trends(metrics_data)
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cycles_analyzed": len(cycles),
                "drift_analysis": drift_analysis,
                "overall_drift_index": overall_drift,
                "anomalies": anomalies,
                "trends": trends,
                "drift_status": self._classify_drift_status(overall_drift),
                "recommendations": self._generate_recommendations(overall_drift, anomalies)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _extract_metrics(self, cycles: List[Dict]) -> Dict[str, List[float]]:
        """Извлечение метрик из циклов"""
        metrics = {
            'RSS': [],
            'COS': [],
            'FAITH': [],
            'Growth': [],
            'Resonance': [],
            'confidence': [],
            'phase': []
        }
        
        for cycle in cycles:
            for metric in metrics.keys():
                if metric in cycle and cycle[metric] is not None:
                    metrics[metric].append(float(cycle[metric]))
        
        return metrics
    
    def _calculate_drift(self, values: List[float]) -> Dict[str, float]:
        """Расчёт дрейфа для одной метрики"""
        if len(values) < 2:
            return {"drift": 0.0, "std": 0.0, "trend": 0.0}
        
        try:
            values_array = np.array(values)
            
            # Стандартное отклонение
            std_dev = float(np.std(values_array))
            
            # Линейный тренд
            x = np.arange(len(values))
            trend_slope = float(np.polyfit(x, values_array, 1)[0])
            
            # Дрейф как комбинация изменчивости и тренда
            drift = std_dev + abs(trend_slope) * len(values)
            
            # Нормализация дрейфа
            normalized_drift = min(drift, 1.0)
            
            return {
                "drift": normalized_drift,
                "std": std_dev,
                "trend": trend_slope,
                "min": float(np.min(values_array)),
                "max": float(np.max(values_array)),
                "mean": float(np.mean(values_array))
            }
            
        except Exception as e:
            return {"error": str(e), "drift": 0.0}
    
    def _calculate_overall_drift(self, drift_analysis: Dict[str, Dict]) -> float:
        """Расчёт общего индекса дрейфа"""
        if not drift_analysis:
            return 0.0
        
        # Веса для разных метрик
        weights = {
            'RSS': 0.2,
            'COS': 0.2,
            'FAITH': 0.2,
            'Resonance': 0.25,
            'confidence': 0.15
        }
        
        weighted_drift = 0.0
        total_weight = 0.0
        
        for metric, analysis in drift_analysis.items():
            if 'drift' in analysis and not isinstance(analysis['drift'], str):
                weight = weights.get(metric, 0.1)
                weighted_drift += analysis['drift'] * weight
                total_weight += weight
        
        return weighted_drift / total_weight if total_weight > 0 else 0.0
    
    def _detect_anomalies(self, metrics_data: Dict[str, List[float]]) -> List[Dict[str, Any]]:
        """Детекция аномалий в метриках"""
        anomalies = []
        
        for metric, values in metrics_data.items():
            if len(values) < 3:
                continue
                
            try:
                values_array = np.array(values)
                
                # Z-score аномалии
                z_scores = np.abs((values_array - np.mean(values_array)) / np.std(values_array))
                anomaly_indices = np.where(z_scores > 2.0)[0]
                
                for idx in anomaly_indices:
                    anomalies.append({
                        "metric": metric,
                        "index": int(idx),
                        "value": float(values_array[idx]),
                        "z_score": float(z_scores[idx]),
                        "severity": "high" if z_scores[idx] > 3.0 else "medium"
                    })
                    
            except Exception:
                continue
        
        return anomalies
    
    def _analyze_trends(self, metrics_data: Dict[str, List[float]]) -> Dict[str, str]:
        """Анализ трендов в метриках"""
        trends = {}
        
        for metric, values in metrics_data.items():
            if len(values) < 3:
                trends[metric] = "insufficient_data"
                continue
                
            try:
                x = np.arange(len(values))
                slope = np.polyfit(x, values, 1)[0]
                
                if slope > 0.01:
                    trends[metric] = "increasing"
                elif slope < -0.01:
                    trends[metric] = "decreasing"
                else:
                    trends[metric] = "stable"
                    
            except Exception:
                trends[metric] = "error"
        
        return trends
    
    def _classify_drift_status(self, overall_drift: float) -> str:
        """Классификация статуса дрейфа"""
        if overall_drift < 0.1:
            return "stable"
        elif overall_drift < 0.3:
            return "moderate_drift"
        else:
            return "high_drift"
    
    def _generate_recommendations(self, overall_drift: float, anomalies: List[Dict]) -> List[str]:
        """Генерация рекомендаций на основе анализа"""
        recommendations = []
        
        if overall_drift > 0.3:
            recommendations.append("🔴 Критический дрейф: требуется немедленная стабилизация системы")
        elif overall_drift > 0.1:
            recommendations.append("🟡 Умеренный дрейф: рекомендуется мониторинг и корректировка")
        
        if len(anomalies) > 5:
            recommendations.append("⚠️ Обнаружено много аномалий: проверьте стабильность входных данных")
        
        high_severity_anomalies = [a for a in anomalies if a.get('severity') == 'high']
        if high_severity_anomalies:
            recommendations.append("🚨 Критические аномалии: требуется детальный анализ")
        
        if not recommendations:
            recommendations.append("✅ Система стабильна, продолжайте мониторинг")
        
        return recommendations
    
    def check_observability(self) -> Dict[str, Any]:
        """Проверка общей наблюдаемости системы"""
        try:
            # Добавляем src в путь
            sys.path.append('src')
            
            from telemetry.journal import latest
            from core.metrics import get_metrics_snapshot
            
            # Получение данных
            cycles = latest(100)  # Последние 100 циклов
            current_metrics = get_metrics_snapshot()
            
            # Анализ дрейфа
            drift_analysis = self.analyze_drift(cycles)
            
            # Проверка полноты логирования
            logging_completeness = self._check_logging_completeness(cycles)
            
            # Проверка доступности метрик
            metrics_availability = self._check_metrics_availability(current_metrics)
            
            # Общая оценка наблюдаемости
            observability_score = self._calculate_observability_score(
                drift_analysis, logging_completeness, metrics_availability
            )
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "observability_score": observability_score,
                "drift_analysis": drift_analysis,
                "logging_completeness": logging_completeness,
                "metrics_availability": metrics_availability,
                "status": self._classify_observability_status(observability_score),
                "recommendations": self._generate_observability_recommendations(observability_score)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "failed"
            }
    
    def _check_logging_completeness(self, cycles: List[Dict]) -> Dict[str, Any]:
        """Проверка полноты логирования"""
        if not cycles:
            return {"completeness": 0.0, "missing_fields": []}
        
        required_fields = ['RSS', 'COS', 'FAITH', 'Resonance', 'timestamp']
        field_counts = {field: 0 for field in required_fields}
        
        for cycle in cycles:
            for field in required_fields:
                if field in cycle and cycle[field] is not None:
                    field_counts[field] += 1
        
        total_cycles = len(cycles)
        completeness = sum(field_counts.values()) / (len(required_fields) * total_cycles)
        
        missing_fields = [field for field, count in field_counts.items() 
                         if count < total_cycles * 0.8]
        
        return {
            "completeness": completeness,
            "missing_fields": missing_fields,
            "field_coverage": {field: count/total_cycles for field, count in field_counts.items()}
        }
    
    def _check_metrics_availability(self, metrics: Dict) -> Dict[str, Any]:
        """Проверка доступности метрик"""
        required_metrics = ['RSS', 'COS', 'FAITH', 'Growth', 'Resonance', 'confidence']
        available_metrics = [metric for metric in required_metrics if metric in metrics]
        
        availability = len(available_metrics) / len(required_metrics)
        
        return {
            "availability": availability,
            "available_metrics": available_metrics,
            "missing_metrics": [m for m in required_metrics if m not in metrics]
        }
    
    def _calculate_observability_score(self, drift_analysis: Dict, logging_completeness: Dict, 
                                     metrics_availability: Dict) -> float:
        """Расчёт общей оценки наблюдаемости"""
        # Веса компонентов
        drift_weight = 0.4
        logging_weight = 0.3
        metrics_weight = 0.3
        
        # Оценка дрейфа (обратная зависимость)
        drift_score = 1.0 - min(drift_analysis.get('overall_drift_index', 0.5), 1.0)
        
        # Оценка логирования
        logging_score = logging_completeness.get('completeness', 0.0)
        
        # Оценка доступности метрик
        metrics_score = metrics_availability.get('availability', 0.0)
        
        # Взвешенная сумма
        observability_score = (
            drift_score * drift_weight +
            logging_score * logging_weight +
            metrics_score * metrics_weight
        )
        
        return min(observability_score, 1.0)
    
    def _classify_observability_status(self, score: float) -> str:
        """Классификация статуса наблюдаемости"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _generate_observability_recommendations(self, score: float) -> List[str]:
        """Генерация рекомендаций по наблюдаемости"""
        recommendations = []
        
        if score < 0.4:
            recommendations.append("🔴 Критически низкая наблюдаемость: требуется полная реструктуризация мониторинга")
        elif score < 0.6:
            recommendations.append("🟡 Низкая наблюдаемость: улучшите логирование и мониторинг")
        elif score < 0.8:
            recommendations.append("🟢 Хорошая наблюдаемость: продолжайте улучшения")
        else:
            recommendations.append("✅ Отличная наблюдаемость: система хорошо контролируется")
        
        return recommendations

def main():
    """Основная функция для запуска анализа наблюдаемости"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Анализ наблюдаемости TERAG AI-REPS')
    parser.add_argument('--output', '-o', help='Путь для сохранения отчёта')
    parser.add_argument('--config', '-c', default='.auditconfig.yaml', help='Путь к конфигурации')
    
    args = parser.parse_args()
    
    auditor = ObservabilityAuditor(args.config)
    result = auditor.check_observability()
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()



































