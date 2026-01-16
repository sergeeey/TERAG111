import sys
import json
import argparse
from pathlib import Path
import chromadb
from chromadb.config import Settings
import networkx as nx
from neo4j import GraphDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TERAGRAG:
    def __init__(self, db_path="chroma_db", neo4j_uri="bolt://localhost:7687", neo4j_user="neo4j", neo4j_password="12345"):
        self.db_path = db_path
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        # РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.chroma_collection = self.chroma_client.get_collection("codebase")
        
        # РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ NetworkX
        if Path("code_graph.gml").exists():
            self.nx_graph = nx.read_gml("code_graph.gml")
        else:
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
    
    def search(self, query, n_results=5, use_graph=False):
        # РЎРµРјР°РЅС‚РёС‡РµСЃРєРёР№ РїРѕРёСЃРє РІ ChromaDB
        results = self.chroma_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        print(f"Query: {query}")
        print("Semantic Search Results:")
        print("=" * 50)
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            print(f"{i+1}. {metadata['file_name']} (similarity: {1-distance:.3f})")
            print(f"   Path: {metadata['file_path']}")
            print(f"   Content: {doc[:200]}...")
            print()
        
        # Р“СЂР°С„РѕРІС‹Р№ РїРѕРёСЃРє РµСЃР»Рё Р·Р°РїСЂРѕС€РµРЅ
        if use_graph and self.neo4j_available:
            self._graph_search(query)
    
    def _graph_search(self, query):
        print("Graph Search Results:")
        print("=" * 50)
        
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (f:File)
                WHERE f.file_name CONTAINS  OR f.file_path CONTAINS 
                RETURN f.file_name, f.file_path, f.file_type
                LIMIT 5
            """, query=query)
            
            for record in result:
                print(f"FILE: {record['f.file_name']} ({record['f.file_type']})")
                print(f"   Path: {record['f.file_path']}")
                print()

def main():
    parser = argparse.ArgumentParser(description="Enhanced RAG with graph support")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--n-results", type=int, default=5, help="Number of results")
    parser.add_argument("--use-graph", action="store_true", help="Use graph search")
    args = parser.parse_args()
    
    rag = TERAGRAG()
    
    if args.query:
        rag.search(args.query, n_results=args.n_results, use_graph=args.use_graph)
    else:
        query = input("Enter your question: ")
        rag.search(query, use_graph=True)

if __name__ == "__main__":
    main()
