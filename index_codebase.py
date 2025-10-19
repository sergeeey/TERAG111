#!/usr/bin/env python3
"""
🔍 RAG Codebase Indexer
Индексирует код проекта для RAG-поиска
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import json
import hashlib
from datetime import datetime

class CodebaseIndexer:
    def __init__(self, db_path: str = "chroma_db"):
        """Инициализация индексера"""
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="codebase",
            metadata={"description": "TERAG Immersive Shell codebase"}
        )
        
        # Расширения файлов для индексации
        self.code_extensions = {
            '.ts', '.tsx', '.js', '.jsx', '.py', '.md', '.json', 
            '.yml', '.yaml', '.toml', '.txt', '.css', '.scss'
        }
        
        # Исключаемые директории
        self.exclude_dirs = {
            'node_modules', '.git', 'dist', 'build', '.next', 
            'chroma_db', '__pycache__', '.pytest_cache'
        }
    
    def should_index_file(self, file_path: Path) -> bool:
        """Проверяет, нужно ли индексировать файл"""
        # Проверяем расширение
        if file_path.suffix not in self.code_extensions:
            return False
        
        # Проверяем исключаемые директории
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return False
        
        return True
    
    def read_file_content(self, file_path: Path) -> str:
        """Читает содержимое файла с обработкой ошибок"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                print(f"WARNING: Cannot read {file_path}: {e}")
                return ""
        except Exception as e:
            print(f"WARNING: Error reading {file_path}: {e}")
            return ""
    
    def create_file_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Создаёт метаданные для файла"""
        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_extension": file_path.suffix,
            "file_size": len(content),
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "content_hash": hashlib.md5(content.encode()).hexdigest(),
            "line_count": len(content.splitlines()),
            "language": self.detect_language(file_path)
        }
    
    def detect_language(self, file_path: Path) -> str:
        """Определяет язык программирования по расширению"""
        ext_to_lang = {
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.py': 'python',
            '.md': 'markdown',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.css': 'css',
            '.scss': 'scss'
        }
        return ext_to_lang.get(file_path.suffix, 'text')
    
    def chunk_content(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Разбивает содержимое файла на чанки"""
        lines = content.splitlines()
        chunks = []
        chunk_size = 50  # строк на чанк
        overlap = 10     # перекрытие между чанками
        
        for i in range(0, len(lines), chunk_size - overlap):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            
            if chunk_content.strip():
                chunks.append({
                    "content": chunk_content,
                    "start_line": i + 1,
                    "end_line": min(i + chunk_size, len(lines)),
                    "chunk_index": len(chunks)
                })
        
        return chunks
    
    def index_directory(self, directory: Path) -> Dict[str, int]:
        """Индексирует директорию"""
        stats = {
            "files_processed": 0,
            "files_skipped": 0,
            "chunks_created": 0,
            "errors": 0
        }
        
        print(f"Indexing directory: {directory}")
        
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue
            
            if not self.should_index_file(file_path):
                stats["files_skipped"] += 1
                continue
            
            try:
                content = self.read_file_content(file_path)
                if not content:
                    stats["files_skipped"] += 1
                    continue
                
                # Создаём метаданные
                metadata = self.create_file_metadata(file_path, content)
                
                # Разбиваем на чанки
                chunks = self.chunk_content(content, file_path)
                
                # Добавляем каждый чанк в коллекцию
                for chunk in chunks:
                    chunk_id = f"{file_path.name}_{chunk['chunk_index']}"
                    chunk_metadata = {
                        **metadata,
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"],
                        "chunk_index": chunk["chunk_index"]
                    }
                    
                    self.collection.add(
                        documents=[chunk["content"]],
                        metadatas=[chunk_metadata],
                        ids=[chunk_id]
                    )
                    
                    stats["chunks_created"] += 1
                
                stats["files_processed"] += 1
                print(f"OK: Indexed: {file_path.relative_to(directory)} ({len(chunks)} chunks)")
                
            except Exception as e:
                print(f"ERROR: Error indexing {file_path}: {e}")
                stats["errors"] += 1
        
        return stats
    
    def create_index_summary(self, stats: Dict[str, int]) -> Dict[str, Any]:
        """Создаёт сводку индексации"""
        return {
            "indexed_at": datetime.now().isoformat(),
            "total_files_processed": stats["files_processed"],
            "total_files_skipped": stats["files_skipped"],
            "total_chunks_created": stats["chunks_created"],
            "total_errors": stats["errors"],
            "collection_size": self.collection.count()
        }

def main():
    parser = argparse.ArgumentParser(description="Index codebase for RAG search")
    parser.add_argument("--path", default=".", help="Path to codebase directory")
    parser.add_argument("--db-path", default="chroma_db", help="ChromaDB database path")
    parser.add_argument("--reset", action="store_true", help="Reset existing database")
    
    args = parser.parse_args()
    
    # Проверяем путь
    codebase_path = Path(args.path)
    if not codebase_path.exists():
        print(f"❌ Path does not exist: {codebase_path}")
        sys.exit(1)
    
    # Сбрасываем базу если нужно
    if args.reset and Path(args.db_path).exists():
        import shutil
        shutil.rmtree(args.db_path)
        print(f"Reset database: {args.db_path}")
    
    # Создаём индексер
    indexer = CodebaseIndexer(args.db_path)
    
    print("Starting codebase indexing...")
    print(f"Directory: {codebase_path.absolute()}")
    print(f"Database: {args.db_path}")
    print()
    
    # Индексируем
    stats = indexer.index_directory(codebase_path)
    
    # Создаём сводку
    summary = indexer.create_index_summary(stats)
    
    # Сохраняем сводку
    summary_path = Path(args.db_path) / "index_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Выводим результаты
    print()
    print("INDEXING SUMMARY")
    print("==================")
    print(f"OK: Files processed: {stats['files_processed']}")
    print(f"SKIP: Files skipped: {stats['files_skipped']}")
    print(f"CHUNKS: Chunks created: {stats['chunks_created']}")
    print(f"ERRORS: Errors: {stats['errors']}")
    print(f"COLLECTION: Collection size: {summary['collection_size']}")
    print(f"SUMMARY: Summary saved: {summary_path}")
    
    if stats['errors'] == 0:
        print("\nSUCCESS: Indexing completed successfully!")
    else:
        print(f"\nWARNING: Indexing completed with {stats['errors']} errors")

if __name__ == "__main__":
    main()
