#!/usr/bin/env python3
"""
Тест Self-Organizing Graph — проверка динамической категоризации
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
    print("🌱 Тестирование Self-Organizing Graph...")
    print("=" * 60)
    print()
    
    try:
        from src.core.self_organizing_graph import SelfOrganizingGraph
        from src.integration.lmstudio_client import LMStudioClient
        from installer.app.modules.graph_updater import GraphUpdater
        
        # Проверяем наличие sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            embedder = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ SentenceTransformer загружен")
        except ImportError:
            print("⚠️ sentence-transformers не установлен, embeddings будут отключены")
            embedder = None
        
        # Инициализация
        print("📡 Инициализация компонентов...")
        lm_client = LMStudioClient()
        await lm_client.connect()
        
        graph_updater = GraphUpdater(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "terag_neo4j_2025")
        )
        
        sog = SelfOrganizingGraph(
            graph_updater=graph_updater,
            lm_client=lm_client,
            embedder=embedder,
            similarity_threshold=0.65
        )
        print("✅ Self-Organizing Graph инициализирован")
        print()
        
        # Тест 1: Категоризация нового текста
        print("=" * 60)
        print("📝 Тест 1: Категоризация нового текста")
        print("=" * 60)
        print()
        
        test_texts = [
            "В психологии код-ревью усиливает эмпатию между разработчиками",
            "Квантовые вычисления открывают новые возможности для машинного обучения",
            "Когнитивные искажения влияют на принятие решений в программировании"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"📄 Текст {i}: {text[:60]}...")
            result = await sog.categorize_and_store(
                text=text,
                source_url=f"https://example.com/article/{i}",
                confidence=0.8
            )
            
            if result['action'] == 'create_new_cluster':
                print(f"   ✅ Создан новый кластер: {result['cluster_name']}")
                print(f"   Тип: {result['cluster_type']}")
            else:
                print(f"   ✅ Связан с существующим кластером: {result['cluster_name']}")
                print(f"   Схожесть: {result['similarity']:.2f}")
            print()
        
        # Тест 2: Поиск похожих кластеров
        print("=" * 60)
        print("🔍 Тест 2: Поиск похожих кластеров")
        print("=" * 60)
        print()
        
        test_text = "Психология программирования и когнитивные процессы"
        embedding = sog._get_embedding(test_text)
        
        if embedding is not None:
            similar = await sog.find_similar_clusters(embedding, limit=3)
            print(f"📄 Текст: {test_text}")
            print(f"✅ Найдено похожих кластеров: {len(similar)}")
            for cluster_name, similarity in similar:
                print(f"   • {cluster_name}: {similarity:.2f}")
        else:
            print("⚠️ Embeddings недоступны, пропускаем тест")
        print()
        
        # Тест 3: Применение правил роста
        print("=" * 60)
        print("🌳 Тест 3: Применение правил роста")
        print("=" * 60)
        print()
        
        sog.apply_growth_rules()
        print("✅ Правила роста применены")
        print()
        
        # Тест 4: Decay старых концептов
        print("=" * 60)
        print("⏰ Тест 4: Decay старых концептов")
        print("=" * 60)
        print()
        
        sog.decay_old_concepts()
        print("✅ Decay применён к старым концептам")
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













