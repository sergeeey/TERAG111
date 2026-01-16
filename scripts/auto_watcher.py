#!/usr/bin/env python3
"""
TERAG Auto Watcher
Автоматически отслеживает изменения в папке data/ и обновляет граф знаний
"""

import time
import sys
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from src.core.doc_converter import convert_all_to_txt, get_converted_files
from src.core.kag_builder import run_batch_processing

WATCH_PATH = Path("data")
CHECK_INTERVAL = 5  # секунд между проверками
PROCESSED_EXTENSIONS = {'.docx', '.pdf', '.xlsx', '.xls', '.txt', '.md'}

class DocHandler(FileSystemEventHandler):
    """Обработчик событий файловой системы"""
    
    def __init__(self):
        self.last_processed = 0
        self.processing = False
    
    def on_created(self, event):
        """Обработка создания нового файла"""
        if not event.is_directory and self._should_process(event.src_path):
            print(f"📄 Новый файл обнаружен: {Path(event.src_path).name}")
            self._schedule_processing()
    
    def on_modified(self, event):
        """Обработка изменения файла"""
        if not event.is_directory and self._should_process(event.src_path):
            print(f"📝 Файл изменён: {Path(event.src_path).name}")
            self._schedule_processing()
    
    def _should_process(self, file_path):
        """Проверяет, нужно ли обрабатывать файл"""
        path = Path(file_path)
        return path.suffix.lower() in PROCESSED_EXTENSIONS
    
    def _schedule_processing(self):
        """Планирует обработку с задержкой"""
        current_time = time.time()
        if current_time - self.last_processed > 10:  # Минимум 10 секунд между обработками
            self.last_processed = current_time
            print("⏰ Планируется обновление графа знаний...")
            # Запускаем обработку в отдельном потоке
            import threading
            threading.Timer(2.0, self._process_documents).start()
    
    def _process_documents(self):
        """Обрабатывает документы и обновляет граф"""
        if self.processing:
            return
        
        self.processing = True
        try:
            print("🔄 Начинаем обновление графа знаний...")
            
            # Конвертируем документы
            print("📄 Конвертация документов...")
            converted_dir = convert_all_to_txt(str(WATCH_PATH))
            
            # Проверяем, есть ли новые файлы для обработки
            converted_files = get_converted_files(converted_dir)
            if not converted_files:
                print("ℹ️ Нет новых документов для обработки")
                return
            
            print(f"📚 Найдено {len(converted_files)} конвертированных файлов")
            
            # Обновляем граф знаний
            print("🧠 Обновление графа знаний...")
            run_batch_processing()
            
            print("✅ Граф знаний успешно обновлён!")
            print("📊 Проверьте дашборд: http://127.0.0.1:8000/api/static/index.html")
            
        except Exception as e:
            print(f"❌ Ошибка при обновлении графа: {e}")
        finally:
            self.processing = False

def process_documents_manually():
    """Ручная обработка всех документов"""
    print("🔄 Ручное обновление графа знаний...")
    try:
        converted_dir = convert_all_to_txt(str(WATCH_PATH))
        run_batch_processing()
        print("✅ Граф знаний обновлён!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Основная функция"""
    print("=" * 60)
    print("👁 TERAG Auto Watcher запущен")
    print("=" * 60)
    print(f"📁 Отслеживаемая папка: {WATCH_PATH.resolve()}")
    print(f"⏱️ Интервал проверки: {CHECK_INTERVAL} секунд")
    print(f"📄 Поддерживаемые форматы: {', '.join(PROCESSED_EXTENSIONS)}")
    print("=" * 60)
    print("💡 Просто скопируйте новые документы в папку data/")
    print("🛑 Нажмите Ctrl+C для остановки")
    print("=" * 60)
    
    # Создаём обработчик событий
    event_handler = DocHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_PATH), recursive=True)
    
    try:
        # Запускаем наблюдение
        observer.start()
        print("✅ Наблюдение активно!")
        
        # Обрабатываем существующие документы при запуске
        print("\n🔄 Первичная обработка существующих документов...")
        process_documents_manually()
        
        # Основной цикл
        while True:
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
        observer.stop()
        print("✅ TERAG Auto Watcher остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        observer.join()

if __name__ == "__main__":
    main()

































