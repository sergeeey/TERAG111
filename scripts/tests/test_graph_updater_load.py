#!/usr/bin/env python3
"""
Нагрузочный тест GraphUpdater: проверка интеграции с OSINT pipeline
"""
import sys
import os
import time
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "installer" / "app" / "modules"))

# Загружаем .env
from dotenv import load_dotenv
load_dotenv()

from installer.app.modules.graph_updater import GraphUpdater

def generate_test_facts(count: int) -> List[Dict[str, Any]]:
    """Генерация тестовых фактов"""
    facts = []
    concepts = ["AI", "ML", "NLP", "Computer Vision", "Robotics", "IoT", "Blockchain", "Quantum Computing"]
    relations = ["IMPACTS", "ENABLES", "REQUIRES", "RELATED_TO", "INFLUENCES"]
    
    for i in range(count):
        subject = concepts[i % len(concepts)]
        obj = concepts[(i + 1) % len(concepts)]
        relation = relations[i % len(relations)]
        
        facts.append({
            "subject": f"{subject} {i // len(concepts) + 1}",
            "predicate": relation,
            "object": f"{obj} {i // len(concepts) + 1}",
            "source": f"https://example.com/article/{i}",
            "confidence": 0.7 + (i % 30) / 100
        })
    
    return facts

def generate_test_signals(count: int) -> List[Dict[str, Any]]:
    """Генерация тестовых сигналов"""
    signals = []
    concepts = ["EdgeAI", "Causal Reasoning", "Graph Neural Networks", "Federated Learning"]
    domains = ["Semantic Intelligence", "AI Architecture", "Distributed Systems", "Knowledge Graphs"]
    
    for i in range(count):
        signals.append({
            "concept": f"{concepts[i % len(concepts)]} v{i // len(concepts) + 1}",
            "domain": domains[i % len(domains)],
            "novelty_score": 0.7 + (i % 20) / 100,
            "confidence": 0.75 + (i % 25) / 100
        })
    
    return signals

def add_facts_batch(updater: GraphUpdater, facts: List[Dict[str, Any]]) -> Dict[str, int]:
    """Добавление фактов батчами"""
    added = 0
    failed = 0
    
    for fact in facts:
        fact_dict = {
            "subject": fact["subject"],
            "predicate": fact["predicate"],
            "object": fact["object"]
        }
        
        if updater.add_fact(fact_dict, source=fact["source"], confidence=fact["confidence"]):
            added += 1
        else:
            failed += 1
    
    return {"added": added, "failed": failed}

def add_signals_batch(updater: GraphUpdater, signals: List[Dict[str, Any]]) -> Dict[str, int]:
    """Добавление сигналов батчами"""
    added = 0
    failed = 0
    
    for signal in signals:
        if updater.add_signal(
            concept=signal["concept"],
            domain=signal["domain"],
            novelty_score=signal["novelty_score"],
            confidence=signal["confidence"]
        ):
            added += 1
        else:
            failed += 1
    
    return {"added": added, "failed": failed}

def test_concurrent_writes(updater: GraphUpdater, num_threads: int = 5, facts_per_thread: int = 10):
    """Тест конкурентной записи"""
    print(f"\n🔄 Тест конкурентной записи ({num_threads} потоков, {facts_per_thread} фактов на поток)...")
    
    all_facts = generate_test_facts(num_threads * facts_per_thread)
    facts_per_thread_list = [
        all_facts[i * facts_per_thread:(i + 1) * facts_per_thread]
        for i in range(num_threads)
    ]
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(add_facts_batch, updater, facts)
            for facts in facts_per_thread_list
        ]
        
        results = [f.result() for f in futures]
    
    elapsed = time.time() - start_time
    
    total_added = sum(r["added"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    
    print(f"   ✅ Добавлено: {total_added}, ❌ Ошибок: {total_failed}")
    print(f"   ⏱️  Время: {elapsed:.2f}s ({total_added / elapsed:.1f} фактов/сек)")
    
    return {"added": total_added, "failed": total_failed, "elapsed": elapsed}

def main():
    print("🧩 Нагрузочный тест GraphUpdater")
    print("=" * 60)
    print()
    
    # Инициализация
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "terag_neo4j_2025")
    
    try:
        updater = GraphUpdater(uri=uri, user=user, password=password)
        
        if not updater.driver:
            print("❌ Не удалось подключиться к Neo4j")
            return 1
        
        print("✅ Подключение к Neo4j установлено")
        
        # Получаем начальную статистику
        initial_stats = updater.get_graph_stats()
        print(f"\n📊 Начальное состояние графа:")
        print(f"   • Узлов: {initial_stats.get('nodes', 0)}")
        print(f"   • Связей: {initial_stats.get('relations', 0)}")
        print(f"   • Entities: {initial_stats.get('entities', 0)}")
        print(f"   • Signals: {initial_stats.get('signals', 0)}")
        
        # Тест 1: Последовательное добавление фактов
        print("\n" + "=" * 60)
        print("📝 Тест 1: Последовательное добавление фактов (50 фактов)")
        print("=" * 60)
        
        facts = generate_test_facts(50)
        start_time = time.time()
        result = add_facts_batch(updater, facts)
        elapsed = time.time() - start_time
        
        print(f"   ✅ Добавлено: {result['added']}, ❌ Ошибок: {result['failed']}")
        print(f"   ⏱️  Время: {elapsed:.2f}s ({result['added'] / elapsed:.1f} фактов/сек)")
        
        # Тест 2: Последовательное добавление сигналов
        print("\n" + "=" * 60)
        print("📡 Тест 2: Последовательное добавление сигналов (20 сигналов)")
        print("=" * 60)
        
        signals = generate_test_signals(20)
        start_time = time.time()
        result = add_signals_batch(updater, signals)
        elapsed = time.time() - start_time
        
        print(f"   ✅ Добавлено: {result['added']}, ❌ Ошибок: {result['failed']}")
        print(f"   ⏱️  Время: {elapsed:.2f}s ({result['added'] / elapsed:.1f} сигналов/сек)")
        
        # Тест 3: Конкурентная запись
        print("\n" + "=" * 60)
        print("🔄 Тест 3: Конкурентная запись")
        print("=" * 60)
        
        concurrent_result = test_concurrent_writes(updater, num_threads=5, facts_per_thread=10)
        
        # Финальная статистика
        print("\n" + "=" * 60)
        print("📊 Финальное состояние графа:")
        print("=" * 60)
        
        final_stats = updater.get_graph_stats()
        print(f"   • Узлов: {final_stats.get('nodes', 0)} (+{final_stats.get('nodes', 0) - initial_stats.get('nodes', 0)})")
        print(f"   • Связей: {final_stats.get('relations', 0)} (+{final_stats.get('relations', 0) - initial_stats.get('relations', 0)})")
        print(f"   • Entities: {final_stats.get('entities', 0)} (+{final_stats.get('entities', 0) - initial_stats.get('entities', 0)})")
        print(f"   • Signals: {final_stats.get('signals', 0)} (+{final_stats.get('signals', 0) - initial_stats.get('signals', 0)})")
        print(f"   • Domains: {final_stats.get('domains', 0)}")
        
        print("\n" + "=" * 60)
        print("✅ Нагрузочный тест завершён успешно!")
        print("=" * 60)
        
        updater.close()
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())













