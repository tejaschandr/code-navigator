from ollama import Client

class CodeEmbedder:
    def __init__(self):
        self.client = Client()
        self.model = "nomic-embed-text"
    
    def embed(self, text):
        response = self.client.embeddings(
            model=self.model,
            prompt=text
        )
        return response['embedding']
    
    def embed_chunk(self, chunk):
        text = f"""
File: {chunk['filepath']}
Function: {chunk['name']}
Lines: {chunk['start_line']}-{chunk['end_line']}

{chunk['content']}
"""
        
        embedding = self.embed(text)
        
        return {
            'embedding': embedding,
            'text': text,
            'metadata': {
                'filepath': chunk['filepath'],
                'name': chunk['name'],
                'start_line': chunk['start_line'],
                'end_line': chunk['end_line']
            }
        }

if __name__ == "__main__":
    from chunker import CodeChunker
    from pathlib import Path
    
    print("Pulling embedding model...")
    import subprocess
    subprocess.run(['ollama', 'pull', 'nomic-embed-text'])
    
    chunker = CodeChunker()
    embedder = CodeEmbedder()
    
    chunks = chunker.chunk_file(Path("scanner.py"))
    
    print(f"Embedding {len(chunks)} chunks...")
    embedded = embedder.embed_chunk(chunks[0])
    
    print(f"Embedding dimension: {len(embedded['embedding'])}")
    print(f"First few values: {embedded['embedding'][:5]}")