"""
Когнитивный аудитор для анализа AI-систем
Анализирует метрики RSS/COS/FAITH/Growth/Resonance и когнитивную когерентность
"""

import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import numpy as np

class CognitiveAuditor:
    """Аудитор когнитивных метрик и резонанса"""
    
    def __init__(self, config_path: str = ".auditconfig.yaml"):
        self.config = self._load_config(config_path)
        self.metrics_history = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Загрузка конфигурации аудита"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки конфигурации: {e}")
            return {}
    
    def analyze_cognitive_metrics(self) -> Dict[str, Any]:
        """Анализ когнитивных метрик системы"""
        try:
            # Добавляем src в путь для импорта
            sys.path.append('src')
            
            from core.metrics import get_metrics_snapshot
            from core.health import get_health
            from core.cognitive_resonance import get_phase, phase_alignment_index
            from telemetry.journal import latest
            
            # Получение текущих метрик
            metrics = get_metrics_snapshot()
            health = get_health()
            current_phase = get_phase()
            
            # Анализ истории когнитивных циклов
            cycles = latest(50)  # Последние 50 циклов
            phases = [cycle.get('phase', 0) for cycle in cycles if 'phase' in cycle]
            
            # Расчёт индекса выравнивания фаз
            pai = phase_alignment_index(phases) if phases else 0.0
            
            # Анализ трендов
            rss_values = [cycle.get('RSS', 0) for cycle in cycles if 'RSS' in cycle]
            resonance_values = [cycle.get('Resonance', 0) for cycle in cycles if 'Resonance' in cycle]
            
            # Статистика дрейфа
            rss_drift = np.std(rss_values) if rss_values else 0.0
            resonance_drift = np.std(resonance_values) if resonance_values else 0.0
            
            # Оценка стабильности
            stability_score = self._calculate_stability_score(metrics, health, pai)
            
            # Когнитивная когерентность
            coherence_score = self._calculate_coherence_score(metrics, cycles)
            
            result = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "current_metrics": metrics,
                "health_status": health,
                "phase_analysis": {
                    "current_phase": current_phase,
                    "phase_alignment_index": pai,
                    "phases_analyzed": len(phases)
                },
                "drift_analysis": {
                    "rss_std": float(rss_drift),
                    "resonance_std": float(resonance_drift),
                    "cycles_analyzed": len(cycles)
                },
                "cognitive_scores": {
                    "stability_score": stability_score,
                    "coherence_score": coherence_score,
                    "overall_cognitive_health": (stability_score + coherence_score) / 2
                },
                "thresholds": self.config.get('cognitive_audit', {}).get('thresholds', {}),
                "compliance": self._check_compliance(metrics, health)
            }
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "failed"
            }
    
    def _calculate_stability_score(self, metrics: Dict, health: Dict, pai: float) -> float:
        """Расчёт оценки стабильности когнитивной системы"""
        try:
            # Базовые метрики стабильности
            rss = metrics.get('RSS', 0)
            cos = metrics.get('COS', 0)
            faith = metrics.get('FAITH', 0)
            resonance = metrics.get('Resonance', 0)
            confidence = metrics.get('confidence', 0)
            
            # Веса для разных метрик
            weights = {
                'rss': 0.2,
                'cos': 0.2, 
                'faith': 0.2,
                'resonance': 0.25,
                'confidence': 0.15
            }
            
            # Нормализованные оценки
            scores = {
                'rss': min(rss, 1.0),
                'cos': min(cos, 1.0),
                'faith': min(faith, 1.0),
                'resonance': min(resonance, 1.0),
                'confidence': min(confidence, 1.0)
            }
            
            # Взвешенная сумма
            stability = sum(scores[metric] * weights[metric] for metric in scores)
            
            # Корректировка на PAI
            stability = stability * (0.7 + 0.3 * pai)
            
            # Корректировка на статус здоровья
            health_penalty = {
                'ok': 1.0,
                'warning': 0.9,
                'critical': 0.7
            }.get(health.get('status', 'critical'), 0.7)
            
            return min(stability * health_penalty, 1.0)
            
        except Exception:
            return 0.0
    
    def _calculate_coherence_score(self, metrics: Dict, cycles: List[Dict]) -> float:
        """Расчёт когнитивной когерентности"""
        try:
            if not cycles:
                return 0.0
                
            # Анализ согласованности метрик во времени
            rss_values = [c.get('RSS', 0) for c in cycles if 'RSS' in c]
            resonance_values = [c.get('Resonance', 0) for c in cycles if 'Resonance' in c]
            
            if not rss_values or not resonance_values:
                return 0.0
            
            # Корреляция между метриками
            correlation = np.corrcoef(rss_values, resonance_values)[0, 1]
            correlation_score = max(0, correlation) if not np.isnan(correlation) else 0.0
            
            # Стабильность трендов
            rss_trend = self._calculate_trend_stability(rss_values)
            resonance_trend = self._calculate_trend_stability(resonance_values)
            
            # Общая когерентность
            coherence = (correlation_score * 0.4 + rss_trend * 0.3 + resonance_trend * 0.3)
            
            return min(coherence, 1.0)
            
        except Exception:
            return 0.0
    
    def _calculate_trend_stability(self, values: List[float]) -> float:
        """Расчёт стабильности тренда"""
        if len(values) < 2:
            return 0.0
            
        try:
            # Простой анализ тренда через разности
            diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
            std_diffs = np.std(diffs)
            
            # Стабильность обратно пропорциональна стандартному отклонению
            stability = max(0, 1.0 - min(std_diffs, 1.0))
            return stability
            
        except Exception:
            return 0.0
    
    def _check_compliance(self, metrics: Dict, health: Dict) -> Dict[str, bool]:
        """Проверка соответствия пороговым значениям"""
        thresholds = self.config.get('cognitive_audit', {}).get('thresholds', {})
        
        compliance = {}
        for metric, threshold in thresholds.items():
            if metric in metrics:
                compliance[metric] = metrics[metric] >= threshold
            else:
                compliance[metric] = False
                
        # Дополнительная проверка статуса здоровья
        compliance['health_status'] = health.get('status') == 'ok'
        
        return compliance
    
    def generate_cognitive_report(self, output_path: str = None) -> str:
        """Генерация отчёта о когнитивном состоянии"""
        analysis = self.analyze_cognitive_metrics()
        
        if 'error' in analysis:
            report = f"# ❌ Ошибка когнитивного анализа\n\n{analysis['error']}"
        else:
            scores = analysis['cognitive_scores']
            compliance = analysis['compliance']
            
            # Определение статуса
            overall_score = scores['overall_cognitive_health']
            if overall_score >= 0.8:
                status_icon = "🟢"
                status_text = "Отлично"
            elif overall_score >= 0.6:
                status_icon = "🟡"
                status_text = "Хорошо"
            else:
                status_icon = "🔴"
                status_text = "Требует внимания"
            
            report = f"""# 🧠 Когнитивный аудит TERAG AI-REPS

**Статус:** {status_icon} {status_text}  
**Общая оценка:** {overall_score:.3f}  
**Время анализа:** {analysis['timestamp']}  

## 📊 Текущие метрики
- **RSS:** {analysis['current_metrics']['RSS']:.3f}
- **COS:** {analysis['current_metrics']['COS']:.3f}
- **FAITH:** {analysis['current_metrics']['FAITH']:.3f}
- **Growth:** {analysis['current_metrics']['Growth']:.6f}
- **Resonance:** {analysis['current_metrics']['Resonance']:.3f}
- **Confidence:** {analysis['current_metrics']['confidence']:.3f}

## 🏥 Состояние здоровья
- **Статус:** {analysis['health_status']['status']}
- **Фазовый дрейф:** {analysis['health_status']['resonance_phase_drift']:.3f}

## 🔄 Анализ резонанса
- **Текущая фаза:** {analysis['phase_analysis']['current_phase']:.3f}
- **Индекс выравнивания фаз:** {analysis['phase_analysis']['phase_alignment_index']:.3f}
- **Проанализировано циклов:** {analysis['phase_analysis']['phases_analyzed']}

## 📈 Оценки когнитивности
- **Стабильность:** {scores['stability_score']:.3f}
- **Когерентность:** {scores['coherence_score']:.3f}
- **Общее здоровье:** {scores['overall_cognitive_health']:.3f}

## ✅ Соответствие порогам
"""
            for metric, is_compliant in compliance.items():
                icon = "✅" if is_compliant else "❌"
                report += f"- {icon} {metric}\n"
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report

def main():
    """Основная функция для запуска когнитивного аудита"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Когнитивный аудитор TERAG AI-REPS')
    parser.add_argument('--output', '-o', help='Путь для сохранения отчёта')
    parser.add_argument('--config', '-c', default='.auditconfig.yaml', help='Путь к конфигурации')
    
    args = parser.parse_args()
    
    auditor = CognitiveAuditor(args.config)
    report = auditor.generate_cognitive_report(args.output)
    
    if not args.output:
        print(report)

if __name__ == "__main__":
    main()



































