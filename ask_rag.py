#!/usr/bin/env python3
"""
🔍 RAG Query Interface
Интерфейс для поиска по индексированному коду
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from datetime import datetime

class RAGQueryInterface:
    def __init__(self, db_path: str = "chroma_db"):
        """Инициализация RAG-интерфейса"""
        self.db_path = db_path
        
        if not Path(db_path).exists():
            print(f"❌ Database not found: {db_path}")
            print("💡 Run: python index_codebase.py")
            sys.exit(1)
        
        self.client = chromadb.PersistentClient(path=db_path)
        try:
            self.collection = self.client.get_collection("codebase")
        except Exception as e:
            print(f"❌ Cannot access collection: {e}")
            sys.exit(1)
    
    def search(self, query: str, n_results: int = 5, file_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Выполняет поиск по запросу"""
        try:
            # Подготавливаем фильтры
            where_filter = {}
            if file_filter:
                where_filter["file_name"] = {"$contains": file_filter}
            
            # Выполняем поиск
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # Обрабатываем результаты
            processed_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                processed_results.append({
                    "rank": i + 1,
                    "content": doc,
                    "metadata": metadata,
                    "similarity_score": 1 - distance,  # Конвертируем расстояние в схожесть
                    "file_path": metadata.get("file_path", "unknown"),
                    "file_name": metadata.get("file_name", "unknown"),
                    "start_line": metadata.get("start_line", 0),
                    "end_line": metadata.get("end_line", 0),
                    "language": metadata.get("language", "unknown")
                })
            
            return processed_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def search_functions(self, function_name: str) -> List[Dict[str, Any]]:
        """Ищет функции по имени"""
        query = f"function {function_name} definition implementation"
        return self.search(query, n_results=10)
    
    def search_imports(self, module_name: str) -> List[Dict[str, Any]]:
        """Ищет импорты модуля"""
        query = f"import {module_name} from require"
        return self.search(query, n_results=10)
    
    def search_in_file(self, file_name: str, query: str) -> List[Dict[str, Any]]:
        """Ищет в конкретном файле"""
        return self.search(query, file_filter=file_name)
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """Получает полное содержимое файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Cannot read file {file_path}: {e}")
            return None
    
    def format_results(self, results: List[Dict[str, Any]], show_content: bool = True) -> str:
        """Форматирует результаты для вывода"""
        if not results:
            return "ERROR: No results found"
        
        output = []
        output.append(f"Found {len(results)} results:")
        output.append("")
        
        for result in results:
            output.append(f"FILE: {result['file_name']} (lines {result['start_line']}-{result['end_line']})")
            output.append(f"   Similarity: {result['similarity_score']:.3f}")
            output.append(f"   Language: {result['language']}")
            output.append(f"   Path: {result['file_path']}")
            
            if show_content:
                # Показываем первые 3 строки контента
                content_lines = result['content'].split('\n')[:3]
                for line in content_lines:
                    if line.strip():
                        output.append(f"   > {line.strip()}")
                if len(result['content'].split('\n')) > 3:
                    output.append("   > ...")
            
            output.append("")
        
        return '\n'.join(output)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получает статистику базы данных"""
        try:
            count = self.collection.count()
            
            # Получаем уникальные файлы
            all_metadata = self.collection.get()['metadatas']
            unique_files = set(meta.get('file_path', '') for meta in all_metadata)
            
            # Получаем языки
            languages = {}
            for meta in all_metadata:
                lang = meta.get('language', 'unknown')
                languages[lang] = languages.get(lang, 0) + 1
            
            return {
                "total_chunks": count,
                "unique_files": len(unique_files),
                "languages": languages,
                "database_path": self.db_path
            }
        except Exception as e:
            return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Query indexed codebase")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--db-path", default="chroma_db", help="ChromaDB database path")
    parser.add_argument("--n-results", type=int, default=5, help="Number of results to return")
    parser.add_argument("--file", help="Filter by file name")
    parser.add_argument("--function", help="Search for function definition")
    parser.add_argument("--import-search", help="Search for import statements")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--no-content", action="store_true", help="Don't show content preview")
    
    args = parser.parse_args()
    
    # Создаём интерфейс
    rag = RAGQueryInterface(args.db_path)
    
    # Показываем статистику
    if args.stats:
        stats = rag.get_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("DATABASE STATISTICS")
            print("====================")
            if "error" in stats:
                print(f"ERROR: {stats['error']}")
            else:
                print(f"Total chunks: {stats['total_chunks']}")
                print(f"Unique files: {stats['unique_files']}")
                print(f"Languages:")
                for lang, count in stats['languages'].items():
                    print(f"   {lang}: {count}")
        return
    
    # Проверяем запрос
    if not args.query and not args.function and not args.import_search:
        print("ERROR: No query provided")
        print("Usage examples:")
        print("   python ask_rag.py 'loadGraph function'")
        print("   python ask_rag.py --function loadGraph")
        print("   python ask_rag.py --import-search react")
        print("   python ask_rag.py --stats")
        return
    
    # Выполняем поиск
    if args.function:
        results = rag.search_functions(args.function)
    elif args.import_search:
        results = rag.search_imports(args.import_search)
    else:
        results = rag.search(args.query, n_results=args.n_results, file_filter=args.file)
    
    # Выводим результаты
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        formatted = rag.format_results(results, show_content=not args.no_content)
        print(formatted)

if __name__ == "__main__":
    main()
