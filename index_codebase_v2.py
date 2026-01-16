import os
import sys
import json
from pathlib import Path
from datetime import datetime
import chromadb
from chromadb.config import Settings
import networkx as nx
from neo4j import GraphDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TERAGIndexer:
    def __init__(self, db_path="chroma_db", neo4j_uri="bolt://localhost:7687", neo4j_user="neo4j", neo4j_password="12345"):
        self.db_path = db_path
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        # РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.chroma_collection = self.chroma_client.get_or_create_collection("codebase")
        
        # РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ NetworkX РіСЂР°С„Р°
        self.nx_graph = nx.DiGraph()
        
        # РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ Neo4j
        try:
            self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            self.neo4j_available = True
            logger.info("Neo4j connection established")
        except Exception as e:
            logger.warning(f"Neo4j not available: {e}")
            self.neo4j_available = False
            self.neo4j_driver = None
    
    def index_repository(self, repo_path):
        logger.info(f"Indexing repository: {repo_path}")
        
        code_extensions = {'.py', '.ts', '.tsx', '.js', '.jsx', '.md', '.json', '.yml', '.yaml'}
        files_processed = 0
        
        for file_path in Path(repo_path).rglob("*"):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    file_id = f"file_{hash(str(file_path))}"
                    self.chroma_collection.add(
                        documents=[content],
                        metadatas=[{
                            "file_path": str(file_path),
                            "file_name": file_path.name,
                            "file_type": file_path.suffix,
                            "indexed_at": datetime.now().isoformat()
                        }],
                        ids=[file_id]
                    )
                    
                    files_processed += 1
                    logger.info(f"Indexed: {file_path}")
                    
                except Exception as e:
                    logger.error(f"Error indexing {file_path}: {e}")
        
        logger.info(f"Indexing completed. Processed {files_processed} files")
        return files_processed

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Index codebase with graph support")
    parser.add_argument("--path", default=".", help="Path to repository")
    args = parser.parse_args()
    
    indexer = TERAGIndexer()
    files_processed = indexer.index_repository(args.path)
    print(f"SUCCESS: Indexed {files_processed} files")

if __name__ == "__main__":
    main()
