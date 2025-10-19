# TERAG Initialization Task for Cursor IDE

## 🎯 Цель
Подготовить среду разработки и воспроизвести базовую инфраструктуру TERAG:
Ollama runtime → RAG service → Graph layer → CI pipeline.

---

## 1️⃣ Проверить среду
```bash
ollama --version
python --version
```

Если Python < 3.10 — установить актуальную ([https://python.org](https://python.org)).

---

## 2️⃣ Установить зависимости Python

```bash
pip install chromadb langchain langchain-community ragas fastapi uvicorn neo4j networkx pyvis loguru
```

---

## 3️⃣ Создать индексатор кода

Создай файл:
`index_codebase.py`

```python
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
import os

def index_repository(repo_path):
    loader = DirectoryLoader(repo_path, glob="**/*.py")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_documents(docs)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    Chroma.from_documents(texts, embeddings, persist_directory="./chroma_store").persist()

if __name__ == "__main__":
    path = input("Введите путь к проекту: ")
    index_repository(path)
    print("✅ Индексация завершена.")
```

---

## 4️⃣ Создать RAG-запросник

Файл: `ask_rag.py`

```python
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import Ollama

def ask(query):
    llm = Ollama(model="deepseek-coder:6.7b")
    db = Chroma(persist_directory="./chroma_store", embedding_function=None)
    retriever = db.as_retriever(search_kwargs={"k": 5})
    qa = RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=retriever)
    print(qa.run(query))

if __name__ == "__main__":
    q = input("Введите вопрос: ")
    ask(q)
```

---

## 5️⃣ Настроить Neo4j (Graph-слой)

1. Установить Neo4j CE ([https://neo4j.com/download-center/#community](https://neo4j.com/download-center/#community))
2. В `.env` добавить:

   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=12345
   ```
3. Проверить соединение:

   ```bash
   python -c "from neo4j import GraphDatabase; GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','12345'))"
   ```

---

## 6️⃣ Подключить RAG к Cursor

**Settings → AI Models**

```
Provider: OpenAI
Base URL: http://localhost:11434/v1
API Key: ollama
```

**Settings → MCP Servers**

```
Name: local_rag
Command: python
Args: ["ask_rag.py"]
```

---

## 7️⃣ Проверить всё

```bash
python index_codebase.py --path "C:\Dev\Projects\TERAG"
python ask_rag.py "Где реализована функция loadGraph?"
```

Ожидаемый результат: ответ из кода с путём к файлу.

---

## ✅ Готово

После выполнения всех шагов Cursor получит:

* подключённый Ollama runtime;
* локальную RAG-память проекта;
* возможность выполнять запросы прямо из IDE (`@local_rag search`).
