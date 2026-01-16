#!/usr/bin/env python3
"""
Полный тест GraphUpdater: add_fact, add_signal, get_graph_stats
"""
import sys
import os
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "installer" / "app" / "modules"))

# Загружаем .env
from dotenv import load_dotenv
load_dotenv()

from installer.app.modules.graph_updater import GraphUpdater

def main():
    print("🧩 Полный тест GraphUpdater...")
    print("=" * 60)
    print()
    
    # Инициализация
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "terag_neo4j_2025")
    
    print(f"Подключение к Neo4j: {uri}")
    print()
    
    try:
        updater = GraphUpdater(uri=uri, user=user, password=password)
        
        if not updater.driver:
            print("❌ Не удалось подключиться к Neo4j")
            return 1
        
        print("✅ Подключение к Neo4j установлено")
        print()
        
        # 1. Тест add_fact()
        print("=" * 60)
        print("📝 Тест 1: add_fact()")
        print("=" * 60)
        print()
        
        test_facts = [
            {
                "subject": "Graph Neural Networks",
                "predicate": "ENABLES",
                "object": "Knowledge Reasoning",
                "source": "https://arxiv.org/abs/2501.12345",
                "confidence": 0.88
            },
            {
                "subject": "Knowledge Reasoning",
                "predicate": "REQUIRES",
                "object": "Graph Database",
                "source": "https://example.com/knowledge",
                "confidence": 0.85
            }
        ]
        
        added_facts = 0
        for i, fact in enumerate(test_facts, 1):
            fact_dict = {
                "subject": fact["subject"],
                "predicate": fact["predicate"],
                "object": fact["object"]
            }
            
            result = updater.add_fact(
                fact_dict,
                source=fact["source"],
                confidence=fact["confidence"]
            )
            
            if result:
                print(f"✅ {i}. {fact['subject']} -[{fact['predicate']}]-> {fact['object']}")
                added_facts += 1
            else:
                print(f"❌ {i}. Не удалось добавить факт")
            print()
        
        # 2. Тест add_signal()
        print("=" * 60)
        print("📡 Тест 2: add_signal()")
        print("=" * 60)
        print()
        
        test_signals = [
            {
                "concept": "EdgeAI",
                "domain": "Semantic Intelligence",
                "novelty_score": 0.87,
                "confidence": 0.9
            },
            {
                "concept": "Causal Reasoning",
                "domain": "AI Architecture",
                "novelty_score": 0.82,
                "confidence": 0.88
            }
        ]
        
        added_signals = 0
        for i, signal in enumerate(test_signals, 1):
            result = updater.add_signal(
                concept=signal["concept"],
                domain=signal["domain"],
                novelty_score=signal["novelty_score"],
                confidence=signal["confidence"]
            )
            
            if result:
                print(f"✅ {i}. Signal: {signal['concept']} (domain: {signal['domain']})")
                print(f"   Novelty: {signal['novelty_score']}, Confidence: {signal['confidence']}")
                added_signals += 1
            else:
                print(f"❌ {i}. Не удалось добавить сигнал")
            print()
        
        # 3. Тест get_graph_stats()
        print("=" * 60)
        print("📊 Тест 3: get_graph_stats()")
        print("=" * 60)
        print()
        
        stats = updater.get_graph_stats()
        
        if "error" in stats:
            print(f"❌ Ошибка получения статистики: {stats['error']}")
        else:
            print("✅ Статистика графа:")
            print(f"   • Всего узлов: {stats['nodes']}")
            print(f"   • Всего связей: {stats['relations']}")
            print(f"   • Entities: {stats['entities']}")
            print(f"   • Signals: {stats['signals']}")
            print(f"   • Domains: {stats['domains']}")
        
        print()
        print("=" * 60)
        print("✅ Итоговый отчёт:")
        print("=" * 60)
        print(f"   • Фактов добавлено: {added_facts}/{len(test_facts)}")
        print(f"   • Сигналов добавлено: {added_signals}/{len(test_signals)}")
        print(f"   • Всего узлов в графе: {stats.get('nodes', 0)}")
        print(f"   • Всего связей в графе: {stats.get('relations', 0)}")
        print()
        print("💡 Откройте Neo4j Browser: http://localhost:7474")
        print("   Запрос: MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 20")
        
        updater.close()
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())













