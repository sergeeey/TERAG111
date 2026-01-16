#!/usr/bin/env python3
"""
Тест добавления фактов в Neo4j через GraphUpdater
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
    print("🧩 Тестирование GraphUpdater.add_fact()...")
    print("=" * 60)
    print()
    
    # Инициализация
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "terag_neo4j_2025")
    
    print(f"Подключение к Neo4j: {uri}")
    print(f"User: {user}")
    print()
    
    try:
        updater = GraphUpdater(uri=uri, user=user, password=password)
        
        if not updater.driver:
            print("❌ Не удалось подключиться к Neo4j")
            return 1
        
        print("✅ Подключение к Neo4j установлено")
        print()
        
        # Тестовые факты
        test_facts = [
            {
                "subject": "AI",
                "predicate": "IMPACTS",
                "object": "Governance",
                "source": "https://example.com/ai-governance",
                "confidence": 0.92
            },
            {
                "subject": "AI Governance",
                "predicate": "RELATED_TO",
                "object": "Ethical AI",
                "source": "https://example.com/ethics",
                "confidence": 0.85
            },
            {
                "subject": "Ethical AI",
                "predicate": "REQUIRES",
                "object": "Transparency",
                "source": "https://example.com/transparency",
                "confidence": 0.78
            }
        ]
        
        print("📝 Добавление фактов в граф:")
        print()
        
        added = 0
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
                print(f"   Confidence: {fact['confidence']}, Source: {fact['source']}")
                added += 1
            else:
                print(f"❌ {i}. Не удалось добавить факт")
            print()
        
        # Проверяем граф
        print("=" * 60)
        print("🔍 Проверка графа:")
        print()
        
        with updater.driver.session() as session:
            # Количество узлов
            nodes_result = session.run("MATCH (n:Entity) RETURN count(n) as count")
            nodes_count = nodes_result.single()["count"]
            print(f"✅ Узлов Entity: {nodes_count}")
            
            # Количество связей
            rels_result = session.run("MATCH ()-[r:RELATION]->() RETURN count(r) as count")
            rels_count = rels_result.single()["count"]
            print(f"✅ Связей RELATION: {rels_count}")
            
            # Примеры фактов
            print()
            print("📊 Примеры фактов в графе:")
            facts_result = session.run("""
                MATCH (a:Entity)-[r:RELATION]->(b:Entity)
                RETURN a.name as subject, r.type as predicate, b.name as object, r.confidence as confidence
                LIMIT 5
            """)
            
            for record in facts_result:
                print(f"   {record['subject']} -[{record['predicate']}]-> {record['object']} (conf: {record['confidence']})")
        
        print()
        print("=" * 60)
        print(f"✅ Тест завершён! Добавлено фактов: {added}/{len(test_facts)}")
        print()
        print("💡 Откройте Neo4j Browser: http://localhost:7474")
        print("   Запрос: MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 10")
        
        updater.close()
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())













