"""
OSINT Digest Generator
Генерирует ежедневный дайджест с топ сигналами и трендами
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter

logger = logging.getLogger(__name__)

try:
    from installer.app.modules.graph_updater import GraphUpdater
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False
    logger.warning("GraphUpdater not available, digest will use file-based sources only")


class OSINTDigestGenerator:
    """Генератор OSINT-дайджеста для ежедневных отчётов"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.missions_dir = Path("missions")
        self.signals_file = self.data_dir / "weak_signals.json"
        self.discoveries_file = self.data_dir / "discoveries_report.md"
        self.graph_updater = None
        
        if GRAPH_AVAILABLE:
            try:
                self.graph_updater = GraphUpdater()
                if not self.graph_updater.driver:
                    self.graph_updater = None
            except Exception as e:
                logger.warning(f"Could not initialize GraphUpdater: {e}")
                self.graph_updater = None
    
    def get_recent_signals_from_graph(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить последние сигналы из графа знаний"""
        if not self.graph_updater or not self.graph_updater.driver:
            return []
        
        try:
            with self.graph_updater.driver.session() as session:
                # Запрос последних сигналов за N дней
                query = """
                MATCH (s:Signal)
                WHERE s.discovered_at >= datetime() - duration({days: $days})
                RETURN s
                ORDER BY s.novelty_index DESC, s.confidence_ratio DESC
                LIMIT $limit
                """
                result = session.run(query, {"days": days, "limit": limit})
                
                signals = []
                for record in result:
                    node = record["s"]
                    signals.append({
                        "name": node.get("name", "Unknown"),
                        "novelty_index": node.get("novelty_index", 0.0),
                        "confidence": node.get("confidence_ratio", 0.0),
                        "source_url": node.get("source_url", ""),
                        "discovered_at": node.get("discovered_at", ""),
                        "description": node.get("description", "")
                    })
                
                return signals
        except Exception as e:
            logger.error(f"Error getting signals from graph: {e}")
            return []
    
    def get_recent_signals_from_files(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить последние сигналы из файлов"""
        signals = []
        
        # Читаем weak_signals.json если существует
        if self.signals_file.exists():
            try:
                with open(self.signals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        signals.extend(data)
                    elif isinstance(data, dict) and "signals" in data:
                        signals.extend(data["signals"])
            except Exception as e:
                logger.warning(f"Could not read signals file: {e}")
        
        # Фильтруем по дате и сортируем
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_signals = []
        
        for signal in signals:
            extracted_at = signal.get("extracted_at", signal.get("discovered_at", ""))
            if extracted_at:
                try:
                    # Пробуем разные форматы даты
                    signal_date = None
                    try:
                        signal_date = datetime.fromisoformat(extracted_at.replace('Z', '+00:00'))
                    except:
                        try:
                            # Формат без времени
                            signal_date = datetime.strptime(extracted_at[:10], "%Y-%m-%d")
                        except:
                            pass
                    
                    if signal_date:
                        # Сравниваем только дату (без времени)
                        if signal_date.date() >= cutoff_date.date():
                            recent_signals.append(signal)
                    else:
                        # Если не удалось распарсить, включаем (может быть новым)
                        recent_signals.append(signal)
                except:
                    # Если ошибка при парсинге, включаем сигнал
                    recent_signals.append(signal)
            else:
                # Если нет даты, включаем (может быть новым)
                recent_signals.append(signal)
        
        # Если нет сигналов с корректной датой, но есть сигналы вообще - используем все
        if not recent_signals and signals:
            recent_signals = signals
        
        # Сортируем по novelty_index и confidence
        recent_signals.sort(
            key=lambda x: (
                x.get("novelty_index", 0.0),
                x.get("confidence", 0.0)
            ),
            reverse=True
        )
        
        return recent_signals[:limit]
    
    def get_top_signals(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Получить топ сигналы (из графа или файлов)"""
        # Пробуем получить из графа
        signals = self.get_recent_signals_from_graph(days=7, limit=limit * 2)
        
        # Если недостаточно, дополняем из файлов
        if len(signals) < limit:
            file_signals = self.get_recent_signals_from_files(days=7, limit=limit * 2)
            # Объединяем и дедуплицируем
            existing_names = {s.get("name", "") for s in signals}
            for sig in file_signals:
                if sig.get("name", "") not in existing_names:
                    signals.append(sig)
                    existing_names.add(sig.get("name", ""))
        
        # Сортируем и возвращаем топ
        signals.sort(
            key=lambda x: (
                x.get("novelty_index", 0.0),
                x.get("confidence", 0.0)
            ),
            reverse=True
        )
        
        return signals[:limit]
    
    def analyze_trends(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ трендов на основе сигналов"""
        if not signals:
            return {
                "trends": [],
                "domains": [],
                "avg_novelty": 0.0,
                "avg_confidence": 0.0
            }
        
        # Извлекаем домены из source_url
        domains = []
        for signal in signals:
            url = signal.get("source_url", "")
            if url:
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    if domain:
                        domains.append(domain)
                except:
                    pass
        
        domain_counter = Counter(domains)
        top_domains = [domain for domain, _ in domain_counter.most_common(3)]
        
        # Вычисляем средние метрики
        novelties = [s.get("novelty_index", 0.0) for s in signals if s.get("novelty_index")]
        confidences = [s.get("confidence", 0.0) for s in signals if s.get("confidence")]
        
        avg_novelty = sum(novelties) / len(novelties) if novelties else 0.0
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Определяем тренды
        trends = []
        if avg_novelty > 0.8:
            trends.append("Высокая новизна сигналов")
        if avg_confidence > 0.7:
            trends.append("Высокая уверенность")
        if len(signals) > 5:
            trends.append("Активный период обнаружения")
        
        return {
            "trends": trends,
            "domains": top_domains,
            "avg_novelty": avg_novelty,
            "avg_confidence": avg_confidence,
            "total_signals": len(signals)
        }
    
    def format_signal(self, signal: Dict[str, Any], index: int) -> str:
        """Форматирование одного сигнала для Telegram"""
        name = signal.get("name", "Unknown Signal")
        novelty = signal.get("novelty_index", 0.0)
        confidence = signal.get("confidence", 0.0)
        source = signal.get("source_url", "")
        description = signal.get("description", "")
        
        # Эмодзи для уровня новизны
        novelty_emoji = "🔥" if novelty > 0.8 else "⭐" if novelty > 0.6 else "💡"
        
        # Форматируем
        lines = [f"{index}. {novelty_emoji} *{name}*"]
        
        if description:
            # Обрезаем описание до 150 символов
            desc = description[:150] + "..." if len(description) > 150 else description
            lines.append(f"   {desc}")
        
        metrics = []
        if novelty > 0:
            metrics.append(f"новизна: {novelty:.2f}")
        if confidence > 0:
            metrics.append(f"уверенность: {confidence:.2f}")
        
        if metrics:
            lines.append(f"   _{', '.join(metrics)}_")
        
        if source:
            # Обрезаем URL для читаемости
            display_url = source.replace("https://", "").replace("http://", "")[:50]
            lines.append(f"   [Источник]({source})")
        
        return "\n".join(lines)
    
    def generate_digest(self) -> str:
        """Генерация полного дайджеста"""
        # Получаем топ сигналы
        top_signals = self.get_top_signals(limit=3)
        
        # Анализируем тренды
        trends_data = self.analyze_trends(top_signals)
        
        # Формируем дайджест
        lines = ["🔍 *OSINT Digest*", ""]
        
        if not top_signals:
            lines.append("_Новых сигналов не обнаружено за последние 7 дней._")
            return "\n".join(lines)
        
        # Топ сигналы
        lines.append("*Топ-3 новых сигнала:*")
        lines.append("")
        
        for i, signal in enumerate(top_signals, 1):
            lines.append(self.format_signal(signal, i))
            lines.append("")
        
        # Тренды
        if trends_data["trends"]:
            lines.append("*Тренды:*")
            for trend in trends_data["trends"]:
                lines.append(f"• {trend}")
            lines.append("")
        
        # Статистика
        stats = []
        if trends_data["avg_novelty"] > 0:
            stats.append(f"Средняя новизна: {trends_data['avg_novelty']:.2f}")
        if trends_data["avg_confidence"] > 0:
            stats.append(f"Средняя уверенность: {trends_data['avg_confidence']:.2f}")
        if trends_data["total_signals"] > 0:
            stats.append(f"Всего сигналов: {trends_data['total_signals']}")
        
        if stats:
            lines.append(f"*Статистика:* {', '.join(stats)}")
        
        # Топ домены
        if trends_data["domains"]:
            lines.append("")
            lines.append(f"*Топ источники:* {', '.join(trends_data['domains'][:3])}")
        
        return "\n".join(lines)


def generate_daily_digest() -> str:
    """Удобная функция для генерации дайджеста"""
    generator = OSINTDigestGenerator()
    return generator.generate_digest()

