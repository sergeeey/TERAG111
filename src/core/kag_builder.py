import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.doc_converter import convert_all_to_txt, get_converted_files

# Автоматическая конвертация документов
print("Запуск конвертации документов...")
CONVERTED_DIR = convert_all_to_txt("data")
print(f"Конвертация завершена. Файлы в: {CONVERTED_DIR}")

# Папка с конвертированными документами
DATA_DIR = CONVERTED_DIR

# Папка, куда будут сохраняться результаты
OUTPUT_DIR = Path("data") / "graph_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_triplets_from_text(text: str, language: str = "ru"):
    """
    Извлечение знаний (SPO-триплетов) с поддержкой языков
    """
    lines = text.split("\n")
    triplets = []
    
    for line in lines:
        if len(line.strip()) > 10:
            # Определяем язык из имени файла или используем переданный
            if language == "en":
                # Английская логика
                triplets.append({
                    "subject": "Document",
                    "predicate": "mentions",
                    "object": line.strip()[:60],
                    "confidence": 0.85,
                    "language": "en"
                })
            else:
                # Русская логика (по умолчанию)
                triplets.append({
                    "subject": "Документ",
                    "predicate": "упоминает",
                    "object": line.strip()[:60],
                    "confidence": 0.85,
                    "language": "ru"
                })
    
    return triplets

def process_document(doc_path: Path):
    """
    Обработка одного документа: чтение и извлечение знаний
    """
    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Определяем язык из имени файла
        filename = doc_path.stem
        if filename.endswith('_en'):
            language = "en"
        elif filename.endswith('_ru'):
            language = "ru"
        else:
            language = "ru"  # По умолчанию русский

        triplets = extract_triplets_from_text(text, language)
        result = {
            "file": str(doc_path),
            "language": language,
            "triplets_count": len(triplets),
            "triplets": triplets,
            "processed_at": datetime.now().isoformat()
        }

        out_file = OUTPUT_DIR / f"{doc_path.stem}_graph.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"Processed: {doc_path.name} ({len(triplets)} triplets, language: {language})")
    except Exception as e:
        print(f"Error processing {doc_path}: {e}")

def run_batch_processing():
    """
    Поиск и обработка всех конвертированных документов
    """
    # Получаем список конвертированных файлов
    all_docs = get_converted_files(DATA_DIR)
    
    if not all_docs:
        print("Нет конвертированных документов для обработки")
        return
    
    print(f"Найдено конвертированных документов: {len(all_docs)}")
    
    total_triplets = 0
    processed_count = 0
    
    for doc in all_docs:
        try:
            process_document(doc)
            processed_count += 1
            
            # Подсчитываем триплеты из результата
            result_file = OUTPUT_DIR / f"{doc.stem}_graph.json"
            if result_file.exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    total_triplets += result.get('triplets_count', 0)
                    
        except Exception as e:
            print(f"Ошибка обработки {doc.name}: {e}")
    
    print(f"Обработка завершена:")
    print(f"   Обработано: {processed_count} документов")
    print(f"   Извлечено: {total_triplets} триплетов")
    print(f"   Результаты: {OUTPUT_DIR}")
    
    # Создаём сводный отчёт
    create_summary_report(processed_count, total_triplets)

def build_kag_graph(converted_dir=None):
    """
    Строит граф знаний из конвертированных документов
    """
    if converted_dir:
        global DATA_DIR
        DATA_DIR = Path(converted_dir)
    
    print("🧠 Построение графа знаний...")
    run_batch_processing()
    print("✅ Граф знаний построен!")

def create_summary_report(processed_count: int, total_triplets: int):
    """Создание сводного отчёта по обработке"""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "processed_documents": processed_count,
        "total_triplets": total_triplets,
        "average_triplets_per_doc": total_triplets / max(processed_count, 1),
        "conversion_dir": str(DATA_DIR),
        "output_dir": str(OUTPUT_DIR)
    }
    
    summary_file = OUTPUT_DIR / "processing_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"Сводный отчёт: {summary_file}")

if __name__ == "__main__":
    run_batch_processing()
