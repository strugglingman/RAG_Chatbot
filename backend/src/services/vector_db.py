"""Vector database service"""
import chromadb
from chromadb.utils.embedding_functions import sentence_transformer_embedding_function


class VectorDB:
    """ChromaDB wrapper"""
    
    def __init__(self, path: str, model_name: str):
        self.embedding_fun = sentence_transformer_embedding_function.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            name="docs",
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.embedding_fun
        )
    
    def upsert(self, ids: list, documents: list, metadatas: list):
        """Insert or update documents"""
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    
    def query(self, query_texts: list, n_results: int, where: dict = None, include: list = None):
        """Query similar documents"""
        return self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where,
            include=include or ["documents", "metadatas", "distances"]
        )
    
    def get(self, include: list = None):
        """Get all documents"""
        return self.collection.get(include=include or ["documents", "metadatas"])
