#!/usr/bin/env python3
"""
Тест TERAG Evolution Loop
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.core.evolution_loop import TERAGEvolutionLoop
import os

async def main():
    print("=" * 60)
    print("🧠 Тест TERAG Evolution Loop")
    print("=" * 60)
    print()
    
    # Инициализация компонентов
    graph_driver = None
    lm_client = None
    
    try:
        from neo4j import GraphDatabase
        graph_driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "terag_neo4j_2025"))
        )
        print("✅ Neo4j подключён")
    except Exception as e:
        print(f"⚠️ Neo4j не доступен: {e}")
    
    try:
        from src.integration.lmstudio_client import LMStudioClient
        lm_client = LMStudioClient()
        await lm_client.connect()
        print("✅ LM Studio подключён")
    except Exception as e:
        print(f"⚠️ LM Studio не доступен: {e}")
    
    print()
    
    # Создаём Evolution Loop
    loop = TERAGEvolutionLoop(
        graph_driver=graph_driver,
        lm_client=lm_client,
        enable_visualization=True
    )
    
    # Тестовый запрос
    query = "Как TERAG может оптимизировать OSINT анализ?"
    
    print(f"📝 Запрос: {query}")
    print()
    print("🚀 Запуск Evolution Loop...")
    print()
    
    # Запускаем цикл
    result = await loop.run(query, visualize=True)
    
    # Выводим результаты
    print("=" * 60)
    print("📊 Результаты")
    print("=" * 60)
    print()
    
    if result.get("success"):
        print("✅ Успешно завершено")
        print(f"⏱️  Время выполнения: {result.get('duration_seconds', 0):.2f} сек")
        print()
        
        final_report = result.get("final_report", {})
        print(f"📄 Отчёт:")
        print(f"   Уверенность: {final_report.get('confidence', 0.0):.2f}")
        print(f"   Статус проверки: {final_report.get('verification_status', 'unknown')}")
        print()
        print(f"   Вывод:")
        print(f"   {final_report.get('conclusion', 'N/A')[:200]}...")
        print()
        
        if "visualization" in result:
            print(f"📊 Визуализация: {result['visualization']}")
            print()
        
        system_health = result.get("system_health", {})
        print(f"🏥 Здоровье системы: {system_health.get('status', 'unknown')}")
        print(f"   Доверие: {system_health.get('trust', 0.0):.2f}")
        print(f"   Точность: {system_health.get('accuracy', 0.0):.2f}")
    else:
        print("❌ Ошибка выполнения")
        print(f"   {result.get('error', 'Unknown error')}")
    
    # Закрываем соединения
    if graph_driver:
        graph_driver.close()
    
    if lm_client:
        await lm_client.close()
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())













