import chromadb
from typing import List, Dict, Any, Optional

class SemanticMemoryStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        # Using default embedding function (all-MiniLM-L6-v2) for now
        self.collection = self.client.get_or_create_collection(name="memory_semantic")

    def store_turn(self, turn_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Stores a conversation turn in the semantic memory."""
        self.collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[turn_id]
        )

    def query_memory(self, query: str, n_results: int = 5) -> List[str]:
        """Queries the semantic memory for similar past turns."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        if results and "documents" in results and results["documents"]:
            return results["documents"][0]
        return []

    def clear(self):
        """Clears all semantic memory."""
        self.client.delete_collection("memory_semantic")
        self.collection = self.client.create_collection(name="memory_semantic")

global_semantic_store = SemanticMemoryStore()
