import faiss
import numpy as np
import pickle
import openai
import os
from dotenv import load_dotenv
load_dotenv
# Set your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not set! Please set it using `export OPENAI_API_KEY=<your_api_key>` and retry.")

# Embed text chunks using OpenAI's embedding model
def embed_text_chunks(chunks, batch_size=32):
    embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        response = openai.Embedding.create(
            model="text-embedding-ada-002", 
            input=batch, 
            api_key=openai_api_key
        )
        batch_embeddings = [datum["embedding"] for datum in response["data"]]
        embeddings.extend(batch_embeddings)
    embeddings = np.array(embeddings)

    # Normalize for cosine similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms

# Build FAISS index with metadata (text chunks mapped to embeddings)
def build_faiss_index_with_metadata(embeddings, chunks):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Using inner product for cosine similarity
    index.add(embeddings)
    return index, chunks

# Save FAISS index and metadata
def save_index_with_metadata(index, chunks, index_file, metadata_file):
    faiss.write_index(index, index_file)
    with open(metadata_file, 'wb') as f:
        pickle.dump(chunks, f)

# Load FAISS index and metadata
def load_index_with_metadata(index_file, metadata_file):
    index = faiss.read_index(index_file)
    with open(metadata_file, 'rb') as f:
        chunks = pickle.load(f)
    return index, chunks

# Query FAISS index
def query_faiss_index(index, query_embedding, k=5):
    if query_embedding.ndim == 1:
        query_embedding = np.expand_dims(query_embedding, axis=0)
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
    distances, indices = index.search(query_embedding, k)
    return indices[0], distances[0]