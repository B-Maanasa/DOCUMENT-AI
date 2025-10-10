# modules/embed_retrieve.py

import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from modules.extract_text_tables import load_chunks as load_text_chunks
from modules.extract_images_charts import load_chunks as load_image_chunks

class EmbedRetrieve:
    def __init__(self, chunks_files, faiss_index_file, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """
        chunks_files: list of pickle files containing chunks
        faiss_index_file: path to save FAISS index
        """
        self.chunks_files = chunks_files
        self.faiss_index_file = faiss_index_file
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.chunks = []

    def load_all_chunks(self):
        all_chunks = []
        for f in self.chunks_files:
            if os.path.exists(f):
                if "images" in f or "charts" in f:
                    all_chunks.extend(load_image_chunks(f))
                else:
                    all_chunks.extend(load_text_chunks(f))
        # Filter out empty content
        self.chunks = [c for c in all_chunks if c.get("content", "").strip()]
        print(f"✅ Loaded {len(self.chunks)} valid chunks.")

    def build_index(self):
        if not self.chunks:
            raise ValueError("❌ No chunks found to build embeddings. Make sure PDFs were processed correctly.")

        texts = [c["content"] for c in self.chunks]

        # Encode embeddings
        print("⏳ Generating embeddings...")
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        dim = embeddings.shape[1]

        # Build FAISS index
        print("⏳ Building FAISS index...")
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)

        # Save index and chunks
        faiss.write_index(index, self.faiss_index_file)
        with open(self.faiss_index_file.replace(".idx", "_chunks.pkl"), "wb") as f:
            pickle.dump(self.chunks, f)

        print(f"FAISS index saved with {len(self.chunks)} chunks.")

    def load_index(self):
        if not os.path.exists(self.faiss_index_file):
            raise FileNotFoundError(f"{self.faiss_index_file} not found. Build index first.")
        self.index = faiss.read_index(self.faiss_index_file)
        with open(self.faiss_index_file.replace(".idx", "_chunks.pkl"), "rb") as f:
            self.chunks = pickle.load(f)
        print(f"✅ FAISS index loaded with {len(self.chunks)} chunks.")

    def search(self, query, top_k=5):
        if not hasattr(self, "index"):
            self.load_index()
        query = [query]
        query_emb = self.model.encode(query, convert_to_numpy=True)
        distances, indices = self.index.search(query_emb, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx >= len(self.chunks):
                continue  # skip invalid index
            chunk = self.chunks[idx]
            results.append({"chunk": chunk, "distance": dist})
        if not results:
            return [{"chunk": {"content": "❌ No relevant data found."}, "distance": None}]
        return results
