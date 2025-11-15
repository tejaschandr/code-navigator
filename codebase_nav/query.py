import chromadb
from chromadb.config import Settings
from ollama import Client
from .embedder import CodeEmbedder

class CodeNavigator:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = ".codebase-nav"
        self.client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_collection("codebase")
        self.embedder = CodeEmbedder()
        self.llm = Client()
    
    def search(self, query, n_results=5):
        query_embedding = self.embedder.embed(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results
    
    def ask(self, question):
        print(f"\n Searching for: {question}")
        
        results = self.search(question, n_results=7)
        
        if not results['documents'][0]:
            return "No relevant code found."
        
        context = "\n\n---\n\n".join(results['documents'][0]) # Document is a list of strings
        
        prompt = f"""You are analyzing a codebase. Answer the question based on this code:

{context}

Question: {question}

Provide specific file names and line numbers in your answer. Be concise."""

        print(f" Thinking...")
        
        response = self.llm.chat(
            model="qwen2.5:7b", # Fast but not best model, would be better if i had a better machine
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        print(f"\n Answer:\n")
        full_response = ""
        for chunk in response:
            content = chunk['message']['content']
            print(content, end='', flush=True)
            full_response += content
        
        print("\n")
        return full_response

if __name__ == "__main__":
    #LLM Generated Interactive Mode, might modify for less verbose output
    nav = CodeNavigator()
    
    print("=" * 60)
    print("Codebase Navigator - Interactive Mode")
    print("=" * 60)
    print(f"Indexed chunks: {nav.collection.count()}")
    print("\nAsk questions about your codebase (or 'quit' to exit)")
    print("=" * 60)
    
    while True:
        question = input("\n You: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if not question:
            continue
        
        nav.ask(question)