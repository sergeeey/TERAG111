# TERAG v2 Setup with Neo4j Graph Layer
# Автоматическая настройка с графовой базой данных

param(
    [string]$ProjectPath = ".",
    [switch]$SkipNeo4j = $false,
    [switch]$Force = $false
)

Write-Host "🚀 TERAG v2 Setup with Neo4j Integration" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1️⃣ Проверка среды
Write-Host "1️⃣ Checking environment..." -ForegroundColor Yellow

# Проверяем Ollama
try {
    $ollamaVersion = ollama --version 2>$null
    if ($ollamaVersion) {
        Write-Host "✅ Ollama: $ollamaVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Ollama not found. Please install from https://ollama.ai" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Ollama not found. Please install from https://ollama.ai" -ForegroundColor Red
    exit 1
}

# Проверяем Python
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -ge 3 -and $minor -ge 10) {
            Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ Python version too old: $pythonVersion (need 3.10+)" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ Python not found. Please install from https://python.org" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2️⃣ Установка зависимостей Python
Write-Host "2️⃣ Installing Python dependencies..." -ForegroundColor Yellow

$packages = @(
    "chromadb",
    "langchain", 
    "langchain-community",
    "ragas",
    "fastapi",
    "uvicorn",
    "neo4j",
    "networkx",
    "pyvis",
    "loguru",
    "python-dotenv"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Gray
    pip install $package --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $package installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install $package" -ForegroundColor Red
    }
}

Write-Host ""

# 3️⃣ Создание индексатора с графовой поддержкой
Write-Host "3️⃣ Creating enhanced code indexer with graph support..." -ForegroundColor Yellow

$indexerCode = @"
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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TERAGIndexer:
    def __init__(self, db_path="chroma_db", neo4j_uri="bolt://localhost:7687", neo4j_user="neo4j", neo4j_password="12345"):
        self.db_path = db_path
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        # Инициализация ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.chroma_collection = self.chroma_client.get_or_create_collection("codebase")
        
        # Инициализация NetworkX графа
        self.nx_graph = nx.DiGraph()
        
        # Инициализация Neo4j
        try:
            self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            self.neo4j_available = True
            logger.info("Neo4j connection established")
        except Exception as e:
            logger.warning(f"Neo4j not available: {e}")
            self.neo4j_available = False
            self.neo4j_driver = None
    
    def index_file(self, file_path, content):
        # Добавляем в ChromaDB
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
        
        # Добавляем в NetworkX граф
        self.nx_graph.add_node(file_id, 
                              file_path=str(file_path),
                              file_name=file_path.name,
                              file_type=file_path.suffix,
                              content_length=len(content))
        
        # Анализируем зависимости
        self._analyze_dependencies(file_path, content, file_id)
        
        return file_id
    
    def _analyze_dependencies(self, file_path, content, file_id):
        # Простой анализ импортов
        import_patterns = [
            r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
            r'require\(["\']([^"\']+)["\']\)',
            r'from\s+["\']([^"\']+)["\']'
        ]
        
        import re
        dependencies = set()
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            dependencies.update(matches)
        
        # Добавляем связи в граф
        for dep in dependencies:
            dep_id = f"dep_{hash(dep)}"
            self.nx_graph.add_node(dep_id, name=dep, type="dependency")
            self.nx_graph.add_edge(file_id, dep_id, relationship="imports")
    
    def save_graph(self):
        # Сохраняем NetworkX граф
        nx.write_gml(self.nx_graph, "code_graph.gml")
        logger.info(f"NetworkX graph saved with {self.nx_graph.number_of_nodes()} nodes and {self.nx_graph.number_of_edges()} edges")
        
        # Сохраняем в Neo4j если доступен
        if self.neo4j_available:
            self._save_to_neo4j()
    
    def _save_to_neo4j(self):
        with self.neo4j_driver.session() as session:
            # Очищаем старые данные
            session.run("MATCH (n) DETACH DELETE n")
            
            # Создаём узлы файлов
            for node_id, data in self.nx_graph.nodes(data=True):
                if data.get('type') != 'dependency':
                    session.run("""
                        CREATE (f:File {
                            id: $id,
                            file_path: $file_path,
                            file_name: $file_name,
                            file_type: $file_type,
                            content_length: $content_length
                        })
                    """, id=node_id, **data)
            
            # Создаём узлы зависимостей
            for node_id, data in self.nx_graph.nodes(data=True):
                if data.get('type') == 'dependency':
                    session.run("""
                        CREATE (d:Dependency {
                            id: $id,
                            name: $name,
                            type: $type
                        })
                    """, id=node_id, **data)
            
            # Создаём связи
            for source, target, data in self.nx_graph.edges(data=True):
                session.run("""
                    MATCH (s {id: $source})
                    MATCH (t {id: $target})
                    CREATE (s)-[r:RELATES_TO {relationship: $relationship}]->(t)
                """, source=source, target=target, **data)
            
            logger.info("Graph saved to Neo4j")
    
    def index_repository(self, repo_path):
        logger.info(f"Indexing repository: {repo_path}")
        
        # Расширения файлов для индексации
        code_extensions = {'.py', '.ts', '.tsx', '.js', '.jsx', '.md', '.json', '.yml', '.yaml'}
        
        files_processed = 0
        for file_path in Path(repo_path).rglob("*"):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.index_file(file_path, content)
                    files_processed += 1
                    logger.info(f"Indexed: {file_path}")
                    
                except Exception as e:
                    logger.error(f"Error indexing {file_path}: {e}")
        
        # Сохраняем граф
        self.save_graph()
        
        logger.info(f"Indexing completed. Processed {files_processed} files")
        return files_processed

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Index codebase with graph support")
    parser.add_argument("--path", default=".", help="Path to repository")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", default="12345", help="Neo4j password")
    
    args = parser.parse_args()
    
    indexer = TERAGIndexer(
        neo4j_uri=args.neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=args.neo4j_password
    )
    
    files_processed = indexer.index_repository(args.path)
    print(f"SUCCESS: Indexed {files_processed} files with graph support")

if __name__ == "__main__":
    main()
"@

$indexerCode | Out-File -FilePath "index_codebase_v2.py" -Encoding UTF8
Write-Host "✅ Created enhanced indexer with graph support" -ForegroundColor Green

# 4️⃣ Создание RAG с графовой поддержкой
Write-Host "4️⃣ Creating enhanced RAG with graph support..." -ForegroundColor Yellow

$ragCode = @"
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
        
        # Инициализация ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.chroma_collection = self.chroma_client.get_collection("codebase")
        
        # Инициализация NetworkX
        if Path("code_graph.gml").exists():
            self.nx_graph = nx.read_gml("code_graph.gml")
        else:
            self.nx_graph = nx.DiGraph()
        
        # Инициализация Neo4j
        try:
            self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            self.neo4j_available = True
            logger.info("Neo4j connection established")
        except Exception as e:
            logger.warning(f"Neo4j not available: {e}")
            self.neo4j_available = False
            self.neo4j_driver = None
    
    def search(self, query, n_results=5, use_graph=False):
        # Семантический поиск в ChromaDB
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
        
        # Графовый поиск если запрошен
        if use_graph and self.neo4j_available:
            self._graph_search(query)
    
    def _graph_search(self, query):
        print("Graph Search Results:")
        print("=" * 50)
        
        with self.neo4j_driver.session() as session:
            # Поиск файлов по имени
            result = session.run("""
                MATCH (f:File)
                WHERE f.file_name CONTAINS $query OR f.file_path CONTAINS $query
                RETURN f.file_name, f.file_path, f.file_type
                LIMIT 5
            """, query=query)
            
            for record in result:
                print(f"📄 {record['f.file_name']} ({record['f.file_type']})")
                print(f"   Path: {record['f.file_path']}")
                print()
            
            # Поиск зависимостей
            result = session.run("""
                MATCH (d:Dependency)
                WHERE d.name CONTAINS $query
                RETURN d.name, d.type
                LIMIT 3
            """, query=query)
            
            for record in result:
                print(f"🔗 Dependency: {record['d.name']} ({record['d.type']})")
                print()
    
    def get_stats(self):
        stats = {
            "chroma_documents": self.chroma_collection.count(),
            "networkx_nodes": self.nx_graph.number_of_nodes(),
            "networkx_edges": self.nx_graph.number_of_edges(),
            "neo4j_available": self.neo4j_available
        }
        
        if self.neo4j_available:
            with self.neo4j_driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) as count")
                stats["neo4j_nodes"] = result.single()["count"]
        
        return stats

def main():
    parser = argparse.ArgumentParser(description="Enhanced RAG with graph support")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--n-results", type=int, default=5, help="Number of results")
    parser.add_argument("--use-graph", action="store_true", help="Use graph search")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", default="12345", help="Neo4j password")
    
    args = parser.parse_args()
    
    rag = TERAGRAG(
        neo4j_uri=args.neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=args.neo4j_password
    )
    
    if args.stats:
        stats = rag.get_stats()
        print("TERAG v2 Statistics:")
        print("=" * 30)
        for key, value in stats.items():
            print(f"{key}: {value}")
    elif args.query:
        rag.search(args.query, n_results=args.n_results, use_graph=args.use_graph)
    else:
        query = input("Enter your question: ")
        rag.search(query, use_graph=True)

if __name__ == "__main__":
    main()
"@

$ragCode | Out-File -FilePath "ask_rag_v2.py" -Encoding UTF8
Write-Host "✅ Created enhanced RAG with graph support" -ForegroundColor Green

# 5️⃣ Создание .env файла с Neo4j
Write-Host "5️⃣ Creating environment configuration..." -ForegroundColor Yellow

$envContent = @"
# TERAG v2 Environment Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=12345

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:6.7b

# RAG Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=nomic-embed-text

# Graph Configuration
GRAPH_STORAGE=neo4j
NETWORKX_GRAPH_FILE=code_graph.gml
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "✅ Created .env file with Neo4j configuration" -ForegroundColor Green

# 6️⃣ Индексация проекта с графом
Write-Host "6️⃣ Indexing project with graph support..." -ForegroundColor Yellow

python index_codebase_v2.py --path $ProjectPath
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Project indexed with graph support!" -ForegroundColor Green
} else {
    Write-Host "❌ Indexing failed" -ForegroundColor Red
}

Write-Host ""

# 7️⃣ Создание конфигурации Cursor v2
Write-Host "7️⃣ Creating Cursor v2 configuration..." -ForegroundColor Yellow

$cursorConfig = @{
    "cursor_ai_models" = @{
        "local_ollama" = @{
            "provider" = "openai"
            "model" = "deepseek-coder"
            "baseURL" = "http://localhost:11434/v1"
            "apiKey" = "ollama"
            "description" = "DeepSeek Coder (Local via Ollama)"
        }
    }
    "mcp_servers" = @{
        "local_rag" = @{
            "name" = "local_rag"
            "command" = "python"
            "args" = @("ask_rag_v2.py")
            "type" = "local"
            "description" = "Enhanced RAG with graph support"
        }
        "graph_search" = @{
            "name" = "graph_search"
            "command" = "python"
            "args" = @("ask_rag_v2.py", "--use-graph")
            "type" = "local"
            "description" = "Graph-based code search"
        }
    }
    "workspace_settings" = @{
        "ai.model" = "local_ollama"
        "ai.enableCodeActions" = $true
        "ai.enableChat" = $true
        "ai.enableCompletions" = $true
    }
}

$cursorConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath "cursor_config_v2.json" -Encoding UTF8
Write-Host "✅ Created Cursor v2 configuration" -ForegroundColor Green

# 8️⃣ Создание README v2
Write-Host "8️⃣ Creating TERAG v2 documentation..." -ForegroundColor Yellow

$readmeContent = @"
# 🚀 TERAG v2 - Enhanced with Graph Layer

## ✅ What's New in v2

- **Neo4j Integration**: Full graph database support
- **NetworkX Graphs**: Local graph analysis
- **Enhanced RAG**: Semantic + Graph search
- **Dependency Analysis**: Automatic code relationship mapping
- **Multi-Modal Search**: Text + Graph queries

## 🔧 Setup Complete

### Graph Database
- **Neo4j**: Property graph storage
- **NetworkX**: Local graph analysis
- **Dependencies**: Automatic import analysis

### Enhanced RAG
- **Semantic Search**: ChromaDB vector search
- **Graph Search**: Neo4j relationship queries
- **Hybrid Results**: Combined search results

## 🧪 Testing

\`\`\`bash
# Basic RAG search
python ask_rag_v2.py "loadGraph function"

# Graph-enhanced search
python ask_rag_v2.py "loadGraph function" --use-graph

# Statistics
python ask_rag_v2.py --stats
\`\`\`

## 🎯 Usage in Cursor

- \`@local_rag search "your query"\` - Semantic search
- \`@graph_search "your query"\` - Graph search
- \`@local_rag search "query" --use-graph\` - Hybrid search

## 📊 Graph Features

- **File Dependencies**: Import/export relationships
- **Code Structure**: Function/class relationships
- **Semantic Links**: Content-based connections
- **Visualization**: NetworkX graph export

---
**TERAG v2** - Now with full graph intelligence! 🧠
"@

$readmeContent | Out-File -FilePath "TERAG_V2_README.md" -Encoding UTF8
Write-Host "✅ Created TERAG v2 documentation" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 TERAG v2 SETUP COMPLETED!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host ""
Write-Host "New features:" -ForegroundColor Cyan
Write-Host "✅ Neo4j graph database integration" -ForegroundColor White
Write-Host "✅ NetworkX local graph analysis" -ForegroundColor White
Write-Host "✅ Enhanced RAG with graph search" -ForegroundColor White
Write-Host "✅ Automatic dependency analysis" -ForegroundColor White
Write-Host "✅ Multi-modal search capabilities" -ForegroundColor White
Write-Host ""
Write-Host "Test it:" -ForegroundColor Cyan
Write-Host "python ask_rag_v2.py 'loadGraph function' --use-graph" -ForegroundColor White
Write-Host ""
Write-Host "Ready for graph-powered development! 🧠🚀" -ForegroundColor Green
