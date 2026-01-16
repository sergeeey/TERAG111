#!/usr/bin/env python3
"""
TERAG Manual Update
Ручное обновление графа знаний
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from src.core.doc_converter import convert_all_to_txt, get_converted_files
from src.core.kag_builder import run_batch_processing

def main():
    """Ручное обновление графа знаний"""
    print("=" * 60)
    print("TERAG Manual Update - Ручное обновление")
    print("=" * 60)
    
    try:
        # 1. Конвертируем документы
        print("1. Конвертация документов...")
        converted_dir = convert_all_to_txt("data")
        print(f"   Конвертированные файлы: {converted_dir}")
        
        # 2. Обрабатываем документы
        print("\n2. Обработка документов...")
        run_batch_processing()
        
        # 3. Проверяем результаты
        print("\n3. Проверка результатов...")
        converted_files = get_converted_files(converted_dir)
        print(f"   Всего конвертированных файлов: {len(converted_files)}")
        
        # 4. Проверяем статистику API
        print("\n4. Проверка API статистики...")
        try:
            import requests
            response = requests.get("http://127.0.0.1:8000/api/graph/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"   Документов в графе: {stats.get('documents', 0)}")
                print(f"   Триплетов в графе: {stats.get('triplets', 0)}")
                print(f"   Узлов в графе: {stats.get('nodes', 0)}")
                print(f"   Связей в графе: {stats.get('edges', 0)}")
            else:
                print(f"   Ошибка API: {response.status_code}")
        except Exception as e:
            print(f"   Ошибка подключения к API: {e}")
        
        print("\n✅ Обновление завершено!")
        print("📊 Проверьте дашборд: http://127.0.0.1:8000/api/static/index.html")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

































