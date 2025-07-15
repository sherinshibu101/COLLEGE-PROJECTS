import os
import faiss
import numpy as np
import pickle
import streamlit as st

from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential

# Get the GitHub token from Streamlit secrets or environment
token = st.secrets.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
endpoint = "https://models.github.ai/inference"
model_name = "openai/text-embedding-3-large"

client = EmbeddingsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token)
)

def embed_text_chunks(chunks):
    # chunks: list of strings
    if not isinstance(chunks, list) or not all(isinstance(chunk, str) and chunk.strip() for chunk in chunks):
        raise ValueError("Input 'chunks' must be a list of non-empty strings.")

    response = client.embed(input=chunks, model=model_name)
    if not hasattr(response, "data"):
        st.error(f"Embedding API response missing 'data' key: {response}")
        raise KeyError("API response missing 'data' key")
    embeddings = [item.embedding for item in response.data]
    embeddings = np.array(embeddings)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms

def get_query_embedding(query):
    response = client.embed(input=[query], model=model_name)
    if not hasattr(response, "data"):
        st.error(f"Embedding API response missing 'data' key: {response}")
        raise KeyError("API response missing 'data' key")
    embedding = np.array(response.data[0].embedding)
    return embedding / np.linalg.norm(embedding)

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index

def build_faiss_index_with_metadata(embeddings, chunks):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index, chunks

def save_index_with_metadata(index, chunks, index_file, metadata_file):
    faiss.write_index(index, index_file)
    with open(metadata_file, 'wb') as f:
        pickle.dump(chunks, f)

def load_index_with_metadata(index_file, metadata_file):
    index = faiss.read_index(index_file)
    with open(metadata_file, 'rb') as f:
        chunks = pickle.load(f)
    return index, chunks

def query_faiss_index(index, query_embedding, k=5):
    if query_embedding.ndim == 1:
        query_embedding = np.expand_dims(query_embedding, axis=0)
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
    distances, indices = index.search(query_embedding, k)
    return indices[0], distances[0]
