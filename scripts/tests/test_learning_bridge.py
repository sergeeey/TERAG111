#!/usr/bin/env python3
"""
Тест Learning Bridge — проверка когнитивной адаптации TERAG
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
    print("🧠 Тестирование Learning Bridge...")
    print("=" * 60)
    print()
    
    try:
        from src.integration.learning_bridge import LearningBridge
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
        
        bridge = LearningBridge(lm_client=lm_client, graph_updater=graph_updater)
        print("✅ Learning Bridge инициализирован")
        print()
        
        # Тест 1: Получение контекста из графа
        print("=" * 60)
        print("📚 Тест 1: Получение контекста из графа")
        print("=" * 60)
        print()
        
        context = await bridge.get_context_from_graph(limit=3)
        if context:
            print("✅ Контекст получен:")
            print(context[:200] + "..." if len(context) > 200 else context)
        else:
            print("⚠️ Контекст пуст (граф может быть пустым)")
        print()
        
        # Тест 2: Классификация домена
        print("=" * 60)
        print("🏷️  Тест 2: Классификация домена")
        print("=" * 60)
        print()
        
        test_texts = [
            "Python error handling best practices using try-except blocks",
            "Neural networks and deep learning architectures for AI",
            "Cognitive biases in decision making processes"
        ]
        
        for text in test_texts:
            domain = await bridge.classify_domain(text)
            print(f"✅ Текст: {text[:50]}...")
            print(f"   Домен: {domain}")
            print()
        
        # Тест 3: Reasoning с контекстом
        print("=" * 60)
        print("💭 Тест 3: Reasoning с контекстом")
        print("=" * 60)
        print()
        
        question = "What are best practices for error handling in Python?"
        print(f"❓ Вопрос: {question}")
        print()
        
        result = await bridge.reason_with_context(
            question=question,
            domain="Programming",
            save_result=True
        )
        
        print(f"✅ Ответ получен:")
        print(f"   {result.get('text', '')[:200]}...")
        print(f"   Контекст использован: {result.get('context_used', False)}")
        print(f"   Домен: {result.get('domain', 'N/A')}")
        
        if result.get('learned'):
            learned = result['learned']
            print(f"   Сохранено фактов: {learned.get('facts_count', 0)}")
        print()
        
        # Тест 4: Best practices
        print("=" * 60)
        print("⭐ Тест 4: Получение best practices")
        print("=" * 60)
        print()
        
        practices = bridge.get_best_practices("Programming", limit=3)
        if practices:
            print(f"✅ Найдено практик: {len(practices)}")
            for i, practice in enumerate(practices, 1):
                print(f"   {i}. {practice['concept']} (confidence: {practice['confidence']:.2f})")
        else:
            print("⚠️ Best practices не найдены (граф может быть пустым)")
        print()
        
        # Финальная статистика
        print("=" * 60)
        print("📊 Финальная статистика графа:")
        print("=" * 60)
        print()
        
        stats = graph_updater.get_graph_stats()
        print(f"   • Узлов: {stats.get('nodes', 0)}")
        print(f"   • Связей: {stats.get('relations', 0)}")
        print(f"   • Entities: {stats.get('entities', 0)}")
        print(f"   • Signals: {stats.get('signals', 0)}")
        print(f"   • Domains: {stats.get('domains', 0)}")
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













