import os
import sys
from pathlib import Path
import chromadb

def quick_index():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("codebase")
    
    files_to_index = [
        "src/**/*.tsx", "src/**/*.ts", "src/**/*.js", "src/**/*.jsx",
        "*.md", "*.json", "*.py"
    ]
    
    count = 0
    for pattern in files_to_index:
        for file_path in Path(".").glob(pattern):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    collection.add(
                        documents=[content],
                        metadatas=[{"file_path": str(file_path), "file_name": file_path.name}],
                        ids=[f"doc_{count}"]
                    )
                    count += 1
                    print(f"Indexed: {file_path}")
                except Exception as e:
                    print(f"Error indexing {file_path}: {e}")
    
    print(f"SUCCESS: Indexed {count} files")

if __name__ == "__main__":
    quick_index()
