#!/usr/bin/env python3
"""
Тест автоматического обновления TERAG
"""

import time
import requests
import json
from pathlib import Path

def test_auto_update():
    """Тестирует автоматическое обновление системы"""
    
    print("=== Тест автоматического обновления TERAG ===")
    
    # 1. Получаем текущую статистику
    print("1. Получение текущей статистики...")
    try:
        response = requests.get("http://127.0.0.1:8000/api/graph/stats")
        if response.status_code == 200:
            current_stats = response.json()
            print(f"   Текущие документы: {current_stats.get('documents', 0)}")
            print(f"   Текущие триплеты: {current_stats.get('triplets', 0)}")
        else:
            print(f"   Ошибка получения статистики: {response.status_code}")
            return
    except Exception as e:
        print(f"   Ошибка подключения к API: {e}")
        return
    
    # 2. Создаём тестовый файл
    print("\n2. Создание тестового файла...")
    test_file = Path("data/test_auto_update.txt")
    test_content = f"""
Тестовый документ для автоматического обновления TERAG

Этот документ создан для проверки системы автоматического наблюдения.

Ключевые функции:
- Автоматическое обнаружение новых файлов
- Конвертация в текстовый формат
- Извлечение триплетов знаний
- Обновление графа знаний
- Обновление метрик AI-REPS

Система должна:
1. Обнаружить этот файл при создании
2. Конвертировать его в папку converted
3. Извлечь знания в виде триплетов
4. Обновить граф знаний
5. Обновить метрики на дашборде

Дата создания: {time.strftime('%Y-%m-%d %H:%M:%S')}
Статус: Тестирование автоматической обработки

Дополнительная информация:
- Система мониторинга файлов
- Обработка в реальном времени
- Интеграция с AI-REPS
- Обновление метрик
- Построение графа знаний
"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"   Файл создан: {test_file}")
    
    # 3. Ждём обработки
    print("\n3. Ожидание автоматической обработки...")
    for i in range(30):  # Ждём до 30 секунд
        time.sleep(1)
        print(f"   Ожидание... {i+1}/30")
        
        # Проверяем, появился ли файл в converted
        converted_file = Path("data/converted/test_auto_update.txt")
        if converted_file.exists():
            print(f"   Файл конвертирован: {converted_file}")
            break
    else:
        print("   Таймаут: файл не был обработан автоматически")
        return
    
    # 4. Проверяем обновление статистики
    print("\n4. Проверка обновления статистики...")
    try:
        response = requests.get("http://127.0.0.1:8000/api/graph/stats")
        if response.status_code == 200:
            new_stats = response.json()
            print(f"   Новые документы: {new_stats.get('documents', 0)}")
            print(f"   Новые триплеты: {new_stats.get('triplets', 0)}")
            
            # Сравниваем статистику
            if new_stats.get('documents', 0) > current_stats.get('documents', 0):
                print("   ✅ Количество документов увеличилось!")
            else:
                print("   ⚠️ Количество документов не изменилось")
                
            if new_stats.get('triplets', 0) > current_stats.get('triplets', 0):
                print("   ✅ Количество триплетов увеличилось!")
            else:
                print("   ⚠️ Количество триплетов не изменилось")
        else:
            print(f"   Ошибка получения статистики: {response.status_code}")
    except Exception as e:
        print(f"   Ошибка проверки статистики: {e}")
    
    # 5. Очистка
    print("\n5. Очистка тестовых файлов...")
    try:
        test_file.unlink()
        print("   Тестовый файл удален")
    except:
        pass
    
    try:
        converted_file.unlink()
        print("   Конвертированный файл удален")
    except:
        pass
    
    print("\n=== Тест завершен ===")

if __name__ == "__main__":
    test_auto_update()

































