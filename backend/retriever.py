import json
import os
import faiss
import numpy as np
try:
    from .embed import embedder
except ImportError:
    from embed import embedder

class Retriever:
    def __init__(self, data_path):
        self.data_path = data_path
        self.sections = []
        self.index = None
        self.load_data()
        self.build_index()

    def load_data(self):
        if not os.path.exists(self.data_path):
            print(f"Data path {self.data_path} does not exist.")
            return
        
        with open(self.data_path, 'r') as f:
            self.sections = json.load(f)

    def build_index(self):
        if not self.sections:
            return

        texts = [f"{s['title']}: {s['description']}" for s in self.sections]
        embeddings = embedder.get_embeddings(texts)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

    def retrieve(self, query, top_k=3):
        if self.index is None:
            return []

        query_embedding = embedder.get_embeddings([query])
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < len(self.sections):
                results.append(self.sections[idx])
        
        return results

    def retrieve_law(self, query, top_k=3):
        return self.retrieve(query, top_k=top_k)

# Singleton instance
data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'ipc_sections.json')
retriever = Retriever(data_file)
