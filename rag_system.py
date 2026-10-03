from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class HomeRAGSystem:
    def __init__(self):
        print("Loading embedding model (first time takes a moment)...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        print("RAG system ready!")
    
    def log_to_text(self, log_entry):
        """Convert structured JSON log into natural language sentence"""
        timestamp = log_entry['timestamp']
        event_type = log_entry['event_type']
        name = log_entry.get('name', 'Someone')
        
        if event_type == "face_recognized":
            return f"{name} entered the home on {timestamp}."
        elif event_type == "new_registration":
            return f"{name} was registered as a new household member on {timestamp}."
        return f"Event on {timestamp}: {event_type}"
    
    def build_index_from_logs(self, logs):
        """Build FAISS index from all logs"""
        self.documents = [self.log_to_text(log) for log in logs]
        
        if self.documents:
            embeddings = self.embedder.encode(self.documents)
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(np.array(embeddings).astype('float32'))
        
        print(f"Indexed {len(self.documents)} log entries")
    
    def retrieve_relevant_logs(self, query, k=3, max_distance=1.5):
        """Find most relevant past events for a given question"""
        if len(self.documents) == 0:
            return []
        
        query_embedding = self.embedder.encode([query])
        k = min(k, len(self.documents))
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'), k
        )
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if dist <= max_distance and 0 <= idx < len(self.documents):
                results.append((self.documents[idx], dist))
        
        return results