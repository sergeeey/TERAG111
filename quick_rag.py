import sys
import chromadb

def quick_search(query):
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("codebase")
    
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    print(f"Query: {query}")
    print("Results:")
    for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"{i+1}. {meta['file_name']}")
        print(f"   {doc[:200]}...")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        quick_search(" ".join(sys.argv[1:]))
    else:
        query = input("Enter query: ")
        quick_search(query)
