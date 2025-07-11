
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path


class SmartSearch_FAISS:

    def __init__(self, modelname="./gte-large") -> None:
        self.model = SentenceTransformer(modelname)
        self.index = None


    def open_file(self, filepath: str):
        path = Path(filepath)
        if path.exists():
            self.index = faiss.read_index(filepath)
            return True
        return False


    def texts_to_vector(self, texts, device: str = None):
        if self.model: 
            embeddings = self.model.encode(texts, show_progress_bar=True, device=device)
            return embeddings, embeddings.shape[1]
        return None, 0


    def add_texts_to_index(self, texts: list, device: str = None) -> bool:
        vector, dimension = self.texts_to_vector(texts)
        if not self.index and dimension > 0:
            self.index = faiss.IndexFlatL2(dimension)

        if (self.index is not None) and (vector is not None):
            self.index.add(vector)
            return True
        return False


    def save_index(self, filepath: str):
        if self.index:
            faiss.write_index(self.index, filepath)


    def add_str_to_index(self, text: str) -> bool:
        return self.add_texts_to_index([ text ])


    def search_batched(self, query: str, k: int = 20):
        if self.model:
            query_embedding = self.model.encode([query])

            distances, indices = self.index.search(query_embedding, k)

            if indices.size > 0:
                return indices[0].tolist(), distances[0].tolist()
        return [], []
