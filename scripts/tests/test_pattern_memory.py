#!/usr/bin/env python3
"""
Тест Pattern Memory — проверка распознавания и сохранения паттернов
"""
import sys
import os
import asyncio
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "installer" / "app" / "modules"))

# Загружаем .env
from dotenv import load_dotenv
load_dotenv()

async def main():
    print("🧠 Тестирование Pattern Memory...")
    print("=" * 60)
    print()
    
    try:
        from src.core.pattern_memory import PatternMemory
        from src.integration.lmstudio_client import LMStudioClient
        from installer.app.modules.graph_updater import GraphUpdater
        
        # Инициализация
        print("📡 Инициализация компонентов...")
        lm_client = LMStudioClient()
        await lm_client.connect()
        
        graph_updater = GraphUpdater(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "terag_neo4j_2025")
        )
        
        pattern_mem = PatternMemory(
            graph_updater=graph_updater,
            lm_client=lm_client
        )
        print("✅ Pattern Memory инициализирован")
        print()
        
        # Тест 1: Классификация успешного результата
        print("=" * 60)
        print("✅ Тест 1: Классификация успешного результата")
        print("=" * 60)
        print()
        
        success_result = {
            "task": "OSINT summarization",
            "output": "Relevant and accurate summary generated with high confidence",
            "quality_score": 0.92
        }
        
        classification = await pattern_mem.classify_pattern(success_result)
        print(f"📄 Результат: {success_result['task']}")
        print(f"✅ Классификация: {classification['classification']}")
        print(f"📝 Причина: {classification['reason']}")
        print(f"🏷️  Паттерн: {classification['pattern_name']}")
        print(f"📊 Confidence: {classification['confidence']:.2f}")
        print()
        
        # Тест 2: Классификация неудачного результата
        print("=" * 60)
        print("❌ Тест 2: Классификация неудачного результата")
        print("=" * 60)
        print()
        
        failure_result = {
            "task": "OSINT summarization",
            "output": "Summary generated but contains errors",
            "quality_score": 0.45,
            "error": "Low confidence in extracted facts"
        }
        
        classification2 = await pattern_mem.classify_pattern(failure_result)
        print(f"📄 Результат: {failure_result['task']}")
        print(f"❌ Классификация: {classification2['classification']}")
        print(f"📝 Причина: {classification2['reason']}")
        print(f"🏷️  Паттерн: {classification2['pattern_name']}")
        print()
        
        # Тест 3: Сохранение паттернов
        print("=" * 60)
        print("💾 Тест 3: Сохранение паттернов в граф")
        print("=" * 60)
        print()
        
        stored1 = await pattern_mem.store_pattern(classification)
        stored2 = await pattern_mem.store_pattern(classification2)
        
        print(f"✅ Успешный паттерн сохранён: {stored1}")
        print(f"❌ Неудачный паттерн сохранён: {stored2}")
        print()
        
        # Тест 4: Связывание паттернов
        print("=" * 60)
        print("🔗 Тест 4: Связывание паттернов")
        print("=" * 60)
        print()
        
        if stored1 and stored2:
            linked = pattern_mem.link_patterns(
                success_name=classification['pattern_name'],
                failure_name=classification2['pattern_name']
            )
            print(f"✅ Паттерны связаны: {linked}")
        print()
        
        # Тест 5: Получение лучших практик
        print("=" * 60)
        print("⭐ Тест 5: Получение лучших практик")
        print("=" * 60)
        print()
        
        best = await pattern_mem.get_best_practices(limit=5)
        if best:
            print(f"✅ Найдено практик: {len(best)}")
            for i, practice in enumerate(best, 1):
                print(f"   {i}. {practice['name']} (occurrences: {practice.get('occurrences', 0)})")
        else:
            print("⚠️ Best practices не найдены (граф может быть пустым)")
        print()
        
        # Тест 6: Статистика паттернов
        print("=" * 60)
        print("📊 Тест 6: Статистика паттернов")
        print("=" * 60)
        print()
        
        stats = pattern_mem.get_pattern_stats()
        print(f"   • Всего паттернов: {stats['total']}")
        print(f"   • Успешных: {stats['success']}")
        print(f"   • Неудачных: {stats['failure']}")
        print(f"   • Средняя сила связей: {stats['avg_strength']:.2f}")
        print()
        
        # Тест 7: Обучение на результате
        print("=" * 60)
        print("🎓 Тест 7: Обучение на результате")
        print("=" * 60)
        print()
        
        test_result = {
            "task": "Reasoning with context",
            "output": "Accurate reasoning with high confidence",
            "quality_score": 0.88
        }
        
        learn_result = await pattern_mem.learn_from_result(test_result)
        print(f"✅ Обучение завершено")
        print(f"   Классификация: {learn_result['classification']['classification']}")
        print(f"   Паттерн: {learn_result['pattern_name']}")
        print()
        
        print("=" * 60)
        print("✅ Тест завершён успешно!")
        print("=" * 60)
        
        await lm_client.close()
        graph_updater.close()
        
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))













