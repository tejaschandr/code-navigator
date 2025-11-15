import chromadb
from chromadb.config import Settings
from pathlib import Path
from .scanner import CodeScanner
from .chunker import CodeChunker
from .embedder import CodeEmbedder
from .utils import get_db_path

class CodeIndexer:
    """Class for indexing a code repository; creats an embedding database
        Methods:
            -index_repository: Scans the specified directory, chunks the code files, embeds them, and indexes into a ChromaDB collection
            - get_stats: provides statistics on the indexed code chunks
    """
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = ".codebase-nav"
        
        self.client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))
        
        self.collection = self.client.get_or_create_collection(
            name="codebase",
            metadata={"description": "Code chunks with embeddings"}
        )
        
        self.scanner = CodeScanner(".")
        self.chunker = CodeChunker()
        self.embedder = CodeEmbedder()
    
    def index_repository(self, root_path="."):
        # Scan and process code files from specifid directory
        print(f" Scanning {root_path}...")
        self.scanner.root_path = Path(root_path)
        files = self.scanner.scan()
        
        print(f" Found {len(files)} files")
        
        total_chunks = 0
        
        for i, filepath in enumerate(files):
            print(f"Processing [{i+1}/{len(files)}]: {filepath}")
            
            try:
                chunks = self.chunker.chunk_file(filepath)
                
                for chunk in chunks:
                    embedded = self.embedder.embed_chunk(chunk)
                    
                    chunk_id = f"{filepath}:{chunk['name']}:{chunk['start_line']}"
                    
                    self.collection.add(
                        ids=[chunk_id],
                        embeddings=[embedded['embedding']],
                        documents=[embedded['text']],
                        metadatas=[embedded['metadata']]
                    )
                    
                    total_chunks += 1
            
            except Exception as e:
                print(f"    Error processing {filepath}: {e}")
        
        print(f"\n Indexed {total_chunks} code chunks from {len(files)} files")
        print(f" Database saved to .codebase-nav/")
    
    def get_stats(self):
        """Show indexing statistics"""
        count = self.collection.count()
        print(f" Database contains {count} code chunks")
    

if __name__ == "__main__":
    import sys
    
    indexer = CodeIndexer()
    
    if len(sys.argv) > 1:
        indexer.index_repository(sys.argv[1])
    else:
        indexer.index_repository(".")
    
    indexer.get_stats()